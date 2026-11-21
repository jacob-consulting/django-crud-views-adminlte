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

- Status: anticipated · Severity: cosmetic
- Symptom: a fresh project shows a Home link to `/`, docs links (`sidebar_docs_url`), AdminLTE.io footer text and a
  search button, none of which belong to the project.
- Minimal repro: render any page with `ADMINLTE` unset; see `DEFAULTS` in `django_adminlte4/conf.py`
  (`sidebar_docs_url`, `footer_left`, `footer_right`, `navbar_search`).
- Workaround: `ADMINLTE["sidebar_docs_url"] = ""` in `tests/crud_views_adminlte/settings.py`; footer, search and the
  Home entry are set in the demo and test settings as they are hit.
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
  components; no `cached.Loader` in tests), documented for adopters later.
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
- Workaround: `SILENCED_SYSTEM_CHECKS = ["adminlte.W003"]` in `tests/crud_views_adminlte/settings.py` (and the demo,
  to be documented for adopters); the theme's `crud_views_adminlte.E010`-`E015` check the `viewset` entries, but the
  host's typo detection for its own keys is lost. `test_host_menu_check_rejects_custom_keys` in
  `tests/crud_views_adminlte/test_host_drift.py` fails once the host accepts custom keys.
- Proposed upstream fix: let a filter declare the keys it consumes (e.g. a `menu_keys` class attribute collected from
  `ADMINLTE["filters"]`), or an `ADMINLTE["menu_item_keys"]` setting extending `MENU_ITEM_KEYS`.
- Verified against: adminlte-django 0.3.3

