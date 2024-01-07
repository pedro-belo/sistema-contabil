from equibook.core import facade
from equibook.core.tests import base


class AccountModelTestCase(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
        self.period = base.create_period(self.user)

    def test_in_progress(self):
        self.period.status = facade.AccountingPeriod.Status.IN_PROGRESS
        self.period.save()
        return self.assertEqual(self.period.in_progress(), True)

    def test_closing_accounts(self):
        self.period.status = facade.AccountingPeriod.Status.CLOSING_ACCOUNTS
        self.period.save()
        return self.assertEqual(self.period.closing_accounts(), True)

    def test_closed(self):
        self.period.status = facade.AccountingPeriod.Status.CLOSED
        self.period.save()
        return self.assertEqual(self.period.closed(), True)

    def test_start_date_dmy(self):
        d = self.period.start_date.strftime("%d/%m/%Y")
        self.assertEqual(self.period.start_date_dmy(), d)
        

    def test_end_date_dmy(self):
        d = self.period.end_date.strftime("%d/%m/%Y")
        self.assertEqual(self.period.end_date_dmy(), d)

    def test_is_period_closeable_today(self):
        today = base.date.today()
        self.period.start_date = today
        self.period.end_date = today
        self.period.save()
        self.assertEqual(self.period.is_period_closeable(), False)

    def test_is_period_closeable_yesterday(self):
        today = base.date.today()
        date = today - base.timedelta(days=1)
        self.period.start_date = date
        self.period.end_date = date
        self.period.save()
        self.assertEqual(self.period.is_period_closeable(), True)

    def test_is_period_closeable_tomorrow(self):
        today = base.date.today()
        date = today + base.timedelta(days=1)
        self.period.start_date = date
        self.period.end_date = date
        self.period.save()
        self.assertEqual(self.period.is_period_closeable(), False)

    def test_days_to_close_period_today(self):
        today = base.date.today()

        self.period.start_date = today
        self.period.end_date = today
        self.period.save()

        self.assertEqual(self.period.days_to_close_period(), 0)

    def test_days_to_close_period_tomorrow(self):
        today = base.date.today()

        self.period.start_date = today
        self.period.end_date = today + base.timedelta(days=1)
        self.period.save()

        self.assertEqual(self.period.days_to_close_period(), 1)
