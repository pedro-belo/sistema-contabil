from equibook.core.tests import base


class AccountingPeriodCreateFirstViewTestCase(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
        self.url_create = base.reverse("core:accounting-period-create")
        self.form_data = {"start_date": "2023-01-01", "end_date": "2023-01-31"}

    def test_get_authenticated_ne_period(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url_create)
        self.assertEqual(response.status_code, 200)

    def _test_get_authenticated_and_period_exists(self, status):
        base.facade.AccountingPeriod.objects.all().delete()
        period = base.create_period(self.user)
        period.status = status
        period.save()

        self.client.force_login(self.user)
        response = self.client.get(self.url_create)
        self.assertEqual(response.status_code, 404)

    def test_get_authenticated_and_period_exists(self):
        for value in base.facade.AccountingPeriod.Status.values:
            self._test_get_authenticated_and_period_exists(status=value)

    def test_get_unauthenticated(self):
        response = self.client.get(self.url_create)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.url_login_next(self.url_create))

    def test_create_authenticated(self):
        period_count = base.facade.AccountingPeriod.objects.count()

        self.client.force_login(self.user)
        response = self.client.post(self.url_create, self.form_data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.reverse("core:balance-accounts"))

        created = base.facade.AccountingPeriod.objects.last()
        self.assertEqual(
            created.start_date.strftime("%Y-%m-%d"), self.form_data["start_date"]
        )
        self.assertEqual(
            created.end_date.strftime("%Y-%m-%d"), self.form_data["end_date"]
        )
        self.assertEqual(base.facade.AccountingPeriod.objects.count(), period_count + 1)

    def test_create_unauthenticated(self):
        period_count = base.facade.AccountingPeriod.objects.count()
        response = self.client.post(self.url_create, self.form_data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.url_login_next(self.url_create))
        self.assertEqual(base.facade.AccountingPeriod.objects.count(), period_count)
