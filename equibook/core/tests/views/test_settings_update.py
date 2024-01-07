from equibook.core.tests import base
from equibook.core import facade
from decimal import Decimal


class AccountSettingViewTests(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()

    def test_get_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(base.reverse("core:setting-update"))
        self.assertEqual(response.status_code, 200)

    def test_get_unauthenticated(self):
        expected_url = (
            base.reverse("users:login") + "?next=" + base.reverse("core:setting-update")
        )

        response = self.client.get(base.reverse("core:setting-update"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)

    def _test_update_authenticated(self):
        setting = facade.get_app_settings(self.user)
        self.assertEqual(setting.entity, "Entity Name")
        self.assertEqual(setting.base_currency, facade.Currency.BRL)
        self.assertEqual(setting.current_currency, facade.Currency.BRL)
        self.assertEqual(setting.theme, facade.Setting.Theme.LIGHT)
        self.assertEqual(setting.exchange_rate, 0)

    def test_update_authenticated(self):
        self._test_update_authenticated()

        setting = facade.get_app_settings(self.user)
        self.client.force_login(self.user)

        data = {
            "entity": f"{setting.entity} updated",
            "current_currency": facade.Currency.JPY,
            "exchange_rate": 1,
            "theme": facade.Setting.Theme.DARK,
        }

        response = self.client.post(base.reverse("core:setting-update"), data=data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.reverse("core:setting-update"))

        setting = facade.get_app_settings(self.user)
        self.assertEqual(setting.entity, data["entity"])
        self.assertEqual(setting.base_currency, facade.Currency.BRL)
        self.assertEqual(setting.current_currency, data["current_currency"])
        self.assertEqual(setting.theme, data["theme"])
        self.assertEqual(setting.exchange_rate, Decimal(data["exchange_rate"]))
        self.client.force_login(self.user)

    def test_update_unauthenticated(self):
        setting = facade.get_app_settings(self.user)

        data = {
            "entity": f"{setting.entity} updated",
            "current_currency": facade.Currency.JPY,
            "exchange_rate": 1,
            "theme": facade.Setting.Theme.DARK,
        }

        expected_url = (
            base.reverse("users:login") + "?next=" + base.reverse("core:setting-update")
        )

        response = self.client.post(base.reverse("core:setting-update"), data=data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)
