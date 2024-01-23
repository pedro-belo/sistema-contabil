from equibook.core.tests import base
from equibook.core import facade
from equibook.core.facade.base import create_dict
from equibook.core.facade.trial_balance import TrialBalanceItem, TrialBalance
from equibook.core.cache.account import cache_get_accounts


class TrialBalanceTestCase(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
        self.period = base.create_period(self.user)

        (
            self.asset,
            self.equity,
            self.expense,
            self.revenue,
        ) = base.setup_accounting_scenario(self.user, self.period)

        self.accounts_d = create_dict(cache_get_accounts(self.user))
        self.trial_balance = TrialBalance(
            transaction=facade.Transaction.objects.get(next=None)
        )

    def test_trial_balance_accounts_items(self):
        result = self.trial_balance.get_result()
        self.assertEqual(len(result["accounts"].keys()), 4)
        self.assertIn(self.asset.id, result["accounts"])
        self.assertIn(self.equity.id, result["accounts"])
        self.assertIn(self.expense.id, result["accounts"])
        self.assertIn(self.revenue.id, result["accounts"])        

    def test_asset(self):
        result = self.trial_balance.get_result()
        asset = result["accounts"][self.asset.id]
        self.assertEqual(asset.balance(), 1000)
        self.assertEqual(asset.debit_sum(), 1800)
        self.assertEqual(asset.credit_sum(), 800)

    def test_equity(self):
        result = self.trial_balance.get_result()
        equity = result["accounts"][self.equity.id]
        self.assertEqual(equity.balance(), 1000)
        self.assertEqual(equity.debit_sum(), 0)
        self.assertEqual(equity.credit_sum(), 1000)

    def test_expense(self):
        result = self.trial_balance.get_result()
        expense = result["accounts"][self.expense.id]
        self.assertEqual(expense.balance(), 500)
        self.assertEqual(expense.debit_sum(), 700)
        self.assertEqual(expense.credit_sum(), 200)

    def test_revenue(self):
        result = self.trial_balance.get_result()
        revenue = result["accounts"][self.revenue.id]
        self.assertEqual(revenue.balance(), 500)
        self.assertEqual(revenue.debit_sum(), 100)
        self.assertEqual(revenue.credit_sum(), 600)

class TrialBalanceItemTestCase(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
        self.period = base.create_period(self.user)

        self.acc1, self.acc2, self.acc3 = base.create_children_accounts(
            user=self.user,
            root=facade.Account.objects.get_asset(self.user),
        )

        self.accounts_d = create_dict(cache_get_accounts(self.user))

        self.balance_item = TrialBalanceItem(
            account_id=self.acc3.id, accounts_d=self.accounts_d
        )

    def test_trial_balance_item_credit_sum(self):
        self.balance_item.credit.append(1)
        self.balance_item.credit.append(3)
        self.balance_item.credit.append(7)

        self.assertEqual(self.balance_item.debit_sum(), 0)
        self.assertEqual(self.balance_item.credit_sum(), 11)

    def test_trial_balance_item_debit_sum(self):
        self.balance_item.debit.append(1)
        self.balance_item.debit.append(3)
        self.balance_item.debit.append(7)

        self.assertEqual(self.balance_item.debit_sum(), 11)
        self.assertEqual(self.balance_item.credit_sum(), 0)

    def test_get_path(self):
        path = self.balance_item.get_path()
        self.assertEqual(len(path), 2)
        account = facade.Account.objects.get(pk=self.balance_item.account["id"])

        parent = account.parent
        self.assertEqual(path[1]["id"], parent.id)
        self.assertEqual(path[1]["name"], parent.name)

        parent = parent.parent
        self.assertEqual(path[0]["id"], parent.id)
        self.assertEqual(path[0]["name"], parent.name)

    def test_balance_debit(self):
        item = TrialBalanceItem(
            account_id=facade.Account.objects.get_asset(self.user).id,
            accounts_d=self.accounts_d,
        )

        item.debit.append(3)
        item.debit.append(7)

        self.assertEqual(item.balance_debit(), 10)
        self.assertEqual(item.balance_credit(), 0)
        self.assertEqual(item.balance(), 10)

    def test_balance_credit(self):
        item = TrialBalanceItem(
            account_id=facade.Account.objects.get_equity(self.user).id,
            accounts_d=self.accounts_d,
        )

        item.credit.append(3)
        item.credit.append(7)

        self.assertEqual(item.balance_debit(), 0)
        self.assertEqual(item.balance_credit(), 10)
        self.assertEqual(item.balance(), 10)

    def test_balance_result_debit(self):
        item = TrialBalanceItem(
            account_id=facade.Account.objects.get_result(self.user).id,
            accounts_d=self.accounts_d,
        )
        item.debit.append(1)
        self.assertEqual(item.balance_debit(), 0)
        self.assertEqual(item.balance_credit(), 0)
        self.assertEqual(item.balance(), 1)

    def test_balance_result_credit(self):
        item = TrialBalanceItem(
            account_id=facade.Account.objects.get_result(self.user).id,
            accounts_d=self.accounts_d,
        )
        item.credit.append(1)
        self.assertEqual(item.balance_debit(), 0)
        self.assertEqual(item.balance_credit(), 0)
        self.assertEqual(item.balance(), 1)
