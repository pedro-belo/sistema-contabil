from equibook.core.facade import base
from equibook.core.cache.transaction import cache_get_period_transactions
from equibook.core.cache.account import cache_get_accounts


def has_key(d: dict, k):
    return k in d.keys()


class TrialBalanceItemData:
    def __init__(self, account: dict, cache_accounts: list) -> None:
        self.accounts_d = {acc["id"]: acc for acc in cache_accounts}
        self.account = account
        self.name = account["name"]
        self.credit = []
        self.debit = []

    def cd_dc_sub(self):
        return (
            self.moviment_debit() - self.moviment_credit()
            if self.account["balance_type"] == base.TypeOfBalance.DEBIT
            else self.moviment_credit() - self.moviment_debit()
        )

    def _balance(self, balance_type):
        match balance_type:
            case base.TypeOfBalance.DEBIT:
                return self.moviment_debit() - self.moviment_credit()

            case base.TypeOfBalance.CREDIT:
                self.moviment_credit() - self.moviment_debit()

            case base.TypeOfBalance.UNDEF:
                return -1

            case _:
                raise ValueError

    def balance_undef(self, expected):
        credit_sum = sum(self.credit)
        debit_sum = sum(self.debit)

        if expected == base.TypeOfBalance.DEBIT and debit_sum > credit_sum:
            return debit_sum - credit_sum

        if expected == base.TypeOfBalance.CREDIT and credit_sum > credit_sum:
            return credit_sum - debit_sum

        return 0

    def balance_credit(self):
        if self.account["balance_type"] == base.TypeOfBalance.UNDEF:
            return self.balance_undef(base.TypeOfBalance.CREDIT)

        return (
            self.moviment_credit() - self.moviment_debit()
            if self.account["balance_type"] == base.TypeOfBalance.CREDIT
            else 0
        )

    def balance_debit(self):
        if self.account["balance_type"] == base.TypeOfBalance.UNDEF:
            return self.balance_undef(base.TypeOfBalance.DEBIT)

        return (
            self.moviment_debit() - self.moviment_credit()
            if self.account["balance_type"] == base.TypeOfBalance.DEBIT
            else 0
        )

    def get_path(self):
        accounts = self.accounts_d[self.account["id"]]["path"]
        path = []

        for account_id in accounts:
            account = self.accounts_d[account_id]
            path.append(
                {
                    "id": account["id"],
                    "name": account["name"],
                }
            )

        return path

    def moviment_credit(self):
        return sum(self.credit)

    def moviment_debit(self):
        return sum(self.debit)


def create_trial_balance_item(transaction, data, operations, **kwargs):
    fn = lambda operation: operation["transaction_id"] == transaction["id"]

    cache_accounts = (
        kwargs["cache_accounts"]
        if has_key(kwargs, "cache_accounts")
        else cache_get_accounts(transaction["user_id"])
    )
    cache_accounts_d = {acc["id"]: acc for acc in cache_accounts}

    for operation in filter(fn, operations):
        account = cache_accounts_d[operation["account_id"]]

        if account["id"] not in data["accounts"]:
            data["accounts"][account["id"]] = TrialBalanceItemData(
                account, cache_accounts=cache_accounts
            )

        if operation["type"] == base.OperationType.CREDIT:
            data["accounts"][account["id"]].credit.append(operation["value"])
            data["moviment_c_sum"] += operation["value"]

        if operation["type"] == base.OperationType.DEBIT:
            data["accounts"][account["id"]].debit.append(operation["value"])
            data["moviment_d_sum"] += operation["value"]


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
        if has_key(kwargs, "cache_transactions")
        else cache_get_period_transactions(
            period_id=transaction.period_id,
            user_id=transaction.user_id,
        )
    )
    cache_accounts = (
        kwargs["cache_accounts"]
        if has_key(kwargs, "cache_accounts")
        else cache_get_accounts(transaction.user_id)
    )

    balancete = create_trial_balance(
        transaction=transaction,
        cache_transactions=cache_transactions,
        cache_accounts=cache_accounts,
    )

    extra_fields = {
        "account_name": base.F("account__name"),
        "account_type": base.F("account__account_type"),
    }

    for instance in transaction.transaction_operation.annotate(**extra_fields).values():
        operation = {
            "id": instance["id"],
            "date": instance["date"].strftime("%d-%m-%Y"),
            "account_name": instance["account_name"],
            "account_balance": balancete["accounts"][
                instance["account_id"]
            ].cd_dc_sub(),
            "account_type": base.TypeOfAccount(instance["account_type"]).label,
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


def create_trial_balance(transaction: base.Transaction, **kwargs):
    result = {
        "accounts": {},
        "moviment_c_sum": 0,
        "balance_c_sum": 0,
        "moviment_d_sum": 0,
        "balance_d_sum": 0,
    }

    cache_transactions = (
        kwargs["cache_transactions"]
        if has_key(kwargs, "cache_transactions")
        else cache_get_period_transactions(
            period_id=transaction.period_id,
            user_id=transaction.user_id,
        )
    )
    transactions_d = {t["id"]: t for t in cache_transactions}

    cache_accounts = (
        kwargs["cache_accounts"]
        if has_key(kwargs, "cache_accounts")
        else cache_get_accounts(transaction.user_id)
    )

    first = cache_transactions[-1]
    operations = list(
        base.Operation.objects.filter(transaction__user_id=transaction.user_id).values()
    )

    while first:
        create_trial_balance_item(
            transaction=first,
            data=result,
            operations=operations,
            cache_transactions=cache_transactions,
            cache_accounts=cache_accounts,
        )

        if first["id"] == transaction.id:
            break

        first = transactions_d[first["next_id"]]

    for k in result["accounts"]:
        result["balance_d_sum"] += result["accounts"][k].balance_debit()
        result["balance_c_sum"] += result["accounts"][k].balance_credit()

    return result


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
