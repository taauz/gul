"""Saytga mos uslubdagi boshqaruv paneli (faqat is_staff foydalanuvchilar)."""
from datetime import timedelta

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import FlowerForm, FlowerTypeForm, WrapOptionForm
from .models import Flower, FlowerType, Order, WrapOption

User = get_user_model()


def _fmt(n):
    return f"{int(n):,}".replace(",", " ")


def _card(title, sub, kind, color, dark="", bg="", petals="", ribbon=False, image="", tag=""):
    return {"title": title, "sub": sub, "kind": kind, "color": color, "dark": dark, "bg": bg,
            "petals": petals, "ribbon": ribbon, "image": image, "tag": tag}


def _flower_card(o):
    sub = f"{_fmt(o.price)} so'm"
    if o.discount_percent():
        sub += f" · -{o.discount_percent()}%"
    return _card(o.name, sub, "flower", o.color, o.dark_color, o.bg_color,
                 image=o.image.url if o.image else "", tag=o.badge)


def _type_card(o):
    return _card(o.name, f"{_fmt(o.price_per_stem)} so'm / dona · {o.petal_count} barg",
                 "type", o.color, o.dark_color, petals=o.petal_count)


def _wrap_card(o):
    return _card(o.name, f"{_fmt(o.price)} so'm" + (" · lentali" if o.has_ribbon else ""),
                 "wrap", o.color, ribbon=o.has_ribbon)


CONFIG = {
    "flowers": {"model": Flower, "form": FlowerForm, "title": "Buketlar (tayyor sotuvda)",
                "single": "buket", "card": _flower_card, "kind": "flower",
                "hint": "Bu yerdagilar sayt bosh sahifasida tayyor buket sifatida sotiladi."},
    "types": {"model": FlowerType, "form": FlowerTypeForm, "title": "Dona gullar (o'zi yasash uchun)",
              "single": "dona gul", "card": _type_card, "kind": "type",
              "hint": "Bu yerdagilar 'O'zingiz yasang' bo'limida bittalab tanlanadigan gullar."},
    "wraps": {"model": WrapOption, "form": WrapOptionForm, "title": "Qadoq qog'ozlari",
              "single": "qadoq", "card": _wrap_card, "kind": "wrap",
              "hint": "Konstruktorda dasta o'ralganda tanlanadigan qog'oz turlari."},
}


def _cfg(key):
    cfg = CONFIG.get(key)
    if not cfg:
        raise Http404
    return cfg


@staff_member_required
def dashboard(request):
    today = timezone.localdate()
    start = today - timedelta(days=6)
    rows = (
        Order.objects.exclude(status="bekor").filter(created_at__date__gte=start)
        .annotate(day=TruncDate("created_at")).values("day")
        .annotate(n=Count("id"), s=Sum("total")).order_by("day")
    )
    by_day = {r["day"]: r for r in rows}
    max_n = max([r["n"] for r in by_day.values()], default=0) or 1
    days = []
    for i in range(7):
        d = start + timedelta(days=i)
        r = by_day.get(d)
        n = r["n"] if r else 0
        days.append({"label": d.strftime("%d.%m"), "n": n, "s": (r["s"] or 0) if r else 0,
                     "pct": max(6, round(n / max_n * 100)) if n else 0})

    stats = {
        "new_orders": Order.objects.filter(status="yangi").count(),
        "today_orders": Order.objects.filter(created_at__date=today).count(),
        "revenue": Order.objects.filter(status="bajarildi").aggregate(s=Sum("total"))["s"] or 0,
        "customers": User.objects.filter(is_staff=False).count(),
        "flowers": Flower.objects.filter(is_active=True).count(),
    }
    recent = Order.objects.prefetch_related("items")[:6]
    return render(request, "shop/panel/dashboard.html", {
        "active": "dashboard", "stats": stats, "days": days, "recent": recent,
    })


@staff_member_required
def orders(request):
    status = request.GET.get("status", "")
    qs = Order.objects.prefetch_related("items")
    if status in dict(Order.STATUS_CHOICES):
        qs = qs.filter(status=status)
    counts = {r["status"]: r["n"] for r in Order.objects.values("status").annotate(n=Count("id"))}
    tabs = [{"key": "", "label": "Hammasi", "n": sum(counts.values())}] + [
        {"key": k, "label": label, "n": counts.get(k, 0)} for k, label in Order.STATUS_CHOICES
    ]
    return render(request, "shop/panel/orders.html", {
        "active": "orders", "orders": qs[:200], "tabs": tabs, "current": status,
        "statuses": Order.STATUS_CHOICES,
    })


@staff_member_required
@require_POST
def order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    status = request.POST.get("status")
    if status in dict(Order.STATUS_CHOICES):
        order.status = status
        order.save(update_fields=["status"])
        messages.success(request, f"Buyurtma #{order.pk} holati yangilandi")
    return redirect("panel" if request.POST.get("next") == "dashboard" else "panel_orders")


@staff_member_required
def users(request):
    customers = (
        User.objects.filter(is_staff=False).select_related("profile")
        .annotate(orders_count=Count("orders")).order_by("-date_joined")[:300]
    )
    return render(request, "shop/panel/users.html", {"active": "users", "customers": customers})


@staff_member_required
def crud_list(request, key):
    cfg = _cfg(key)
    items = []
    for obj in cfg["model"].objects.order_by("-id" if key == "flowers" else "id"):
        card = cfg["card"](obj)
        card.update(pk=obj.pk, active=obj.is_active)
        items.append(card)
    return render(request, "shop/panel/list.html", {
        "active": key, "key": key, "cfg": cfg, "items": items,
    })


@staff_member_required
def crud_form(request, key, pk=None):
    cfg = _cfg(key)
    obj = get_object_or_404(cfg["model"], pk=pk) if pk else None
    if request.method == "POST":
        form = cfg["form"](request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Saqlandi" if obj else "Yangi " + cfg["single"] + " qo'shildi")
            return redirect("panel_list", key=key)
    else:
        form = cfg["form"](instance=obj)
    return render(request, "shop/panel/form.html", {
        "active": key, "key": key, "cfg": cfg, "form": form, "obj": obj,
    })


@staff_member_required
@require_POST
def crud_delete(request, key, pk):
    obj = get_object_or_404(_cfg(key)["model"], pk=pk)
    obj.delete()
    messages.success(request, "O'chirildi")
    return redirect("panel_list", key=key)


@staff_member_required
@require_POST
def crud_toggle(request, key, pk):
    obj = get_object_or_404(_cfg(key)["model"], pk=pk)
    obj.is_active = not obj.is_active
    obj.save(update_fields=["is_active"])
    messages.success(request, "Sayt ko'rinishi yangilandi")
    return redirect("panel_list", key=key)
