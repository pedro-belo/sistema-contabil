from equibook.core.tests import base
from equibook.core import facade


class TransactionUpdateViewTests(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
        self.period = base.create_period(self.user)
        _, _, self.account = base.create_children_accounts(self.user)
        self.transaction = base.create_credts_and_debits(
            account=self.account,
            account_period=self.period,
            value=100,
        )
        self.form_data = {
            "title": f"{self.transaction.title}...",
            "description": f"{self.transaction.description}...",
            "archived": not self.transaction.archived,
        }

    def test_get_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(
            base.reverse("core:transaction-update", args=[self.transaction.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_get_unauthenticated(self):
        expected_url = (
            base.reverse("users:login")
            + "?next="
            + base.reverse("core:transaction-update", args=[self.transaction.id])
        )

        response = self.client.get(
            base.reverse("core:transaction-update", args=[self.transaction.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)

    def test_update_authenticated(self):
        self.client.force_login(self.user)

        response = self.client.post(
            base.reverse("core:transaction-update", args=[self.transaction.id]),
            data=self.form_data,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            base.reverse("core:transaction-detail", args=[self.transaction.id]),
        )

        updated = facade.Transaction.objects.get(pk=self.transaction.pk)
        self.assertEqual(updated.title, self.form_data["title"])
        self.assertEqual(updated.description, self.form_data["description"])
        self.assertEqual(updated.archived, self.form_data["archived"])

    def test_update_unauthenticated(self):
        expected_url = (
            base.reverse("users:login")
            + "?next="
            + base.reverse("core:transaction-update", args=[self.transaction.id])
        )

        response = self.client.post(
            base.reverse("core:transaction-update", args=[self.transaction.id]),
            data=self.form_data,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)

        transaction = facade.Transaction.objects.get(pk=self.transaction.pk)
        self.assertEqual(transaction.title, self.transaction.title)
        self.assertEqual(transaction.description, self.transaction.description)
        self.assertEqual(transaction.archived, self.transaction.archived)

    def test_get_authenticated_period_closed(self):
        self.period.status = facade.AccountingPeriod.Status.CLOSED
        self.period.save()

        base.create_period(self.user)

        self.client.force_login(self.user)

        response = self.client.get(
            base.reverse("core:transaction-update", args=[self.transaction.id])
        )

        self.assertEqual(response.status_code, 404)

    def test_update_authenticated_period_closed(self):
        """
            Tentativa atulizar a transação de um período que já foi finalizado 
        """
        self.period.status = facade.AccountingPeriod.Status.CLOSED
        self.period.save()

        base.create_period(self.user)

        self.client.force_login(self.user)

        response = self.client.post(
            base.reverse("core:transaction-update", args=[self.transaction.id]),
            data=self.form_data,
        )

        self.assertEqual(response.status_code, 404)

        transaction = facade.Transaction.objects.get(pk=self.transaction.pk)
        self.assertEqual(transaction.title, self.transaction.title)
        self.assertEqual(transaction.description, self.transaction.description)
        self.assertEqual(transaction.archived, self.transaction.archived)
