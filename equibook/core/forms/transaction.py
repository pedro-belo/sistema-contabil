from typing import Any
from django import forms
from equibook.core import facade
from shared import forms as base


class TransactionForm(base.FormCustom, forms.ModelForm):
    light = {
        "title": {"class": base.entry_light},
        "description": {"class": base.entry_light},
    }

    dark = {
        "title": {"class": base.entry_dark},
        "description": {"class": base.entry_dark},
    }

    def __init__(self, *args, account_period, **kwargs):
        if "instance" in kwargs:
            self.light["archived"] = {
                "class": "form-check-input",
                "role": "switch",
            }
            self.dark["archived"] = {
                "class": "form-check-input",
                "role": "switch",
            }

        super().__init__(*args, **kwargs)
        self.account_period = account_period

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        cleaned_data["account_period"] = self.account_period
        return cleaned_data


class TransactionCreateForm(TransactionForm):
    class Meta:
        model = facade.Transaction
        fields = (
            "title",
            "description",
        )


class TransactionUpdateForm(TransactionForm):
    class Meta:
        model = facade.Transaction
        fields = (
            "title",
            "description",
            "archived",
        )
