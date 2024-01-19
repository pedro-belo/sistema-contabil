from equibook.core.tests import base
from equibook.core import facade


class AccountingPeriodDistributeResultsTestCase(base.TestCase):
    CASE_EARN = 1
    CASE_LOSS = -1
    CASE_ZERO = 0

    def setUp(self) -> None:
        self.user = base.create_default_user()

        self.asset = facade.Account.objects.get_asset(self.user)
        self.equity = facade.Account.objects.get_equity(self.user)
        self.expense = facade.Account.objects.get_expense(self.user)
        self.revenue = facade.Account.objects.get_revenue(self.user)
        self.result = facade.Account.objects.get_expense(self.user)

        self.loss_account = facade.create_account(
            user=self.user,
            parent=self.equity,
            form_data={"name": "Prejuizo"},
        )

        self.earn_account = facade.create_account(
            user=self.user,
            parent=self.equity,
            form_data={"name": "Lucro"},
        )

        self.period = base.create_period(
            self.user, status=facade.AccountingPeriod.Status.CLOSING_ACCOUNTS
        )

    def prepare_case(self, c: int):
        _, _, asset = base.create_children_accounts(self.user, root=self.asset)
        _, equity, _ = base.create_children_accounts(self.user, root=self.equity)
        _, _, expense = base.create_children_accounts(self.user, root=self.expense)
        _, revenue, _ = base.create_children_accounts(self.user, root=self.revenue)

        # AUMENTO DE CAPITAL
        # ASSET: 1000, EQUITY: 1000
        base.create_debit_and_credit(
            period=self.period, value=1000, debit=asset, credit=equity
        )

        # GASTO COM X
        # ASSET: 1000 - 400 = 600
        # EXPENSE: 400
        base.create_debit_and_credit(
            period=self.period, value=400, debit=expense, credit=asset
        )

        # ~GASTO
        # ASSET: 600 + 200 = 800
        # EXPENSE: 400 - 200 = 200
        base.create_debit_and_credit(
            period=self.period, value=200, debit=asset, credit=expense
        )

        # RECEITA COM A
        # ASSET: 800 + 600 = 1400
        # REVENUE: 600
        base.create_debit_and_credit(
            period=self.period, value=600, debit=asset, credit=revenue
        )

        # ~RECEITA
        # ASSET: 1300
        # REVENUE: 500
        base.create_debit_and_credit(
            period=self.period, value=100, debit=revenue, credit=asset
        )

        # Exense = Revenue
        # EXPENSE: 200 + 300 = 500
        # ASSET: 1300 - 300 = 1000
        base.create_debit_and_credit(
            period=self.period, value=300, debit=expense, credit=asset
        )

        self.assertEqual(asset.get_individual_balance(), 1000)
        self.assertEqual(expense.get_individual_balance(), 500)
        self.assertEqual(revenue.get_individual_balance(), 500)

    def accounting_period_distribute_results(self):
        facade.accounting_period_close_accounts(self.period, form={})
        facade.accounting_period_distribute_results(
            self.period,
            form_data={
                "loss_account": self.loss_account,
                "earn_account": self.earn_account,
            },
        )

    def test_result_loss(self):
        self.prepare_case(c=self.CASE_LOSS)

        _, expense, _ = base.create_children_accounts(self.user, root=self.expense)
        _, asset, _ = base.create_children_accounts(self.user, root=self.asset)

        LOSS = 1

        base.create_debit_and_credit(
            period=self.period, value=LOSS, debit=expense, credit=asset
        )

        self.accounting_period_distribute_results()

        self.assertEqual(self.loss_account.get_individual_balance(), -LOSS)
        self.assertEqual(self.earn_account.get_individual_balance(), 0)

    def test_result_earn(self):
        _, revenue, _ = base.create_children_accounts(self.user, root=self.revenue)
        _, asset, _ = base.create_children_accounts(self.user, root=self.asset)

        EARN = 1

        base.create_debit_and_credit(
            period=self.period, value=EARN, debit=asset, credit=revenue
        )

        self.accounting_period_distribute_results()

        self.assertEqual(self.loss_account.get_individual_balance(), 0)
        self.assertEqual(self.earn_account.get_individual_balance(), EARN)

    def test_result_zero(self):
        ...


