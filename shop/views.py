import json
import re
from functools import wraps

from django.conf import settings
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .auth_api import user_payload
from .models import (Comment, Flower, FlowerType, Order, OrderItem, Rating,
                     WrapOption)


def _json(request):
    try:
        return json.loads(request.body or "{}")
    except ValueError:
        return {}


def api_login_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"ok": False, "error": "auth"}, status=401)
        return view(request, *args, **kwargs)
    return wrapper


def home(request):
    flowers = (
        Flower.objects.filter(is_active=True)
        .annotate(avg=Avg("ratings__value"), cnt=Count("ratings", distinct=True))
        .prefetch_related("comments")
    )
    flowers_data = [{
        "id": f.id,
        "name": f.name,
        "price": f.price,
        "old": f.old_price or 0,
        "discount": f.discount_percent(),
        "badge": f.badge,
        "color": f.color,
        "dark": f.dark_color,
        "bg": f.bg_color,
        "image": f.image.url if f.image else "",
        "desc": f.description,
        "avg": round(f.avg or 0, 1),
        "cnt": f.cnt,
        "comments": [{"name": c.name, "text": c.text} for c in list(f.comments.all())[:30]],
    } for f in flowers]

    types_data = [{
        "id": t.id, "name": t.name, "price": t.price_per_stem,
        "color": t.color, "dark": t.dark_color, "petals": t.petal_count,
    } for t in FlowerType.objects.filter(is_active=True)]

    wraps_data = [{
        "id": w.id, "name": w.name, "price": w.price,
        "color": w.color, "ribbon": w.has_ribbon,
    } for w in WrapOption.objects.filter(is_active=True)]

    return render(request, "shop/index.html", {
        "flowers_data": flowers_data,
        "types_data": types_data,
        "wraps_data": wraps_data,
        "me_data": user_payload(request.user),
        "config_data": {
            "google_client_id": settings.GOOGLE_CLIENT_ID,
            "panel_url": reverse("panel"),
        },
    })


@require_POST
@api_login_required
def add_comment(request, pk):
    flower = get_object_or_404(Flower, pk=pk, is_active=True)
    text = str(_json(request).get("text", "")).strip()[:280]
    if not text:
        return JsonResponse({"ok": False, "error": "Fikr bo'sh"}, status=400)
    name = (request.user.first_name or request.user.username)[:60]
    Comment.objects.create(flower=flower, user=request.user, name=name, text=text)
    return JsonResponse({"ok": True, "comment": {"name": name, "text": text}})


@require_POST
@api_login_required
def add_rating(request, pk):
    flower = get_object_or_404(Flower, pk=pk, is_active=True)
    try:
        value = int(_json(request).get("value", 0))
    except (TypeError, ValueError):
        value = 0
    if not 1 <= value <= 5:
        return JsonResponse({"ok": False, "error": "Baho 1 dan 5 gacha bo'lishi kerak"}, status=400)
    Rating.objects.update_or_create(flower=flower, user=request.user, defaults={"value": value})
    agg = flower.ratings.aggregate(avg=Avg("value"), cnt=Count("id"))
    return JsonResponse({"ok": True, "avg": round(agg["avg"] or 0, 1), "cnt": agg["cnt"]})


def _build_lines(items):
    """Narxlarni mijoz emas, server hisoblaydi. (nomi, soni, narxi, tafsilot) ro'yxatini qaytaradi."""
    lines = []
    types = {str(t.id): t for t in FlowerType.objects.filter(is_active=True)}
    for it in items[:50]:
        kind = it.get("type")
        qty = max(1, min(int(it.get("qty") or 1), 50))
        if kind == "ready":
            flower = Flower.objects.filter(pk=it.get("id"), is_active=True).first()
            if flower:
                lines.append((flower.name, qty, flower.price, ""))
        elif kind == "custom":
            total, parts = 0, []
            for type_id, amount in (it.get("selections") or {}).items():
                flower_type, amount = types.get(str(type_id)), int(amount)
                if flower_type and 0 < amount <= 200:
                    total += flower_type.price_per_stem * amount
                    parts.append(f"{flower_type.name} x{amount}")
            if not parts:
                continue
            wrap = WrapOption.objects.filter(pk=it.get("wrap"), is_active=True).first()
            if wrap:
                total += wrap.price
                parts.append(wrap.name)
            lines.append(("O'zi yasagan dasta", qty, total, ", ".join(parts)[:255]))
    return lines


@require_POST
@api_login_required
def create_order(request):
    data = _json(request)
    customer = data.get("customer") or {}
    name = str(customer.get("name", "")).strip()[:120]
    phone = str(customer.get("phone", "")).strip()[:30]
    pay = customer.get("pay") if customer.get("pay") in dict(Order.PAYMENT_CHOICES) else "Naqd"
    if not name or len(re.sub(r"\D", "", phone)) < 9:
        return JsonResponse({"ok": False, "error": "Ism va telefon raqamini to'g'ri kiriting"}, status=400)

    try:
        lines = _build_lines(data.get("items") or [])
    except (TypeError, ValueError, AttributeError):
        return JsonResponse({"ok": False, "error": "Savat ma'lumoti noto'g'ri"}, status=400)
    if not lines:
        return JsonResponse({"ok": False, "error": "Savat bo'sh"}, status=400)

    order = Order.objects.create(
        user=request.user,
        customer_name=name,
        phone=phone,
        address=str(customer.get("addr", "")).strip()[:255],
        payment_type=pay,
        total=sum(qty * price for _, qty, price, _ in lines),
    )
    OrderItem.objects.bulk_create([
        OrderItem(order=order, name=n, qty=q, price=p, details=d) for n, q, p, d in lines
    ])
    return JsonResponse({"ok": True, "order_id": order.id})


@api_login_required
def my_orders(request):
    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related("items").order_by("-created_at")[:50]
    )
    data = [{
        "id": o.id,
        "date": o.created_at.strftime("%d.%m.%Y %H:%M"),
        "status": o.status,
        "status_label": o.get_status_display(),
        "total": o.total,
        "pay": o.get_payment_type_display(),
        "items": [{"name": it.name, "qty": it.qty} for it in o.items.all()],
    } for o in orders]
    return JsonResponse({"ok": True, "orders": data})
