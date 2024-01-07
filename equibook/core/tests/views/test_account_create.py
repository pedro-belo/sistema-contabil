from equibook.core.tests import base
from equibook.core import facade


class AccountUpdateViewTests(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()

    def test_get_authenticated(self):
        parent_account = facade.Account.objects.get_equity(self.user)

        self.client.force_login(self.user)

        response = self.client.get(
            base.reverse("core:account-create", args=[parent_account.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_get_unauthenticated(self):
        parent_account = facade.Account.objects.get_equity(self.user)

        expected_url = (
            base.reverse("users:login")
            + "?next="
            + base.reverse("core:account-create", args=[parent_account.id])
        )

        response = self.client.get(
            base.reverse("core:account-create", args=[parent_account.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)

    def test_create_authenticated(self):
        num_accounts = facade.Account.objects.count()
        parent_account = facade.Account.objects.get_asset(self.user)

        self.client.force_login(self.user)

        data = {"name": f"shinzou wo sasageyo"}

        response = self.client.post(
            base.reverse("core:account-create", args=[parent_account.id]),
            data=data,
        )

        account = facade.Account.objects.last()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, base.reverse("core:account-detail", args=[account.id])
        )

        self.assertEqual(account.name, data["name"])
        self.assertEqual(facade.Account.objects.count(), num_accounts + 1)

    def test_create_unauthenticated(self):
        num_accounts = facade.Account.objects.count()
        parent_account = facade.Account.objects.get_asset(self.user)

        expected_url = (
            base.reverse("users:login")
            + "?next="
            + base.reverse("core:account-create", args=[parent_account.id])
        )

        data = {"name": f"shinzou wo sasageyo"}

        response = self.client.post(
            base.reverse("core:account-create", args=[parent_account.id]),
            data=data,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)
        self.assertEqual(facade.Account.objects.count(), num_accounts)
