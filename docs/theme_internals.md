# Theme internals

How the theme maps django-crud-views onto adminlte-django. Every override, CSS rule and workaround has an entry in the
upstream tracker (`superpowers/notes/upstream-tracker.md`, IDs `C<n>` for django-crud-views, `A<n>` for
adminlte-django) and a `tracker <ID>` comment at the place. The theme overrides no `adminlte/master.html` and no
`adminlte/partials/*`, and monkeypatches nothing.

## Page and blocks

`crud_views_adminlte/page.html` (`CRUD_VIEWS_EXTENDS`) extends the host's `adminlte/page.html` and maps the crud_views
blocks onto it:

| Host block | Filled with |
|---|---|
| `title` | the view's header, plus the ViewSet Navigation owner, through the host's title prefix and postfix |
| `extra_css` / `extra_js` | `{% cv_css %}` / `{% cv_js %}` |
| `content_header` | replaced with the host's own frame (tracker A7), see below |
| `content` | `cv_filter`, `cv_content`, `{% cv_config %}` |
| `messages` | not overridden: the host renders messages, once, for crud and non-crud pages alike (tracker C2, A9) |

The host's `page_title` is a fixed `<h3>` next to the breadcrumb, with no slot for the header icon, a subtitle, action
buttons or the ViewSet Navigation owner header. The theme therefore overrides `content_header` (a `master.html` block,
so still extension) with the host's `app-content-header` / `container-fluid` / `row` frame and re-declares
`page_title` and `breadcrumb` inside it; the context actions (`cv_context`) sit under the breadcrumb (tracker A7,
`test_host_content_header_markup` fails when the host's frame changes). The page title follows
`CRUD_VIEWS_HEADER_LEVEL` at the host's `h3` size; with a ViewSet Navigation bar, a heading that repeats the active tab is
left out.

## Overrides and workarounds

| Where | What | Tracker |
|---|---|---|
| `templates/crud_views/tags/breadcrumb.html` | upstream's breadcrumb items without the `<nav><ol>` wrapper, shadowing upstream globally; `test_breadcrumb_copy_tracks_upstream` keeps the loop equal | C1 |
| `templates/crud_views_adminlte/page.html` | no Home crumb of the host's: `CRUD_VIEWS_BREADCRUMB_PREFIX` provides it | A8 |
| `menu.py` `ViewSetHrefFilter`, `ViewSetGateFilter` | two filters, because the host runs per-process filters first | A2, A10 |
| `menu.py` `entry_view_class`, `ViewSetHrefFilter.__init__` | imports the URLconf before looking a ViewSet up | C5 |
| `menu.py` `icon_class` | the CSS classes of a crud_views icon, from public hooks | C4 |
| `menu.py` `ViewSetGateFilter._allowed` | `cv_has_access(user)`: permission only | C6, C7 |
| `checks.py` E010-E015 | menu entry checks; `text` required | C3 |
| `settings`: `SILENCED_SYSTEM_CHECKS` | silences the host's `adminlte.W003` | A11 |
| `buttons.py` `*:container` keys | `border-0 p-0 m-0` on the `<fieldset>` button rows AdminLTE would box | A15 |
| `buttons.py` `card:title` | `float-none mb-1` | A17 |
| `crud_views_adminlte.css` `.cv-adminlte-badge-blue` | the manage legend's blue badge | A6 |
| `crud_views_adminlte.css` `.card-header.d-flex::after` | AdminLTE's clearfix breaks flex headers | A18 |
| `crud_views_adminlte.css` `.table-container` | scrolls sideways on a narrow screen | C9 |
| `settings`: `DJANGO_TABLES2_TEMPLATE` | crud_views' table template, see below | A19 |

Settings the host leaves with defaults that leak into every project (docs link, footer text, search button) are listed
under A3; the demo overrides each. Open gap with no workaround: a menu header that stays when its entries are all hidden
(A14). Fixed upstream and adopted: the sorted column's `aria-sort` (C8, #393), bulk actions offered only to viewers who
may enter them (C10, #399) and a danger style for destructive bulk actions (C11, #400).

Brand colours need one rule per component, because the host's compiled stylesheet ignores `--bs-primary` in buttons and
focus states (A13); the demo does this in `example/static/acme/acme.css`, not the theme.

## Guards against upstream drift

The theme's copies and assumptions have tests that fail when upstream changes: `test_breadcrumb_copy_tracks_upstream`
(C1), `test_host_content_header_markup` (A7), `test_host_runs_static_filters_first` (A2),
`test_host_gate_keeps_emptied_parent_after_href` (A10), `test_host_menu_check_rejects_custom_keys` (A11),
`test_host_messages_partial_drops_extra_tags` (A9), and `test_button_keys_cover_upstream`, which fails when upstream
adds a button-class key the theme does not set yet. See `tests/crud_views_adminlte/`.

## Tables

**Choice:** `DJANGO_TABLES2_TEMPLATE = "crud_views/table/bootstrap5.html"`, crud_views' own table template, not the
host's `django_tables2/adminlte.html`.

**Why:** adminlte-django's template wraps a table in a card (`card-body p-0 table-responsive`, pagination in the card
footer), but it extends django-tables2's `django_tables2/bootstrap5.html`, not crud_views' template, and cannot be
pointed at another base. Under it crud_views list pages lose the sort-direction icon of the sorted column, the
pagination icons and their hidden labels, the active page as `aria-current="page"` and the disabled previous/next
items (tracker A19, checked in the browser on the demo's orders list). The bulk select column, the toolbar, the empty
state and the absence of a card in a card were fine under either template; the lost sort and pagination markup
decided it.

**Consequences:**

- Adopters must set `DJANGO_TABLES2_TEMPLATE = "crud_views/table/bootstrap5.html"` in their settings (tracker A19); it
  is part of the [installation](installation.md#settings) block.

- List tables sit on the page background, as in crud_views' Bootstrap theme, not in an AdminLTE card.
- crud_views' wrapper `div.table-container` has no class key and is not `.table-responsive`; the theme's stylesheet
  lets it scroll sideways (`position: relative; overflow-x: auto`, tracker C9), so a wide list does not push the page
  sideways on a phone. Row action menus open with Popper's `fixed` strategy and are not clipped by the scroller.
- The sorted column carries `aria-sort`, and a table with a `prefix` shows its sort icon: both come from upstream's
  header since django-crud-views #393 (tracker C8). The theme keeps no copy of the `table.thead` block;
  `test_sorted_column_aria_sort` covers both cases.
- Revisit after #393: if a card frame is wanted, a theme template extending `crud_views/table/bootstrap5.html` and
  overriding only `table-wrapper` with the host's card markup would combine both (logged with A19, not done).

## Bulk selection

Bulk selection (django-crud-views #392) needs nothing beyond the class registry:

- The seven layout `bulk:*` keys (`buttons.py`) are plain Bootstrap 5.3 classes, checked in the browser on table and
  cards, light and dark, at 375px; the `bulk` label mode stays upstream's default (`both`).
- The toolbar buttons take their class from the destination's `cv_action_variant` (django-crud-views #400, tracker
  C11): `bulk:primary` to `bulk:danger`, plus an `:icon` key each, set to the `context:*` values because the toolbar is
  a page-level button row like the context toolbar. The demo marks "Cancel orders" as danger (`btn
  btn-outline-danger`); a destination without a variant renders secondary.
- The toolbar offers only the actions the viewer may enter (django-crud-views #399, tracker C10); with none left, the
  page has no toolbar and no checkboxes. The stock templates do this.
- The toolbar renders above the table wrapper or the card grid; `crud_views/js/bulk.js` comes with `{% cv_js %}`.
- The review page (`view_bulk_form.html`) renders in the theme's page like any custom form view; its blocked records
  are a `{% cv_alert "warning" %}`.
- Result and warning messages go through the host's messages partial, once, like every other message (tracker C2).
