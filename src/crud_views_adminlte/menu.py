"""ViewSet entries for adminlte-django's sidebar menu (``ADMINLTE["menu"]``).

An entry ``{"viewset": "<name>", "text": "...", "view": "<key>"}`` (``view`` defaults to ``"list"``, ``icon`` defaults
to the ViewSet's ``icon_header``) links to that crud_views view and is shown only to users who may open it. Add the
theme's filters in front of the host's::

    from django_adminlte4.conf import DEFAULT_FILTERS
    from crud_views_adminlte.menu import VIEWSET_FILTERS

    ADMINLTE = {..., "filters": [*VIEWSET_FILTERS, *DEFAULT_FILTERS]}

Two filters, because the host runs every request-independent filter (``per_request = False``) once per process before
any per-request one, whatever the configured order (tracker A2): ``ViewSetHrefFilter`` resolves the URL and icon in
that once-per-process half, ahead of the host's ``HrefFilter`` (which would otherwise set ``href="#"``);
``ViewSetGateFilter`` checks access per request. Misconfiguration is reported by the system checks
``crud_views_adminlte.E010``-``E015`` (``crud_views_adminlte.checks.check_menu``).
"""

from __future__ import annotations

from typing import Any

from django.urls import NoReverseMatch, get_resolver, get_urlconf, reverse
from django_adminlte4.menu.filters import BaseFilter

Item = dict[str, Any]

# crud_views is imported inside the functions: settings modules import VIEWSET_FILTERS from here, before the app
# registry is ready (crud_views.lib.viewset imports models).

#: Dotted paths of the theme's menu filters, to be listed before the host's ``DEFAULT_FILTERS``.
VIEWSET_FILTERS: list[str] = [
    "crud_views_adminlte.menu.ViewSetHrefFilter",
    "crud_views_adminlte.menu.ViewSetGateFilter",
]

DEFAULT_VIEW = "list"


def entry_view_class(item: Item):
    """The crud_views view class a menu entry points to; None when the entry cannot be linked from the menu.

    Unusable entries (unknown ViewSet or view key, a child ViewSet, an object view) are reported by the system checks;
    at runtime they are left out of the menu instead of breaking every page.
    """
    from crud_views.lib.exceptions import ViewSetKeyFoundError, ViewSetNotFoundError
    from crud_views.lib.viewset import ViewSet

    try:
        viewset = ViewSet.get_viewset(item["viewset"])
        view_class = viewset.get_view_class(item.get("view", DEFAULT_VIEW))
    except (ViewSetNotFoundError, ViewSetKeyFoundError):
        return None
    if viewset.has_parent or view_class.cv_object:
        return None
    return view_class


def icon_class(value: str | None) -> str | None:
    """The CSS classes of a crud_views icon value, for the host's ``<i class="nav-icon {{ item.icon }}">``.

    tracker C4: crud_views renders icons to HTML (``render_icon``) but has no accessor for the classes alone, so this
    repeats ``font_renderer``'s class formatting from the public ``resolve_icon`` and ``get_libraries``. Icons of a
    non-``font`` renderer (SVG sprites, ...) have no class form: None, the entry then needs its own ``icon``.
    """
    from crud_views.lib.icons import get_libraries, resolve_icon

    resolved = resolve_icon(value)
    if resolved is None:
        return None
    prefix, name = resolved
    if not prefix:
        return name
    config = get_libraries().get(prefix)
    if not isinstance(config, dict) or config.get("renderer", "font") != "font":
        return None
    template = config.get("class")
    if not isinstance(template, str):
        return None
    try:
        classes = template.format(name=name)
        if config.get("placement") == "host":
            classes = config.get("standalone", "{name_class}").format(name_class=classes)
    except Exception:
        return None
    return classes


class ViewSetHrefFilter(BaseFilter):
    """Resolve ``href`` (and a missing ``icon``) of ``viewset`` entries, once per process (per language).

    Must come before the host's ``HrefFilter``, which skips items that already have ``href`` (tracker A2).
    ``text`` is required in the entry: crud_views has no request-free label accessor (tracker C3).
    """

    per_request = False  # tracker A2: runs in the host's once-per-process half, ahead of HrefFilter

    def __init__(self, request: Any = None) -> None:
        super().__init__(request)
        # tracker C5: ViewSets register when their views module is imported, which the URLconf does; a menu built
        # before the first URL resolution of the process (first request, a template rendered outside a request)
        # would find no ViewSet. Built once per process (per language), so this costs nothing per request.
        get_resolver(get_urlconf()).url_patterns  # noqa: B018

    def transform(self, item: Item) -> Item | None:
        if isinstance(item.get("submenu"), list):
            item["submenu"] = [child for child in map(self.transform, item["submenu"]) if child is not None]
        if "viewset" not in item:
            return item
        view_class = entry_view_class(item)
        if view_class is None:
            return None
        viewset = view_class.cv_viewset
        try:
            item["href"] = reverse(viewset.get_router_name(item.get("view", DEFAULT_VIEW)))
        except NoReverseMatch:
            item["href"] = "#"  # as the host's HrefFilter does for an unresolvable route
        if "icon" not in item:
            icon = icon_class(viewset.icon_header)
            if icon:
                item["icon"] = icon
        return item


class ViewSetGateFilter(BaseFilter):
    """Drop ``viewset`` entries the request's user may not open, per request.

    Access is the view class's ``cv_has_access(user)`` (model level, no object), the check crud_views itself uses for
    links that have no object (sibling and collection buttons). Anonymous users, and requests without a user, see no
    ``viewset`` entry at all (Review Focus 1). A submenu parent left without children by this filter is dropped unless
    it links somewhere itself: the host's ``GateFilter`` cannot do that once ``HrefFilter`` has given every parent
    ``href="#"`` (tracker A10).
    """

    def transform(self, item: Item) -> Item | None:
        submenu = item.get("submenu")
        if isinstance(submenu, list) and submenu:
            item["submenu"] = [child for child in map(self.transform, submenu) if child is not None]
            # tracker A10: the host's GateFilter keeps the emptied parent, which HrefFilter has given href="#"
            if not item["submenu"] and "viewset" not in item and not self._links(item):
                return None
        if "viewset" in item and not self._allowed(item):
            return None
        return item

    @staticmethod
    def _links(item: Item) -> bool:
        return any(key in item for key in ("url", "route")) or item.get("href", "#") != "#"

    def _allowed(self, item: Item) -> bool:
        user = getattr(self.request, "user", None)
        if user is None or not user.is_authenticated:
            return False
        view_class = entry_view_class(item)
        return view_class is not None and view_class.cv_has_access(user)
