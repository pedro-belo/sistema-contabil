from equibook.core.tests import base
from equibook.core import facade


class TransactionCreateViewTestCase(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
        self.period = base.create_period(self.user)
        self.url_create = base.reverse("core:transaction-create")
        self.form_data = {
            "title": "transaction",
            "description": "transaction desc",
        }

    def test_get_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url_create)
        self.assertEqual(response.status_code, 200)

    def test_get_authenticated_ne_period(self):
        self.period.delete()
        self.client.force_login(self.user)

        response = self.client.get(self.url_create)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(facade.AccountingPeriod.objects.count(), 0)

    def test_create_authenticated_ne_period(self):
        self.period.delete()
        self.client.force_login(self.user)

        response = self.client.post(self.url_create)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(facade.AccountingPeriod.objects.count(), 0)

    def test_get_unauthenticated(self):
        response = self.client.get(self.url_create)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.url_login_next(self.url_create))

    def test_create_authenticated(self):
        self.assertEqual(facade.Transaction.objects.count(), 0)

        self.client.force_login(self.user)

        response = self.client.post(self.url_create, data=self.form_data)

        transaction = facade.Transaction.objects.last()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.reverse("core:transaction-list"))

        self.assertEqual(transaction.title, self.form_data["title"])
        self.assertEqual(transaction.description, self.form_data["description"])
        self.assertEqual(
            facade.Transaction.objects.filter(period=self.period).count(), 1
        )

    def test_create_unauthenticated(self):
        response = self.client.post(self.url_create, data=self.form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.url_login_next(self.url_create))
        self.assertEqual(facade.Transaction.objects.count(), 0)
