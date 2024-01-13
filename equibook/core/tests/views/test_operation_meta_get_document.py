from equibook.core.tests import base
from equibook.core import facade


@base.override_settings(MEDIA_ROOT="/tmp")
class OperationMetaGetDocumentViewTestCase(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
        self.period = base.create_period(self.user)
        _, _, self.account = base.create_children_accounts(self.user)

        self.transaction = base.create_credts_and_debits(
            account=self.account, account_period=self.period, value=10, credit=False
        )

        self.operation = self.transaction.transaction_operation.first()

        document = base.create_uploadfile(name="BR-E11")
        self.document_name, self.document_content = document.name, document.read()
        document.seek(0)

        self.operation_meta = facade.OperationMeta.objects.create(
            description="description", document=document, operation=self.operation
        )

        self.url_download = base.reverse(
            "core:operation-meta-download", args=[self.operation_meta.id]
        )

    def _test_get_authenticated(self, close_period: bool):
        if close_period:
            self.period.status = facade.AccountingPeriod.Status.CLOSED
            self.period.save()
            base.create_period(self.user)

        self.client.force_login(self.user)

        response = self.client.get(self.url_download)

        date = str(base.datetime.now())[0:10]

        content_disposition = (
            f'attachment; filename="{self.operation_meta.document.name} - {date}'
        )
        self.assertTrue(response["Content-Disposition"].startswith(content_disposition))
        self.assertEqual(response.content, self.document_content)
        self.assertEqual(response.status_code, 200)

    def test_get_authenticated(self):
        self._test_get_authenticated(close_period=False)

    def test_get_authenticated_closed_period(self):
        self._test_get_authenticated(close_period=True)

    def test_get_unauthenticated(self):
        response = self.client.get(self.url_download)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.url_login_next(self.url_download))
