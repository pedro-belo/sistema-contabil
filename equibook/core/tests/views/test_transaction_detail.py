from equibook.core.tests import base
from equibook.core import facade


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

    def test_get_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(
            base.reverse("core:transaction-detail", args=[self.transaction.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_get_unauthenticated(self):
        expected_url = (
            base.reverse("users:login")
            + "?next="
            + base.reverse("core:transaction-detail", args=[self.transaction.id])
        )

        response = self.client.get(
            base.reverse("core:transaction-detail", args=[self.transaction.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)
