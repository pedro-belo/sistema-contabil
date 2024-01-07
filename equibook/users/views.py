from django.shortcuts import redirect
from equibook.core import facade
from django.contrib.auth.views import (
    LoginView as DjLoginView,
    LogoutView as DjLogoutView,
)
from django.views.generic import FormView
from .forms import UserCreationForm, AuthenticationForm
from django.db.transaction import atomic
from django.contrib import messages


class UserCreationView(FormView):
    form_class = UserCreationForm
    template_name = "registration/create.html"

    @atomic
    def form_valid(self, form: UserCreationForm):
        user = form.save()
        facade.user_setup(user=user, form_data=form.cleaned_data)
        messages.add_message(
            self.request,
            messages.SUCCESS,
            message=f"Usuário {user.username} cadastrado com sucesso.",
        )
        return redirect("users:login")


class LoginView(DjLoginView):
    form_class = AuthenticationForm


class LogoutView(DjLogoutView):
    ...
