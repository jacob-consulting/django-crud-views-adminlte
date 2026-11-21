# AdminLTE theme (extension of adminlte-django) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A django-crud-views theme package `crud_views_adminlte` that plugs into the third-party shell adminlte-django,
the Acme Roasters demo on top, and an upstream tracker of every friction found on the way.

**Architecture:** One theme app listed before `crud_views`; its `page.html` extends adminlte-django's `adminlte/page.html`
and overrides only the host's `content_header` block; button classes, label modes, icons and CSS are registered through
crud_views' hooks in `ready()`; two menu filters plug ViewSets into adminlte-django's `ADMINLTE["menu"]` pipeline. The
demo is copied from the CoreUI sibling and rewired as an ordinary adminlte-django project.

**Tech Stack:** Python 3.12–3.15, Django 6.0/6.1, adminlte-django 0.3.x (`django_adminlte4`, django-components),
django-crud-views (`main` @ `75a42851`), django-tables2, django-filter, crispy-bootstrap5, pytest/pytest-django, nox,
uv, Task, ruff, mkdocs.

**Spec:** `superpowers/specs/2026-11-21-adminlte-theme-design.md` (read it first; this plan does not repeat its reasons).

**Reference checkouts** (paths relative to this repo): CoreUI sibling `../../django-crud-views-core-ui` (the template for
almost everything: tooling, tests, example, tracker format), crud_views `../../django-crud-views`, extensions
`../../django-crud-views-extensions`. adminlte-django is read from the installed package in `.venv` (never edit it).

## Global Constraints

- Python 3.12–3.15 × Django 6.0, 6.1; local development Python 3.15 / Django 6.1. Cells outside declared support
  (Django 6.0 × Python 3.15; adminlte-django × Python 3.15) run, and are marked unsupported, not dropped silently.
- `adminlte-django (>=0.3.3,<0.4)`; `django-crud-views (>=0.30)` declared floor (as CoreUI; release floor script guards
  it); local editable sources `../../django-crud-views`, `../../django-crud-views-extensions`.
- nox installs `django-crud-views[workflow,polymorphic,guardian,ordered] @ git+https://github.com/jacob-consulting/django-crud-views@<PIN>`,
  `PIN` a single constant in `noxfile.py`, starting at `75a42851101be7db75c93e5b7de22764a3ff0949`.
- `../../django-crud-views` and `../../django-crud-views-extensions` are read-only for this repo (pin bumps fast-forward
  the local checkout to what the maintainer merged; nothing else).
- No override of `adminlte/master.html`; a `adminlte/partials/*` override only as a logged last resort. No
  monkeypatching of crud_views or adminlte-django.
- **Tracker rule:** every override, theme CSS rule or workaround gets an entry in `superpowers/notes/upstream-tracker.md`
  in the same commit, and a `# tracker <ID>` / `{# tracker <ID> #}` comment at the workaround. IDs: `C<n>` for
  django-crud-views findings, `A<n>` for adminlte-django findings. Entry fields: status (anticipated / confirmed /
  filed / done), severity (blocker / annoyance / cosmetic), symptom, minimal repro, workaround (file reference),
  proposed upstream fix, verified against `<commit>`.
- App code in `example/` never imports `crud_views_adminlte`.
- `ADMINLTE["assets_mode"] = "static"` in the demo and the test settings.
- Brand "Acme Roasters", primary sienna `#a0522d`; demo accounts `alex` / `sam` / `kim` (password `demo`), `admin`/`admin`
  from the Taskfile, as CoreUI.
- Ruff with the CoreUI configuration (line length 120); `uv run ruff format . && uv run ruff check .` before each commit.
- Test suites run with `pytest -n auto`. `unset VIRTUAL_ENV` before uv commands if the parent shell sets one.

## Review Focus

1. **Anonymous user hits a page that renders the menu** (login page, 403/404 pages): the gate filter must not crash on
   `AnonymousUser` and must hide every ViewSet entry. Test in Task 4.
2. **A ViewSet entry for a child ViewSet** (needs a parent pk, cannot be reversed globally): system check error at
   startup, never a `NoReverseMatch` on every page. Test in Task 4.
3. **The theme's filters missing from, or misordered in, `ADMINLTE["filters"]`** while the menu has `viewset` entries:
   the host would silently render `href="#"` links. System check error. Test in Task 4.
