from equibook.core import facade
from equibook.core.tests import base


class AccountModelTestCase(base.TestCase):
    def setUp(self) -> None:
        self.user = base.create_default_user()
    
    def test_to_dict_except_dark_mode(self):
        user_settings = self.user.user_settings
        setting_d = user_settings.to_dict()
        self.assertEqual(setting_d["entity"], user_settings.entity)
        self.assertEqual(setting_d["base_currency"]["code"], user_settings.base_currency)
        self.assertEqual(setting_d["base_currency"]["label"], user_settings.get_base_currency_display())
        self.assertEqual(setting_d["current_currency"]["code"], user_settings.current_currency)
        self.assertEqual(setting_d["current_currency"]["label"], user_settings.get_current_currency_display())
        self.assertEqual(setting_d["exchange_rate"], user_settings.exchange_rate)
        self.assertEqual(setting_d["defined_first_period"], False)
        self.assertEqual(setting_d["theme"]["code"], user_settings.theme)
        self.assertEqual(setting_d["theme"]["label"], user_settings.get_theme_display())

    def test_to_dict_dark_mode_light(self):
        user_settings = self.user.user_settings
        user_settings.theme = facade.Setting.Theme.LIGHT
        user_settings.save()
        setting_d = user_settings.to_dict()
        self.assertEqual(setting_d["DARK_MODE"], False)

    def test_to_dict_dark_mode_dark(self):
        user_settings = self.user.user_settings
        user_settings.theme = facade.Setting.Theme.DARK
        user_settings.save()
        setting_d = user_settings.to_dict()
        self.assertEqual(setting_d["DARK_MODE"], True)
