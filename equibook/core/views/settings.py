from equibook.core import facade
from . import base


class SettingUpdateView(base.UpdateView):
    form_class = base.SettingForm
    template_name = "core/settings/update.html"

    def get_object(self, queryset=None):
        return facade.get_app_settings(self.request.user)

    def get_success_url(self) -> str:
        return base.reverse("core:setting-update")


url_patterns = [
    base.path(
        "settings/update/",
        SettingUpdateView.as_view(),
        name="setting-update",
    ),
]
