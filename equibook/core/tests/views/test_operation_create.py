from equibook.core.tests import base
from equibook.core import facade


class OperationCreateViewTestCase(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
        self.period = base.create_period(self.user)

        _, self.account, _ = base.create_children_accounts(
            user=self.user,
            root=facade.Account.objects.get_asset(self.user),
        )

        self.transaction = facade.create_transaction(
            user=self.user,
            form_data={
                "title": "Transaction",
                "description": "Description",
                "account_period": self.period,
            },
        )

        self.form_data = {
            "account": self.account.id,
            "type": facade.OperationType.DEBIT,
            "value": "10",
            "date": self.period.start_date.strftime("%d/%m/%Y"),
        }

        self.url_create = base.reverse(
            "core:operation-create", args=[self.transaction.id]
        )

    def test_get_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url_create)
        self.assertEqual(response.status_code, 200)

    def test_get_unauthenticated(self):
        response = self.client.get(self.url_create)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.url_login_next(self.url_create))

    def test_create_authenticated(self):
        self.client.force_login(self.user)

        self.assertEqual(facade.Operation.objects.count(), 0)

        response = self.client.post(self.url_create, data=self.form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.reverse("core:transaction-list"))

        created = facade.Operation.objects.last()
        self.assertEqual(created.account_id, self.account.id)
        self.assertEqual(created.type, self.form_data["type"])
        self.assertEqual(created.value, base.Decimal(self.form_data["value"]))

        self.assertEqual(created.date.day, self.period.start_date.day)
        self.assertEqual(created.date.month, self.period.start_date.month)
        self.assertEqual(created.date.year, self.period.start_date.year)

        self.assertEqual(facade.Operation.objects.count(), 1)

    def test_create_closed_period(self):
        self.period.status = facade.AccountingPeriod.Status.CLOSED
        self.period.save()

        base.create_period(self.user)

        self.client.force_login(self.user)

        self.assertEqual(facade.Operation.objects.count(), 0)

        response = self.client.post(self.url_create, data=self.form_data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(facade.Operation.objects.count(), 0)

    def test_create_unauthenticated(self):
        self.assertEqual(facade.Operation.objects.count(), 0)

        response = self.client.post(self.url_create, data=self.form_data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.url_login_next(self.url_create))
        self.assertEqual(facade.Operation.objects.count(), 0)
