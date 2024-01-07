from equibook.core.tests import base
from equibook.core import facade


class AccountUpdateViewTests(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
        self.accounts = base.create_children_accounts(self.user)

    def reverse_delete_url(self, id):
        return base.reverse("core:account-delete", args=[id])

    def test_get_authenticated(self):
        _, _, account = self.accounts
        self.client.force_login(self.user)
        response = self.client.get(self.reverse_delete_url(account.id))
        self.assertEqual(response.status_code, 404)

    def test_get_unauthenticated(self):
        _, _, account = self.accounts

        expected_url = (
            base.reverse("users:login") + "?next=" + self.reverse_delete_url(account.id)
        )

        response = self.client.get(self.reverse_delete_url(account.id))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)

    def test_delete_authenticated(self):
        _, account_parent, account = self.accounts

        self.client.force_login(self.user)

        response = self.client.post(
            self.reverse_delete_url(account.id),
            data={},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, base.reverse("core:account-detail", args=[account_parent.id])
        )

        self.assertEqual(facade.Account.objects.filter(id=account.id).count(), 0)

    def test_delete_unauthenticated(self):
        _, _, account = self.accounts

        expected_url = (
            base.reverse("users:login") + "?next=" + self.reverse_delete_url(account.id)
        )

        response = self.client.post(
            self.reverse_delete_url(account.id),
            data={},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)
        self.assertEqual(facade.Account.objects.filter(id=account.id).count(), 1)
