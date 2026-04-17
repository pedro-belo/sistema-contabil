from django import forms
from equibook.core.models import AccountingPeriod, Account
from shared import forms as base


class TransactionHistoryExportForm(base.FormCustom, forms.Form):
    widget_attrs = {
        "period": {"class": base.form_select, "size": "5"},
        "account": {"class": base.form_select},
    }

    period = forms.ModelMultipleChoiceField(
        queryset=AccountingPeriod.objects.none(),
        required=False,
        label="Período(s) Contábil(is)",
        widget=forms.SelectMultiple(),
    )

    account = forms.ModelChoiceField(
        queryset=Account.objects.none(),
        required=False,
        label="Conta",
        empty_label="Todas as contas",
    )

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["period"].queryset = AccountingPeriod.objects.filter(
            user=user
        ).order_by("-start_date")
        self.fields["account"].queryset = Account.objects.for_user(
            user, include_root=False
        ).order_by("name")
