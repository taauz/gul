"""Ro'yxatdan o'tish / kirish: telefon (SMS kod) va Google."""
import json
import re
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model, login, logout
from django.http import JsonResponse
from django.utils import timezone
from django.utils.crypto import constant_time_compare, salted_hmac
from django.views.decorators.http import require_POST

from .models import PhoneCode, Profile
from .sms import send_sms

User = get_user_model()
PHONE_RE = re.compile(r"^998\d{9}$")


def _json(request):
    try:
        return json.loads(request.body or "{}")
    except ValueError:
        return {}


def _err(message, status=400, **extra):
    return JsonResponse({"ok": False, "error": message, **extra}, status=status)


def normalize_phone(raw):
    digits = re.sub(r"\D", "", str(raw or ""))
    if len(digits) == 9:
        digits = "998" + digits
    return digits if PHONE_RE.match(digits) else None


def _hash(phone, code):
    return salted_hmac("gulzor.otp", f"{phone}:{code}").hexdigest()


def user_payload(user):
    if not user.is_authenticated:
        return {"auth": False}
    profile = getattr(user, "profile", None)
    return {
        "auth": True,
        "name": user.first_name or user.username,
        "phone": (profile.phone if profile and profile.phone else ""),
        "email": user.email,
        "is_staff": user.is_staff,
    }


@require_POST
def send_code(request):
    data = _json(request)
    name = str(data.get("name", "")).strip()[:60]
    phone = normalize_phone(data.get("phone"))
    if len(name) < 2:
        return _err("Ismingizni kiriting")
    if not phone:
        return _err("Telefon raqami noto'g'ri (+998 XX XXX XX XX)")

    now = timezone.now()
    last = PhoneCode.objects.filter(phone=phone).order_by("-created_at").first()
    if last:
        wait = settings.OTP_RESEND_SECONDS - int((now - last.created_at).total_seconds())
        if wait > 0:
            return _err(f"Kodni qayta yuborish uchun {wait} soniya kuting", 429, wait=wait)
    recent = PhoneCode.objects.filter(phone=phone, created_at__gte=now - timedelta(hours=1)).count()
    if recent >= 5:
        return _err("Juda ko'p urinish. Bir soatdan keyin qayta urinib ko'ring", 429)

    code = f"{secrets.randbelow(1_000_000):06d}"
    entry = PhoneCode.objects.create(phone=phone, code_hash=_hash(phone, code))
    if not send_sms(phone, f"Gulzor: tasdiqlash kodi {code}. Uni hech kimga bermang."):
        entry.delete()
        return _err("SMS yuborib bo'lmadi, birozdan keyin qayta urinib ko'ring", 502)

    out = {"ok": True, "wait": settings.OTP_RESEND_SECONDS}
    if settings.SHOW_DEV_CODE:
        out["dev_code"] = code
    return JsonResponse(out)


@require_POST
def verify_code(request):
    data = _json(request)
    phone = normalize_phone(data.get("phone"))
    code = re.sub(r"\D", "", str(data.get("code", "")))
    name = str(data.get("name", "")).strip()[:60]
    if not phone or len(code) != 6:
        return _err("Kodni to'liq kiriting")

    entry = PhoneCode.objects.filter(phone=phone).order_by("-created_at").first()
    if not entry or (timezone.now() - entry.created_at).total_seconds() > settings.OTP_TTL_SECONDS:
        return _err("Kod muddati tugagan. Yangi kod so'rang", expired=True)
    if entry.attempts >= settings.OTP_MAX_ATTEMPTS:
        return _err("Urinishlar tugadi. Yangi kod so'rang", expired=True)

    entry.attempts += 1
    entry.save(update_fields=["attempts"])
    if not constant_time_compare(entry.code_hash, _hash(phone, code)):
        left = settings.OTP_MAX_ATTEMPTS - entry.attempts
        return _err(f"Kod noto'g'ri (yana {left} ta urinish)", left=left)

    PhoneCode.objects.filter(phone=phone).delete()

    profile = Profile.objects.filter(phone=phone).select_related("user").first()
    if profile:
        user = profile.user
    else:
        user = User.objects.filter(username=phone).first()
        if not user:
            user = User(username=phone, first_name=name)
            user.set_unusable_password()
            user.save()
        Profile.objects.get_or_create(user=user, defaults={"phone": phone, "provider": "phone"})
    if not user.is_active:
        return _err("Bu akkaunt bloklangan", 403)
    if name and not user.first_name:
        user.first_name = name
        user.save(update_fields=["first_name"])

    login(request, user)
    return JsonResponse({"ok": True, "user": user_payload(user)})


@require_POST
def google_login(request):
    if not settings.GOOGLE_CLIENT_ID:
        return _err("Google orqali kirish hali sozlanmagan", 503)
    credential = str(_json(request).get("credential", ""))
    try:
        from google.auth.transport import requests as g_requests
        from google.oauth2 import id_token
        info = id_token.verify_oauth2_token(credential, g_requests.Request(), settings.GOOGLE_CLIENT_ID)
    except ImportError:
        return _err("google-auth o'rnatilmagan: pip install -r requirements.txt", 503)
    except ValueError:
        return _err("Google tokeni yaroqsiz")
    except Exception:
        return _err("Google bilan bog'lanib bo'lmadi, qayta urinib ko'ring", 502)

    email = (info.get("email") or "").lower()
    if not email or not info.get("email_verified"):
        return _err("Google pochtasi tasdiqlanmagan")
    name = (info.get("name") or email.split("@")[0])[:150]

    user = User.objects.filter(email__iexact=email).first()
    if not user:
        username = email[:150]
        if User.objects.filter(username=username).exists():
            username = f"g_{info.get('sub', secrets.token_hex(6))}"[:150]
        user = User(username=username, email=email, first_name=name)
        user.set_unusable_password()
        user.save()
    if not user.is_active:
        return _err("Bu akkaunt bloklangan", 403)
    Profile.objects.get_or_create(user=user, defaults={"provider": "google"})

    login(request, user)
    return JsonResponse({"ok": True, "user": user_payload(user)})


@require_POST
def logout_view(request):
    logout(request)
    return JsonResponse({"ok": True})
