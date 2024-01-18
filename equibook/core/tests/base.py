from django.urls import reverse
from decimal import Decimal
from django.test import TestCase, override_settings
from time import time
from equibook.core import facade
from equibook.users.models import User
from model_bakery import baker
from datetime import date, timedelta, datetime
from django.core.files.uploadedfile import SimpleUploadedFile


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


# TODO: Remove todas as chamadas
def create_credts_and_debits(
    account: facade.Account,
    account_period: facade.AccountingPeriod,
    value,
    credit=True,
    debit=True,
    reperat=1,
):
    raise Exception("REMOVER")


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
