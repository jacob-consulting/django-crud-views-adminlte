"""The Acme sidebar: adminlte-django's ``ADMINLTE["menu"]``, replacing the CoreUI demo's ``acme_nav`` tag library.

``viewset`` entries are resolved and permission-gated by the theme's filters (``crud_views_adminlte.menu``); ``route``
entries with ``can`` by the host's own. Icons are named through ``config.icons``.
"""

from config.icons import icon_class as _icon

MENU: list[dict] = [
    {"text": "Dashboard", "route": "dashboard:index", "icon": _icon("dashboard")},
    {"header": "Sales"},
    # Account managers hold only `add_customer` globally (their view rights are Guardian object grants), so the
    # customer list's own access check decides who sees this entry.
    {"viewset": "customer", "text": "Customers", "icon": _icon("customer")},
    {"viewset": "orders", "text": "Orders", "icon": _icon("order")},
    {"viewset": "subscriptions", "text": "Subscriptions", "icon": _icon("subscription")},
    {"header": "Catalog"},
    {"viewset": "product", "text": "Products", "icon": _icon("product")},
    {"viewset": "category", "text": "Categories", "icon": _icon("category")},
    {"header": "Roastery"},
    {"viewset": "lot", "text": "Green lots", "icon": _icon("lot")},
    {"viewset": "batch", "text": "Roast batches", "icon": _icon("batch")},
    # the shipment list checks `sales.view_order` and scopes the rows to the user's customers
    {"viewset": "shipment", "text": "Shipments", "icon": _icon("shipment")},
    {"header": "Developer"},
    {"viewset": "showcaseitem", "text": "Form showcase", "icon": _icon("showcase")},
    {"text": "How this is themed", "route": "theming", "icon": _icon("theming")},
    # tracker A14: the host keeps a header whose entries are all hidden; this section has one gated entry, so the
    # header carries the same `can` (the other sections are gated per ViewSet, which a header cannot repeat)
    {"header": "Users", "can": "auth.view_user"},
    {"text": "Users", "route": "dashboard:users", "icon": _icon("users"), "can": "auth.view_user"},
]
