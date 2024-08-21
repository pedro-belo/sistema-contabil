from django import forms
from equibook.core import facade
from shared import forms as base


class SettingForm(base.FormCustom, forms.ModelForm):
    widget_attrs = {
        "entity": {"class": base.form_input_text},
        "current_currency": {"class": base.form_select},
        "exchange_rate": {"class": base.form_input_text},
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
        fields = ("entity", "current_currency", "exchange_rate")
