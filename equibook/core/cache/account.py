from equibook.core.models import Account
from django.core.cache import cache

cache_key = lambda user_id: f"u{user_id}_account"


def _get_accounts_list(user_id):
    accounts_list = []
    for account in Account.objects.filter(user_id=user_id):
        accounts_list.append(
            {
                "id": account.id,
                "name": account.name,
                "full_name": str(account),
                "path": [
                    acc.id for acc in account.get_path(self_include=False, reverse=True)
                ],
                "children": [
                    children["id"] for children in account.account_set.values("id")
                ],
                "balance_type": account.balance_type,
                "account_type": account.account_type,
                "parent": account.parent_id,
                "root_type": account.root_type,
                "user_id": account.user_id,
            }
        )

    return accounts_list


def cache_get_accounts(user_id):
    key = cache_key(user_id)
    accounts_list = cache.get(key, None)

    if accounts_list is None:
        accounts_list = _get_accounts_list(user_id)
        cache.set(key, accounts_list)

    return accounts_list


def cache_get_accounts_refresh(user_id):
    key = cache_key(user_id)
    cache.set(key, None)
    cache_get_accounts(user_id)
