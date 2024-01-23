from equibook.core.tests import base
from equibook.core import facade


class AccountUpdateViewTestCase(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
        self.account = facade.Account.objects.get_asset(self.user)
        self.url_update = base.reverse("core:account-update", args=[self.account.id])
        self.form_data = {"name": f"{self.account.name} updated"}

    def test_get_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url_update)
        self.assertEqual(response.status_code, 200)

    def test_get_unauthenticated(self):
        response = self.client.get(self.url_update)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.url_login_next(self.url_update))

    def test_update_authenticated(self):
        self.client.force_login(self.user)

        response = self.client.post(self.url_update, data=self.form_data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            base.reverse("core:account-detail", args=[self.account.id]),
        )

        account = facade.Account.objects.get_asset(self.user)
        self.assertEqual(account.name, self.form_data["name"])

    def test_update_unauthenticated(self):
        response = self.client.post(self.url_update, data=self.form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.url_login_next(self.url_update))
