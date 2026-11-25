from django import template

register = template.Library()


@register.filter
def money(value):
    """185000 -> '185 000 so'm'"""
    try:
        return f"{int(value):,}".replace(",", " ") + " so'm"
    except (TypeError, ValueError):
        return value
