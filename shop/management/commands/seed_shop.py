from django.core.management.base import BaseCommand

from shop.models import Flower, FlowerType, WrapOption

FLOWERS = [
    # nomi, narx, eski narx, belgi, asosiy, to'q, fon
    ("Pushti orzu", 185000, None, "Hit", "#eb9fb5", "#c96c8a", "#f8e3ea"),
    ("Bahor tongi", 210000, None, "Yangi", "#f4e07c", "#d1a93a", "#f7f1d8"),
    ("Oq nafosat", 165000, None, "", "#ffffff", "#d8cfc0", "#f2ece1"),
    ("Yolg'iz atirgul", 95000, None, "", "#d1567a", "#8f2f4d", "#f6dde5"),
    ("Sokin bog'", 240000, None, "", "#bcd6b0", "#7fa06f", "#e6efe0"),
    ("Kuzgi olov", 198000, 230000, "Chegirma", "#e88a3c", "#b1591b", "#f7e3cc"),
    ("Lavanda tushi", 175000, None, "", "#b9a3e0", "#7e63b8", "#efe9f8"),
    ("Shaftoli shabada", 189000, None, "Yangi", "#f6b79a", "#d98461", "#fcebe2"),
    ("Qizil sevgi", 320000, None, "Hit", "#c8354f", "#7e1730", "#f9dfe4"),
    ("Osmon rangi", 205000, None, "", "#8fb2e8", "#4f74b8", "#e6eefb"),
    ("Quyosh nuri", 149000, 175000, "Chegirma", "#f7c948", "#c98f0e", "#fdf1cf"),
    ("Marjon tong", 225000, None, "", "#f08a8a", "#c25555", "#fbe3e1"),
    ("Bahor lolalari", 155000, None, "", "#e8604a", "#a8341f", "#fbe1da"),
    ("Nafis pion", 265000, None, "Yangi", "#f6cfe0", "#d193b0", "#fbeef4"),
    ("Ipak orzu", 180000, None, "", "#f5e6d3", "#cdb493", "#faf3ea"),
    ("Binafsha kecha", 210000, 240000, "Chegirma", "#b57edc", "#7a3fa8", "#f1e5fa"),
]

TYPES = [
    ("Atirgul", 12000, "#d1567a", "#8f2f4d", 6),
    ("Lola", 9000, "#e05a3c", "#a3341c", 5),
    ("Xrizantema", 8000, "#f4e07c", "#c9a227", 10),
    ("Gvozdika", 7000, "#eb9fb5", "#c96c8a", 8),
    ("Pion", 15000, "#f0c6d6", "#c9899f", 8),
    ("Orxideya", 18000, "#c9a0d8", "#8a5aa3", 5),
    ("Romashka", 6000, "#ffffff", "#d8cfc0", 8),
    ("Iris", 10000, "#6f7fd1", "#3f4d99", 6),
    ("Gipsofila", 5000, "#f4eef7", "#d8c9e0", 12),
    ("Kalla", 13000, "#f5f2ea", "#c9c2b0", 1),
    ("Gerbera", 11000, "#f4845f", "#c24f2c", 12),
    ("Liliya", 14000, "#f6a5c0", "#c9668a", 6),
    ("Nargis", 7000, "#f7e26b", "#d2a91f", 6),
    ("Sunbul", 9000, "#9c8bd8", "#6a58ad", 7),
]

WRAPS = [
    ("Kraft qog'oz", 8000, "#c9a56b", False),
    ("Oq qog'oz", 6000, "#f4f1ea", False),
    ("Rangli sellofan", 10000, "#f3b9c9", False),
    ("Lentali qadoq", 15000, "#efd6dc", True),
    ("Qora premium", 12000, "#3a3a40", True),
]


class Command(BaseCommand):
    help = "Gulzor uchun namunaviy ma'lumotlarni yuklaydi (qayta ishga tushirsa ham dublikat qilmaydi)"

    def handle(self, *args, **options):
        made = 0
        for name, price, old, badge, color, dark, bg in FLOWERS:
            _, created = Flower.objects.get_or_create(name=name, defaults={
                "price": price, "old_price": old, "badge": badge,
                "color": color, "dark_color": dark, "bg_color": bg})
            made += created
        self.stdout.write(self.style.SUCCESS(f"Buketlar: +{made} (jami {Flower.objects.count()})"))

        made = 0
        for name, price, color, dark, petals in TYPES:
            _, created = FlowerType.objects.get_or_create(name=name, defaults={
                "price_per_stem": price, "color": color, "dark_color": dark, "petal_count": petals})
            made += created
        self.stdout.write(self.style.SUCCESS(f"Gul turlari: +{made} (jami {FlowerType.objects.count()})"))

        made = 0
        for name, price, color, ribbon in WRAPS:
            _, created = WrapOption.objects.get_or_create(name=name, defaults={
                "price": price, "color": color, "has_ribbon": ribbon})
            made += created
        self.stdout.write(self.style.SUCCESS(f"Qadoqlar: +{made} (jami {WrapOption.objects.count()})"))
