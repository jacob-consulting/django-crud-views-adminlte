from django.apps import apps
from django.core.checks import CheckMessage, Error, Tags, register
from django.utils.module_loading import import_string

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


def _menu_entries(items, path="ADMINLTE['menu']"):
    """(location, item) of every ``viewset`` entry, submenus included."""
    for index, item in enumerate(items or []):
        if not isinstance(item, dict):
            continue
        location = f"{path}[{index}]"
        if "viewset" in item:
            yield location, item
        if isinstance(item.get("submenu"), list):
            yield from _menu_entries(item["submenu"], f"{location}['submenu']")


def _filter_classes(filters) -> list:
    classes = []
    for spec in filters or []:
        try:
            classes.append(import_string(spec) if isinstance(spec, str) else spec)
        except ImportError:
            continue  # the host reports its own broken filter paths when it builds the menu
    return classes


def _entry_errors(location: str, item: dict) -> list[CheckMessage]:
    from crud_views.lib.exceptions import ViewSetNotFoundError
    from crud_views.lib.viewset import ViewSet

    from crud_views_adminlte.menu import DEFAULT_VIEW

    name, key = item["viewset"], item.get("view", DEFAULT_VIEW)
    try:
        viewset = ViewSet.get_viewset(name)
    except ViewSetNotFoundError:
        return [
            Error(
                f"{location} names ViewSet {name!r}, which is not registered.",
                hint="Use the name= of a ViewSet whose views are in the URLconf.",
                id="crud_views_adminlte.E010",
            )
        ]
    if viewset.has_parent:
        return [
            Error(
                f"{location} names ViewSet {name!r}, a child of {viewset.parent.name!r}: its URLs need the parent's "
                "primary key, so it cannot be linked from the menu.",
                hint=f"Link the parent ViewSet {viewset.parent.name!r} instead; its pages link to the children.",
                id="crud_views_adminlte.E011",
            )
        ]
    if not (viewset.is_view_registered(key) or (key == "list" and viewset.is_view_registered("card"))):
        return [
            Error(
                f"{location} names view {key!r} of ViewSet {name!r}, which has no such view.",
                hint=f"Registered views: {', '.join(sorted(viewset.get_all_views())) or 'none'}.",
                id="crud_views_adminlte.E012",
            )
        ]
    if viewset.get_view_class(key).cv_object:
        return [
            Error(
                f"{location} names view {key!r} of ViewSet {name!r}, an object view: its URL needs a primary key, "
                "so it cannot be linked from the menu.",
                hint="Link a view without an object, such as 'list' or 'create'.",
                id="crud_views_adminlte.E015",
            )
        ]
    errors = []
    if not item.get("text"):
        # tracker C3: crud_views has no request-free label accessor for a ViewSet, so the entry names its own text
        errors.append(
            Error(
                f"{location} (ViewSet {name!r}) has no 'text': the menu link would have no label.",
                hint='Add "text", e.g. "text": _("Authors").',
                id="crud_views_adminlte.E014",
            )
        )
    return errors


@register(Tags.urls)
def check_menu(app_configs=None, **kwargs) -> list[CheckMessage]:
    """Errors for ``viewset`` entries in ``ADMINLTE["menu"]`` that would not resolve, and for a filter pipeline that
    would ignore them (the host would render ``href="#"`` links for every user)."""
    from django.urls import get_resolver
    from django_adminlte4.conf import get_config
    from django_adminlte4.menu.filters import HrefFilter

    from crud_views_adminlte.menu import ViewSetGateFilter, ViewSetHrefFilter

    config = get_config()
    entries = list(_menu_entries(config.get("menu")))
    if not entries:
        return []
    get_resolver().url_patterns  # noqa: B018 - import the URLconf, which registers the ViewSets (tracker C5)

    errors: list[CheckMessage] = []
    filters = _filter_classes(config.get("filters"))
    href = [i for i, klass in enumerate(filters) if isinstance(klass, type) and issubclass(klass, ViewSetHrefFilter)]
    host = [i for i, klass in enumerate(filters) if isinstance(klass, type) and issubclass(klass, HrefFilter)]
    gate = any(isinstance(klass, type) and issubclass(klass, ViewSetGateFilter) for klass in filters)
    if not href or (host and min(host) < min(href)) or not gate:
        errors.append(
            Error(
                "ADMINLTE['menu'] has 'viewset' entries, but ADMINLTE['filters'] does not run ViewSetHrefFilter "
                'before HrefFilter and ViewSetGateFilter: the entries would render as href="#" for every user.',
                hint="Set ADMINLTE['filters'] = [*VIEWSET_FILTERS, *DEFAULT_FILTERS] (crud_views_adminlte.menu, "
                "django_adminlte4.conf).",
                id="crud_views_adminlte.E013",
            )
        )
    for location, item in entries:
        errors.extend(_entry_errors(location, item))
    return errors
