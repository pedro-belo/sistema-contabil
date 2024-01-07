from django import forms
from equibook.core import facade
from . import base


class AccountingPeriodCreateFirstForm(base.FormCustom, forms.ModelForm):
    light = {
        "start_date": {"class": base.entry_light},
        "end_date": {"class": base.entry_light},
    }

    dark = {
        "start_date": {"class": base.entry_dark},
        "end_date": {"class": base.entry_dark},
    }

    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get("start_date", None)
        end_date = cleaned_data.get("end_date", None)

        if (
            (start_date is not None)
            and (end_date is not None)
            and (start_date >= end_date)
        ):
            raise forms.ValidationError(
                "A data inicial deve ser maior que a data final"
            )

    class Meta:
        model = facade.AccountingPeriod
        fields = "start_date", "end_date"
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


class AccountingPeriodCloseForm(base.FormCustom, forms.ModelForm):
    light = {
        "start_date": {"class": base.entry_light},
        "end_date": {"class": base.entry_light},
        "loss_account": {"class": base.select_light},
        "earn_account": {"class": base.select_light},
    }

    dark = {
        "start_date": {"class": base.entry_dark},
        "end_date": {"class": base.entry_dark},
        "loss_account": {"class": base.select_dark},
        "earn_account": {"class": base.select_dark},
    }

    def __init__(
        self, *args, curr_period: facade.AccountingPeriod, equity_accounts, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.curr_period = curr_period
        self.fields["loss_account"].queryset = equity_accounts
        self.fields["earn_account"].queryset = equity_accounts

    loss_account = forms.ModelChoiceField(queryset=facade.Account.objects.none())
    earn_account = forms.ModelChoiceField(queryset=facade.Account.objects.none())

    def _clean_check_date_range(self, cleaned_data: dict):
        start_date = cleaned_data.get("start_date", None)
        end_date = cleaned_data.get("end_date", None)

        if start_date and start_date <= self.curr_period.end_date:
            raise forms.ValidationError(
                "O novo período contábil deve após o período anterior."
            )

        if (start_date and end_date) and (start_date >= end_date):
            raise forms.ValidationError(
                "A data inicial deve ser maior que a data final"
            )

    def clean_check_accounts(self, cleaned_data):
        loss_account = cleaned_data.get("loss_account", None)
        earn_account = cleaned_data.get("earn_account", None)

        if (loss_account and earn_account) and (loss_account.id == earn_account.id):
            raise forms.ValidationError(
                "Contas para lucro e prejuizo devem ser diferentes"
            )

    def clean(self):
        cleaned_data = super().clean()
        self._clean_check_date_range(cleaned_data=cleaned_data)
        self.clean_check_accounts(cleaned_data=cleaned_data)
        return cleaned_data

    class Meta:
        model = facade.AccountingPeriod
        fields = "start_date", "end_date"
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


class AccountingPeriodCreateForm(base.FormCustom, forms.Form):
    ...
