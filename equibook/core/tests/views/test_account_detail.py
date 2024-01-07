from equibook.core.tests import base
from equibook.core import facade


class AccountDetailViewTests(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()

    def test_get_authenticated(self):
        account = facade.Account.objects.get_asset(self.user)
        self.client.force_login(self.user)
        response = self.client.get(
            base.reverse("core:account-detail", args=[account.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_get_unauthenticated(self):
        account = facade.Account.objects.get_asset(self.user)

        expected_url = (
            base.reverse("users:login")
            + "?next="
            + base.reverse("core:account-detail", args=[account.id])
        )

        response = self.client.get(
            base.reverse("core:account-detail", args=[account.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)
