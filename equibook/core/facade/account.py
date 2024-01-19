from equibook.core.facade import base


def create_account(
    user: base.User, parent: base.Account, form_data: dict
) -> base.Account:
    
    if parent is None:
        raise ValueError("Parent account cannot be null")

    account = base.Account()
    account.name = form_data["name"]
    account.balance_type = parent.balance_type
    account.account_type = base.TypeOfAccount.SUBDIVISION
    account.root_type = parent.root_type if parent.root_type else parent.account_type
    account.parent = parent
    account.user = user
    account.save()
    return account
