from django.urls import reverse
from decimal import Decimal
from django.test import TestCase, override_settings
from time import time
from equibook.core import facade
from equibook.users.models import User
from model_bakery import baker
from datetime import date, timedelta, datetime
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Sum


def create_default_user(**kwargs):
    user = baker.make(User, **kwargs)
    facade.user_setup(
        user,
        form_data={
            "entity": "Entity Name",
            "base_currency": facade.Currency.BRL,
        },
    )
    return user


def create_children_accounts(user, root: facade.Account = None):
    acc1 = root if root else facade.Account.objects.get_asset(user)

    acc2 = facade.create_account(
        user=user,
        parent=acc1,
        form_data={"name": "ACC2"},
    )

    acc3 = facade.create_account(
        user=user,
        parent=acc2,
        form_data={"name": "ACC3"},
    )
    return acc1, acc2, acc3


def create_debit_and_credit(
    period: facade.AccountingPeriod,
    value: Decimal,
    debit: facade.Account = None,
    credit: facade.Account = None,
    repeat: int = 1,
) -> facade.Transaction:
    if (debit is None) and (credit is None):
        raise ValueError

    if (debit and credit) and (debit.id == credit.id):
        raise ValueError

    form_data = {
        "title": f"T-{time()}",
        "description": f"D-{time()}",
        "account_period": period,
    }

    transaction = facade.create_transaction(user=period.user, form_data=form_data)

    for _ in range(0, repeat):
        if credit is not None:
            facade.Operation.objects.create(
                transaction=transaction,
                account=credit,
                value=value,
                type=facade.OperationType.CREDIT,
                date=date.today(),
            )

        if debit is not None:
            facade.Operation.objects.create(
                transaction=transaction,
                account=debit,
                value=value,
                type=facade.OperationType.DEBIT,
                date=date.today(),
            )

    return transaction


def create_period(user, **kwargs):
    return facade.AccountingPeriod.objects.create(
        user=user,
        start_date=kwargs.get("start_date", date(year=2024, month=1, day=31)),
        end_date=kwargs.get("end_date", date(year=2024, month=2, day=29)),
        status=kwargs.get("status", facade.AccountingPeriod.Status.IN_PROGRESS),
    )


def create_uploadfile(name):
    return SimpleUploadedFile(
        name=name,
        content=b"The acidity of the ketchup and sweetness of the sauce blend together giving \
                it the soul warming feel of home cooking!",
        content_type="text/plain",
    )


def url_login_next(next: str):
    return reverse("users:login") + "?next=" + next

def setup_accounting_scenario(user, period):
    _, _, asset = create_children_accounts(user, root=facade.Account.objects.get_asset(user))
    _, equity, _ = create_children_accounts(user, root=facade.Account.objects.get_equity(user))
    _, _, expense = create_children_accounts(user, root=facade.Account.objects.get_expense(user))
    _, revenue, _ = create_children_accounts(user, root=facade.Account.objects.get_revenue(user))

    # AUMENTO DE CAPITAL
    # ASSET: 1000, EQUITY: 1000
    create_debit_and_credit(
        period=period, value=1000, debit=asset, credit=equity
    )

    # GASTO COM X
    # ASSET: 1000 - 400 = 600
    # EXPENSE: 400
    create_debit_and_credit(
        period=period, value=400, debit=expense, credit=asset
    )

    # ~GASTO
    # ASSET: 600 + 200 = 800
    # EXPENSE: 400 - 200 = 200
    create_debit_and_credit(
        period=period, value=200, debit=asset, credit=expense
    )

    # RECEITA COM A
    # ASSET: 800 + 600 = 1400
    # REVENUE: 600
    create_debit_and_credit(
        period=period, value=600, debit=asset, credit=revenue
    )

    # ~RECEITA
    # ASSET: 1300
    # REVENUE: 500
    create_debit_and_credit(
        period=period, value=100, debit=revenue, credit=asset
    )

    # Exense = Revenue
    # EXPENSE: 200 + 300 = 500
    # ASSET: 1300 - 300 = 1000
    create_debit_and_credit(
        period=period, value=300, debit=expense, credit=asset
    )

    return asset, equity, expense, revenue
