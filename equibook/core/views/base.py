from django.contrib import messages  # NOQA
from typing import Any  # NOQA
from django.http.response import HttpResponse  # NOQA
from equibook.core import facade  # NOQA
from equibook.users.models import User  # NOQA
from django.contrib.auth.mixins import LoginRequiredMixin as DjLoginRequiredMixin
from django.views import generic  # NOQA
from django.db import transaction  # NOQA
from django.db.models import QuerySet  # NOQA

from django.http import (  # NOQA
    Http404 as PageNotFound,
    HttpRequest,
    HttpResponse as DjHttpResponse,
)

from equibook.core.forms import (  # NOQA
    TransactionCreateForm,
    TransactionUpdateForm,
    OperationForm,
    SettingForm,
    AccountForm,
    OperationMetaForm,
    AccountingPeriodCreateFirstForm,
    AccountingPeriodCloseForm,
    AccountingPeriodCreateForm,
)

from django.shortcuts import redirect, get_object_or_404  # NOQA
from django.urls import reverse  # NOQA
from django.db.transaction import atomic  # NOQA
from django.urls import path  # NOQA


class FormMixin:
    use_form_dark_mode = True

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        if self.use_form_dark_mode:
            kwargs["dark_mode"] = self.app_settings["DARK_MODE"]

        return kwargs


def get_user_accounting_period(user):
    return facade.AccountingPeriod.objects.filter(user=user).get(
        status__in=[
            facade.AccountingPeriod.Status.IN_PROGRESS,
            facade.AccountingPeriod.Status.CLOSING_ACCOUNTS,
        ]
    )


class LoginRequiredMixin(DjLoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.app_settings = facade.get_app_settings(request.user, to_dict=True)
            try:
                self.period: facade.AccountingPeriod = get_user_accounting_period(
                    request.user
                )
            except facade.AccountingPeriod.DoesNotExist:
                self.period = None

        return super().dispatch(request, *args, **kwargs)


class FormView(FormMixin, LoginRequiredMixin, generic.FormView):
    ...


class DetailView(LoginRequiredMixin, generic.DetailView):
    ...


class TemplateView(LoginRequiredMixin, generic.TemplateView):
    ...


class ListView(LoginRequiredMixin, generic.ListView):
    ...


class UpdateView(FormMixin, LoginRequiredMixin, generic.UpdateView):
    ...


class CreateView(FormMixin, LoginRequiredMixin, generic.CreateView):
    ...


class DeleteView(LoginRequiredMixin, generic.DeleteView):
    ...


class View(LoginRequiredMixin, generic.View):
    ...


def get_transaction(view, key="transaction_id"):
    try:
        return facade.Transaction.objects.for_period(view.period).get(
            pk=view.kwargs[key]
        )
    except facade.Transaction.DoesNotExist:
        raise PageNotFound()
