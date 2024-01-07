from equibook.core.models import (
    Setting,
    Account,
    TypeOfAccount,
    TypeOfBalance,
    AccountingPeriod,
)


def user_has_period(user) -> bool:
    return AccountingPeriod.objects.filter(user=user).exists()


def user_setup(user, form_data):
    setting = Setting()
    setting.user = user
    setting.entity = form_data["entity"]
    setting.base_currency = form_data["base_currency"]
    setting.current_currency = form_data["base_currency"]
    setting.defined_first_period = False
    setting.exchange_rate = 0
    setting.save()

    Account.objects.create(
        user=user,
        name=TypeOfAccount.ASSET.label,
        account_type=TypeOfAccount.ASSET,
        balance_type=TypeOfBalance.DEBIT,
    )
    Account.objects.create(
        user=user,
        name=TypeOfAccount.LIABILITY.label,
        account_type=TypeOfAccount.LIABILITY,
        balance_type=TypeOfBalance.CREDIT,
    )
    Account.objects.create(
        user=user,
        name=TypeOfAccount.EQUITY.label,
        account_type=TypeOfAccount.EQUITY,
        balance_type=TypeOfBalance.CREDIT,
    )
    Account.objects.create(
        user=user,
        name=TypeOfAccount.REVENUE.label,
        account_type=TypeOfAccount.REVENUE,
        balance_type=TypeOfBalance.CREDIT,
    )
    Account.objects.create(
        user=user,
        name=TypeOfAccount.EXPENSE.label,
        account_type=TypeOfAccount.EXPENSE,
        balance_type=TypeOfBalance.DEBIT,
    )
    Account.objects.create(
        user=user,
        name=TypeOfAccount.RESULT.label,
        account_type=TypeOfAccount.RESULT,
        balance_type=TypeOfBalance.UNDEF,
    )