4. **A crud_views flash message and a host page in the same request** (redirect after create, then the dashboard): the
   message shows exactly once, in the host's markup, on whichever page renders first. Test in Task 3.
5. **The host's own breadcrumb on non-crud pages next to crud_views' breadcrumb prefix**: no duplicated "Home" crumb on
   crud_views pages. Test in Task 3 (crud page) and Task 5 (dashboard).

---

## Pin bump procedure (used by Tasks 7, 8, 10)

Run when a tracked upstream change (#391, #393, #394) is merged to crud_views `main`:

1. `git -C ../../django-crud-views fetch origin && git -C ../../django-crud-views merge --ff-only <commit>`; set `PIN` in
   `noxfile.py` to `<commit>`; `uv lock` (lock must not change apart from crud_views).
2. `task test` green; `uvx nox -s tests examples` green for at least the 3.15/6.1 and 3.12/6.0 cells.
3. Every tracker entry: re-check; mark fixed upstream with the commit; remove workarounds the change made unnecessary
   (grep for their tracker IDs); log new friction; update "verified against".
4. Browser pass over the pages the upstream change touches (light and dark).
5. Commit `chore: bump django-crud-views to <short> (#<n>)` with the tracker changes.

---

### Task 1: Prerequisites, repository scaffold, tooling, tracker skeleton

**Files:**
- Delete: `src/django_crud_views_adminlte/`, `uv.lock` (regenerated)
- Create/replace: `pyproject.toml`, `noxfile.py`, `Taskfile.yaml`, `.gitignore`, `.pre-commit-config.yaml`, `mkdocs.yml`,
  `LICENSE` (MIT, Alexander Jacob), `README.md`, `CHANGELOG.md`, `CLAUDE.md`, `scripts/check_dist.py`,
  `scripts/check_release_floor.py`, `src/crud_views_adminlte/__init__.py` (`__version__ = "0.1.0"`),
  `src/crud_views_adminlte/apps.py` (empty `ready()` for now), `superpowers/notes/upstream-tracker.md`, `dev/README.md`
- Create: `tests/__init__.py`, `tests/crud_views_adminlte/{__init__,settings,urls}.py`,
  `tests/crud_views_adminlte/testapp/` (models, one top-level ViewSet `author` with list/detail/create/update/delete,
  one child ViewSet `book` of `author`, migrations), `tests/crud_views_adminlte/test_package.py`

**Interfaces:**
- Produces: test settings module `tests.crud_views_adminlte.settings` with the full adminlte-django setup:
  `INSTALLED_APPS` order `django.contrib.*`, `django_components`, `django_adminlte4`, `crispy_forms`, `crispy_bootstrap5`,
  `django_tables2`, `django_filters`, `crud_views_adminlte`, `crud_views.apps.CrudViewsConfig`,
  `crud_views_object_detail`, `tests.crud_views_adminlte.testapp`; `TEMPLATES` with `APP_DIRS=False`, loaders
  `django.template.loaders.filesystem.Loader`, `django.template.loaders.app_directories.Loader`,
  `django_components.template_loader.Loader` (order as adminlte-django's `docs/installation.md` requires), builtin
  `django_components.templatetags.component_tags`, context processor `django_adminlte4.context_processors.adminlte`;
  `ADMINLTE = {"assets_mode": "static", "sidebar_docs_url": "", "menu": [...]}`; `CRUD_VIEWS_EXTENDS =
  "crud_views_adminlte/page.html"`; `CRISPY_TEMPLATE_PACK = "bootstrap5"`.
- Produces: testapp URL names `author-list`, `author-detail`, … and the child `book-list` under an author pk (crud_views
  defaults).

- [ ] **Step 1: Prerequisites.** `git -C ../../django-crud-views merge --ff-only origin/main`; verify
  `git -C ../../django-crud-views rev-parse HEAD` = `75a42851…`. `git init` here, first commit = the approved spec and
  this plan.
- [ ] **Step 2: Port tooling from CoreUI.** `pyproject.toml`: name `django-crud-views-adminlte`, hatchling, wheel
  `src/crud_views_adminlte` only, deps `django (>=6.0)`, `django-crud-views (>=0.30)`, `adminlte-django[tables,crispy] (>=0.3.3,<0.4)`,
  extras `examples` / `test` / `dev` as CoreUI (drop the crispy-pack pins), Django 6.0/6.1 classifiers. `noxfile.py`:
  `DJANGO_VERSIONS = ["6.0", "6.1"]`, `PIN` constant, one suite `tests/crud_views_adminlte`, `skip_unsupported` marking
  (session.log + run, not skip, for the out-of-support cells, per Global Constraints), installed-origin check for
  `crud_views_adminlte`. Taskfile and scripts as CoreUI with names replaced; `check_dist.py` list without
  `django_coreui`.
- [ ] **Step 3: Tracker skeleton.** Header (purpose: crud_views inside a host it does not own; reference commits
  `75a42851`, adminlte-django 0.3.3), status/severity legend, entry template with the Global Constraints fields, two
  sections `## django-crud-views (C)` and `## adminlte-django (A)`. Pre-log from the spec: A1 navbar/sidebar/footer are
  includes, not blocks; A2 `HrefFilter` runs before any per-request filter; A3 defaults leaking into projects (Home `/`,
  docs links, footer, search); A4 `APP_DIRS=False` / django-components required; A5 Python 3.15 undeclared.
- [ ] **Step 4: Write `test_package.py`:** `test_version` (`crud_views_adminlte.__version__ == "0.1.0"`),
  `test_system_check_clean` (`call_command("check", fail_level="WARNING")` raises nothing),
  `test_list_page_renders` (logged-in superuser GET `author-list` → 200, contains `class="app-main"` from the host
  shell).
- [ ] **Step 5: Run** `uv sync --extra examples --extra test --extra dev && uv run pytest -n auto tests/crud_views_adminlte
  --ds tests.crud_views_adminlte.settings`. Expected: `test_list_page_renders` FAILS (no `page.html` yet), others pass.
  Mark it `xfail(strict=True, reason="Task 3")`.
- [ ] **Step 6: Commit** `chore: scaffold django-crud-views-adminlte`.

### Task 2: Theme registration: buttons, label modes, icons, CSS, app-order check

**Files:**
- Create: `src/crud_views_adminlte/buttons.py`, `icons.py`, `checks.py`,
  `static/crud_views_adminlte/crud_views_adminlte.css`
- Modify: `src/crud_views_adminlte/apps.py`
- Test: `tests/crud_views_adminlte/test_registration.py`

**Interfaces:**
- Produces: `ADMINLTE_BUTTON_CLASSES: dict[str, str]`, `ADMINLTE_ICONS: dict[str, str]` (crud_views semantic name →
  `bi:<name>`), check ids `crud_views_adminlte.E001` (app order).

- [ ] **Step 1: Write tests:**
  - `test_button_keys_cover_upstream`: `set(DEFAULT_BUTTON_CLASSES) - set(ADMINLTE_BUTTON_CLASSES) == set()` (from
    `crud_views.lib.button_classes`), so every upstream key at the pin — including `bulk:*` — has a deliberate value.
  - `test_button_classes_registered`: `get_button_classes()["list:primary"] == ADMINLTE_BUTTON_CLASSES["list:primary"]`.
  - `test_workflow_keys_only_with_workflow_app` (as CoreUI's test).
  - `test_icons_registered`: for every key in `crud_views.lib.icons` defaults, `get_icons()[key].startswith("bi:")`.
  - `test_label_mode_defaults`: form → `both`; `bulk` keeps upstream's `both`.
  - `test_assets_registered`: rendered list page contains `crud_views_adminlte/crud_views_adminlte.css`.
  - `test_app_order_check`: with `override_settings(INSTALLED_APPS=[... crud_views before theme ...])` the check returns
    one `Error` id `crud_views_adminlte.E001`.
- [ ] **Step 2: Run, expect failures** (ImportError on `crud_views_adminlte.buttons`).
- [ ] **Step 3: Implement.** `buttons.py`: start from CoreUI's `COREUI_BUTTON_CLASSES` keys; values are plain Bootstrap
  5.3 classes (AdminLTE adds none for buttons): drop CoreUI's `cv-coreui-*` helpers in favour of Bootstrap utilities
  where possible; Tabler `btn-ghost-*` → `btn-link`/`btn-outline-*` (pick in the browser in Task 6); `bulk:*` keys
  with upstream's values unless AdminLTE needs different. Module docstring records each translation, as CoreUI does.
  `icons.py`: map each crud_views semantic icon to a Bootstrap Icons name (renderer is upstream's built-in `bi`
  library, no SVG table, so no W001-style check). `checks.py`: app-order Error as CoreUI's E002, renamed E001.
  `apps.py` `ready()`: `register_icons`, `register_label_mode_defaults({"form": "both"})`, `register_button_classes`
  (workflow filter as CoreUI), `register_assets("crud_views_adminlte", css=[...])`; no JS (stock Bootstrap 5).
- [ ] **Step 4: Run tests, expect PASS.**
- [ ] **Step 5: Commit** `feat: register AdminLTE button classes, icons and assets`.

### Task 3: `page.html`: crud_views inside the host's page

**Files:**
- Create: `src/crud_views_adminlte/templates/crud_views_adminlte/page.html`,
  `src/crud_views_adminlte/templatetags/crud_views_adminlte.py` (only if a tag is needed, e.g. the CoreUI
  `heading_repeats_tab` equivalent)
- Modify: tracker; CSS if needed
- Test: `tests/crud_views_adminlte/test_theme.py`, `tests/crud_views_adminlte/test_host_drift.py`

**Interfaces:**
- Consumes: host blocks of `adminlte/master.html` (`title`, `extra_css`, `content_header`, `messages`, `content`,
  `extra_js`) and `adminlte/page.html` (`page_title`, `breadcrumb`).
- Produces: template `crud_views_adminlte/page.html` (the `CRUD_VIEWS_EXTENDS` target), its own blocks for projects:
  `cv_navbar`, `page_title`, `cv_paragraph`, `cv_context`, `breadcrumb`, `cv_filter`, `cv_content` (names as CoreUI's
  `page.html`).

- [ ] **Step 1: Write drift tests** (`test_host_drift.py`): load `adminlte/master.html` and `adminlte/page.html` via the
  configured loaders and assert the block names above exist (parse with `django.template.loader_tags.BlockNode` over
  `template.template.nodelist`), and that `page.html`'s `breadcrumb` block sits inside an `<ol class="breadcrumb`
  (source string check). A failing drift test names the host file and version.
- [ ] **Step 2: Write theme tests** (`test_theme.py`, lxml + cssselect on responses):
  - `test_header`: author list → `.app-content-header` contains the header icon, the crud_views heading text, the
    paragraph, and the context action button (create).
  - `test_breadcrumb_items_inside_host_ol`: `ol.breadcrumb` exists once; it has no nested `ol`/`nav`; its `li` items
    are crud_views' crumbs.
  - `test_breadcrumb_no_duplicate_home` (Review Focus 5): with `CRUD_VIEWS_BREADCRUMB_PREFIX = [{"title": "Home",
    "url_name": ...}]` exactly one crumb text "Home".
  - `test_message_once_through_host` (Review Focus 4): POST a valid create, follow the redirect; the success text
    appears exactly once, inside the host's message markup (the selector from `adminlte/partials/messages.html`); then
    GET a second page: zero occurrences.
  - `test_navbar_owner_header`: a child list page with ViewSet Navigation shows the owner header and tabs at the top of
    the content header, once.
  - `test_no_cv_messages_markup`: crud_views' own alert wrapper class is absent from the page.
  - Remove the `xfail` from `test_list_page_renders`.
- [ ] **Step 3: Run, expect failures.**
- [ ] **Step 4: Implement `page.html`:** extends `adminlte/page.html`; maps blocks per the spec ("`crud_views_adminlte`"
  section); overrides `content_header` with the host's `app-content-header` / `container-fluid` / `row` markup, title
  row with `cv_heading` at h3 size, subtitle, actions on the right, and re-declares `{% block breadcrumb %}` inside an
  `ol.breadcrumb` there; leaves `messages` alone. Breadcrumb items-only: if `cv_breadcrumb` renders its own
  `<nav><ol>`, render items without it by the least-invasive means (an upstream hook if one exists at the pin, else a
  theme override of the breadcrumb template), and log **C1** (no items-only breadcrumb for host-owned containers;
  #393's class keys do not cover it). Log **A6** (`page_title` in a fixed `<h3>`, no subtitle/actions slots). Log
  **C2** for anything lost by not using `cv_messages` (icons, `extra_tags`, no "host renders messages" mode). Log
  duplicate-Home handling as **C3** or **A7** depending on which side is fixed.
- [ ] **Step 5: Run all theme tests, expect PASS; `manage.py check` equivalent clean.**
- [ ] **Step 6: Commit** `feat: page template mapping crud_views onto adminlte-django` (with tracker entries).

### Task 4: Menu filters: ViewSets in `ADMINLTE["menu"]`

**Files:**
- Create: `src/crud_views_adminlte/menu.py`
- Modify: `src/crud_views_adminlte/checks.py`, tracker
- Test: `tests/crud_views_adminlte/test_menu.py`

**Interfaces:**
- Consumes: `ViewSet.get_viewset(name)`, `viewset.get_router_name(key)`, `viewset.get_view_class(key).cv_has_access(user)`,
  `viewset.parent`; host `BaseFilter`, `HrefFilter` (skips items that already have `href`), `split_filters`.
- Produces:
  - `ViewSetHrefFilter(BaseFilter)`, `per_request = False`: for items with `viewset` (and optional `view`, default
    `"list"`), sets `href = reverse(viewset.get_router_name(view))`; fills `text` / `icon` from the ViewSet if the
    item omits them and crud_views exposes them; recurses into `submenu`.
  - `ViewSetGateFilter(BaseFilter)`, `per_request = True`: drops `viewset` items when
    `not view_class.cv_has_access(request.user)` (anonymous → dropped); parent-with-empty-submenu handled by the host's
    `GateFilter` semantics (put ours before it).
  - `VIEWSET_FILTERS: list[str]` = the two dotted paths, documented usage:
    `ADMINLTE["filters"] = [*VIEWSET_FILTERS, *DEFAULT_FILTERS]` (`DEFAULT_FILTERS` from `django_adminlte4.conf`).
  - Check ids: `crud_views_adminlte.E010` unknown ViewSet name, `E011` child ViewSet entry, `E012` unknown `view` key,
    `E013` `viewset` entries present but `ViewSetHrefFilter` not before `HrefFilter` or `ViewSetGateFilter` missing.

- [ ] **Step 1: Write tests** (build menus through the host's context processor on a `RequestFactory` request, so the
  real pipeline and its caching run):
  - `test_href_resolved`: `{"viewset": "author", "text": "Authors"}` → `href == reverse("author-list")`.
  - `test_view_key`: `{"viewset": "author", "view": "create"}` → create URL.
  - `test_hidden_without_permission` (user without view perm) / `test_shown_with_permission`.
  - `test_anonymous_hides_entries` (Review Focus 1): `AnonymousUser` → no ViewSet items, no exception.
  - `test_active_on_child_pages`: request path of a `book` list under an author → the `author` item is active (host
    `ActiveFilter` from the derived `href`; if crud_views' child URLs do not nest under the parent's prefix, the filter
    sets `active` patterns explicitly and this is logged).
  - `test_submenu_parent_dropped_when_all_children_hidden`.
  - `test_checks`: E010 (`"nope"`), E011 (`"book"`, Review Focus 2), E012 (`"view": "nope"`), E013 (filters left at
    host defaults, Review Focus 3); each returns exactly that error id.
  - `test_cache_survives_settings_change`: `override_settings(ADMINLTE=...)` twice gives two different menus (host
    clears its prefilter cache).
- [ ] **Step 2: Run, expect failures.**
- [ ] **Step 3: Implement `menu.py` and the checks** per Interfaces. Use only public crud_views API; where a need is
  private (registry iteration, `_REGISTRY`, no `ViewSet` icon/label accessor, no "can user see this view" without the
  view class), log **C4…** with the exact call used. Log **A2** confirmation with the two-filter workaround.
- [ ] **Step 4: Run, expect PASS.**
- [ ] **Step 5: Commit** `feat: ViewSet entries for the adminlte-django menu`.

### Task 5: Example: copy the CoreUI demo and rewire it onto adminlte-django

**Files:**
- Copy: `../../django-crud-views-core-ui/example/` → `example/` (without `db.sqlite3`, `media/`, `staticfiles/`,
  `__pycache__`)
- Delete: `example/templates/django_coreui/`, `example/config/templatetags/acme_nav.py`
- Create: `example/config/menu.py`
- Modify: `example/config/settings.py`, `example/config/icons.py`, `example/templates/registration/login.html`,
  `example/templates/project/crud_views.html`, `example/static/acme/acme.css`, Taskfile paths if needed
- Test: `example/config/test_pages.py` (new), existing example tests

**Interfaces:**
- Consumes: `VIEWSET_FILTERS` (Task 4), the test settings pattern (Task 1).
- Produces: `ACME_ICONS: dict[str, str]` semantic name → Bootstrap Icons name (same keys as CoreUI's table);
  `CRUD_VIEWS_ICONS = {k: f"bi:{v}" for k, v in ACME_ICONS.items()}`; `example/config/menu.py` `MENU: list[dict]`
  (headers and `viewset` entries replacing `acme_nav`; icons `f"bi bi-{ACME_ICONS[...]}"`).

- [ ] **Step 1: Write `test_pages.py`:** `test_every_page_renders` — log in as `alex`, iterate every crud_views list,
  detail (first object), create and update URL of every registered ViewSet plus the non-crud URLs (dashboard, theming,
  users, manage), assert status 200 and no `TemplateSyntaxError`/`VariableDoesNotExist` in logs;
  `test_dashboard_breadcrumb_single_home` (Review Focus 5, host page); `test_menu_per_role` — `sam` does not see the
  roastery entries, `kim` does not see sales (use the role/permission split the seed defines).
- [ ] **Step 2: Copy and rewire settings:** the full adminlte-django setup (as test settings), `ADMINLTE` with `title`
  / `logo` / `logo_alt_text` "Acme Roasters", `logo_img` the Acme logo if one exists in `example/static/acme/`,
  `sidebar_docs_url: ""`, `footer_left` / `footer_right` Acme text, `navbar_search: False` unless the demo uses it,
  `filters: [*VIEWSET_FILTERS, *DEFAULT_FILTERS]`, `menu: MENU`. Keep `CRUD_VIEWS_EXTENDS = "project/crud_views.html"`
  (now extending `crud_views_adminlte/page.html`). Remove `django_coreui`, `crud_views_coreui`, `crispy_coreui`,
  `COREUI*` settings. Login template extends the host's `registration/login.html` and adds the demo-account buttons
  in its `auth_body` (or the narrowest host block that works). Brand colour via `--bs-primary*` (and AdminLTE's
  `data-lte-primary` if it fits) in `acme.css`. Every host default overridden here gets an **A3** sub-entry.
- [ ] **Step 3: Run** `cd example && uv run pytest -n auto`. Expected: `test_pages.py` passes except pages whose
  templates still contain CoreUI markup or `{% load coreui %}`; list those failures (they are Task 6).
- [ ] **Step 4: Commit** `feat(example): Acme Roasters on adminlte-django`.

### Task 6: Example: AdminLTE markup for the demo's own templates

**Files:**
- Modify: the Python files that import the CoreUI packages (`example/config/{showcode,views}.py`,
  `example/showcase/{models,views,tests}.py`, `example/dashboard/tests.py`),
  dashboard templates (`example/dashboard/templates/…`), user list, order detail, packing slip
  (`example/sales/…`, `example/shipping/…`), `example/templates/project/{theming,code_panel,code_panel_shell}.html`,
  `example/config/views.py` (theming page file list), CoreUI-specific example tests
- Test: the existing example tests (ported expectations), `test_pages.py`

- [ ] **Step 1: Port example tests** that assert CoreUI markup to AdminLTE/Bootstrap 5 markup; run, expect failures.
- [ ] **Step 2: Rewrite templates:** `{% load coreui %}` `{% icon "x" %}` → crud_views' `{% cv_icon "x" %}` (semantic
  names via `CRUD_VIEWS_ICONS`; if app templates cannot use semantic icons without crud_views' tag, log it as **C5**);
  CoreUI classes → Bootstrap 5/AdminLTE; dashboard KPIs and cards with adminlte-django components
  (`{% component "adminlte_small_box" … %}`, info boxes, cards) where a matching component exists; charts with the
  host's chart component if it covers the demo's charts, else keep ApexCharts and say so in the theming page. The
  theming page lists this project's theme files, computed at render time, and names the host package and version.
  The showcase app imports `crispy_coreui`'s layout objects: switch to crispy-bootstrap5's (`FloatingField`, `Switch`)
  and keep its form covering every field type. Extensions widgets (datetimepicker, typeahead): check under AdminLTE
  light/dark; any CSS goes in `acme.css` or the theme CSS with a tracker entry.
- [ ] **Step 3: Choose button class values in the browser** (Task 2's open picks) on list, detail, form, manage and
  workflow pages; update `buttons.py`; light and dark.
- [ ] **Step 4: Run** `task test`; all green; `uv run python example/manage.py check --fail-level WARNING` clean.
- [ ] **Step 5: Commit** `feat(example): AdminLTE markup for dashboard, detail and theming pages`.

### Task 7: Pin bump for #391 (when merged)

- [ ] Run the **Pin bump procedure**. Expected outcome: no theme change (AdminLTE keeps the `bs` prefix); add a
  test `test_no_data_prefix_override` only if #391 adds a setting the theme must leave at default. Tracker: note #391
  as "no effect on a stock-Bootstrap host" under the C section (useful evidence for #391's design).

### Task 8: Tables and bulk selection (after #393; see spec for the fallback if it slips)

**Files:**
- Modify: settings (`DJANGO_TABLES2_TEMPLATE`), possibly `src/crud_views_adminlte/templates/crud_views/table/…` (only if
  needed, logged), `buttons.py` (`bulk:*` values), CSS
- Modify (example): orders ViewSet gets bulk actions (e.g. "mark as packed", "cancel") in `example/sales/views.py`
- Test: `tests/crud_views_adminlte/test_tables.py`, `test_bulk.py`, example tests

- [ ] **Step 1: Pin bump to the #393 merge** (procedure). If #393 is not merged when Task 6 is done, skip this step,
  use the host's `django_tables2/adminlte.html` path, write no `table.thead` copy, and log the missing sorted-column
  state as waiting on #393.
- [ ] **Step 2: Write tests:** `test_table_in_card` (list page table inside the chosen template's wrapper, once — no
  card in a card); `test_sorted_column_aria_sort` (sorted column `th[aria-sort="ascending"]`, with and without a table
  prefix; xfail strict when on the fallback path); `test_bulk_toolbar` (bulk-enabled testapp list shows toolbar,
  select-all and per-row checkboxes with the theme's `bulk:*` classes); `test_bulk_form_page_renders`;
  `test_bulk_result_message_through_host` (result message once, host markup); `test_bulk_card_view` (card layout
  select).
- [ ] **Step 3: Decide the table template** (crud_views' `crud_views/table/bootstrap5.html` vs host
  `django_tables2/adminlte.html`) from the tests and the browser; record the choice and why in `docs/theme_internals.md`;
  any conflict is a **C**/**A** entry.
- [ ] **Step 4: Bulk in the demo:** orders list with two bulk actions; browser check of selection JS, select-all,
  blocked items page, card view, dark mode, 375px.
- [ ] **Step 5: Run** `task test`; green. **Commit** `feat: tables and bulk selection under AdminLTE`.

### Task 9: Docs

**Files:**
- Create: `docs/{index,installation,menu,theme_internals,demo,development}.md`, `docs/requirements.{in,txt}`
- Modify: `README.md`, `mkdocs.yml`, `CLAUDE.md` (final commands, architecture, conventions)

- [ ] **Step 1:** installation = the full adminlte-django settings block plus the theme lines and filter list, tested
  by copying it into a test (`test_docs_settings_snippet`: the snippet, `exec`'d into a settings dict, contains every
  key the test settings need); menu = `viewset` entries, the four checks, ordering rule; theme_internals = block
  mapping, overrides and their tracker IDs.
- [ ] **Step 2:** `uvx nox -s docs` (mkdocs strict) green. **Commit** `docs: user guide`.

### Task 10: #394 bump, matrix, browser pass, tracker close-out

- [ ] **Step 1:** Pin bump for #394 when merged (procedure); dark-mode check on manage and formset pages.
- [ ] **Step 2:** `task test:matrix` (all nox sessions) green; out-of-support cells reported as such.
- [ ] **Step 3:** Browser pass (spec "Testing"): every page as alex, sam, kim; light, dark, auto; sidebar
  collapsed/mini; 375px; dropdowns, modals, tooltips, tabs, accordions, filters, formsets, ViewSet Navigation, bulk,
  menu active states. Fix or log each defect.
- [ ] **Step 4:** Tracker close-out section (as CoreUI's): table of every entry with final status and the theme file
  that handles it; a short comparison note: which C entries are new compared with the Tabler/CoreUI trackers (the
  "host-owned shell" findings), which repeat.
- [ ] **Step 5: Commit** `docs: tracker close-out`.
