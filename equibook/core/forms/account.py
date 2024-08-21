from django import forms
from equibook.core import facade
from shared import forms as base


class AccountForm(base.FormCustom, forms.ModelForm):
    widget_attrs = {
        "name": {"class": base.form_input_text},
    }

    class Meta:
        model = facade.Account
        fields = ("name",)
