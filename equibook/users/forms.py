from equibook.users.models import User
from django.contrib.auth.forms import (
    AuthenticationForm as DjAuthenticationForm,
    UserCreationForm as DjUserCreationForm,
    UsernameField,
)
from django import forms
from equibook.core.models import Currency
from shared import forms as base


class AuthenticationForm(base.FormCustom, DjAuthenticationForm):
    widget_attrs = {
        "username": {"label": "Usuário", "class": "form-control"},
        "password": {"label": "Senha", "class": "form-control"},
    }


class UserCreationForm(base.FormCustom, DjUserCreationForm):
    widget_attrs = {
        "username": {"label": "Usuário", "class": "form-control"},
        "password1": {"label": "Senha", "class": "form-control"},
        "password2": {"label": "Repetir Senha", "class": "form-control"},
        "email": {"label": "Email", "class": "form-control"},
        "entity": {"label": "Nome", "class": "form-control"},
        "base_currency": {"label": "Moeda Base", "class": "form-select"},
    }

    entity = forms.CharField(max_length=255)

    base_currency = forms.ChoiceField(choices=Currency.choices)

    class Meta:
        model = User
        fields = ("username", "email")
        field_classes = {"username": UsernameField}
