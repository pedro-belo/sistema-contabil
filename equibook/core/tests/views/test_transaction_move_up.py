from equibook.core.tests import base
from equibook.core import facade


class TransactionDeleteViewTests(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
        self.period = base.create_period(self.user)
        _, _, self.account = base.create_children_accounts(self.user)

        transactions = []
        for i in range(1, 11):
            transactions.append(
                base.create_credts_and_debits(
                    account=self.account,
                    account_period=self.period,
                    value=i * 10,
                )
            )
        self.transactions = [
            facade.Transaction.objects.get(id=transaction.id)
            for transaction in transactions
        ]

    def _test_post_authenticated(self, direction):
        self.client.force_login(self.user)

        response = self.client.post(
            base.reverse(
                f"core:transaction-move-{direction}", args=[self.transactions[0].id]
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_post_authenticated_up(self):
        self._test_post_authenticated(direction="up")

    def test_post_authenticated_down(self):
        self._test_post_authenticated(direction="down")

    def _test_get_unauthenticated(self, direction):
        url = base.reverse(
            f"core:transaction-move-{direction}", args=[self.transactions[0].id]
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.url_login_next(url))

    def test_get_unauthenticated_up(self):
        self._test_get_unauthenticated(direction="up")

    def test_get_unauthenticated_down(self):
        self._test_get_unauthenticated(direction="down")

    def test_ensure_order(self):
        self.assertEqual(self.transactions[0].next_id, self.transactions[1].id)
        self.assertEqual(getattr(self.transactions[0], "previous", None), None)
        self.assertEqual(self.transactions[-1].next, None)
        self.assertEqual(self.transactions[-1].previous.id, self.transactions[-2].id)

    def test_move_down(self):
        self.client.force_login(self.user)

        transaction_id = self.transactions[-1].id

        for count in range(len(self.transactions) - 2, -1, -1):
            response = self.client.get(
                base.reverse("core:transaction-move-down", args=[transaction_id])
            )

            updated = facade.Transaction.objects.get(pk=transaction_id)

            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, base.reverse("core:transaction-list"))
            self.assertEqual(updated.next_id, self.transactions[count].id)

    def test_move_up(self):
        self.client.force_login(self.user)

        transaction_id = self.transactions[0].id

        for count in range(2, len(self.transactions) - 1):
            response = self.client.get(
                base.reverse("core:transaction-move-up", args=[transaction_id])
            )

            updated = facade.Transaction.objects.get(pk=transaction_id)

            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, base.reverse("core:transaction-list"))
            self.assertEqual(updated.next_id, self.transactions[count].id)
