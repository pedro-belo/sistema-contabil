from equibook.core.tests import base
from equibook.core import facade
from equibook.core.facade.base import create_dict
from equibook.core.facade.trial_balance import TrialBalanceItem
from equibook.core.cache.account import cache_get_accounts


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
