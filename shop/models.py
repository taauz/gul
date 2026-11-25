from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models

hex_validator = RegexValidator(
    r'^#[0-9a-fA-F]{6}$',
    "Rang #rrggbb ko'rinishida bo'lishi kerak (masalan #d1567a)",
)


def flower_upload_to(instance, filename):
    return "flowers/%s" % filename


class Flower(models.Model):
    """Tayyor buket — do'kon vitrinasidagi asosiy gul."""
    name = models.CharField("Nomi", max_length=120)
    price = models.PositiveIntegerField("Narxi (so'm)")
    old_price = models.PositiveIntegerField("Eski narx (chegirma uchun)", null=True, blank=True)
    badge = models.CharField("Belgi (Yangi, Hit ...)", max_length=20, blank=True)
    color = models.CharField("Asosiy rang", max_length=7, default="#eb9fb5", validators=[hex_validator])
    dark_color = models.CharField("To'q rang", max_length=7, default="#c96c8a", validators=[hex_validator])
    bg_color = models.CharField("Fon rangi", max_length=7, default="#f8e3ea", validators=[hex_validator])
    image = models.ImageField("Haqiqiy surat (ixtiyoriy)", upload_to=flower_upload_to, blank=True, null=True)
    description = models.TextField("Tavsif", blank=True)
    is_active = models.BooleanField("Vitrinada ko'rinsin", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Buket"
        verbose_name_plural = "Buketlar"
        ordering = ["-id"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        is_new_upload = bool(self.image) and not self.image._committed
        if is_new_upload:
            from .utils import standardize_image
            processed = standardize_image(self.image)
            self.image.save(self.image.name, processed, save=False)
        super().save(*args, **kwargs)

    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return round((1 - self.price / self.old_price) * 100)
        return 0

    def average_rating(self):
        values = list(self.ratings.values_list("value", flat=True))
        return round(sum(values) / len(values), 1) if values else 0

    def rating_count(self):
        return self.ratings.count()


class Comment(models.Model):
    flower = models.ForeignKey(Flower, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             on_delete=models.SET_NULL, related_name="comments")
    name = models.CharField("Mijoz ismi", max_length=60)
    text = models.CharField("Fikr", max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Komment"
        verbose_name_plural = "Kommentlar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name}: {self.text[:30]}"


class Rating(models.Model):
    flower = models.ForeignKey(Flower, related_name="ratings", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             on_delete=models.CASCADE, related_name="ratings")
    value = models.PositiveSmallIntegerField("Baho (1-5)",
                                             validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Reyting"
        verbose_name_plural = "Reytinglar"
        constraints = [
            models.UniqueConstraint(fields=["flower", "user"], name="one_rating_per_user_per_flower"),
        ]

    def __str__(self):
        return f"{self.flower.name} — {self.value}★"


class FlowerType(models.Model):
    """O'zi gul dastasi yasash bo'limi uchun bitta gul turi (Atirgul, Lola ...)."""
    name = models.CharField("Nomi", max_length=60)
    price_per_stem = models.PositiveIntegerField("Bir dona narxi (so'm)")
    color = models.CharField("Asosiy rang", max_length=7, default="#d1567a", validators=[hex_validator])
    dark_color = models.CharField("To'q rang", max_length=7, default="#8f2f4d", validators=[hex_validator])
    petal_count = models.PositiveSmallIntegerField("Gulbarglar soni (1-16)", default=6,
                                                   validators=[MinValueValidator(1), MaxValueValidator(16)])
    is_active = models.BooleanField("Faol", default=True)

    class Meta:
        verbose_name = "Gul turi (konstruktor uchun)"
        verbose_name_plural = "Gul turlari (konstruktor uchun)"
        ordering = ["id"]

    def __str__(self):
        return self.name


class WrapOption(models.Model):
    name = models.CharField("Nomi", max_length=60)
    price = models.PositiveIntegerField("Narxi (so'm)")
    color = models.CharField("Qog'oz rangi", max_length=7, default="#c9a56b", validators=[hex_validator])
    has_ribbon = models.BooleanField("Lenta bilan", default=False)
    is_active = models.BooleanField("Faol", default=True)

    class Meta:
        verbose_name = "Qadoq qog'ozi"
        verbose_name_plural = "Qadoq qog'ozlari"
        ordering = ["id"]

    def __str__(self):
        return self.name


class Profile(models.Model):
    """Mijoz profili: telefon (SMS kod bilan tasdiqlangan) yoki Google orqali kirgan."""
    PROVIDERS = [("phone", "Telefon"), ("google", "Google")]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="profile", on_delete=models.CASCADE)
    phone = models.CharField("Telefon", max_length=20, unique=True, null=True, blank=True)
    provider = models.CharField("Kirish usuli", max_length=10, choices=PROVIDERS, default="phone")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mijoz profili"
        verbose_name_plural = "Mijoz profillari"

    def __str__(self):
        return f"{self.user} ({self.get_provider_display()})"


class PhoneCode(models.Model):
    """Bir martalik SMS kod (kodning o'zi emas, xeshi saqlanadi)."""
    phone = models.CharField(max_length=20, db_index=True)
    code_hash = models.CharField(max_length=64)
    attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone} @ {self.created_at:%H:%M:%S}"


class Order(models.Model):
    PAYMENT_CHOICES = [("Naqd", "Naqd pul"), ("Karta", "Plastik karta")]
    STATUS_CHOICES = [
        ("yangi", "Yangi"),
        ("tayyorlanmoqda", "Tayyorlanmoqda"),
        ("bajarildi", "Bajarildi"),
        ("bekor", "Bekor qilindi"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             on_delete=models.SET_NULL, related_name="orders")
    customer_name = models.CharField("Mijoz ismi", max_length=120)
    phone = models.CharField("Telefon", max_length=30)
    address = models.CharField("Manzil / olib ketish", max_length=255, blank=True)
    payment_type = models.CharField("To'lov turi", max_length=10, choices=PAYMENT_CHOICES, default="Naqd")
    status = models.CharField("Holati", max_length=16, choices=STATUS_CHOICES, default="yangi")
    total = models.PositiveIntegerField("Jami summa (so'm)", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.pk} — {self.customer_name} ({self.get_status_display()})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    name = models.CharField("Mahsulot nomi", max_length=150)
    qty = models.PositiveIntegerField("Soni", default=1)
    price = models.PositiveIntegerField("Bir dona narxi")
    details = models.CharField("Tafsilot (gullar tarkibi)", max_length=255, blank=True)

    class Meta:
        verbose_name = "Buyurtma qatori"
        verbose_name_plural = "Buyurtma qatorlari"

    def __str__(self):
        return f"{self.name} x{self.qty}"
