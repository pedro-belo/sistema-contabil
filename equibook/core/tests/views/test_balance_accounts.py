from equibook.core.tests import base
from equibook.core import facade


class BalanceAccountsViewTestCase(base.TestCase):
    def setUp(self):
        self.user = base.create_default_user()
        self.url_ac_balance = base.reverse("core:balance-accounts")

    def test_get_unauthenticated(self):
        url = self.url_ac_balance
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.url_login_next(self.url_ac_balance))

    def test_get_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url_ac_balance)
        self.assertEqual(response.status_code, 200)

    def test_context(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url_ac_balance)

        self.assertEqual(
            response.context_data["asset"],
            facade.Account.objects.get_asset(self.user),
        )

        self.assertEqual(
            response.context_data["equity"],
            facade.Account.objects.get_equity(self.user),
        )

        self.assertEqual(
            response.context_data["liability"],
            facade.Account.objects.get_liability(self.user),
        )
