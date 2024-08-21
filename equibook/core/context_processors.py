from equibook.core.facade import settings

app_name = "core"


def app_settings(request):
    if app_name != request.resolver_match.app_name or (
        not request.user.is_authenticated
    ):
        return {}

    app_settings = settings.get_app_settings(request.user, to_dict=True)

    return {"app_settings": app_settings}
