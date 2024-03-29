from equibook.core import facade
from . import base


class BalanceOrResultAccountsView(base.TemplateView):
    def get_accounts(self, user):
        raise NotImplementedError

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update(self.get_accounts(self.request.user))
        return context_data


class BalanceAccountsView(BalanceOrResultAccountsView):
    template_name = "core/reports/balance_sheet_accounts.html"
    balance_sheet_accounts_active = True

    def get_accounts(self, user):
        return facade.get_balance_accounts(user)


class ResultAccountsView(BalanceOrResultAccountsView):
    template_name = "core/reports/result_accounts.html"
    result_accounts_active = True

    def get_accounts(self, user):
        return facade.get_result_accounts(user)


class TrialBalanceView(base.DetailView):
    template_name = "core/reports/trial_balance.html"

    def get_queryset(self):
        return facade.Transaction.objects.for_user(self.request.user)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        cache_transactions = facade.cache_get_user_transactions(self.request.user.id)
        trial_balance = facade.TrialBalance(
            self.get_object(), cache_transactions=cache_transactions
        )
        context_data["trial_balance"] = trial_balance.get_results_sorted_by_name()
        return context_data


url_patterns = [
    base.path(
        "trial-balance/<int:pk>/",
        TrialBalanceView.as_view(),
        name="trial-balance",
    ),
    base.path(
        "",
        BalanceAccountsView.as_view(),
        name="balance-accounts",
    ),
    base.path(
        "result-accounts/",
        ResultAccountsView.as_view(),
        name="result-accounts",
    ),
]
