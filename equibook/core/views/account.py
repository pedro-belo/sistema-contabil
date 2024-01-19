from equibook.core import facade
from . import base


def get_user_accounts(user):
    return facade.Account.objects.for_user(user).exclude(
        account_type=facade.AccountType.RESULT
    )


def get_parent(view):
    id = view.kwargs["parent_id"]
    try:
        return get_user_accounts(view.request.user.id).get(id=id)
    except facade.Account.DoesNotExist:
        raise base.PageNotFound()


class AccountCreateView(base.FormView):
    template_name = "core/account/create.html"
    form_class = base.AccountForm

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["parent"] = get_parent(self)
        return context_data

    def form_valid(self, form):
        obj = facade.create_account(
            user=self.request.user,
            parent=get_parent(self),
            form_data=form.cleaned_data,
        )
        facade.cache_get_accounts_refresh(user_id=self.request.user.id)
        return base.redirect("core:account-detail", pk=obj.id)


class AccountUpdateView(base.UpdateView):
    template_name = "core/account/update.html"
    form_class = base.AccountForm

    def get_queryset(self):
        return get_user_accounts(self.request.user)

    def form_valid(self, form):
        result = super().form_valid(form)
        facade.cache_get_accounts_refresh(user_id=self.request.user.id)
        return result

    def get_success_url(self) -> str:
        return base.reverse("core:account-detail", args=[self.get_object().id])


class AccountDetailView(base.DetailView):
    template_name = "core/account/detail.html"
    form_class = base.AccountForm
    context_object_name = "account"

    def get_queryset(self):
        return get_user_accounts(self.request.user)

    def get_transactions_in_account(self):
        transactions = facade.Transaction.objects.for_period(
            self.period, accounts=[self.get_object()]
        ).exclude(archived=True)
        return [
            facade.get_transaction_details(transaction) for transaction in transactions
        ]

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **{"transactions": self.get_transactions_in_account(), **kwargs}
        )


class AccountDeleteView(base.DeleteView):
    def get_queryset(self):
        return facade.Account.objects.for_user(
            user=self.request.user,
            include_root=False,
        )

    def get_object(self, queryset=None):
        account: facade.Account = super().get_object()

        if not account.can_remove():
            raise base.PageNotFound()

        return account

    def get(self, *args, **kwargs):
        raise base.PageNotFound()

    def get_success_url(self) -> str:
        return base.reverse("core:account-detail", args=[self.object.parent.id])

    def form_valid(self, form):
        result = super().form_valid(form=form)
        facade.cache_get_accounts_refresh(user_id=self.request.user.id)
        return result


url_patterns = [
    base.path(
        "account/<int:pk>/detail/",
        AccountDetailView.as_view(),
        name="account-detail",
    ),
    base.path(
        "account/<int:pk>/update/",
        AccountUpdateView.as_view(),
        name="account-update",
    ),
    base.path(
        "account/<int:pk>/delete/",
        AccountDeleteView.as_view(),
        name="account-delete",
    ),
    base.path(
        "account/<int:parent_id>/create/",
        AccountCreateView.as_view(),
        name="account-create",
    ),
]
