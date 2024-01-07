from django.utils import timezone  # NOQA
from django.db.models import Sum, F  # NOQA
from datetime import datetime  # NOQA
from django.http import HttpResponse  # NOQA
from django.db.models import QuerySet  # NOQA
from equibook.users.models import User  # NOQA
from django.db.transaction import atomic  # NOQA
from equibook.core.cache.transaction import cache_get_period_transactions  # NOQA

from equibook.core.models import (  # NOQA
    Transaction,
    OperationType,
    Account,
    AccountingPeriod,
    TypeOfBalance,
    Operation,
    OperationMeta,
    TypeOfAccount,
    Setting,
)

from equibook.core.forms import (  # NOQA
    AccountForm,
    TransactionCreateForm,
    TransactionUpdateForm,
    AccountingPeriodCreateFirstForm,
    AccountingPeriodCloseForm,
    AccountingPeriodCreateForm,
)


def get_last_transaction(period: AccountingPeriod):
    transactions = Transaction.objects.for_period(period)
    return transactions.get(next=None) if transactions.count() > 0 else None


def get_first_transaction(period: AccountingPeriod):
    transactions = cache_get_period_transactions(
        period_id=period.id,
        user_id=period.user_id,
    )
    return transactions[-1]
