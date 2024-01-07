from django.urls import reverse
from django.test import TestCase
from equibook.core import facade
from equibook.users.models import User
from model_bakery import baker


class BalanceAccountsViewTest(TestCase):
    def setUp(self):
        self.user = baker.make(User)
        facade.user_setup(
            self.user,
            form_data={
                "entity": "Entity Name",
                "base_currency": facade.Currency.BRL,
            },
        )

    def test_get_unauthenticated(self):
        url = reverse("core:balance-accounts")
        login_url = reverse("users:login")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        self.assertIn(login_url, response.url)

    def test_get_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("core:balance-accounts"))
        self.assertEqual(response.status_code, 200)

    def test_context(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("core:balance-accounts"))
        self.assertEqual(
            response.context_data["asset"], facade.Account.objects.get_asset(self.user)
        )
        self.assertEqual(
            response.context_data["equity"],
            facade.Account.objects.get_equity(self.user),
        )
        self.assertEqual(
            response.context_data["liability"],
            facade.Account.objects.get_liability(self.user),
        )
