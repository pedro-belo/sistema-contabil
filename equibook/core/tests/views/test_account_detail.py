from equibook.core.tests import base
from equibook.core import facade


class AccountDetailViewTestCase(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
        self.account = facade.Account.objects.get_asset(self.user)
        self.url_detail = base.reverse("core:account-detail", args=[self.account.id])

    def test_get_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 200)

    def test_get_unauthenticated(self):
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.url_login_next(self.url_detail))