class AccountingPeriodCloseAccountsTestCase(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
        facade.Account.objects.get_revenue(self.user)

        self.asset = facade.Account.objects.get_asset(self.user)
        self.result = facade.Account.objects.get_result(self.user)
        self.liability = facade.Account.objects.get_liability(self.user)
        self.equity = facade.Account.objects.get_equity(self.user)
        self.revenue = facade.Account.objects.get_revenue(self.user)
        self.expense = facade.Account.objects.get_expense(self.user)

        self.period = base.create_period(
            self.user, status=facade.AccountingPeriod.Status.CLOSING_ACCOUNTS
        )

    def test_no_transactions(self):
        facade.accounting_period_close_accounts(self.period, form={})
        self.assertEqual(facade.Transaction.objects.count(), 0)

    def test_revenue_balance(self):
        _, asset, _ = base.create_children_accounts(user=self.user, root=self.asset)

        _, _, revenue = base.create_children_accounts(
            user=self.user,
            root=facade.Account.objects.get_revenue(self.user),
        )

        base.create_debit_and_credit(self.period, value=10, debit=asset, credit=revenue)
        self.assertEqual(revenue.get_individual_balance(), 10)

        base.create_debit_and_credit(self.period, value=5, debit=revenue, credit=asset)
        self.assertEqual(revenue.get_individual_balance(), 5)

        facade.accounting_period_close_accounts(self.period, form={})
        self.assertEqual(revenue.get_individual_balance(), 0)

    def test_expense_balance(self):
        _, asset, _ = base.create_children_accounts(user=self.user, root=self.asset)

        _, _, expense = base.create_children_accounts(
            user=self.user,
            root=facade.Account.objects.get_expense(self.user),
        )

        base.create_debit_and_credit(
            self.period, value=10, debit=asset, credit=self.equity
        )
        self.assertEqual(expense.get_individual_balance(), 0)

        base.create_debit_and_credit(self.period, value=10, debit=expense, credit=asset)
        self.assertEqual(expense.get_individual_balance(), 10)

        base.create_debit_and_credit(self.period, value=5, debit=asset, credit=expense)
        self.assertEqual(expense.get_individual_balance(), 5)

        facade.accounting_period_close_accounts(self.period, form={})
        self.assertEqual(expense.get_individual_balance(), 0)

    def test_result_balance(self):
        _, _, asset = base.create_children_accounts(user=self.user, root=self.asset)
        _, equity, _ = base.create_children_accounts(user=self.user, root=self.equity)
        _, _, expense = base.create_children_accounts(user=self.user, root=self.expense)
        _, revenue, _ = base.create_children_accounts(user=self.user, root=self.revenue)

        # AUMENTO DE CAPITAL
        # ASSET: 10
        # EQUITY: 10
        base.create_debit_and_credit(
            period=self.period, value=10, debit=asset, credit=equity
        )

        # GASTO X
        # ASSET: 10 - 8 = 2
        # EXPENSE: 8
        base.create_debit_and_credit(
            period=self.period, value=8, debit=expense, credit=asset
        )

        # RECEITA A
        # ASSET: 2 + 20 = 22
        # REVENUE: 20
        base.create_debit_and_credit(
            period=self.period, value=20, debit=asset, credit=revenue
        )

        # GASTO Y
        # ASSET: 22 - 16 = 6
        # EXPENSE: 8 + 16 = 24
        base.create_debit_and_credit(
            period=self.period, value=16, debit=expense, credit=asset
        )

        # RECEITA B
        # ASSET: 6 + 32 = 38
        # REVENUE: 20 + 32 = 52
        base.create_debit_and_credit(
            period=self.period, value=32, debit=asset, credit=revenue
        )

        EXPENSE_BALANCE = 24
        REVENUE_BALANCE = 52
        self.assertEqual(expense.get_individual_balance(), EXPENSE_BALANCE)
        self.assertEqual(revenue.get_individual_balance(), REVENUE_BALANCE)
        self.assertEqual(asset.get_individual_balance(), 38)
        self.assertEqual(equity.get_individual_balance(), 10)

        facade.accounting_period_close_accounts(self.period, form={})
        self.assertEqual(expense.get_individual_balance(), 0)
        self.assertEqual(revenue.get_individual_balance(), 0)

        result_operations = facade.Operation.objects.filter(account=self.result)

        debit_sum = result_operations.filter(
            type=facade.OperationType.DEBIT,
        ).aggregate(debit_sum=base.Sum("value"))["debit_sum"]
        self.assertEqual(debit_sum, EXPENSE_BALANCE)

        credit_sum = result_operations.filter(
            type=facade.OperationType.CREDIT,
        ).aggregate(credit_sum=base.Sum("value"))["credit_sum"]
        self.assertEqual(credit_sum, REVENUE_BALANCE)


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
