"""SMS yuborish. Eskiz.uz sozlanmagan bo'lsa, xabar terminalga chiqariladi (faqat sinov uchun)."""
import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)

ESKIZ_API = "https://notify.eskiz.uz/api"
_token = {"value": None, "at": 0.0}


def _post(path, data, token=None):
    req = urllib.request.Request(
        ESKIZ_API + path,
        data=urllib.parse.urlencode(data).encode(),
        method="POST",
    )
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


def _get_token(force=False):
    if not force and _token["value"] and time.time() - _token["at"] < 20 * 24 * 3600:
        return _token["value"]
    data = _post("/auth/login", {"email": settings.ESKIZ_EMAIL, "password": settings.ESKIZ_PASSWORD})
    _token["value"] = data["data"]["token"]
    _token["at"] = time.time()
    return _token["value"]


def send_sms(phone, text):
    """phone: '998901234567'. Provayderga topshirilsa True qaytaradi."""
    if not settings.SMS_CONFIGURED:
        print(f"\n[SMS-TEST] {phone} raqamiga xabar: {text}\n", flush=True)
        return True

    payload = {"mobile_phone": phone, "message": text, "from": settings.ESKIZ_FROM}
    try:
        try:
            _post("/message/sms/send", payload, _get_token())
        except urllib.error.HTTPError as exc:
            if exc.code != 401:
                raise
            _post("/message/sms/send", payload, _get_token(force=True))  # token eskirgan
        return True
    except Exception:
        logger.exception("SMS yuborishda xatolik")
        return False
