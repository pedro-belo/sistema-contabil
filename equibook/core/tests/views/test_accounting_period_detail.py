from equibook.core.tests import base
from equibook.core import facade


class AccountingPeriodDetailViewTestCase(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
        self.url_detail = base.reverse("core:accounting-period-detail")

    def prepare_closing_accounts(self):
        equity = base.facade.Account.objects.get_equity(self.user)

        lucros = base.facade.create_account(
            user=self.user,
            parent=equity,
            form_data={"name": "Lucros"},
        )

        prejuizos = base.facade.create_account(
            user=self.user,
            parent=equity,
            form_data={"name": "Prejuizos"},
        )

        date = base.date.today() - base.timedelta(days=1)
        period = base.create_period(
            self.user,
            start_data=date,
            end_date=date,
            status=base.facade.AccountingPeriod.Status.CLOSING_ACCOUNTS,
        )

        return period, {
            "loss_account": prejuizos.id,
            "earn_account": lucros.id,
            "start_date": base.date.today().strftime("%Y-%m-%d"),
            "end_date": (base.date.today() + base.timedelta(days=1)).strftime(
                "%Y-%m-%d"
            ),
        }

    def _test_redirect_to_url_detail(self, response):
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.url_detail)

    def test_get_authenticated_ne_period(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 404)

    def test_get_authenticated_period_in_progress(self):
        base.create_period(self.user)
        self.client.force_login(self.user)
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 200)

    def test_get_authenticated_period_closing_accounts(self):
        period = base.create_period(self.user)
        period.status = base.facade.AccountingPeriod.Status.CLOSING_ACCOUNTS
        period.save()

        self.client.force_login(self.user)
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 200)

    def test_get_unauthenticated(self):
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.url_login_next(self.url_detail))

    def test_try_close_period_in_progress_d0(self):
        base.create_period(
            self.user,
            start_data=base.date.today(),
            end_date=base.date.today(),
        )
        self.client.force_login(self.user)
        response = self.client.post(self.url_detail)
        self.assertEqual(response.status_code, 404)

    def test_try_close_period_in_progress_dm1(self):
        yesterday = base.date.today() - base.timedelta(days=1)
        period = base.create_period(
            self.user,
            start_data=yesterday,
            end_date=yesterday,
            status=base.facade.AccountingPeriod.Status.IN_PROGRESS,
        )

        self.client.force_login(self.user)

        response = self.client.post(self.url_detail)
        self._test_redirect_to_url_detail(response)

        period = base.facade.AccountingPeriod.objects.get(pk=period.pk)
        self.assertEqual(
            period.status, base.facade.AccountingPeriod.Status.CLOSING_ACCOUNTS
        )

    def test_close_period_and_transactions_count_eq_0(self):
        period, form_data = self.prepare_closing_accounts()
        self.client.force_login(self.user)

        response = self.client.post(self.url_detail, data=form_data)

        self._test_redirect_to_url_detail(response)

        prev_p = base.facade.AccountingPeriod.objects.get(pk=period.pk)
        self.assertEqual(prev_p.status, base.facade.AccountingPeriod.Status.CLOSED)

        next_p = base.facade.AccountingPeriod.objects.get(pk=period.pk + 1)
        self.assertEqual(next_p.status, base.facade.AccountingPeriod.Status.IN_PROGRESS)

    def test_close_period_despesas(self):
        period, form_data = self.prepare_closing_accounts()
        self.client.force_login(self.user)

        _, _, debit = base.create_children_accounts(
            user=self.user,
            root=facade.Account.objects.get_expense(self.user),
        )

        _, _, credit = base.create_children_accounts(
            user=self.user,
            root=facade.Account.objects.get_asset(self.user),
        )

        _ = base.create_debit_and_credit(
            period=period, value=50, debit=debit, credit=credit
        )

        self.assertEqual(debit.get_individual_balance(), 50)

        response = self.client.post(self.url_detail, data=form_data)
        self._test_redirect_to_url_detail(response)

        self.assertEqual(debit.get_individual_balance(), 0)

    def test_close_period_receitas(self):
        period, form_data = self.prepare_closing_accounts()
        self.client.force_login(self.user)

        _, _, debit = base.create_children_accounts(
            user=self.user,
            root=facade.Account.objects.get_asset(self.user),
        )

        _, _, credit = base.create_children_accounts(
            user=self.user,
            root=facade.Account.objects.get_revenue(self.user),
        )

        _ = base.create_debit_and_credit(
            period=period, value=50, debit=debit, credit=credit
        )

        self.assertEqual(credit.get_individual_balance(), 50)

        response = self.client.post(self.url_detail, data=form_data)
        self._test_redirect_to_url_detail(response)

        self.assertEqual(credit.get_individual_balance(), 0)
