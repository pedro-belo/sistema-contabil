from typing import Any
from django.contrib.auth import get_user_model
from equibook.users.models import User
from django.contrib.auth.forms import (
    AuthenticationForm as DjAuthenticationForm,
    UserCreationForm as DjUserCreationForm,
    UsernameField,
)
from django import forms
from equibook.core.models import Currency


class AuthenticationForm(DjAuthenticationForm):
    def __init__(self, request, *args, **kwargs) -> None:
        super().__init__(request, *args, **kwargs)
        self.fields["username"].label = "Usuário"
        self.fields["username"].widget.attrs["class"] = "form-control"

        self.fields["password"].label = "Senha"
        self.fields["password"].widget.attrs["class"] = "form-control"


class UserCreationForm(DjUserCreationForm):
    entity = forms.CharField(max_length=255)

    base_currency = forms.ChoiceField(choices=Currency.choices)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Usuário"
        self.fields["username"].widget.attrs["class"] = "form-control"

        self.fields["password1"].label = "Senha"
        self.fields["password1"].widget.attrs["class"] = "form-control"

        self.fields["password2"].label = "Repetir Senha"
        self.fields["password2"].widget.attrs["class"] = "form-control"

        self.fields["email"].label = "Email"
        self.fields["email"].widget.attrs["class"] = "form-control"

        self.fields["entity"].label = "Nome"
        self.fields["entity"].widget.attrs["class"] = "form-control"

        self.fields["base_currency"].label = "Moeda Base"
        self.fields["base_currency"].widget.attrs["class"] = "form-select"

    class Meta:
        model = User
        fields = ("username", "email")
        field_classes = {"username": UsernameField}
