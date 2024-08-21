from django import forms
from equibook.core import facade
from shared import forms as base


class SettingForm(base.FormCustom, forms.ModelForm):
    light = {
        "entity": {"class": base.entry_light},
        "current_currency": {"class": base.select_light},
        "theme": {"class": base.select_light},
        "exchange_rate": {"class": base.entry_light},
    }

    dark = {
        "entity": {"class": base.entry_dark},
        "current_currency": {"class": base.select_dark},
        "theme": {"class": base.select_dark},
        "exchange_rate": {"class": base.entry_dark},
    }

    def clean(self):
        cleaned_data = super().clean()

        current_currency = cleaned_data.get("current_currency", None)
        exchange_rate = cleaned_data.get("exchange_rate", None)

        if (current_currency is not None) and (exchange_rate is not None):
            if (current_currency != self.instance.base_currency) and (
                exchange_rate <= 0
            ):
                raise forms.ValidationError("A taxa de câmbio deve ser maior que zero")

        return cleaned_data

    class Meta:
        model = facade.Setting
        fields = "entity", "current_currency", "exchange_rate", "theme"
