from equibook.core.tests import base
from equibook.core import facade


class TransactionDeleteViewTestCase(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
        self.period = base.create_period(self.user)
        _, _, self.account = base.create_children_accounts(self.user)
        self.transaction = base.create_credts_and_debits(
            account=self.account,
            account_period=self.period,
            value=100,
        )

        self.url_delete = base.reverse(
            "core:transaction-delete", args=[self.transaction.id]
        )

    def test_get_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url_delete)
        self.assertEqual(response.status_code, 404)

    def test_get_unauthenticated(self):
        response = self.client.get(self.url_delete)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.url_login_next(self.url_delete))

    def test_delete_authenticated(self):
        self.client.force_login(self.user)

        self.assertEqual(facade.Transaction.objects.count(), 1)

        response = self.client.post(
            self.url_delete,
            data={},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.reverse("core:transaction-list"))

        self.assertEqual(facade.Transaction.objects.count(), 0)

    def test_delete_authenticated_to_next_is_not_none(self):
        next = base.create_credts_and_debits(
            account=self.account, account_period=self.period, value=399
        )

        self.assertEqual(facade.Transaction.objects.count(), 2)

        self.client.force_login(self.user)

        response = self.client.post(self.url_delete, data={})

        prev = facade.Transaction.objects.get(id=self.transaction.id)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(prev.next_id, next.id)
        self.assertEqual(facade.Transaction.objects.count(), 2)

    def test_delete_authenticated_period_closed(self):
        self.period.status = facade.AccountingPeriod.Status.CLOSED
        self.period.save()

        base.create_period(self.user)

        self.client.force_login(self.user)

        self.assertEqual(facade.Transaction.objects.count(), 1)

        response = self.client.post(self.url_delete, data={})

        self.assertEqual(response.status_code, 404)
        self.assertEqual(facade.Transaction.objects.count(), 1)

    def test_delete_unauthenticated(self):
        self.assertEqual(facade.Transaction.objects.count(), 1)
        response = self.client.post(self.url_delete, data={})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.url_login_next(self.url_delete))
        self.assertEqual(facade.Transaction.objects.count(), 1)
