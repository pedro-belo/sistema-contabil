from equibook.core.facade import base
from equibook.core.facade.trial_balance import TrialBalance


@base.atomic
def transaction_delete(transaction: base.Transaction):
    previous = getattr(transaction, "previous", None)
    if previous:
        previous.next = None
        previous.save()

    transaction.delete()


@base.atomic
def create_transaction(form_data: dict, user: base.User):
    transactions = base.Transaction.objects.for_user(user)
    previous = transactions.get(next=None) if transactions.count() > 0 else None

    transaction = base.Transaction()
    transaction.title = form_data["title"]
    transaction.description = form_data["description"]
    transaction.period = form_data["account_period"]
    transaction.user = user
    transaction.save()

    if previous:
        previous.next = transaction
        previous.save()

    return transaction


def move_transaction_up(transaction: base.Transaction):
    next = getattr(transaction, "next", None)
    previous = getattr(transaction, "previous", None)

    if next is None:
        # Se não há um próximo, então não existem sentido em mover para frente
        return

    if previous:
        previous.next = next
        transaction.next = None

        transaction.save()
        previous.save()

    transaction.next = next.next
    next.next = None

    next.save()
    transaction.save()

    next.next = transaction
    next.save()


def move_transaction_down(period: base.AccountingPeriod, transaction: base.Transaction):
    previous = getattr(transaction, "previous", None)

    if (previous is None) or (previous.period_id != period.id):
        return

    if getattr(previous, "previous", None):
        previous_previous = previous.previous

        previous_previous.next = transaction
        previous.next = None

        previous.save()
        previous_previous.save()

    previous.next = transaction.next
    transaction.next = previous

    transaction.save()
    previous.save()


@base.atomic
def move_transaction(
    period: base.AccountingPeriod, transaction: base.Transaction, direction: str
):
    if direction == "up":
        move_transaction_up(transaction)
        return

    if direction == "down":
        move_transaction_down(period=period, transaction=transaction)
        return

    raise ValueError("Invalid direction")


def get_transaction_details(transaction: base.Transaction, **kwargs):
    result = {
        "id": transaction.id,
        "title": transaction.title,
        "period_id": transaction.period_id,
        "archived": transaction.archived,
        "operations": [],
        "debit_sum": 0,
        "credit_sum": 0,
        "dc_cd_sub": 0,
        "has_next": transaction.next is not None,
        "has_previous": (getattr(transaction, "previous", None)) is not None
        and (transaction.previous.period == transaction.period),
    }

    cache_transactions = (
        kwargs["cache_transactions"]
        if base.has_key(kwargs, "cache_transactions")
        else base.cache_get_period_transactions(
            period_id=transaction.period_id,
            user_id=transaction.user_id,
        )
    )
    cache_accounts = (
        kwargs["cache_accounts"]
        if base.has_key(kwargs, "cache_accounts")
        else base.cache_get_accounts(transaction.user_id)
    )

    trial_balance = TrialBalance(
        transaction=transaction,
        cache_transactions=cache_transactions,
        cache_accounts=cache_accounts,
    )
    trial_balance_result = trial_balance.get_result()

    extra_fields = {
        "account_name": base.F("account__name"),
        "account_type": base.F("account__account_type"),
    }

    for instance in transaction.transaction_operation.annotate(**extra_fields).values():
        operation = {
            "id": instance["id"],
            "date": instance["date"].strftime("%d-%m-%Y"),
            "account_name": instance["account_name"],
            "account_balance": trial_balance_result["accounts"][
                instance["account_id"]
            ].balance(),
            "account_type": base.AccountType(instance["account_type"]).label,
            "get_type_display": base.OperationType(instance["type"]).label,
            "value": instance["value"],
            "debit": 0,
            "credit": 0,
        }
        if instance["type"] == base.OperationType.CREDIT:
            result["credit_sum"] += operation["value"]
            operation["credit"] = operation["value"]

        if instance["type"] == base.OperationType.DEBIT:
            result["debit_sum"] += operation["value"]
            operation["debit"] = operation["value"]

        result["operations"].append(operation)

    return result
