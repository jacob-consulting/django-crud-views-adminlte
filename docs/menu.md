# Menu

adminlte-django builds the sidebar from `ADMINLTE["menu"]`. The theme adds entries that point at a ViewSet:

```python
ADMINLTE = {
    "menu": [
        {"text": "Dashboard", "route": "dashboard:index", "icon": "bi bi-speedometer2"},
        {"header": "Catalog"},
        {"viewset": "product", "text": "Products"},
        {"viewset": "product", "view": "create", "text": "New product", "icon": "bi bi-plus-lg"},
    ],
    "filters": [*VIEWSET_FILTERS, *DEFAULT_FILTERS],
}
```

| Key | Meaning |
|---|---|
| `viewset` | The `name=` of the ViewSet. Required. |
| `text` | The label. Required (tracker C3: crud_views has no request-free label for a ViewSet). |
| `view` | The view key, default `"list"`. A ViewSet with only a card view works with `"list"`. |
| `icon` | CSS classes of the icon. Default: the ViewSet's `icon_header`, resolved to its classes (tracker C4); a library whose icons are not font classes needs its own `icon`. |

Entries work inside `submenu` too. The other keys (`route`, `url`, `can`, `header`) stay the host's.

## Who sees an entry

The link is shown to a signed-in user for whom the view class's `cv_has_access(user)` is true: the model-level
permission check crud_views itself uses for links without an object.

- **Anonymous users see no ViewSet entry**, including on the sign-in, 403 and 404 pages that render the menu.
- `cv_has_access` answers the permission question only. A view guarded by `LoginRequiredMixin`, a `test_func` or a custom
  `dispatch` is not seen as guarded: the link shows, and the click ends in a redirect or a 403 (tracker C6).
- For Guardian ViewSets, object-level grants cannot be seen without an object, so a list shows to any user who may
  pass the global check, and opens an empty list for a user without grants (tracker C7). The demo's Customers entry is
  an example.
- A submenu parent left with no visible child is dropped, unless it links somewhere itself (tracker A10). A menu
  `header` stays when everything under it is hidden (tracker A14).

## Ordering rule

The host runs every filter that does not depend on the request once per process, before any per-request filter,
whatever the order of `ADMINLTE["filters"]` (tracker A2). The theme therefore has two filters:

- `ViewSetHrefFilter` (once per process): resolves the URL and the icon, and must come before the host's `HrefFilter`,
  which would otherwise set `href="#"`.
- `ViewSetGateFilter` (per request): checks access.

`VIEWSET_FILTERS` lists both; put it in front of `DEFAULT_FILTERS`.

## System checks

```shell
python manage.py check
```

| Id | Meaning |
|---|---|
| `crud_views_adminlte.E010` | The entry names a ViewSet that is not registered (ViewSets register when the URLconf is imported, tracker C5; the check imports it). |
| `crud_views_adminlte.E011` | The ViewSet is a child: its URLs need the parent's primary key and cannot be reversed globally. Link the parent instead. |
| `crud_views_adminlte.E012` | The ViewSet has no view with that key. |
| `crud_views_adminlte.E013` | `ADMINLTE["filters"]` lacks `ViewSetHrefFilter` before `HrefFilter`, or `ViewSetGateFilter`. |
| `crud_views_adminlte.E014` | The entry has no `text`. |
| `crud_views_adminlte.E015` | The view is an object view (detail, update, delete): its URL needs a primary key. Use a view without an object, such as `list` or `create`. |

Misconfiguration is an error at startup rather than a `NoReverseMatch` on every page. At runtime an unusable entry is left
out of the menu.
