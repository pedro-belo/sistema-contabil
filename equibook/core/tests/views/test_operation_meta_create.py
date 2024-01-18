from equibook.core.tests import base
from equibook.core import facade


class OperationMetaCreateViewTestCase(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
        self.period = base.create_period(self.user)

        _, _, debit = base.create_children_accounts(
            user=self.user,
            root=facade.Account.objects.get_asset(self.user),
        )

        self.transaction = base.create_debit_and_credit(
            period=self.period, value=10, debit=debit
        )

        self.operation = self.transaction.transaction_operation.first()

        self.url_create = base.reverse(
            "core:operation-meta-create", args=[self.operation.id]
        )

        document = base.create_uploadfile(name="BR-E11")
        self.document_name, self.document_content = document.name, document.read()

        document.seek(0)

        self.form_data = {
            "description": "BR-E11",
            "document": document,
        }

    def test_get_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url_create)
        self.assertEqual(response.status_code, 200)

    def test_get_unauthenticated(self):
        response = self.client.get(self.url_create)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.url_login_next(self.url_create))

    @base.override_settings(MEDIA_ROOT="/tmp")
    def test_create_authenticated(self):
        self.client.force_login(self.user)

        self.assertEqual(facade.OperationMeta.objects.count(), 0)

        response = self.client.post(self.url_create, data=self.form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            base.reverse("core:transaction-detail", args=[self.transaction.id]),
        )

        created = facade.OperationMeta.objects.last()
        self.assertEqual(created.description, self.form_data["description"])
        self.assertTrue(created.document.name.startswith(self.document_name))
        self.assertEqual(created.document.read(), self.document_content)
        self.assertEqual(facade.OperationMeta.objects.count(), 1)

    def test_create_closed_period(self):
        self.period.status = facade.AccountingPeriod.Status.CLOSED
        self.period.save()

        base.create_period(self.user)

        self.client.force_login(self.user)

        self.assertEqual(facade.OperationMeta.objects.count(), 0)

        response = self.client.post(self.url_create, data=self.form_data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(facade.OperationMeta.objects.count(), 0)

    def test_create_unauthenticated(self):
        self.assertEqual(facade.OperationMeta.objects.count(), 0)
        response = self.client.post(self.url_create, data=self.form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.url_login_next(self.url_create))
        self.assertEqual(facade.OperationMeta.objects.count(), 0)
