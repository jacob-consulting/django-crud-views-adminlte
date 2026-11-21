from django.apps import apps
from django.core.checks import CheckMessage, Error, Tags, register

#: Apps whose templates the theme overrides: Django's app template loader takes the first app that has the template,
#: so the theme must be listed before each of them.
OVERRIDDEN_APPS = ("crud_views", "crud_views_object_detail")


@register(Tags.templates)
def check_app_order(app_configs=None, **kwargs) -> list[CheckMessage]:
    """Error when crud_views_adminlte comes after an app whose templates it overrides."""
    names = [config.name for config in apps.get_app_configs()]
    if "crud_views_adminlte" not in names:
        return []
    theme = names.index("crud_views_adminlte")
    before = [name for name in OVERRIDDEN_APPS if name in names and names.index(name) < theme]
    if not before:
        return []
    return [
        Error(
            f"crud_views_adminlte is listed in INSTALLED_APPS after {', '.join(map(repr, before))}: those apps' "
            "templates win over the theme's overrides (stock crud_views markup).",
            hint="List crud_views_adminlte before crud_views and crud_views_object_detail in INSTALLED_APPS.",
            id="crud_views_adminlte.E001",
        )
    ]
