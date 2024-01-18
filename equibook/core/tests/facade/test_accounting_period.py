from equibook.core.tests import base
from equibook.core import facade


class AccountingPeriodCloseAccountsTestCase(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
        self.period = base.create_period(
            self.user, status=facade.AccountingPeriod.Status.CLOSING_ACCOUNTS
        )

    def test_no_transactions(self):
        facade.accounting_period_close_accounts(self.period, form={})
        self.assertEqual(facade.Transaction.objects.count(), 0)

    def test_receita(self):
        _, asset_d, asset_c = base.create_children_accounts(
            user=self.user,
            root=facade.Account.objects.get_asset(self.user),
        )

        _, _, revenue = base.create_children_accounts(
            user=self.user,
            root=facade.Account.objects.get_revenue(self.user),
        )

        # Aumenta Receita
        base.create_debit_and_credit(
            self.period,
            value=10,
            debit=asset_d,
            credit=revenue,
        )
        self.assertEqual(revenue.get_individual_balance(), 10)

        # Diminui Receita
        base.create_debit_and_credit(
            self.period,
            value=5,
            debit=revenue,
            credit=asset_c,
        )
        self.assertEqual(revenue.get_individual_balance(), 5)

        # Receita encerrada (saldo=0)
        facade.accounting_period_close_accounts(self.period, form={})
        self.assertEqual(revenue.get_individual_balance(), 0)


class CreateFirstAccountPeriodTestCase(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
        self.date = base.date.today()
        self.form_data = {
            "start_date": self.date,
            "end_date": self.date,
        }

    def test_create_first_account_period(self):
        period = facade.create_first_account_period(
            user=self.user, form_data=self.form_data
        )

        self.assertIsNotNone(period.id)
        self.assertEqual(period.status, facade.AccountingPeriod.Status.IN_PROGRESS)
        self.assertEqual(period.user, self.user)
        self.assertEqual(period.start_date, self.date)
        self.assertEqual(period.end_date, self.date)

    def test_period_flag_in_user_setting(self):
        user_setting = facade.get_app_settings(self.user)
        self.assertEqual(user_setting.defined_first_period, False)

        facade.create_first_account_period(user=self.user, form_data=self.form_data)

        user_setting = facade.get_app_settings(self.user)
        self.assertEqual(user_setting.defined_first_period, True)

    def test_create_first_account_period_invalid_date(self):
        start_date = base.date.today()
        end_date = start_date - base.timedelta(days=1)

        with self.assertRaises(ValueError):
            facade.create_first_account_period(
                user=self.user,
                form_data={"start_date": start_date, "end_date": end_date},
            )
