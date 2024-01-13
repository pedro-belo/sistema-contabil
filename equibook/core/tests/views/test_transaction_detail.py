from equibook.core.tests import base


class TransactionDetailViewTests(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
        self.period = base.create_period(self.user)
        _, _, self.account = base.create_children_accounts(self.user)
        self.transaction = base.create_credts_and_debits(
            account=self.account,
            account_period=self.period,
            value=100,
        )

        self.url_detail = base.reverse(
            "core:transaction-detail", args=[self.transaction.id]
        )

    def test_get_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 200)

    def test_get_unauthenticated(self):
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.url_login_next(self.url_detail))
