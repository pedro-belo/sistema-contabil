from equibook.core.tests import base


class AccountingPeriodDetailViewTestCase(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
        self.url_detail = base.reverse("core:accounting-period-detail")

    def test_get_authenticated_no_period(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 404)

    def test_get_authenticated_period_in_progress(self):
        base.create_period(self.user)
        self.client.force_login(self.user)
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 200)

    def test_get_authenticated_period_closing_accounts(self):
        period = base.create_period(self.user)
        period.status = base.facade.AccountingPeriod.Status.CLOSING_ACCOUNTS
        period.save()

        self.client.force_login(self.user)
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 200)

    def test_get_unauthenticated(self):
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.url_login_next(self.url_detail))
