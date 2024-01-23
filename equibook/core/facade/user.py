from equibook.core.models import (
    Setting,
    Account,
    AccountType,
    BalanceType,
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
        name=AccountType.ASSET.label,
        account_type=AccountType.ASSET,
        balance_type=BalanceType.DEBIT,
    )
    Account.objects.create(
        user=user,
        name=AccountType.LIABILITY.label,
        account_type=AccountType.LIABILITY,
        balance_type=BalanceType.CREDIT,
    )
    Account.objects.create(
        user=user,
        name=AccountType.EQUITY.label,
        account_type=AccountType.EQUITY,
        balance_type=BalanceType.CREDIT,
    )
    Account.objects.create(
        user=user,
        name=AccountType.REVENUE.label,
        account_type=AccountType.REVENUE,
        balance_type=BalanceType.CREDIT,
    )
    Account.objects.create(
        user=user,
        name=AccountType.EXPENSE.label,
        account_type=AccountType.EXPENSE,
        balance_type=BalanceType.DEBIT,
    )
    Account.objects.create(
        user=user,
        name=AccountType.RESULT.label,
        account_type=AccountType.RESULT,
        balance_type=BalanceType.UNDEF,
    )
