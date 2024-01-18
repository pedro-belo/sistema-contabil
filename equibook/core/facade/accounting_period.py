from equibook.core.facade import base


@base.atomic
def create_first_account_period(user: base.User, form_data: dict):
    if form_data["end_date"] < form_data["start_date"]:
        raise ValueError("Data final do período deve ser maior ou igual a data inicial")

    accounting_period = base.AccountingPeriod()
    accounting_period.status = base.AccountingPeriod.Status.IN_PROGRESS
    accounting_period.user = user
    accounting_period.start_date = form_data["start_date"]
    accounting_period.end_date = form_data["end_date"]
    accounting_period.save()

    setting = base.Setting.objects.get(user=user)
    setting.defined_first_period = True
    setting.save()

    return accounting_period


def _accounting_period_close_accounts_revenue(
    result: base.Account, revenue: base.Account, transaction: base.Transaction
):
    # "Zerando" saldo da conta de Receita (revenue)
    revenue_balance = revenue.get_individual_balance()
    operation = base.Operation()
    operation.transaction = transaction
    operation.account = revenue
    operation.value = revenue_balance
    operation.type = base.OperationType.DEBIT
    operation.date = base.timezone.now()
    operation.save()

    # Transferência do saldo da conta de Receita para a conta de Resultado.
    operation = base.Operation()
    operation.transaction = transaction
    operation.account = result
    operation.value = revenue_balance
    operation.type = base.OperationType.CREDIT
    operation.date = base.timezone.now()
    operation.save()


def _accounting_period_close_accounts_expense(
    result: base.Account, expense: base.Account, transaction: base.Transaction
):
    expense_balance = expense.get_individual_balance()
    operation = base.Operation()
    operation.transaction = transaction
    operation.account = expense
    operation.value = expense_balance
    operation.type = base.OperationType.CREDIT
    operation.date = base.timezone.now()
    operation.save()

    operation = base.Operation()
    operation.transaction = transaction
    operation.account = result
    operation.value = expense_balance
    operation.type = base.OperationType.DEBIT
    operation.date = base.timezone.now()
    operation.save()


def accounting_period_close_accounts(period, form):
    transactions = base.Transaction.objects.for_period(period)

    try:
        previous = transactions.get(next=None)
    except base.Transaction.DoesNotExist:
        return

    transaction = base.Transaction()
    transaction.period = period
    transaction.user = period.user
    transaction.title = "Encerramento de Contas"
    transaction.description = ""
    transaction.next = None
    transaction.save()

    previous.next = transaction
    previous.save()

    result = base.Account.objects.get_result(period.user)

    revenue_root = base.Account.objects.get_revenue(period.user)
    for revenue in revenue_root.get_children():
        _accounting_period_close_accounts_revenue(
            result=result,
            revenue=revenue,
            transaction=transaction,
        )

    expense_root = base.Account.objects.get_expense(period.user)
    for expense in expense_root.get_children():
        _accounting_period_close_accounts_expense(
            result=result,
            expense=expense,
            transaction=transaction,
        )


def accounting_period_distribute_results(period, form: base.AccountingPeriodCloseForm):
    # Obtem a ultima transacao
    transactions = base.Transaction.objects.for_period(period)

    try:
        previous = transactions.get(next=None)
    except base.Transaction.DoesNotExist:
        return

    transaction = base.Transaction()
    transaction.period = period
    transaction.user = period.user
    transaction.title = "Distribuição de Resultados"
    transaction.description = ""
    transaction.next = None
    transaction.save()

    previous.next = transaction
    previous.save()

    result = base.Account.objects.get_result(period.user)
    operations = result.account_operation.filter(transaction__period=period)

    credit_sum = 0
    debit_sum = 0

    for operation in operations:
        value = operation.value
        if operation.is_credit():
            credit_sum += value
        elif operation.is_debit():
            debit_sum += value
        else:
            raise ValueError

    if credit_sum > debit_sum:
        # Lucro
        operation = base.Operation()
        operation.transaction = transaction
        operation.account = result
        operation.value = credit_sum - debit_sum
        operation.type = base.OperationType.DEBIT
        operation.date = base.timezone.now()
        operation.save()

        operation = base.Operation()
        operation.transaction = transaction
        operation.account = form.cleaned_data["earn_account"]
        operation.value = credit_sum - debit_sum
        operation.type = base.OperationType.CREDIT
        operation.date = base.timezone.now()
        operation.save()

    elif debit_sum > credit_sum:
        # Prejuizo
        operation = base.Operation()
        operation.transaction = transaction
        operation.account = result
        operation.value = debit_sum - credit_sum
        operation.type = base.OperationType.CREDIT
        operation.date = base.timezone.now()
        operation.save()

        operation = base.Operation()
        operation.transaction = transaction
        operation.account = form.cleaned_data["loss_account"]
        operation.value = debit_sum - credit_sum
        operation.type = base.OperationType.DEBIT
        operation.date = base.timezone.now()
        operation.save()
    else:
        raise ValueError("Caso ZERO não considerado...")

    # raise Exception


def accounting_period_close_period(
    period: base.AccountingPeriod, form: base.AccountingPeriodCreateForm
):
    period.status = base.AccountingPeriod.Status.CLOSED
    period.save()

    accounting_period = form.save(commit=False)
    accounting_period.status = base.AccountingPeriod.Status.IN_PROGRESS
    accounting_period.user = period.user
    accounting_period.save()
    return accounting_period
