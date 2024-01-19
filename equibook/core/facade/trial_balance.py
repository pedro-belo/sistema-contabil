from . import base

from equibook.core.cache.transaction import cache_get_period_transactions
from equibook.core.cache.account import cache_get_accounts


def has_key(d: dict, k):
    return k in d.keys()


class TrialBalanceItem:
    def __init__(self, account_id: int, accounts_d: dict) -> None:
        self.accounts_d = accounts_d
        self.account = accounts_d[account_id]
        self.name = self.account["name"]
        self.credit = []
        self.debit = []

    def balance(self):
        match self.account["balance_type"]:
            case base.BalanceType.DEBIT:
                return self.debit_sum() - self.credit_sum()

            case base.BalanceType.CREDIT:
                return self.credit_sum() - self.debit_sum()

            case base.BalanceType.UNDEF:
                return abs(self.debit_sum() - self.credit_sum())

            case _:
                raise ValueError("Invalid")

    def balance_credit(self):
        return (
            self.balance()
            if self.account["balance_type"] == base.BalanceType.CREDIT
            else base.Decimal("0.00")
        )

    def balance_debit(self):
        return (
            self.balance()
            if self.account["balance_type"] == base.BalanceType.DEBIT
            else base.Decimal("0.00")
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

    def credit_sum(self):
        return sum(self.credit)

    def debit_sum(self):
        return sum(self.debit)


class TrialBalance:
    def __init__(self, transaction: base.Transaction, **kwargs):
        self.result = {
            "accounts": {},
            "balance_credit_sum": 0,
            "balance_debit_sum": 0,
            "moviment_credit_sum": 0,
            "moviment_debit_sum": 0,
        }

        self.transaction = transaction

        self.user_operations = list(
            base.Operation.objects.filter(
                transaction__user_id=transaction.user_id
            ).values()
        )

        self.cache_transactions = (
            kwargs["cache_transactions"]
            if has_key(kwargs, "cache_transactions")
            else cache_get_period_transactions(
                period_id=transaction.period_id,
                user_id=transaction.user_id,
            )
        )

        self.cache_accounts = (
            kwargs["cache_accounts"]
            if has_key(kwargs, "cache_accounts")
            else cache_get_accounts(transaction.user_id)
        )

        self.transactions_d = base.create_dict(self.cache_transactions)
        self.accounts_d = base.create_dict(self.cache_accounts)

    def get_result(self):
        first = self.cache_transactions[-1]
        while first:
            self.create_trial_balance_item(transaction=first)

            if first["id"] == self.transaction.id:
                break

            first = self.transactions_d[first["next_id"]]

        self.update_balance_sum()
        return self.result

    def get_results_sorted_by_name(self):
        result = self.get_result()
        accounts = [result["accounts"][account_id] for account_id in result["accounts"]]
        result["accounts"] = sorted(accounts, key=lambda account : account.account["full_name"])
        return result

    def get_operations_in_transaction(self, transaction: dict):
        fn = lambda operation: operation["transaction_id"] == transaction["id"]
        return filter(fn, self.user_operations)

    def create_trial_balance_item(self, transaction):
        for operation in self.get_operations_in_transaction(transaction):
            account_id = operation["account_id"]

            if account_id not in self.result["accounts"]:
                self.result["accounts"][account_id] = TrialBalanceItem(
                    account_id,
                    accounts_d=self.accounts_d,
                )

            if operation["type"] == base.OperationType.CREDIT:
                self.result["accounts"][account_id].credit.append(operation["value"])
                self.result["moviment_credit_sum"] += operation["value"]

            if operation["type"] == base.OperationType.DEBIT:
                self.result["accounts"][account_id].debit.append(operation["value"])
                self.result["moviment_debit_sum"] += operation["value"]

    def update_balance_sum(self):
        for account_id in self.result["accounts"]:
            account = self.result["accounts"][account_id]
            self.result["balance_debit_sum"] += account.balance_debit()
            self.result["balance_credit_sum"] += account.balance_credit()
