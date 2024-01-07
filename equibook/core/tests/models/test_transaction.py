from equibook.core.tests import base


class TransactionModelTestCase(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()

    def test_transaction_balance_zero(self):
        period = base.create_period(self.user)
        _, acc1, _ = base.create_children_accounts(self.user)

        transaction = base.create_credts_and_debits(
            account=acc1, account_period=period, value=20, reperat=2
        )

        balance = transaction.get_balance()
        self.assertEqual(balance["instance"].id, transaction.id)
        self.assertEqual(balance["debit_sum"], 40)
        self.assertEqual(balance["credit_sum"], 40)
        self.assertEqual(balance["is_balanced"], True)


    def test_transaction_balance_credit(self):
        period = base.create_period(self.user)
        _, _, acc2 = base.create_children_accounts(self.user)

        transaction = base.create_credts_and_debits(
            account=acc2, account_period=period, value=20, reperat=2, debit=False
        )

        balance = transaction.get_balance()
        self.assertEqual(balance["instance"].id, transaction.id)
        self.assertEqual(balance["debit_sum"], 0)
        self.assertEqual(balance["credit_sum"], 40)
        self.assertEqual(balance["is_balanced"], False)

def test_transaction_balance_debit(self):
        period = base.create_period(self.user)
        _, _, acc2 = base.create_children_accounts(self.user)

        transaction = base.create_credts_and_debits(
            account=acc2, account_period=period, value=20, reperat=2, credit=False
        )

        balance = transaction.get_balance()
        self.assertEqual(balance["instance"].id, transaction.id)
        self.assertEqual(balance["debit_sum"], 40)
        self.assertEqual(balance["credit_sum"], 0)
        self.assertEqual(balance["is_balanced"], False)
