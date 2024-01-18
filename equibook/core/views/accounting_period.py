from equibook.core import facade
from equibook.core.views import base


class AccountingPeriodCreateFirstView(base.FormView):
    template_name = "core/accounting_period/create_first.html"

    def get_form_class(self) -> type:
        if facade.user_has_period(self.request.user):
            raise base.PageNotFound()

        return base.AccountingPeriodCreateFirstForm

    def form_valid(self, form: base.AccountingPeriodCreateFirstForm):
        facade.create_first_account_period(
            user=self.request.user,
            form_data=form.cleaned_data,
        )

        base.messages.add_message(
            request=self.request,
            level=base.messages.SUCCESS,
            message="O período contábil iniciado",
        )
        return base.redirect("core:balance-accounts")


class AccountingPeriodDetailView(base.FormView):
    template_name = "core/accounting_period/detail.html"
    form_class = base.AccountingPeriodCloseForm
    accounting_period_detail_active = True

    def get_form_class(self):
        if self.period and self.period.in_progress():
            return base.AccountingPeriodCreateForm

        if self.period and self.period.closing_accounts():
            return base.AccountingPeriodCloseForm

        raise base.PageNotFound()

    def _get_form_kwargs_in_progress(self):
        return {}

    def _get_form_kwargs_closing_accounts(self):
        return {
            "curr_period": self.period,
            "equity_accounts": facade.Account.objects.get_equity(
                self.request.user
            ).account_set.all(),
        }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.period.in_progress():
            kwargs.update(self._get_form_kwargs_in_progress())
        if self.period.closing_accounts():
            kwargs.update(self._get_form_kwargs_closing_accounts())
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs = {
            **super().get_context_data(**kwargs),
            "previous_periods": facade.AccountingPeriod.objects.filter(
                user=self.request.user
            ),
            "period": self.period,
            "preconditions": [],
        }

        for transaction in facade.Transaction.objects.for_period(self.period):
            balance = transaction.get_balance()
            if not balance["is_balanced"]:
                kwargs["preconditions"].append(balance)

        return kwargs

    def _form_valid_in_progress(self, form):
        self.period.status = facade.AccountingPeriod.Status.CLOSING_ACCOUNTS
        self.period.save()
        return base.redirect("core:accounting-period-detail")

    def _form_valid_closing_accounts(self, form):
        facade.accounting_period_close_accounts(self.period, form)
        facade.accounting_period_distribute_results(self.period, form)
        facade.accounting_period_close_period(self.period, form)
        return base.redirect("core:accounting-period-detail")

    @base.atomic
    def form_valid(self, form):
        if self.period.in_progress() and self.period.is_period_closeable():
            return self._form_valid_in_progress(form)

        if self.period.closing_accounts():
            return self._form_valid_closing_accounts(form)

        raise base.PageNotFound()


url_patterns = [
    base.path(
        "accounting-period/create/",
        AccountingPeriodCreateFirstView.as_view(),
        name="accounting-period-create",
    ),
    base.path(
        "accounting-period/detail/",
        AccountingPeriodDetailView.as_view(),
        name="accounting-period-detail",
    ),
]
