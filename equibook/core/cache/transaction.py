from equibook.core.models import Transaction
from django.core.cache import cache

cache_key = lambda user_id: f"u{user_id}_transaction_list"


def _get_transactions_list(user_id: int):
    transactions = Transaction.objects.filter(user_id=user_id)
    transaction_list = []

    try:
        transaction = transactions.get(next=None)
    except Transaction.DoesNotExist:
        return []

    while transaction:
        previous = getattr(transaction, "previous", None)
        next_id = transaction.next_id
        previous_id = previous.id if previous else None

        transaction_list.append(
            {
                "id": transaction.id,
                "title": transaction.title,
                "user_id": transaction.user_id,
                "period_id": transaction.period_id,
                "next_id": next_id,
                "previous_id": previous_id,
                "description": transaction.description,
                "archived": transaction.archived,
            }
        )

        transaction = previous

    return transaction_list


def cache_get_user_transactions(user_id):
    key = cache_key(user_id)
    transaction_list = cache.get(key, None)

    if transaction_list is None:
        transaction_list = _get_transactions_list(user_id)
        cache.set(key, transaction_list)

    return transaction_list


def cache_get_period_transactions(user_id, period_id):
    fn = lambda transaction: transaction["period_id"] == period_id
    return list(filter(fn, cache_get_user_transactions(user_id=user_id)))


def cache_get_transactions_refresh(user_id):
    key = cache_key(user_id)
    cache.set(key, None)
    cache_get_user_transactions(user_id)
