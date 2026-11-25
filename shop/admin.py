from django.contrib import admin

from .models import (Comment, Flower, FlowerType, Order, OrderItem, Profile,
                     Rating, WrapOption)


class CommentInline(admin.TabularInline):
    """Mijozlar saytda yozgan fikrlar — bu yerda faqat ko'rish va kerak bo'lsa o'chirish uchun."""
    model = Comment
    extra = 0
    max_num = 0  # bu yerdan yangi komment qo'shilmaydi, faqat saytdan kelganlari ko'rinadi
    fields = ("name", "text", "created_at")
    readonly_fields = ("name", "text", "created_at")
    can_delete = True
    verbose_name = "Mijoz fikri"
    verbose_name_plural = "Mijozlar fikrlari (saytdan kelgan)"


class RatingInline(admin.TabularInline):
    model = Rating
    extra = 0
    max_num = 0
    fields = ("value", "created_at")
    readonly_fields = ("value", "created_at")
    can_delete = True
    verbose_name = "Baho"
    verbose_name_plural = "Baholar (saytdan kelgan)"


@admin.register(Flower)
class FlowerAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "old_price", "badge", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    list_editable = ("price", "is_active")
    inlines = [CommentInline, RatingInline]


@admin.register(FlowerType)
class FlowerTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "price_per_stem", "petal_count", "is_active")
    list_filter = ("is_active",)


@admin.register(WrapOption)
class WrapOptionAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "color", "has_ribbon", "is_active")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "phone", "total", "payment_type", "status", "created_at")
    list_filter = ("status", "payment_type")
    search_fields = ("customer_name", "phone")
    list_editable = ("status",)
    inlines = [OrderItemInline]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "provider", "created_at")
    search_fields = ("phone", "user__first_name", "user__email")


admin.site.register(Comment)
admin.site.register(Rating)

admin.site.site_header = "Gulzor — boshqaruv paneli"
admin.site.site_title = "Gulzor admin"
admin.site.index_title = "Do'kon boshqaruvi"
