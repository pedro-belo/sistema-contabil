from equibook.core.tests import base
from equibook.core import facade


class SettingUpdateViewTestCase(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
        self.url_update = base.reverse("core:setting-update")
        setting = facade.get_app_settings(self.user)
        self.form_data = {
            "entity": f"{setting.entity} updated",
            "current_currency": facade.Currency.JPY,
            "exchange_rate": 1,
        }

    def test_get_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url_update)
        self.assertEqual(response.status_code, 200)

    def test_get_unauthenticated(self):
        response = self.client.get(self.url_update)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.url_login_next(self.url_update))

    def _test_update_authenticated(self):
        setting = facade.get_app_settings(self.user)
        self.assertEqual(setting.entity, "Entity Name")
        self.assertEqual(setting.base_currency, facade.Currency.BRL)
        self.assertEqual(setting.current_currency, facade.Currency.BRL)
        self.assertEqual(setting.exchange_rate, 0)

    def test_update_authenticated(self):
        self._test_update_authenticated()

        setting = facade.get_app_settings(self.user)
        self.client.force_login(self.user)

        response = self.client.post(self.url_update, data=self.form_data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.url_update)

        setting = facade.get_app_settings(self.user)
        self.assertEqual(setting.entity, self.form_data["entity"])
        self.assertEqual(setting.base_currency, facade.Currency.BRL)
        self.assertEqual(setting.current_currency, self.form_data["current_currency"])
        self.assertEqual(
            setting.exchange_rate,
            base.Decimal(self.form_data["exchange_rate"]),
        )
        self.client.force_login(self.user)

    def test_update_unauthenticated(self):
        response = self.client.post(self.url_update, data=self.form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, base.url_login_next(self.url_update))
