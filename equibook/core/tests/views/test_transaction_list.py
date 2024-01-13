from equibook.core.tests import base
from equibook.core import facade


class TransactionListViewTests(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
        self.url_list = base.reverse("core:transaction-list")

    def test_get_unauthenticated(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.url_login_next(self.url_list))

    def test_get_authenticated_ne_period_ne_transaction(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, 200)

    def test_get_authenticated_e_period_ne_transaction(self):
        period = base.create_period(self.user)
        self.client.force_login(self.user)

        for status in facade.AccountingPeriod.Status.values:
            period.status = status
            period.save()

            response = self.client.get(self.url_list)
            self.assertEqual(response.status_code, 200)

    def test_get_authenticated_e_period_e_transaction(self):
        period = base.create_period(self.user)

        _, _, account = base.create_children_accounts(self.user)
        _ = base.create_credts_and_debits(
            account=account, account_period=period, value=120
        )

        self.client.force_login(self.user)

        for status in facade.AccountingPeriod.Status.values:
            period.status = status
            period.save()

            response = self.client.get(self.url_list)
            self.assertEqual(response.status_code, 200)
