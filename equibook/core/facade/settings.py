from equibook.core.facade import base


def get_app_settings(user: base.User, to_dict=False):
    obj, _ = base.Setting.objects.get_or_create(user=user)
    return obj if not to_dict else obj.to_dict()
