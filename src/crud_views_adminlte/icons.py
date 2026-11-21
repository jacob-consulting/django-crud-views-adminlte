"""Bootstrap Icons for every semantic icon name of django-crud-views.

AdminLTE 4 bundles Bootstrap Icons as a font (``bi bi-<name>``), which is exactly what django-crud-views' built-in
``bi`` icon library renders, so the theme registers no library or renderer of its own: only this table. A project
overrides single keys with ``CRUD_VIEWS_ICONS``.
"""

ADMINLTE_ICONS: dict[str, str] = {
    name: f"bi:{icon}"
    for name, icon in {
        "list": "list-ul",
        "card": "card-list",
        "detail": "eye",
        "create": "plus-square",
        "update": "pencil-square",
        "delete": "trash",
        "order-up": "arrow-up-circle",
        "order-down": "arrow-down-circle",
        "manage": "gear",
        "workflow": "diagram-3",
        "actions-menu": "three-dots-vertical",
        "filter": "funnel",
        "filter-close": "x-circle",
        "language": "translate",
        "sort-asc": "sort-up",
        "sort-desc": "sort-down",
        "table-sort-asc": "chevron-double-up",
        "table-sort-desc": "chevron-double-down",
        "page-previous": "chevron-left",
        "page-next": "chevron-right",
        "formset-up": "caret-up-fill",
        "formset-down": "caret-down-fill",
        "formset-add": "plus-lg",
        "formset-delete": "x-square-fill",
        "field-marker": "chevron-double-right",
        "boolean-true": "check-circle-fill",
        "boolean-false": "x-circle-fill",
        "property-detail": "info-circle",
        "text-icon": "journal-text",
        "message-success": "check-circle-fill",
        "message-info": "info-circle-fill",
        "message-warning": "exclamation-triangle-fill",
        "message-error": "exclamation-octagon-fill",
        "message-debug": "bug-fill",
        "save": "floppy",
        "cancel": "x-lg",
        "filter-reset": "arrow-counterclockwise",
    }.items()
}
