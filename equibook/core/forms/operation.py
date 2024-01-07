from django import forms
from equibook.core import facade
from . import base


class OperationForm(base.FormCustom, forms.ModelForm):
    light = {
        "account": {"class": base.select_light},
        "type": {"class": base.select_light},
        "value": {"class": base.entry_light},
        "date": {"class": base.entry_light},
    }

    dark = {
        "account": {"class": base.select_dark},
        "type": {"class": base.select_dark},
        "value": {"class": base.entry_dark},
        "date": {"class": base.entry_dark},
    }

    def clean_value(self):
        value = self.cleaned_data["value"]

        if value <= 0:
            raise forms.ValidationError("Apenas valores maiores que zero.")

        return value

    def clean(self):
        cleaned_data = super().clean()

        account = self.cleaned_data.get("account", None)
        type = self.cleaned_data.get("type", None)
        value = self.cleaned_data.get("value", None)

        if (account is not None) and (type is not None) and (value is not None):
            account_balance = account.get_individual_balance()
            if account.balance_type == facade.TypeOfBalance.DEBIT:
                if (type == facade.TypeOfBalance.CREDIT) and (value > account_balance):
                    raise forms.ValidationError(
                        f"A conta {account.name} não tem saldo suficiente para este crédito."
                    )

            elif account.balance_type == facade.TypeOfBalance.CREDIT:
                if (type == facade.TypeOfBalance.DEBIT) and (value > account_balance):
                    raise forms.ValidationError(
                        f"A conta {account.name} não tem saldo suficiente para este débito."
                    )

            else:
                raise forms.ValidationError("Operação não permitida")

        return cleaned_data

    def __init__(self, *args, accounts, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["account"].queryset = accounts

    class Meta:
        model = facade.Operation
        fields = "account", "type", "value", "date"
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}


class OperationMetaForm(base.FormCustom, forms.ModelForm):
    light = {
        "description": {"class": base.entry_light},
        "document": {"class": base.entry_light},
    }

    dark = {
        "description": {"class": base.entry_dark},
        "document": {"class": base.entry_dark},
    }

    class Meta:
        model = facade.OperationMeta
        fields = "description", "document"
