from equibook.core import facade
from . import base


def archived_is_true(transaction_d: dict):
    return transaction_d["archived"] is True


class TransactionWrapper:
    def __init__(self, transaction_id, cache_accounts, cache_transactions) -> None:
        self.cache_accounts = cache_accounts
        self.cache_transactions = cache_transactions
        self.transaction_id = transaction_id
        self._detail = None

    @property
    def detail(self):
        if self._detail is None:
            self._detail = facade.get_transaction_details(
                facade.Transaction.objects.get(pk=self.transaction_id),
                cache_transactions=self.cache_transactions,
                cache_accounts=self.cache_accounts,
            )

        return self._detail


def get_queryset(period: facade.AccountingPeriod, fn_transaction: callable = None):
    user = period.user

    if period is None:
        return []

    cache_accounts = facade.cache_get_accounts(user.id)

    period_transactions = facade.cache_get_period_transactions(
        period_id=period.id,
        user_id=period.user_id,
    )
    if fn_transaction:
        period_transactions = list(filter(fn_transaction, period_transactions))

    user_transactions = facade.cache_get_user_transactions(user_id=period.user_id)

    cache_transactions_d = {
        transaction["id"]: transaction for transaction in period_transactions
    }

    transactions = []

    try:
        transaction = period_transactions[0]
    except IndexError:
        transaction = None

    while transaction:
        transactions.append(transaction["id"])
        try:
            transaction = cache_transactions_d[transaction["previous_id"]]
        except KeyError:
            break

    return [
        TransactionWrapper(
            pk,
            cache_transactions=user_transactions,
            cache_accounts=cache_accounts,
        )
        for pk in transactions
    ]


class ArchivedTransactionListView(base.ListView):
    context_object_name = "transactions"
    template_name = "core/transaction/archived.html"
    archived_transaction_list_active = True

    def get_queryset(self) -> list:
        return (
            get_queryset(self.period, fn_transaction=archived_is_true)
            if self.period
            else []
        )


class TransactionCreateView(base.FormView):
    form_class = base.TransactionCreateForm
    template_name = "core/transaction/create/main.html"
    transaction_create_active = True

    def post(self, request, *args, **kwargs):
        if self.period is None:
            raise base.PageNotFound()

        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        return {
            **super().get_form_kwargs(),
            "account_period": self.period,
        }

    def form_valid(self, form: base.TransactionCreateForm):
        facade.create_transaction(user=self.request.user, form_data=form.cleaned_data)
        facade.cache_get_transactions_refresh(user_id=self.request.user.id)
        return base.redirect("core:transaction-list")


class TransactionListView(base.ListView):
    paginate_by = 25
    context_object_name = "transactions"
    template_name = "core/transaction/list/main.html"
    transaction_list_active = True

    def get_period_to_list(self, period_id):
        return (
            base.get_object_or_404(
                facade.AccountingPeriod,
                user=self.request.user,
                pk=period_id,
            )
            if period_id
            else self.period
        )

    def get(self, request, *args, **kwargs):
        self.period_to_list = self.get_period_to_list(
            self.kwargs.pop("period_id", None)
        )
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> list:
        return get_queryset(period=self.period_to_list) if self.period else []


class TransactionDetail(base.DetailView):
    context_object_name = "transaction"
    template_name = "core/transaction/detail/main.html"

    def get_queryset(self):
        return facade.Transaction.objects.for_user(self.request.user)


class TransactionUpdate(base.UpdateView):
    form_class = base.TransactionUpdateForm
    context_object_name = "transaction"
    template_name = "core/transaction/update.html"

    def get_queryset(self):
        return facade.Transaction.objects.for_period(self.period)

    def get_success_url(self) -> str:
        return base.reverse("core:transaction-detail", args=[self.get_object().id])

    def get_form_kwargs(self):
        return {
            **super().get_form_kwargs(),
            "account_period": self.period,
        }

    def form_valid(self, form):
        result = super().form_valid(form)
        facade.cache_get_transactions_refresh(user_id=self.request.user.id)
        return result


class BaseMoveTransaction(base.DetailView):
    direction: str

    def get(self, *args, **kwargs):
        facade.move_transaction(
            period=self.period, transaction=self.get_object(), direction=self.direction
        )
        facade.cache_get_transactions_refresh(user_id=self.request.user.id)
        return base.redirect("core:transaction-list")

    def post(self, *args, **kwargs):
        raise base.PageNotFound()

    def get_queryset(self):
        return facade.Transaction.objects.for_period(self.period)

    def get_direction(self):
        raise NotImplementedError


class MoveTransactionDownView(BaseMoveTransaction):
    direction = "down"


class MoveTransactionUpView(BaseMoveTransaction):
    direction = "up"


class TransactionDeleteView(base.DeleteView):
    def get_queryset(self):
        return facade.Transaction.objects.for_period(self.period).filter(next=None)

    def get(self, *args, **kwargs):
        raise base.PageNotFound()

    def form_valid(self, form):
        facade.transaction_delete(self.get_object())
        facade.cache_get_transactions_refresh(user_id=self.request.user.id)
        return base.redirect("core:transaction-list")

url_patterns = [
    base.path(
        "transaction/list/",
        TransactionListView.as_view(),
        name="transaction-list",
    ),
    base.path(
        "transaction/<int:period_id>/list/",
        TransactionListView.as_view(),
        name="transaction-list",
    ),
    base.path(
        "transaction/list/archived/",
        ArchivedTransactionListView.as_view(),
        name="transaction-list-archived",
    ),
    base.path(
        "transaction/create/",
        TransactionCreateView.as_view(),
        name="transaction-create",
    ),
    base.path(
        "transaction/<int:pk>/detail/",
        TransactionDetail.as_view(),
        name="transaction-detail",
    ),
    base.path(
        "transaction/<int:pk>/update/",
        TransactionUpdate.as_view(),
        name="transaction-update",
    ),
    base.path(
        "transaction/<int:pk>/delete/",
        TransactionDeleteView.as_view(),
        name="transaction-delete",
    ),
    base.path(
        "transaction/<int:pk>/move/down/",
        MoveTransactionDownView.as_view(),
        name="transaction-move-down",
    ),
    base.path(
        "transaction/<int:pk>/move/up/",
        MoveTransactionUpView.as_view(),
        name="transaction-move-up",
    ),
]
