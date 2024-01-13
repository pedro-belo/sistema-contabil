from equibook.core.tests import base
from equibook.core import facade


class ResultAccountTestCase(base.TestCase):
    def setUp(self):
        self.user = base.create_default_user()
        self.url_ac_result = base.reverse("core:result-accounts")

    def test_get_unauthenticated(self):
        response = self.client.get(self.url_ac_result)
        self.assertEqual(response.status_code, 302)
        self.assertIn(base.reverse("users:login"), response.url)

    def test_get_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url_ac_result)
        self.assertEqual(response.status_code, 200)

    def test_context(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url_ac_result)
        self.assertEqual(
            response.context_data["revenue"],
            facade.Account.objects.get_revenue(self.user),
        )
        self.assertEqual(
            response.context_data["expense"],
            facade.Account.objects.get_expense(self.user),
        )
