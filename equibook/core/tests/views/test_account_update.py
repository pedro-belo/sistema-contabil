from equibook.core.tests import base
from equibook.core import facade


class AccountUpdateViewTests(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()

    def test_get_authenticated(self):
        account = facade.Account.objects.get_asset(self.user)
        self.client.force_login(self.user)
        response = self.client.get(
            base.reverse("core:account-update", args=[account.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_get_unauthenticated(self):
        account = facade.Account.objects.get_asset(self.user)

        expected_url = (
            base.reverse("users:login")
            + "?next="
            + base.reverse("core:account-update", args=[account.id])
        )

        response = self.client.get(
            base.reverse("core:account-update", args=[account.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)

    def test_update_authenticated(self):
        account = facade.Account.objects.get_asset(self.user)

        self.client.force_login(self.user)

        data = {"name": f"{account.name} updated"}

        response = self.client.post(
            base.reverse("core:account-update", args=[account.id]),
            data=data,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, base.reverse("core:account-detail", args=[account.id])
        )

        account = facade.Account.objects.get_asset(self.user)
        self.assertEqual(account.name, data["name"])

    def test_update_unauthenticated(self):
        account = facade.Account.objects.get_asset(self.user)

        expected_url = (
            base.reverse("users:login")
            + "?next="
            + base.reverse("core:account-update", args=[account.id])
        )

        data = {"name": f"{account.name} updated"}

        response = self.client.post(base.reverse("core:account-update", args=[account.id]), data=data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)
