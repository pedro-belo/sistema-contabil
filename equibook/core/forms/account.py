from django import forms
from equibook.core import facade
from . import base


class AccountForm(base.FormCustom, forms.ModelForm):
    light = {
        "name": {"class": base.entry_light},
    }

    dark = {
        "name": {"class": base.entry_dark},
    }

    class Meta:
        model = facade.Account
        fields = ("name",)
