from equibook.core.tests import base
from equibook.core import facade
from decimal import Decimal


class OperationCreateViewTests(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
        self.period = base.create_period(self.user)
        _, _, self.account = base.create_children_accounts(self.user)

        self.form_data = {
            "account": self.account.id,
            "type": facade.OperationType.DEBIT,
            "value": "10",
            "date": self.period.start_date.strftime("%d/%m/%Y"),
        }

        self.transaction = facade.create_transaction(
            user=self.user,
            form_data={
                "title": "Transaction",
                "description": "Description",
                "account_period": self.period,
            },
        )

    def test_get_authenticated(self):
        self.client.force_login(self.user)

        response = self.client.get(
            base.reverse("core:operation-create", args=[self.transaction.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_get_unauthenticated(self):
        expected_url = (
            base.reverse("users:login")
            + "?next="
            + base.reverse("core:operation-create", args=[self.transaction.id])
        )

        response = self.client.get(
            base.reverse("core:operation-create", args=[self.transaction.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)

    def test_create_authenticated(self):
        self.client.force_login(self.user)

        self.assertEqual(facade.Operation.objects.count(), 0)

        response = self.client.post(
            base.reverse("core:operation-create", args=[self.transaction.id]),
            data=self.form_data,
        )
        created = facade.Operation.objects.last()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.reverse("core:transaction-list"))
        self.assertEqual(created.account_id, self.account.id)
        self.assertEqual(created.type, self.form_data["type"])
        self.assertEqual(created.value, Decimal(self.form_data["value"]))

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

        response = self.client.post(
            base.reverse("core:operation-create", args=[self.transaction.id]),
            data=self.form_data,
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(facade.Operation.objects.count(), 0)

    def test_create_unauthenticated(self):
        expected_url = (
            base.reverse("users:login")
            + "?next="
            + base.reverse("core:operation-create", args=[self.transaction.id])
        )

        self.assertEqual(facade.Operation.objects.count(), 0)

        response = self.client.post(
            base.reverse("core:operation-create", args=[self.transaction.id]),
            data=self.form_data,
        )        

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)
        self.assertEqual(facade.Operation.objects.count(), 0)
