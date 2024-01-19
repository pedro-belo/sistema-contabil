from equibook.core import facade
from equibook.core.tests import base


class AccountModelTestCase(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
        self.asset = facade.Account.objects.get_asset(self.user)
        self.liability = facade.Account.objects.get_liability(self.user)

    def test_root_accounts(self):
        queryset = facade.Account.objects.filter(user=self.user, parent=None)
        accounts = [
            facade.Account.objects.get_asset(self.user),
            facade.Account.objects.get_result(self.user),
            facade.Account.objects.get_liability(self.user),
            facade.Account.objects.get_equity(self.user),
            facade.Account.objects.get_revenue(self.user),
            facade.Account.objects.get_expense(self.user),
        ]

        self.assertEqual(len(accounts), queryset.count())

        for account in queryset:
            self.assertTrue(queryset.contains(account))

    def test_can_remove_root_accounts(self):
        root_accounts = facade.Account.objects.filter(user=self.user, parent=None)
        for account in root_accounts:
            self.assertEqual(account.can_remove(), False)

    def test_can_remove_parent_account(self):
        _, account, _ = base.create_children_accounts(self.user, root=self.asset)
        self.assertEqual(account.can_remove(), False)

    def test_can_delete_if_the_account_has_operation(self):
        _, _, account = base.create_children_accounts(self.user, root=self.asset)
        base.baker.make(facade.Operation, account=account)
        self.assertEqual(account.can_remove(), False)

    def test_can_delete_if_account_is_leaf(self):
        _, _, leaf = base.create_children_accounts(self.user, root=self.asset)
        self.assertEqual(leaf.can_remove(), True)

    def test_account_pretty_name(self):
        acc1, acc2, acc3 = base.create_children_accounts(self.user, root=self.asset)
        self.assertEqual(str(acc3), f"{acc1.name} • {acc2.name} • {acc3.name}")

    def test_get_path(self):
        acc1, acc2, acc3 = base.create_children_accounts(self.user, root=self.asset)
        path = acc3.get_path(self_include=True, reverse=True)
        self.assertEqual(acc1.id, path[0].id)
        self.assertEqual(acc2.id, path[1].id)
        self.assertEqual(acc3.id, path[2].id)

    def test_individual_balance_zero(self):
        period = base.create_period(self.user)
        _, debit, credit = base.create_children_accounts(self.user, root=self.asset)

        base.create_debit_and_credit(
            period=period, debit=debit, credit=credit, value=base.Decimal("20")
        )

        base.create_debit_and_credit(
            period=period, debit=credit, credit=debit, value=base.Decimal("20")
        )

        self.assertEqual(debit.get_individual_balance(), 0)
        self.assertEqual(credit.get_individual_balance(), 0)

    def test_individual_balance_debit(self):
        period = base.create_period(self.user)
        _, debit, credit = base.create_children_accounts(self.user, root=self.asset)

        base.create_debit_and_credit(
            period=period, debit=debit, credit=credit, value=base.Decimal("20")
        )

        self.assertEqual(debit.get_individual_balance(), 20)

    def test_individual_balance_credit(self):
        period = base.create_period(self.user)
        _, debit, credit = base.create_children_accounts(self.user, root=self.liability)

        base.create_debit_and_credit(
            period=period, value=base.Decimal("20"), debit=debit, credit=credit
        )

        self.assertEqual(credit.get_individual_balance(), 20)

    def test_total_account_balance_zero(self):
        period = base.create_period(self.user)
        _, debit, credit = base.create_children_accounts(self.user, root=self.asset)

        base.create_debit_and_credit(
            period=period, value=base.Decimal("50"), debit=debit, credit=credit
        )

        self.assertEqual(self.asset.total_account_balance(), 0)

    def test_total_account_balance_debit(self):
        period = base.create_period(self.user)
        _, debit, _ = base.create_children_accounts(self.user, root=self.asset)
        _, credit, _ = base.create_children_accounts(self.user, root=self.liability)

        base.create_debit_and_credit(
            period=period, value=base.Decimal("50"), debit=debit, credit=credit
        )
        base.create_debit_and_credit(
            period=period, value=base.Decimal("25"), debit=debit, credit=credit
        )

        self.assertEqual(self.asset.total_account_balance(), 75)
        self.assertEqual(self.liability.total_account_balance(), 75)
