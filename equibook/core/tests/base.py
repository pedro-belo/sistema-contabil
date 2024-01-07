from django.urls import reverse
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

def create_children_accounts(user):
    acc1 = facade.Account.objects.get_asset(user)

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


def create_credts_and_debits(
    account: facade.Account,
    account_period: facade.AccountingPeriod,
    value,
    credit=True,
    debit=True,
    reperat=1,
):
    transaction = facade.create_transaction(
        user=account.user,
        form_data={
            "title": f"T-{time()}",
            "description": f"D-{time()}",
            "account_period": account_period,
        },
    )

    for _ in range(0, reperat):
        if credit:
            facade.Operation.objects.create(
                transaction=transaction,
                account=account,
                value=value,
                type=facade.OperationType.CREDIT,
                date=date.today(),
            )
        if debit:
            facade.Operation.objects.create(
                transaction=transaction,
                account=account,
                value=value,
                type=facade.OperationType.DEBIT,
                date=date.today(),
            )

    return transaction

def create_period(user):
    start = date(year=2024, month=1, day=31)
    end = date(year=2024, month=2, day=29)
    return facade.AccountingPeriod.objects.create(
        user=user,
        start_date=start,
        end_date=end,
        status=facade.AccountingPeriod.Status.IN_PROGRESS,
    )

def create_uploadfile(name):
    return SimpleUploadedFile(
            name=name,
            content=b"The acidity of the ketchup and sweetness of the sauce blend together giving \
                it the soul warming feel of home cooking!",
            content_type="text/plain",
        )