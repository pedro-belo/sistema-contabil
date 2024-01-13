from equibook.core.tests import base
from equibook.core import facade


class AccountDeleteViewTests(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
        self.accounts = base.create_children_accounts(self.user)

    def url_delete(self, id):
        return base.reverse("core:account-delete", args=[id])

    def test_get_authenticated(self):
        _, _, account = self.accounts
        self.client.force_login(self.user)
        response = self.client.get(self.url_delete(account.id))
        self.assertEqual(response.status_code, 404)

    def test_get_unauthenticated(self):
        _, _, account = self.accounts
        url_delete = self.url_delete(account.id)

        response = self.client.get(url_delete)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.url_login_next(url_delete))

    def test_delete_authenticated(self):
        _, account_parent, account = self.accounts

        self.client.force_login(self.user)

        response = self.client.post(self.url_delete(account.id), data={})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            base.reverse("core:account-detail", args=[account_parent.id]),
        )

        self.assertEqual(facade.Account.objects.filter(id=account.id).count(), 0)

    def test_delete_unauthenticated(self):
        _, _, account = self.accounts

        url_delete = self.url_delete(account.id)

        response = self.client.post(url_delete, data={})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.url_login_next(url_delete))
        self.assertEqual(facade.Account.objects.filter(id=account.id).count(), 1)
