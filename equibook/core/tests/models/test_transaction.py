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

    def _test_has_prev_next_obj(self):
        period = base.create_period(self.user)
        _, debit, _ = base.create_children_accounts(self.user)

        t1 = base.create_debit_and_credit(period=period, value=10, debit=debit)
        t2 = base.create_debit_and_credit(period=period, value=20, debit=debit)

        period.status = facade.AccountingPeriod.Status.CLOSED
        period.save()

        period = base.create_period(self.user)

        t3 = base.create_debit_and_credit(period=period, value=30, debit=debit)
        t4 = base.create_debit_and_credit(period=period, value=40, debit=debit)

        return (
            facade.Transaction.objects.get(pk=t1.pk),
            facade.Transaction.objects.get(pk=t2.pk),
            facade.Transaction.objects.get(pk=t3.pk),
            facade.Transaction.objects.get(pk=t4.pk),
        )

    def test_has_next(self):
        """
        P1  WP  OP
        T1  T   T
        T2  F   T
        ----------
        P2
        T3  T   T
        T4  F   F
        """
        t1, t2, t3, t4 = self._test_has_prev_next_obj()
        self.assertEqual(t1.has_next(within_period=True), True)
        self.assertEqual(t2.has_next(within_period=True), False)
        self.assertEqual(t3.has_next(within_period=True), True)
        self.assertEqual(t4.has_next(within_period=True), False)
        self.assertEqual(t1.has_next(within_period=False), True)
        self.assertEqual(t2.has_next(within_period=False), True)
        self.assertEqual(t3.has_next(within_period=False), True)
        self.assertEqual(t4.has_next(within_period=False), False)

    def test_has_previous(self):
        """
        P1  WP  OP
        T1  F   F
        T2  T   T
        ----------
        P2
        T3  F   T
        T4  T   T
        """
        t1, t2, t3, t4 = self._test_has_prev_next_obj()
        self.assertEqual(t1.has_previous(within_period=True), False)
        self.assertEqual(t2.has_previous(within_period=True), True)
        self.assertEqual(t3.has_previous(within_period=True), False)
        self.assertEqual(t4.has_previous(within_period=True), True)
        self.assertEqual(t1.has_previous(within_period=False), False)
        self.assertEqual(t2.has_previous(within_period=False), True)
        self.assertEqual(t3.has_previous(within_period=False), True)
        self.assertEqual(t4.has_previous(within_period=False), True)        