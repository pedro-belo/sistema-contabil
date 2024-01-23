from equibook.core.tests import base
from equibook.core import facade


class AccountCreateViewTestCase(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
        self.account = facade.Account.objects.get_equity(self.user)
        self.url_create = base.reverse("core:account-create", args=[self.account.id])
        self.form_data = {"name": f"shinzou wo sasageyo"}

    def test_get_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url_create)
        self.assertEqual(response.status_code, 200)

    def test_get_unauthenticated(self):
        response = self.client.get(self.url_create)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.url_login_next(self.url_create))

    def test_create_authenticated(self):
        num_accounts = facade.Account.objects.count()
        self.client.force_login(self.user)

        response = self.client.post(self.url_create, data=self.form_data)

        created = facade.Account.objects.last()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            base.reverse("core:account-detail", args=[created.id]),
        )

        self.assertEqual(created.name, self.form_data["name"])
        self.assertEqual(facade.Account.objects.count(), num_accounts + 1)

    def test_create_unauthenticated(self):
        num_accounts = facade.Account.objects.count()

        response = self.client.post(self.url_create, data=self.form_data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.url_login_next(self.url_create))
        self.assertEqual(facade.Account.objects.count(), num_accounts)
