# Upstream tracker: what running django-crud-views inside a host it does not own needs

Living list of upstream changes that would make this theme cheaper, collected while building
`crud_views_adminlte`: django-crud-views (**C**) rendering inside the page shell of adminlte-django (**A**, import
`django_adminlte4`), a host that owns the layout, the sidebar menu and its own settings.

Rule: every override, theme CSS rule or workaround gets an entry here in the same commit, and a `# tracker <ID>` /
`{# tracker <ID> #}` comment at the workaround. IDs: `C<n>` for django-crud-views findings, `A<n>` for
adminlte-django findings.

Reference commits: django-crud-views `75a42851101be7db75c93e5b7de22764a3ff0949` (the nox `PIN`), adminlte-django
0.3.3 (PyPI `adminlte-django`; not the unrelated `django-adminlte4`).

Status: **anticipated** (found by reading the code, not yet hit), **confirmed** (the theme needed a workaround or the
problem was reproduced), **filed** (issue number), **done** (fixed upstream and adopted here).

Severity: **blocker**, **annoyance**, **cosmetic**.

## Close-out (2026-11-21, after the browser pass)

Every entry was re-checked against django-crud-views `75a42851` (the nox `PIN`; still `origin/main`) and
adminlte-django 0.3.3, in the full nox matrix (Python 3.12-3.15 x Django 6.0/6.1, package, docs: 18/18 sessions green;
the Python 3.15 cells are logged as unsupported, A5) and in the browser (alex, sam, kim; light, dark and auto; sidebar
expanded and mini; 375px). Nothing is filed or done upstream from this tracker yet; C8 is covered by django-crud-views #393 (CoreUI U10), open.

Pending pin bumps (the upstream PRs are still open; follow "Pin bump procedure" in `superpowers/plans/2026-11-21-adminlte-theme.md` for each when it merges):

- #391 (data-attribute prefix; Task 7): expected to change nothing here. adminlte-django is Bootstrap 5.3, so the
  `data-bs-*` attributes already work; re-run the suites and the browser smoke test only.
- #393 (Task 8 re-check): C8 flips. `test_sorted_column_aria_sort` is `xfail(strict=True)` and fails the suite
  once `aria-sort` and the prefixed sort icon arrive; drop the marker and set C8 to done. Its breadcrumb class keys
  (`breadcrumb:list` / `:item` / `:item-active`) do not solve C1: they style the wrapper, the theme needs it gone.
- #394 (`--cv-*` tokens; Task 10 step 1, deferred): re-check the manage and formset pages in dark mode. Both follow
  the dark mode today (checked in this pass), because AdminLTE defines the `--bs-*` variables upstream's CSS reads;
  no change expected.

| Entry | Final status | Handled by (theme side) |
|---|---|---|
| C1 | confirmed | `src/crud_views_adminlte/templates/crud_views/tags/breadcrumb.html` (items only; drift-tested) |
| C2 | confirmed | none; `crud_views_adminlte/page.html` leaves the `messages` block to the host |
| C3 | confirmed | check `crud_views_adminlte.E014` (`src/crud_views_adminlte/checks.py`): a `viewset` entry carries its `text` |
| C4 | confirmed | `icon_class` in `src/crud_views_adminlte/menu.py` |
| C5 | confirmed | URLconf import in `ViewSetHrefFilter` (`menu.py`) and `check_menu` (`checks.py`) |
| C6 | confirmed | none; `ViewSetGateFilter` asks `cv_has_access(user)`, anonymous users see no `viewset` entry |
| C7 | confirmed | none; pinned by `MenuPerRoleTests` in `example/config/test_pages.py` |
| C8 | covered by #393 (CoreUI U10), open | none; `xfail(strict=True)` in `tests/crud_views_adminlte/test_tables.py` |
| C9 | confirmed | `.table-container` rule in `src/crud_views_adminlte/static/crud_views_adminlte/crud_views_adminlte.css` |
| C10 | confirmed | none (upstream documents it as deliberate) |
| C11 | confirmed | none (upstream documents it as deliberate) |
| A1 | anticipated, not hit | nothing; the sidebar is fed through `ADMINLTE["menu"]`, no partial is overridden |
| A2 | confirmed | `ViewSetHrefFilter` / `ViewSetGateFilter` (`menu.py`), check `crud_views_adminlte.E013` |
| A3 | confirmed (demo) | `ADMINLTE` in `example/config/settings.py` and the test settings |
| A4 | confirmed | loaders / components setup in the test and demo settings, `docs/installation.md` |
| A5 | confirmed | `skip_unsupported` in `noxfile.py` (3.15 cells run and pass) |
| A6 | confirmed (not upstream) | `.cv-adminlte-badge-blue` in `crud_views_adminlte.css` |
| A7 | confirmed | `content_header` override in `src/crud_views_adminlte/templates/crud_views_adminlte/page.html` |
| A8 | confirmed | the theme's `breadcrumb` block plus `CRUD_VIEWS_BREADCRUMB_PREFIX` |
| A9 | confirmed | none; drift test in `tests/crud_views_adminlte/test_host_drift.py` |
| A10 | confirmed | `ViewSetGateFilter` drops the parents it emptied (`menu.py`) |
| A11 | confirmed | `SILENCED_SYSTEM_CHECKS = ["adminlte.W003"]` (settings, documented) |
| A12 | confirmed (demo) | `example/templates/registration/login.html` |
| A13 | confirmed (demo) | `example/static/acme/acme.css` (four more components and a working sidebar rule since the browser pass) |
| A14 | confirmed | none in the theme; the demo gates its Users header with `can` (`example/config/menu.py`) |
| A15 | confirmed | container classes in `src/crud_views_adminlte/buttons.py` |
| A16 | confirmed (demo) | ApexCharts in `example/dashboard/` |
| A17 | confirmed | `card:title` in `buttons.py` |
| A18 | confirmed | `.card-header.d-flex::after` in `crud_views_adminlte.css` |
| A19 | confirmed | crud_views' table template in the settings; recorded in `docs/theme_internals.md` |
| A20 | confirmed | none (cosmetic) |

