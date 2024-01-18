from equibook.core.tests import base
from equibook.core import facade


class ArchivedTransactionListViewTestCase(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
        self.url_archived = base.reverse("core:transaction-list-archived")

    def test_get_unauthenticated(self):
        response = self.client.get(self.url_archived)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.url_login_next(self.url_archived))

    def test_get_authenticated_ne_period(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url_archived)
        self.assertEqual(response.status_code, 200)

    def test_get_authenticated_ne_transaction(self):
        period = base.create_period(self.user)
        self.client.force_login(self.user)

        for status in facade.AccountingPeriod.Status.values:
            period.status = status
            period.save()

            response = self.client.get(self.url_archived)
            self.assertEqual(response.status_code, 200)

    def test_get_authenticated(self):
        period = base.create_period(self.user)

        _, _, account = base.create_children_accounts(
            user=self.user,
            root=facade.Account.objects.get_asset(self.user),
        )

        self.transaction = base.create_debit_and_credit(
            period=period, value=10, debit=account
        )

        self.client.force_login(self.user)

        for status in facade.AccountingPeriod.Status.values:
            period.status = status
            period.save()

            response = self.client.get(self.url_archived)
            self.assertEqual(response.status_code, 200)
