from django import forms

from .models import Flower, FlowerType, WrapOption


def color_widget():
    return forms.TextInput(attrs={"type": "color"})


class FlowerForm(forms.ModelForm):
    class Meta:
        model = Flower
        fields = ["name", "price", "old_price", "badge", "color", "dark_color", "bg_color",
                  "image", "description", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Masalan: Bahor tongi"}),
            "price": forms.NumberInput(attrs={"placeholder": "185000", "min": 0}),
            "old_price": forms.NumberInput(attrs={"placeholder": "Chegirma bo'lsa, eski narx", "min": 0}),
            "badge": forms.TextInput(attrs={"placeholder": "Yangi / Hit / Chegirma"}),
            "color": color_widget(),
            "dark_color": color_widget(),
            "bg_color": color_widget(),
            "description": forms.Textarea(attrs={"rows": 3, "placeholder": "Qisqa tavsif (ixtiyoriy)"}),
        }

    def clean(self):
        data = super().clean()
        price, old = data.get("price"), data.get("old_price")
        if price is not None and old and old <= price:
            self.add_error("old_price", "Eski narx yangi narxdan katta bo'lishi kerak")
        return data


class FlowerTypeForm(forms.ModelForm):
    class Meta:
        model = FlowerType
        fields = ["name", "price_per_stem", "color", "dark_color", "petal_count", "is_active"]
        widgets = {
            "color": color_widget(),
            "dark_color": color_widget(),
            "petal_count": forms.NumberInput(attrs={"min": 1, "max": 16}),
        }


class WrapOptionForm(forms.ModelForm):
    class Meta:
        model = WrapOption
        fields = ["name", "price", "color", "has_ribbon", "is_active"]
        widgets = {"color": color_widget()}
