from equibook.core.facade import base


def get_balance_accounts(user: base.User):
    try:
        return {
            "asset": base.Account.objects.get_asset(user),
            "equity": base.Account.objects.get_equity(user),
            "liability": base.Account.objects.get_liability(user),
        }
    except base.Account.DoesNotExist:
        return {}


def get_result_accounts(user: base.User):
    try:
        return {
            "revenue": base.Account.objects.get_revenue(user),
            "expense": base.Account.objects.get_expense(user),
        }
    except base.Account.DoesNotExist:
        return {}