Comparison with the sibling trackers (Tabler: `tabler-test/dev/crud_views_upstream_findings_roastery.md`; CoreUI:
`django-crud-views-core-ui/superpowers/notes/upstream-tracker.md`):

- New, from the host-owned shell (the host owns the sidebar, the breadcrumb container and the messages slot, so
  crud_views is asked things from outside its own pages): C1 (items without the wrapper), C2 (messages rendered by the
  host), C3 (a ViewSet's label without a request), C4 (an icon as a CSS class), C5 (ViewSet lookup before the URLconf
  is imported), C6 (a "may open" check covering every access mixin), C7 (Guardian lists in navigation). Tabler and
  CoreUI owned their shells and called crud_views' tags in place, so none of these came up there. Closest
  relatives: CoreUI U9 (breadcrumb class keys, #393) touches C1 but solves another problem; Tabler 23 (Guardian
  checks in the object navbar) are the in-page side of C6 / C7.
- New, not shell-related: C10 and C11 (bulk toolbar: actions shown without permission, no danger variant); bulk
  actions were not part of the earlier demos.
- Repeats: C8 = CoreUI U10 (`aria-sort`, filed together as #393). C9 is related to Tabler 5 / 25
  (workflow history and manage tables without `.table-responsive`, fixed upstream in #319 / #366); CoreUI worked
  around it by overriding the table template, which this theme avoids.
- Not repeated: CoreUI U1-U5 / U12 (`data-coreui-*`, `--cui-*` vs `--bs-*`) cannot occur on a Bootstrap 5.3 host.

Open items from the browser pass that are not entries here (third party or demo-only):

- The django-crud-views-extensions datetimepicker popup stays light in dark mode and marks today in its own blue: the
  same finding as Tabler 32 ("The datetimepicker keeps its own look"); belongs to the extensions tracker.
- The showcase's range slider keeps a `form-control` border: crispy-bootstrap5 appends `form-control` to every input,
  `form-range` (set in `example/showcase/views.py`) does not reset the border. Cosmetic, crispy-bootstrap5's behaviour.
- `crud_views_adminlte/page.html` keeps the context-action wrapper (`mt-2`, 0.5rem) on a page without context
  actions. Kept: every crud page in the demo has actions; not worth a conditional.

## Entry template

```markdown
## <ID>. <title>

- Status: anticipated | confirmed | filed (#n) | done · Severity: blocker | annoyance | cosmetic
- Symptom: what the adopter or user sees.
- Minimal repro: the smallest settings / template / call that shows it.
- Workaround: file reference in this repo (or "none yet").
- Proposed upstream fix: what the upstream project could change.
- Verified against: `<commit or release>`
```

## django-crud-views (C)

## C1. No items-only breadcrumb for a host-owned container

- Status: confirmed · Severity: annoyance
- Symptom: `{% cv_breadcrumb %}` always renders its own `<nav aria-label="breadcrumb"><ol class="breadcrumb">`. A host
  page that owns the `<ol>` and offers only a block inside it (adminlte-django's `breadcrumb` block in
  `adminlte/page.html`) would get a `<nav><ol>` nested in its `<ol>`: invalid markup and a doubled breadcrumb style.
  No template block, setting or class key renders the items alone (the class keys planned in #393 style the wrapper,
  they do not remove it).
- Minimal repro: `{% extends "adminlte/page.html" %}{% load crud_views %}{% block breadcrumb %}{% cv_breadcrumb %}{% endblock %}`
  on a view with `CrudViewBreadcrumbMixin`.
- Workaround: `src/crud_views_adminlte/templates/crud_views/tags/breadcrumb.html`, upstream's item loop without the
  wrapper (shadows upstream by app order); `test_breadcrumb_copy_tracks_upstream` in
  `tests/crud_views_adminlte/test_host_drift.py` fails when upstream edits the file.
- Proposed upstream fix: split the template into `crud_views/tags/breadcrumb_items.html` (the `<li>` loop) and the
  wrapper, with a `{% cv_breadcrumb_items %}` tag (as `cv_navbar_items` does for the navbar), or a block around the loop.
- Verified against: `75a42851101be7db75c93e5b7de22764a3ff0949`

## C2. No way to hand crud_views' message rendering to a host

- Status: confirmed · Severity: cosmetic
- Symptom: the theme leaves messages to the host's partial (one look for crud and non-crud pages, each message shown
  once). crud_views' own message customization then does not apply on crud_views pages: the `alert:*` class keys
  (`CRUD_VIEWS_BUTTON_CLASSES`), the `message-*` icons (`CRUD_VIEWS_ICONS`) and the `extra_tags` classes that
  `{% cv_messages %}` appends; the close button is the host's `data-bs-dismiss` rather than crud_views'
  `data-cv-alert-dismiss` adapter. With the stock values the output matches (same Bootstrap classes, the same `bi`
  icons per level), so only a project that customizes them sees the difference.
- Minimal repro: set `CRUD_VIEWS_ICONS = {"message-success": "bi:star"}`, create an object on a theme page: the
  host's alert shows `bi-check-circle-fill`. Compare `{% cv_messages %}` with `adminlte/partials/messages.html` for a
  message with `extra_tags` (see A9).
- Workaround: none; `crud_views_adminlte/page.html` does not override the `messages` block.
- Proposed upstream fix: a documented "host renders messages" mode, e.g. a public `alert_data`-style filter a host
  partial can call per message, so a host can use crud_views' classes and icons without crud_views owning the slot.
- Verified against: `75a42851101be7db75c93e5b7de22764a3ff0949`

## C3. No request-free label for a ViewSet

- Status: confirmed · Severity: annoyance
- Symptom: navigation that lives outside a crud_views page (a host sidebar) cannot ask a ViewSet for its display
  name. `ViewSet.get_meta(context)` is the only accessor for the resolved `verbose_name_plural` (the ViewSet override,
  else the model's or Resource's `_meta`, capitalized, translated), and it needs a `ViewContext` holding a `CrudView`
  instance, which only exists inside a request to one of its views.
- Minimal repro: build `{"viewset": "author"}` into a menu label without a view instance: `get_meta` cannot be
  called; re-deriving from `viewset.verbose_name_plural` / `viewset.model._meta` duplicates upstream's logic.
- Workaround: a `viewset` menu entry must carry its own `text`; `crud_views_adminlte.E014` in
  `src/crud_views_adminlte/checks.py` reports a missing one.
- Proposed upstream fix: a context-free `ViewSet.get_label(plural=True)` (or `verbose_name_plural_display` property)
  that `get_meta` also uses.
- Verified against: `75a42851101be7db75c93e5b7de22764a3ff0949`

## C4. No icon-to-CSS-class accessor

- Status: confirmed · Severity: cosmetic
- Symptom: a host that takes an icon as a CSS class (adminlte-django's `<i class="nav-icon {{ item.icon }}">`)
  cannot use a crud_views icon value (`ViewSet.icon_header = "bi:person-badge"`) directly: crud_views renders icons to
  HTML (`render_icon`) and exposes the bare class only for host-placement libraries (`resolve_icon_name_class`).
- Minimal repro: `render_icon("bi:person-badge")` gives `<i class="bi bi-person-badge" aria-hidden="true"></i>`;
  nothing public returns `"bi bi-person-badge"`.
- Workaround: `icon_class` in `src/crud_views_adminlte/menu.py` repeats `font_renderer`'s class formatting from the
  public `resolve_icon` and `get_libraries` (`font` renderer only; other renderers give no icon, the entry then
  needs its own `icon`). The result is computed once per process with the menu, so a later `CRUD_VIEWS_ICONS`
  change is only seen after an `ADMINLTE` change or a restart.
- Proposed upstream fix: `crud_views.lib.icons.resolve_icon_class(value) -> str | None` for `font` libraries and raw
  classes, used by `font_renderer` itself.
- Verified against: `75a42851101be7db75c93e5b7de22764a3ff0949`

## C5. ViewSet lookup depends on the URLconf having been imported

- Status: confirmed · Severity: annoyance
- Symptom: `ViewSet.get_viewset(name)` raises `ViewSetNotFoundError` until the module that defines the ViewSet has
  been imported, which normally happens only as a side effect of importing the URLconf. Code that looks ViewSets up
  by name before the first URL resolution of the process (a menu built in a fresh worker, a system check, a template
  rendered from a management command) finds none.
- Minimal repro: in a fresh process, `django.setup()` then `ViewSet.get_viewset("author")`: `ViewSetNotFoundError`;
  after `get_resolver().url_patterns` it succeeds. Found as an order-dependent failure under `pytest -n auto`.
- Workaround: `ViewSetHrefFilter.__init__` and `check_menu` import the URLconf first
  (`get_resolver(...).url_patterns`), `src/crud_views_adminlte/menu.py` and `checks.py`;
  `test_menu_built_before_first_url_resolution` in `tests/crud_views_adminlte/test_menu.py`.
- Proposed upstream fix: a documented loading hook (autodiscover of a `viewsets` module per app in
  `CrudViewsConfig.ready()`, or `get_viewset` importing the URLconf on a miss).
- Verified against: `75a42851101be7db75c93e5b7de22764a3ff0949`

## C6. No public "may this user open this view" check

- Status: confirmed · Severity: annoyance
- Symptom: navigation outside crud_views' own pages (a host sidebar) can only ask `view_class.cv_has_access(user)`,
  which answers the permission question only. On a view without `PermissionRequired`, the base
  `CrudView.cv_has_access` returns `True` for every user, so `LoginRequiredMixin` / `UserPassesTestMixin`
  (`test_func`) / custom `dispatch` gates are invisible: a menu link is shown that leads to a login redirect or 403.
- Minimal repro: `class V(LoginRequiredMixin, ListView): ...`; `V.cv_has_access(AnonymousUser())` → `True`.
- Exact call used: `view_class.cv_has_access(user)` (obj `None`) in `ViewSetGateFilter._allowed`,
  `src/crud_views_adminlte/menu.py`.
- Workaround: none for those gates; current behaviour: anonymous users see no `viewset` entry at all (which covers
  login-only views), any other non-permission gate is not reflected in the menu.
- Proposed upstream fix: a public classmethod, e.g. `cv_can_view(user, obj=None)`, that honours every access mixin
  of the view (login required, `test_func`, permission, ancestor policy) without a request, documented for
  navigation code.
- Verified against: `75a42851101be7db75c93e5b7de22764a3ff0949`

## C7. A Guardian ViewSet's menu entry is shown to every signed-in user

- Status: confirmed · Severity: annoyance
- Symptom: for a `GuardianViewSet` with `AncestorPolicy(accept_global_perms=True)` the list view's `cv_has_access(user)`
  (no object) is `True` for a user holding no permission at all, because object-level grants cannot be seen without
  an object. A sidebar entry gated through it (`ViewSetGateFilter`) therefore shows for everyone; the CoreUI demo's
  hand-written menu showed Customers only for `view_customer` / `add_customer`. Related: C6.
- Minimal repro: the demo's `customer` ViewSet; a user without permissions sees "Customers" in the sidebar
  (`MenuPerRoleTests.test_a_user_without_permissions_still_sees_customers_c7` in `example/config/test_pages.py`).
- Workaround: none; the entry opens an empty list for such a user.
- Proposed upstream fix: a "may this user see anything here" check for navigation (global permission or at least
  one object grant), next to the `cv_can_view` proposed in C6.
- Verified against: `75a42851101be7db75c93e5b7de22764a3ff0949`

## C8. The stock table header has no sorted-column state for assistive technology

- Status: covered by #393 (CoreUI U10), open · Severity: annoyance
- Symptom: in `crud_views/table/bootstrap5.html` (block `table.thead`) a sorted `<th>` shows the `table-sort-asc` /
  `table-sort-desc` icon but carries no `aria-sort`, so a screen reader does not learn which column is sorted. The
  icon condition compares `request.GET.sort` with the column name, so a table with a `prefix` (parameter
  `<prefix>sort`) never shows its icon either.
- Minimal repro: the testapp's `bulk_author` list (`BulkAuthorTable.Meta.prefix = "a-"`), `?a-sort=name`: no icon, no
  `aria-sort`; `author-list?sort=name`: icon, no `aria-sort`.
- Workaround: none, deliberately (no `table.thead` copy while #393 is pending, as the spec's fallback path says);
  `test_sorted_column_aria_sort` in `tests/crud_views_adminlte/test_tables.py` is `xfail(strict=True)` for both cases
  and starts passing, so failing the suite, when the pin bump brings #393.
- Proposed upstream fix: #393 (D-03): `aria-sort` and the icon from the bound column (`column.is_ordered`,
  `column.order_by_alias.is_descending`).
- Verified against: `75a42851101be7db75c93e5b7de22764a3ff0949` (waiting on #393)

## C9. The stock table wrapper is not responsive and has no class key

- Status: confirmed · Severity: annoyance
- Symptom: `crud_views/table/bootstrap5.html` wraps the table in a bare `<div class="table-container">`: no
  `.table-responsive`, no `CRUD_VIEWS_BUTTON_CLASSES` key. A list wider than the screen (the demo's orders list at
  375px, wider still with the bulk select column) pushed the whole page sideways (`scrollWidth` 525 at a 375px
  viewport). The buttons' absolutely positioned `.visually-hidden` labels also escape a plain scroller, since their
  containing block is the page's `main`.
- Minimal repro: any list with five or more columns at a 375px viewport.
- Workaround: `.table-container { position: relative; overflow-x: auto; }` in
  `src/crud_views_adminlte/static/crud_views_adminlte/crud_views_adminlte.css`;
  `test_table_container_scrolls_sideways` in `tests/crud_views_adminlte/test_tables.py`. The list action menus use
  Popper's `fixed` strategy (`actions_menu_toggle.html`), so the scroller does not clip them (checked in the browser).
- Proposed upstream fix: a `table:wrapper` class key (default `table-container table-responsive`), or
  `.table-responsive` on the stock wrapper as `view_manage.html` already does for its tables.
- Verified against: `75a42851101be7db75c93e5b7de22764a3ff0949`

## C10. The bulk toolbar shows every action to every viewer

- Status: confirmed · Severity: annoyance
- Symptom: the bulk toolbar renders every action in `cv_bulk_actions` whatever the viewer may do; permission is only
  checked when the form is submitted. In the demo, Kim (Roasters: `roast_order`, no `change_order`) sees
  "Cancel orders" on `/orders/`, and submitting it answers 403. Upstream documents this as deliberate
  (`docs/reference/bulk_actions.md:90`: "The toolbar renders every configured action without scanning the page for
  eligible objects or issuing bulk-permission queries; admission happens on submission.").
- Minimal repro: `example/sales/views/orders.py` `AllOrdersListView` (`cv_bulk_actions = ("bulk_roast",
  "bulk_cancel")`); log in as `kim`, open `/orders/`, select an order, press "Cancel orders": 403
  (`test_roasters_may_not_cancel` in `example/sales/tests/test_bulk.py`).
- Workaround: none.
- Proposed upstream fix: filter the toolbar's actions by each destination's model-level permission
  (`cv_has_access(user)` without object, one check per action, no per-row queries), or an opt-in
  `cv_bulk_actions_filter_by_permission`; a toolbar with no action left renders no checkboxes.
- Verified against: `75a42851101be7db75c93e5b7de22764a3ff0949`

## C11. No danger variant for destructive bulk actions

- Status: confirmed · Severity: cosmetic
- Symptom: every bulk toolbar button is a form submit styled by `form:submit`, so a destructive action ("Cancel
  orders", upstream's own bulk Delete) looks the same as a harmless one ("Mark roasted"); both are the primary button.
  Single-record actions have variants (`list:danger`, `context:danger`), bulk actions have none. Upstream documents
  this as deliberate (`docs/reference/bulk_actions.md:415`: "These are form submit buttons styled by `form:submit`";
  `:421`: "There is no per-action map and no variant.").
- Minimal repro: the demo's `/orders/` toolbar: "Mark roasted" and "Cancel orders" are both `btn btn-primary`.
- Workaround: none.
- Proposed upstream fix: honour the destination's `cv_action_variant` in the toolbar with per-variant class keys
  (`bulk:primary`, `bulk:danger`, ... as for `list:*` / `context:*`), or a per-action class key.
- Verified against: `75a42851101be7db75c93e5b7de22764a3ff0949`

## adminlte-django (A)

## A1. Navbar, sidebar and footer are includes, not blocks

- Status: anticipated · Severity: annoyance
- Symptom: a theme that extends the host page can fill the content blocks, but cannot add to or restyle the navbar,
  the sidebar or the footer through block overrides; they are `{% include %}`d partials.
- Minimal repro: look at `adminlte/master.html`; the navbar, sidebar and footer regions are includes of
  `adminlte/partials/*`, with no `{% block %}` around them.
- Workaround: none yet. The theme feeds the sidebar through `ADMINLTE["menu"]` and a menu filter; an
  `adminlte/partials/*` override would be a last resort and is logged here first (no override of
  `adminlte/master.html`).
- Proposed upstream fix: wrap each include in a named block (`navbar`, `sidebar`, `footer`) so a child template can
  extend or replace it.
- Verified against: adminlte-django 0.3.3

## A2. `HrefFilter` runs before any per-request filter

- Status: confirmed · Severity: annoyance
- Symptom: a menu entry whose URL is only known per request or per ViewSet is given `href="#"`, whatever order
  `ADMINLTE["filters"]` lists the filters in.
- Minimal repro: put a request-dependent filter before `HrefFilter` in `ADMINLTE["filters"]` and give it an item
  without `url`/`route`; `split_filters` in `menu/builder.py` runs the request-independent filters (`HrefFilter`,
  `SearchFilter`) once per process first, so the item is already `href="#"`.
- Workaround: two filters in `src/crud_views_adminlte/menu.py`: `ViewSetHrefFilter` (`per_request = False`, so it
  lands in the once-per-process half, listed before `HrefFilter`, which then skips the items that have `href`) and
  `ViewSetGateFilter` (per request: access). `VIEWSET_FILTERS` puts both in front of `DEFAULT_FILTERS`; check
  `crud_views_adminlte.E013` reports a missing or misordered pair. `test_host_runs_static_filters_first` in
  `tests/crud_views_adminlte/test_host_drift.py` fails when the host changes the split.
- Proposed upstream fix: honour the configured order, or document the split as the contract for custom
  request-independent filters (`per_request = False` already works as that hook; only the docs are missing).
- Verified against: adminlte-django 0.3.3

## A3. Defaults leak into every project

- Status: confirmed · Severity: cosmetic
- Symptom: a fresh project shows a Home link to `/`, docs links (`sidebar_docs_url`), AdminLTE.io footer text and a
  search button, none of which belong to the project.
- Minimal repro: render any page with `ADMINLTE` unset; see `DEFAULTS` in `django_adminlte4/conf.py`
  (`sidebar_docs_url`, `footer_left`, `footer_right`, `navbar_search`).
- Workaround: `ADMINLTE["sidebar_docs_url"] = ""` in `tests/crud_views_adminlte/settings.py`; footer, search and the
  Home entry are set in the demo and test settings as they are hit.
- Demo sub-items (`example/config/settings.py`, `ADMINLTE`; each default overridden there):
  - A3a `sidebar_docs_url` (docs link) set to `""`.
  - A3b `footer_left` (AdminLTE.io copyright, lazy) set to Acme text.
  - A3c `footer_right` ("Anything you want") set to Acme text.
  - A3d `navbar_search` (default `True`, the demo has no search) set to `False`.
  - A3e `title`, `logo`, `logo_alt_text`, `logo_img`, `logo_img_alt` (AdminLTE branding) set to Acme Roasters and the
    demo's favicon mark; `logo_img_class` keeps the default `opacity-75 shadow`.
- Proposed upstream fix: neutral defaults (no external links, no placeholder footer), with the demo content living in
  the demo project only.
- Verified against: adminlte-django 0.3.3

## A4. `APP_DIRS=False` and django-components are required

- Status: confirmed · Severity: annoyance
- Symptom: a project that adds the host and a third-party theme must give up `APP_DIRS=True` for an explicit
  `loaders` list that includes `django_components.template_loader.Loader`, plus `COMPONENTS`, the `component_tags`
  builtin and `ComponentsFileSystemFinder`; without them `adminlte.E002` fires. Every adopter of the theme inherits
  this setup.
- Minimal repro: `uv sync`, then `manage.py check` with `APP_DIRS=True` and no loaders list.
- Workaround: the full setup in `tests/crud_views_adminlte/settings.py` (loaders order filesystem, app_directories,
  components; no `cached.Loader` in tests), documented for adopters in `docs/installation.md` ("Settings").
- Proposed upstream fix: ship the components as plain templates, or register the components loader itself so
  `APP_DIRS=True` keeps working.
- Verified against: adminlte-django 0.3.3, installation.md and `django_adminlte4/checks.py`

## A5. Python 3.15 is not declared

- Status: confirmed · Severity: cosmetic
- Symptom: the package metadata lists Python 3.12-3.14 only; the project's local interpreter is 3.15.
- Minimal repro: `METADATA` of the installed `adminlte_django-0.3.3.dist-info` has `Programming Language :: Python
  :: 3.12` to `3.14` classifiers and `Requires-Python: >=3.12`; it installs and passes the system check on 3.15.1.
- Workaround: none needed to install. The nox matrix runs Python 3.15 cells and logs them as unsupported
  (`skip_unsupported` in `noxfile.py`) instead of dropping them; this project declares 3.12-3.15.
- Proposed upstream fix: add the 3.15 classifier and a CI cell once it is supported.
- Verified against: adminlte-django 0.3.3

## A6. No blue badge utility for the manage legend

- Status: confirmed · Severity: cosmetic
- Symptom: crud_views' manage page legend says "Blue: required permission"; Bootstrap 5.3 / AdminLTE 4 define `--bs-blue`
  but ship no blue badge class, and `bg-primary` would follow the project's primary (sienna in the demo).
- Minimal repro: render a manage page with `manage:badge-permission` set to `badge bg-primary`.
- Workaround: `.cv-adminlte-badge-blue` in `src/crud_views_adminlte/static/crud_views_adminlte/crud_views_adminlte.css`.
  A Bootstrap palette gap, not an upstream (crud_views / adminlte-django) defect; nothing to file.
- Proposed upstream fix: none; kept as the theme's own helper.
- Verified against: Bootstrap 5.3 via adminlte-django 0.3.3

## A7. `page_title` is a fixed `<h3>` with no slot for icon, subtitle or actions

- Status: confirmed · Severity: annoyance
- Symptom: `adminlte/page.html` renders `<h3 class="mb-0">{% block page_title %}{% endblock %}</h3>` next to the
  breadcrumb. A crud_views page needs a heading at its own level (`CRUD_VIEWS_HEADER_LEVEL`, h2 by default), the
  header icon, a subtitle (`cv_paragraph`), the context action buttons and, with ViewSet Navigation, an owner header
  with tabs above the title row; none fits in the `<h3>`.
- Minimal repro: `{% block page_title %}<h2>…</h2><p>…</p>{% endblock %}` gives a heading inside a heading.
- Workaround: `src/crud_views_adminlte/templates/crud_views_adminlte/page.html` overrides `content_header` (a block of
  `adminlte/master.html`, so still extension) with the host's `app-content-header` / `container-fluid` / `row` frame
  and re-declares `page_title` and `breadcrumb` inside it; `test_host_content_header_markup` in
  `tests/crud_views_adminlte/test_host_drift.py` fails when the host's frame changes.
- Proposed upstream fix: blocks around the title element and beside it in `adminlte/page.html` (`page_heading`,
  `page_subtitle`, `page_actions`, `content_header_top`), so a child keeps the host's frame and fills the slots.
- Verified against: adminlte-django 0.3.3

## A8. The breadcrumb's Home crumb is hard-coded

- Status: confirmed · Severity: cosmetic
- Symptom: `adminlte_breadcrumb` always starts with `Home` linking to `/`, with no setting for its label or URL, and
  the crumb list cannot be extended by a page. A crud_views page either keeps the host's auto-derived trail (path
  segments, not the ViewSet hierarchy) or replaces it and loses that Home, so an adopter states Home a second time in
  `CRUD_VIEWS_BREADCRUMB_PREFIX`, and the two can disagree (`/` vs. the dashboard route).
- Minimal repro: `adminlte_breadcrumb` in `django_adminlte4/templatetags/adminlte.py`; `DEFAULTS` in
  `django_adminlte4/conf.py` has no breadcrumb key.
- Workaround: the theme's `breadcrumb` block renders `{% cv_breadcrumb %}` only, so Home appears once (from
  `CRUD_VIEWS_BREADCRUMB_PREFIX`, set in `tests/crud_views_adminlte/settings.py`); `test_breadcrumb_no_duplicate_home`
  in `tests/crud_views_adminlte/test_theme.py`.
- Proposed upstream fix: an `ADMINLTE["breadcrumb_home"]` setting (label, route) used by `adminlte_breadcrumb`, so the
  theme can read the same Home for crud_views' prefix.
- Verified against: adminlte-django 0.3.3

## A9. The messages partial drops `extra_tags`

- Status: confirmed · Severity: cosmetic
- Symptom: `adminlte/partials/messages.html` builds each alert's classes from the level only; a message's
  `extra_tags` (Django's per-message classes, which `{% cv_messages %}` appends) are lost.
- Minimal repro: render the partial with `Message(WARNING, "Careful", extra_tags="cv-sticky")`: no `cv-sticky`.
- Workaround: none (the theme leaves the `messages` block to the host); `test_host_messages_partial_drops_extra_tags`
  in `tests/crud_views_adminlte/test_host_drift.py` fails once the host keeps them.
- Proposed upstream fix: append `{{ message.extra_tags }}` to the alert's class attribute.
- Verified against: adminlte-django 0.3.3

## A10. `GateFilter` never drops a parent it emptied

- Status: confirmed · Severity: cosmetic
- Symptom: a submenu parent whose children are all hidden for the user stays in the sidebar as a dead link (the
  partial renders an empty `submenu` as a plain `<a href="#">`). `GateFilter` drops such a parent only when it has
  none of `url`/`route`/`href`, but in the per-request half `HrefFilter` (static half, run first, A2) has already
  given every parent `href="#"`, so the branch never fires through the context processor.
- Minimal repro: `{"text": "Library", "submenu": [{"text": "Secret", "url": "/secret/", "can": "app.view_secret"}]}`
  for a user without that permission: "Library" is rendered, linking to `#`.
- Workaround: `ViewSetGateFilter` in `src/crud_views_adminlte/menu.py` drops a parent it emptied unless the parent
  links somewhere itself (`url`, `route` or an `href` other than `#`). Parents emptied by the host's own `can` checks
  keep the host behaviour. `test_host_gate_keeps_emptied_parent_after_href` in
  `tests/crud_views_adminlte/test_host_drift.py` fails once the host drops them.
- Proposed upstream fix: in `GateFilter`, treat `href == "#"` like a missing link (or have `HrefFilter` leave
  submenu parents without `href`).
- Verified against: adminlte-django 0.3.3

## A11. The menu check rejects keys of custom filters

- Status: confirmed · Severity: annoyance
- Symptom: `adminlte.W003` warns about every menu-item key outside its fixed `MENU_ITEM_KEYS`, so a project using a
  custom filter's keys (the theme's `"viewset"` / `"view"`) gets a warning per entry on every `check` / `runserver`,
  and `manage.py check --fail-level WARNING` fails.
- Minimal repro: `ADMINLTE = {"menu": [{"viewset": "author", "text": "Authors"}]}`, `manage.py check`.
- Workaround: `SILENCED_SYSTEM_CHECKS = ["adminlte.W003"]` in `tests/crud_views_adminlte/settings.py` (and the demo;
  documented for adopters in `docs/installation.md`, "Silenced check"); the theme's `crud_views_adminlte.E010`-`E015` check the `viewset` entries, but the
  host's typo detection for its own keys is lost. `test_host_menu_check_rejects_custom_keys` in
  `tests/crud_views_adminlte/test_host_drift.py` fails once the host accepts custom keys.
- Proposed upstream fix: let a filter declare the keys it consumes (e.g. a `menu_keys` class attribute collected from
  `ADMINLTE["filters"]`), or an `ADMINLTE["menu_item_keys"]` setting extending `MENU_ITEM_KEYS`.
- Verified against: adminlte-django 0.3.3

## A12. The login page has no block after the form

- Status: confirmed · Severity: cosmetic
- Symptom: `registration/login.html` extends `adminlte/auth/login.html`, whose whole card body is the one block
  `auth_body`; a project adding content to the login card (the demo's account picker) must override `auth_body` and
  call `{{ block.super }}` before its own markup.
- Minimal repro: extend `registration/login.html`; there is no block for content below the form (`auth_footer`).
- Workaround: `example/templates/registration/login.html` overrides `auth_body` and appends below `block.super`.
- Proposed upstream fix: an `auth_after_form` (or `auth_footer`) block inside the card body.
- Verified against: adminlte-django 0.3.3

## A13. The compiled stylesheet ignores `--bs-primary` in buttons and focus states

- Status: confirmed · Severity: annoyance
- Symptom: re-colouring the primary through `--bs-primary*` / `--bs-link-*` recolours links and utilities, but
  `.btn-primary`, `.btn-outline-primary`, `.form-check-input:checked` (and `:indeterminate`, seen on the bulk
  toolbar's "Select this page" in Task 8), the form focus border and the sidebar's active
  link keep the compiled blue; a brand colour needs one override rule per component, in both colour modes.
  AdminLTE's `data-lte-primary` was not used by the host's pages and is not wired by the demo.
- Minimal repro: set `:root { --bs-primary: #a0522d }`; render a primary button.
- Workaround: the rules in `example/static/acme/acme.css` (brand block, plus the range slider's thumb). Seen in the
  browser (Task 6, light and dark): buttons, focus states, checked boxes, the sidebar's active link and the range
  thumb take the brand only through these rules; `BrandTests` in `example/dashboard/tests.py` pins them.
- 2026-11-21, browser pass (Task 10): four more components were still blue, found by scanning every page's computed
  colours for `rgb(13, 110, 253)` in light and dark mode: the active dropdown item (the shell's colour-mode switch,
  row action menus), the active pagination page, the active vertical tab (`nav-pills`, object-detail tabs pack) and
  the accordion pack (focus ring, the open group's chevron; in dark mode Bootstrap draws both chevrons in `#6ea8fe`).
  Each is restated in `acme.css` through its component variable. The earlier sidebar rule
  (`.app-sidebar .nav-link.active`) never applied: it loses to the host's
  `.sidebar-wrapper .sidebar-menu>.nav-item>.nav-link.active`, so the active link stayed AdminLTE's translucent grey.
  It now sets the host's own `--lte-sidebar-menu-active-bg` / `-color` on `.app-sidebar` (and on the dark sidebar
  the shell always renders). `BrandTests` pins the new selectors and the variable.
- Proposed upstream fix: build the host stylesheet with CSS-variable-driven primary component colours, or document a
  Sass override path for `--bs-primary`.
- Verified against: adminlte-django 0.3.3

## A14. A menu header stays when every entry under it is hidden

- Status: confirmed · Severity: cosmetic
- Symptom: `{"header": "Catalog"}` followed by entries the user may not open (gated by `can`, or by the theme's
  `viewset` gate) still renders the "Catalog" header, with nothing under it; a user with few permissions sees a column
  of empty section titles.
- Minimal repro: `ADMINLTE["menu"] = [{"header": "Users"}, {"text": "Users", "url": "/u/", "can": "auth.view_user"}]`
  for a user without `auth.view_user`: the "Users" header is rendered.
- Workaround: none in the theme (the host's `GateFilter` runs after the theme's filters, so no theme filter can see
  the final list); `NavigationTests.test_sections_follow_the_permissions` in `example/dashboard/tests.py` asserts the
  links, not the headers. The demo (Task 10) gates the one header whose section is a single `can` entry: `{"header":
  "Users", "can": "auth.view_user"}` in `example/config/menu.py` (the host's `GateFilter` honours `can` on any item);
  `NavigationTests.test_the_users_header_follows_the_users_permission`. Sections of `viewset` entries cannot repeat
  their gate on the header; with the seeded roles they are never empty (sam and kim see every section except Users).
- Proposed upstream fix: after gating, drop a `header` item followed by no visible item before the next header.
- Verified against: adminlte-django 0.3.3

## A15. Every `<fieldset>` is boxed

- Status: confirmed · Severity: annoyance
- Symptom: AdminLTE styles the bare `fieldset` element (`padding: 1rem; margin-bottom: 1rem; border: 1px solid`)
  and its `legend`. Markup that uses a fieldset only to group controls semantically (crud_views' context and row
  action bars, the formset row controls and the card ordering group, all `<fieldset aria-label=…>`) is drawn as a
  bordered box, the page header's action bar sits in a padded frame and the formset's +/× buttons in nested frames.
- Minimal repro: `<fieldset class="d-flex gap-2"><a class="btn btn-primary">x</a></fieldset>` in any host page.
- Workaround: `context:container`, `list:container`, `formset:container` and `card-order:container` add
  `border-0 p-0 m-0` in `src/crud_views_adminlte/buttons.py`; form sections (crispy fieldsets, the conditional
  wholesale group, the formset) keep AdminLTE's box and legend style on purpose.
  `test_fieldset_containers_undo_adminltes_boxed_fieldset` in `tests/crud_views_adminlte/test_registration.py`.
- Proposed upstream fix: scope the fieldset style to forms (e.g. `.app-content form fieldset:not([class])`) or to an
  opt-in class.
- Verified against: adminlte-django 0.3.3

## A16. The chart component needs the Vite pipeline

- Status: confirmed · Severity: annoyance
- Symptom: `adminlte_chart` renders a `data-chartjs` container, but the code that draws it (`adminlte-plugins.js`,
  `adminlte-charts.js`) exists only as Vite stubs; with `ADMINLTE["assets_mode"] = "static"` (the pre-built bundle
  this theme and its demo use) nothing loads Chart.js, and the chart stays an empty box.
- Minimal repro: `{% component "adminlte_chart" type="bar" series=… categories=… %}{% endcomponent %}` on a page
  with `assets_mode` "static"; `adminlte/dist/js` has no Chart.js and no initialiser.
- Workaround: the demo's revenue chart stays on ApexCharts (`example/dashboard/static/dashboard/revenue-chart.js`,
  pinned with SRI in `example/dashboard/templates/dashboard/index.html`); `DashboardWidgetTests` in
  `example/dashboard/tests.py`. The theming page says so.
- Proposed upstream fix: ship the chart initialiser (and a pinned Chart.js, or a documented CDN hook) in the
  pre-built bundle, or document that the Tool components need Vite.
- Verified against: adminlte-django 0.3.3

## A17. `.card-title` floats left with no margin

- Status: confirmed · Severity: annoyance
- Symptom: AdminLTE's global `.card-title { float: left; margin: 0; font-size: 1.1rem }` is meant for a card header
  next to `.card-tools`. A card title in a card body (Bootstrap's own use, and crud_views' card list via the
  `card:title` key) floats, and the next line of text wraps up beside it.
- Minimal repro: `<div class="card-body"><h5 class="card-title">T</h5><p>Text</p></div>`: "Text" sits right of "T".
- Workaround: `card:title` is `card-title float-none mb-1` in `src/crud_views_adminlte/buttons.py`; the demo's own
  headings use `fs-6 fw-semibold` instead of `card-title` (`example/sales/forms.py`, login page).
  `test_card_title_does_not_float` in `tests/crud_views_adminlte/test_registration.py`.
- Proposed upstream fix: scope the rule to `.card-header > .card-title`.
- Verified against: adminlte-django 0.3.3

## A18. The card header's clearfix breaks flex headers

- Status: confirmed · Severity: cosmetic
- Symptom: `.card-header::after` is a block clearfix (for the floated title and tools). In a header that is a flex
  container (`card-header d-flex justify-content-between`, upstream's manage cards) the pseudo-element becomes a third
  flex item, so the help button lands in the middle of the header instead of at its end.
- Minimal repro: `<div class="card-header d-flex justify-content-between"><h2>T</h2><a class="btn">?</a></div>`.
- Workaround: `.card-header.d-flex::after { display: none; }` in
  `src/crud_views_adminlte/static/crud_views_adminlte/crud_views_adminlte.css`;
  `test_flex_card_header_drops_adminltes_clearfix` in `tests/crud_views_adminlte/test_registration.py`.
- Proposed upstream fix: use `display: flow-root` on `.card-header` instead of the `::after` clearfix, or skip the
  clearfix for `.d-flex` headers.
- Verified against: adminlte-django 0.3.3

## A19. The tables2 card template is tied to tables2's own base template

- Status: confirmed · Severity: annoyance
- Symptom: the host's `django_tables2/adminlte.html` (card, `card-body p-0 table-responsive`, pagination in the card
  footer) `{% extends "django_tables2/bootstrap5.html" %}`, so its wrapper cannot be put around another table
  template. With `DJANGO_TABLES2_TEMPLATE` set to it, crud_views list pages lose what crud_views' table template adds:
  the sort-direction icon (`table-sort-asc` / `-desc`), the pagination icons with hidden labels
  (`pagination:hidden-label`), the active page as `<span aria-current="page">` and the disabled previous/next items.
  The bulk select column and toolbar still work under it, and there is no card in a card (crud_views pages put
  nothing around `{% render_table %}`).
- Minimal repro: `DJANGO_TABLES2_TEMPLATE = "django_tables2/adminlte.html"`; open the demo's `/orders/?sort=customer`:
  no sort icon (seen in the browser, Task 8).
- Workaround: the theme uses crud_views' `crud_views/table/bootstrap5.html` (test and demo settings), without the
  host's card; the choice is recorded in `docs/theme_internals.md` ("Tables"). `test_table_without_host_card` and
  `test_sorted_column_icon` in `tests/crud_views_adminlte/test_tables.py` pin it.
- Proposed upstream fix: ship the card frame as a partial (or a template taking the base to extend from a variable,
  e.g. `{% extends adminlte_tables2_base|default:"django_tables2/bootstrap5.html" %}`), so a project can wrap a
  different table template in the AdminLTE card.
- Verified against: adminlte-django 0.3.3

## A20. Wrapped breadcrumbs get the header's line height per line

- Status: confirmed · Severity: cosmetic
- Symptom: `.app-main .app-content-header .breadcrumb { line-height: 2.5rem }` aligns a one-line breadcrumb with the
  page title. A breadcrumb that wraps (crud_views' nested trails at 375px: Home / Customers / Quiet Corner Roasters /
  Orders / Order #1040) takes 2.5rem per line, so the crumbs stand far apart.
- Minimal repro: the demo's `/customer/28/order/112/detail/` at a 375px viewport: three breadcrumb lines, 40px each.
- Workaround: none (found in the Task 10 browser pass; a theme rule would have to change the one-line alignment too).
- Proposed upstream fix: centre the breadcrumb with `min-height: 2.5rem; align-items: center` instead of the line
  height.
- Verified against: adminlte-django 0.3.3
