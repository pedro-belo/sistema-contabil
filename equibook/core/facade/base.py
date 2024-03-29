from decimal import Decimal  # NOQA
from django.utils import timezone  # NOQA
from django.db.models import Sum, F  # NOQA
from datetime import datetime  # NOQA
from django.http import HttpResponse  # NOQA
from django.db.models import QuerySet  # NOQA
from equibook.users.models import User  # NOQA
from django.db.transaction import atomic  # NOQA
from equibook.core.cache.transaction import cache_get_period_transactions  # NOQA
from equibook.core.cache.account import cache_get_accounts

from equibook.core.models import (  # NOQA
    Transaction,
    OperationType,
    Account,
    AccountingPeriod,
    BalanceType,
    Operation,
    OperationMeta,
    AccountType,
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


def create_dict(items, key="id"):
    return {i[key]: i for i in items}


def has_key(d: dict, k):
    return k in d.keys()
