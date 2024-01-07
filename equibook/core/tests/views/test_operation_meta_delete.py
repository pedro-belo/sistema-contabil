from equibook.core.tests import base
from equibook.core import facade


class TransactionDeleteViewTests(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
        self.period = base.create_period(self.user)
        _, _, self.account = base.create_children_accounts(self.user)

        self.transaction = base.create_credts_and_debits(
            account=self.account, account_period=self.period, value=10, credit=False
        )
        self.operation = self.transaction.transaction_operation.first()
        self.operation_meta = facade.OperationMeta.objects.create(
            description="description", operation=self.operation
        )

    def test_get_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(
            base.reverse("core:operation-meta-delete", args=[self.operation_meta.id])
        )
        self.assertEqual(response.status_code, 404)

    def test_get_unauthenticated(self):
        expected_url = (
            base.reverse("users:login")
            + "?next="
            + base.reverse("core:operation-meta-delete", args=[self.operation_meta.id])
        )

        response = self.client.get(
            base.reverse("core:operation-meta-delete", args=[self.operation_meta.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)

    def test_delete_authenticated(self):
        self.client.force_login(self.user)

        self.assertEqual(facade.OperationMeta.objects.count(), 1)

        response = self.client.post(
            base.reverse("core:operation-meta-delete", args=[self.operation_meta.id]),
            data={},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            base.reverse("core:transaction-detail", args=[self.transaction.id]),
        )

        self.assertEqual(facade.OperationMeta.objects.count(), 0)

    def test_delete_authenticated_period_closed(self):
        self.period.status = facade.AccountingPeriod.Status.CLOSED
        self.period.save()

        base.create_period(self.user)

        self.client.force_login(self.user)

        self.assertEqual(facade.OperationMeta.objects.count(), 1)

        response = self.client.post(
            base.reverse("core:operation-meta-delete", args=[self.operation_meta.id]),
            data={},
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(facade.OperationMeta.objects.count(), 1)

    def test_delete_unauthenticated(self):
        self.assertEqual(facade.OperationMeta.objects.count(), 1)

        expected_url = (
            base.reverse("users:login")
            + "?next="
            + base.reverse("core:operation-meta-delete", args=[self.operation_meta.id])
        )

        response = self.client.post(
            base.reverse("core:operation-meta-delete", args=[self.operation_meta.id]),
            data={},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)
        self.assertEqual(facade.OperationMeta.objects.count(), 1)
