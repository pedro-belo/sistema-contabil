from equibook.core.facade import base


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
