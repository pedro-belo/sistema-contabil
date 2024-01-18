from equibook.core.tests import base
from equibook.core import facade


class TransactionModelTestCase(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
        self.asset = facade.Account.objects.get_asset(self.user)
        self.liability = facade.Account.objects.get_liability(self.user)

    def test_transaction_balance_zero(self):
        period = base.create_period(self.user)
        _, debit, credit = base.create_children_accounts(self.user, self.asset)

        transaction = base.create_debit_and_credit(
            period=period, value=40, debit=debit, credit=credit
        )

        balance = transaction.get_balance()
        self.assertEqual(balance["instance"].id, transaction.id)
        self.assertEqual(balance["debit_sum"], 40)
        self.assertEqual(balance["credit_sum"], 40)
        self.assertEqual(balance["is_balanced"], True)

    def test_transaction_balance_credit(self):
        period = base.create_period(self.user)
        _, credit, _ = base.create_children_accounts(self.user, self.asset)

        transaction = base.create_debit_and_credit(
            period=period, value=40, credit=credit
        )

        balance = transaction.get_balance()
        self.assertEqual(balance["instance"].id, transaction.id)
        self.assertEqual(balance["debit_sum"], 0)
        self.assertEqual(balance["credit_sum"], 40)
        self.assertEqual(balance["is_balanced"], False)

    def test_transaction_balance_debit(self):
        period = base.create_period(self.user)
        _, debit, _ = base.create_children_accounts(self.user)

        transaction = base.create_debit_and_credit(period=period, value=40, debit=debit)

        balance = transaction.get_balance()
        self.assertEqual(balance["instance"].id, transaction.id)
        self.assertEqual(balance["debit_sum"], 40)
        self.assertEqual(balance["credit_sum"], 0)
        self.assertEqual(balance["is_balanced"], False)
