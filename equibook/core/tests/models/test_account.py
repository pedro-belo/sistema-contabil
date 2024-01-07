from equibook.core import facade
from equibook.core.tests import base


class AccountModelTestCase(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()

    def test_can_remove_root_accounts(self):
        root_accounts = [
            facade.Account.objects.get_asset(self.user),
            facade.Account.objects.get_result(self.user),
            facade.Account.objects.get_liability(self.user),
            facade.Account.objects.get_equity(self.user),
            facade.Account.objects.get_revenue(self.user),
            facade.Account.objects.get_expense(self.user),
        ]

        for account in root_accounts:
            self.assertEqual(account.can_remove(), False)

    def test_can_remove_father_account(self):
        """
        ACC2 é "pai" da conta ACC3
        """
        _, acc1, _ = base.create_children_accounts(self.user)
        self.assertEqual(acc1.can_remove(), False)

    def test_can_delete_when_exists_operations(self):
        _, _, account = base.create_children_accounts(self.user)
        base.baker.make(facade.Operation, account=account)
        self.assertEqual(account.can_remove(), False)

    def test_can_delete_when_account_is_a_leaf(self):
        _, _, leaf = base.create_children_accounts(self.user)
        self.assertEqual(leaf.can_remove(), True)

    def test_account_pretty_name(self):
        acc1, acc2, acc3 = base.create_children_accounts(self.user)
        self.assertEqual(str(acc3), f"{acc1.name} • {acc2.name} • {acc3.name}")

    def test_get_path(self):
        acc1, acc2, acc3 = base.create_children_accounts(self.user)
        path = acc3.get_path(self_include=True, reverse=True)
        self.assertEqual(acc1.id, path[0].id)
        self.assertEqual(acc2.id, path[1].id)
        self.assertEqual(acc3.id, path[2].id)

    def test_get_recursive_childrens(self):
        ...
        # TODO

    def test_individual_balance_zero(self):
        period = base.create_period(self.user)
        _, acc, _ = base.create_children_accounts(self.user)

        base.create_credts_and_debits(
            account=acc,
            account_period=period,
            value=20,
        )
        self.assertEqual(acc.get_individual_balance(), 0)

    def test_individual_balance_debit(self):
        period = base.create_period(self.user)
        _, acc, _ = base.create_children_accounts(self.user)

        base.create_credts_and_debits(
            account=acc, account_period=period, value=20, credit=False
        )
        self.assertEqual(acc.get_individual_balance(), 20)

    def test_individual_balance_credit(self):
        period = base.create_period(self.user)
        _, acc, _ = base.create_children_accounts(self.user)

        base.create_credts_and_debits(
            account=acc, account_period=period, value=20, debit=False
        )
        self.assertEqual(acc.get_individual_balance(), -20)

    def test_total_account_balance_zero(self):
        period = base.create_period(self.user)
        _, acc1, acc2 = base.create_children_accounts(self.user)

        base.create_credts_and_debits(account=acc1, account_period=period, value=20)
        base.create_credts_and_debits(account=acc2, account_period=period, value=15)

        self.assertEqual(acc2.total_account_balance(), 0)
        self.assertEqual(acc1.total_account_balance(), 0)

    def test_total_account_balance_debit(self):
        period = base.create_period(self.user)
        _, acc1, acc2 = base.create_children_accounts(self.user)

        base.create_credts_and_debits(
            account=acc1,
            account_period=period,
            value=20,
            credit=False,
        )
        base.create_credts_and_debits(
            account=acc2,
            account_period=period,
            value=15,
            credit=False,
        )

        self.assertEqual(acc1.total_account_balance(), 35)
        self.assertEqual(acc2.total_account_balance(), 15)

    def test_total_account_balance_credit(self):
        period = base.create_period(self.user)
        _, acc1, acc2 = base.create_children_accounts(self.user)

        base.create_credts_and_debits(
            account=acc1,
            account_period=period,
            value=20,
            debit=False,
        )
        base.create_credts_and_debits(
            account=acc2,
            account_period=period,
            value=15,
            debit=False,
        )

        self.assertEqual(acc1.total_account_balance(), -35)
        self.assertEqual(acc2.total_account_balance(), -15)
