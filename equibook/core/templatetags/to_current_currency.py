from django import template
from decimal import Decimal

register = template.Library()


@register.filter(takes_context=True, name="to_current_currency")
def to_current_currency(value, setting):
    exchange_rate = Decimal(setting["exchange_rate"])
    base_code = setting["base_currency"]["code"]
    current_code = setting["current_currency"]["code"]
    return round(value * exchange_rate, 2) if base_code != current_code else value
