from django.urls import reverse
from django.test import TestCase
from equibook.core import facade
from equibook.users.models import User
from model_bakery import baker


class ResultsViewTest(TestCase):
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
        url = reverse("core:result-accounts")
        login_url = reverse("users:login")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        self.assertIn(login_url, response.url)

    def test_get_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("core:result-accounts"))
        self.assertEqual(response.status_code, 200)

    def test_context(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("core:result-accounts"))
        self.assertEqual(
            response.context_data["revenue"],
            facade.Account.objects.get_revenue(self.user),
        )
        self.assertEqual(
            response.context_data["expense"],
            facade.Account.objects.get_expense(self.user),
        )
