"""The Acme app's icon vocabulary: domain meaning -> Bootstrap Icons name (without the ``bi-`` prefix).

App code, templates and seed data name icons by what they stand for (``"customer"``, ``"order"``), never by picture or
library. This table is the only place that knows the library: ``settings.py`` feeds it to ``CRUD_VIEWS_ICONS`` (for
django-crud-views, as ``bi:<name>``), templates render them through crud_views' ``{% cv_icon %}`` with the same
mapping, and ``icon_class`` hands the CSS class to the places that take one (the sidebar menu, the dashboard's
adminlte-django widgets). Another theme keeps the keys and swaps the values.
"""

ACME_ICONS: dict[str, str] = {
    # entities
    "customer": "building",
    "address": "geo-alt",
    "order": "file-earmark-text",
    "subscription": "arrow-repeat",
    "product": "gift",
    "beans": "flower1",
    "equipment": "gear",
    "category": "layers",
    "lot": "box-arrow-in-down",
    "cupping": "cup-hot",
    "batch": "fire",
    "shipment": "truck",
    # menu sections: unused by this demo's sidebar (nav titles carry no icon), kept so the vocabulary stays the same
    # as the sister demo's
    "sales": "building",
    "catalog": "gift",
    "roastery": "fire",
    # property groups
    "about": "info-circle",
    "pricing": "tags",
    "stock": "speedometer",
    "origin": "geo-alt",
    # actions
    "packing-slip": "printer",
    "duplicate": "copy",
    "run-subscriptions": "play-circle",
    "table-view": "table",
    "mark-default": "star",
    # workflow steps and shipment events
    "confirm": "check-lg",
    "roasted": "cup-hot",
    "shipped": "gift",
    "delivered": "check-circle",
    "cancelled": "x-circle",
    "picked-up": "gift",
    "in-transit": "truck",
    # host pages: sidebar entries, dashboard widgets, users, theming and the code panel
    "dashboard": "speedometer2",
    "showcase": "grid",
    "theming": "brush",
    "users": "people",
    "add": "plus-lg",
    "search": "search",
    "trend-up": "arrow-up",
    "trend-down": "arrow-down",
    "revenue": "currency-euro",
    "green-stock": "box-seam",
    "docs": "book",
    "code": "code-slash",
    "file": "file-earmark-code",
}


def icon_class(key: str) -> str:
    """The CSS class of a semantic icon, for markup that takes a class instead of ``{% cv_icon %}``."""
    return f"bi bi-{ACME_ICONS[key]}"
