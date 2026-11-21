# AdminLTE theme for django-crud-views, as an extension of adminlte-django: design

Date: 2026-11-21 · Status: approved (2026-11-21)

## Intent

django-crud-views is being prepared for its 1.0 release. The Tabler (`../../tabler-test`) and CoreUI
(`../../django-crud-views-core-ui`) adaptations exist to find weaknesses in how downstream projects theme it; their
findings live in upstream trackers (CoreUI: `superpowers/notes/upstream-tracker.md`).

Both siblings own their page shell (`django_tabler`, `django_coreui`). This third adaptation tests the case a 1.0 user
hits more often: **dropping crud_views into a page shell somebody else owns**. The shell is
[adminlte-django](https://github.com/ColorlibHQ/adminlte-django) (PyPI `adminlte-django`, import `django_adminlte4`,
0.3.3, MIT, by Colorlib, AdminLTE 4.10.2 on Bootstrap 5.3.9), installed as a dependency, not re-implemented.

**The deliverable is the upstream tracker**: what crud_views makes hard when it lives inside a host it does not
control. The theme package and the demo are the proof that every finding was hit for real.

## Goals

1. `src/crud_views_adminlte/`: a django-crud-views theme that plugs into adminlte-django. Depends on
   `adminlte-django` and `django-crud-views`.
2. **Follow the host's conventions wherever it has one** (decided): the sidebar menu is `ADMINLTE["menu"]`, the
   breadcrumb goes into adminlte-django's `breadcrumb` block, messages use its partial, the login page is its
   `registration/login.html`, crispy uses the stock `bootstrap5` pack it expects, tables follow its tables2 template
   where that is compatible. crud_views adapts to the host, not the other way round.
3. **Menu filter**: a filter for adminlte-django's menu pipeline (`ADMINLTE["filters"]`) that expands ViewSet entries
   such as `{"viewset": "customer", "text": ..., "icon": ...}` into a resolved URL, hidden when the user may not see
   the ViewSet's list view, and active on every page of that ViewSet (and its children). This is the main probe of
   crud_views' public API (registry, URL names, permission checks) from outside.
4. `example/`: Acme Roasters at full parity with the CoreUI demo (dashboard, sales, catalog, roastery, shipping,
   showcase, theming page, users, "Show code" panel, manage pages), set up as an ordinary adminlte-django project,
   plus **one bulk-enabled list** (orders) as a probe of bulk selection (#392), which the sibling demos predate.
   App code never imports `crud_views_adminlte`.
5. `superpowers/notes/upstream-tracker.md`, kept current, with **two sections**: findings against
   django-crud-views (the point) and findings against adminlte-django (logged, not filed; decided). Every override, CSS
   rule or workaround gets an entry in the same change that adds it, as in the siblings.
6. Tests at parity with what applies from the CoreUI theme suite (`tests/crud_views_coreui/`) and the example app
   tests, green across the nox matrix.

## Non-goals

- A page shell or crispy pack of our own (that is what the siblings already show).
- Filing issues or PRs on adminlte-django now; we work around and log, and file later from the log (decided).
- Changing `../../django-crud-views` or `../../django-crud-views-extensions` (read-only; gaps go to the tracker).
- GitHub-facing infrastructure (workflows, Read the Docs, PyPI publish, a public demo); a follow-up, as for CoreUI.
- Theming `django.contrib.admin` (adminlte-django already does) or allauth.
- Supporting Django < 6.0 (adminlte-django requires 6.0+).

## Anti-goals (a failure even if it works)

- **Replacing the host's shell**: overriding `adminlte/master.html` or rebuilding navbar/sidebar from scratch. That
  hides exactly the friction we want to record. Overriding a `partials/*` file is allowed only as a logged last resort.
- Workarounds that are not in the tracker. An unlogged workaround is a lost finding.
- Patching or subclassing crud_views code or adminlte-django code at runtime (monkeypatching).
- A second navigation next to adminlte-django's sidebar (crud_views' ViewSet Navigation tabs on owner pages are fine;
  they are content, not site navigation).

## Constraints

- **Versions**: Python 3.12–3.15 × Django 6.0, 6.1 (adminlte-django's floor; my call to keep 6.0 in the matrix).
  Local development: Python 3.15 (`.python-version`) / Django 6.1.
- **adminlte-django pinned narrowly** (`>=0.3.3,<0.4`): it is 0.x with one author, and the theme hooks into its
  template paths and settings. Drift tests against the installed host templates the theme depends on (block names in
  `adminlte/page.html` / `master.html`, any copied partial).
- adminlte-django brings: `django_components` in `INSTALLED_APPS` and its template loader, `APP_DIRS=False`, the
  `component_tags` builtin, `COMPONENTS` setting, `ComponentsFileSystemFinder`, the `adminlte` context processor. Its
  system check enforces the loader setup. The demo sets `ADMINLTE["assets_mode"] = "static"` (prebuilt assets, no
  Node/Vite; my call).
- Its defaults that leak into every project (Home links to `/`, docs links, footer text, search button) are set or
  worked around in the demo and logged.
- Same editable sources as the siblings, adjusted for this checkout's location: `../../django-crud-views`,
  `../../django-crud-views-extensions`. nox installs django-crud-views from GitHub at the pinned commit (below) until
  1.0.0rc1 is on PyPI.
- Icons: Bootstrap Icons (bundled by adminlte-django); crud_views' built-in `bi` library. Semantic names in app code
  (`"customer"`), mapped in `example/config/icons.py` as in the CoreUI demo.
- **Reference and upstream sequence (decided):** the build starts on django-crud-views `main` @ `75a42851` (the
  #392 bulk-selection merge, 2026-11-21); adminlte-django 0.3.3. The local checkout `../../django-crud-views` is
  fast-forwarded to it (one commit past `fa2f0a7b`) before the build. The upstream changes expected during the build
  land in this order: **#391** (data-attribute prefix), **#393** (breadcrumb class keys, `aria-sort`), **#394**
  (`--cv-*` CSS tokens). Each landing is a **pin bump**, a repeatable checkpoint:
  1. move the pin (local checkout and nox) and re-lock;
  2. run the suites, the nox matrix and the every-page smoke render;
  3. review every tracker entry: mark fixed upstream (with commit), remove workarounds made unnecessary, log new
     friction, update "verified against";
  4. short browser pass over what the upstream change touched.
  Expected effect: #391 none (AdminLTE keeps the default `bs` prefix; output must stay identical); #393 the table
  header and breadcrumb class keys (its keys do not solve the host-owned `<ol>`: that finding stands); #394 a
  dark-mode check on manage and formset pages.
- **The crud_views checkout stays read-only for this repo**, as in the siblings: this build logs findings, it does not
  fix them upstream (pin bumps only pull in what the maintainer merges). Entries use the CoreUI tracker's format plus
  two fields so they are ready to file: status, severity, symptom, minimal repro, workaround (file reference),
  proposed upstream fix, verified against `<commit>`. Each workaround stays in one place and carries its tracker ID
  in a comment, so a bump can remove it cleanly.
- Matrix cells outside declared support (Django 6.0 on Python 3.15; adminlte-django lists Python up to 3.14) run as
  in the CoreUI matrix, marked unsupported rather than dropped silently.

## Approaches considered

- **A. Thin theme package on top of adminlte-django (picked).** `crud_views_adminlte` with `page.html` extending
  `adminlte/page.html`, class/icon registration in `ready()`, the menu filter, partial overrides only as a logged
  last resort. Demo is a normal adminlte-django project. Tests both sides: what a theme author needs from crud_views
  and what an adopter has to configure. Roughly a third of a sibling's size.
- **B. Own `master.html` reusing the host's partials.** Full control, little friction, but replaces the host instead of
  extending it and hides the findings. Rejected.
- **C. No package, integration only in the demo.** Purest adopter view, but nothing reusable and no like-for-like
  comparison with the sibling themes. Rejected.

## Design

### Repo shape (mirror the CoreUI sibling, minus the shell)

```
pyproject.toml        # django-crud-views-adminlte, hatchling, wheel = src/crud_views_adminlte, extras examples/test/dev,
                      # [tool.uv.sources] for the two siblings, ruff + bump-my-version as CoreUI
noxfile.py            # tests, examples, package, docs sessions
Taskfile.yaml         # up, setup, seed, seed:reset, reset, test, test:matrix (as CoreUI)
.pre-commit-config.yaml, mkdocs.yml, CHANGELOG.md, LICENSE (MIT), README.md, CLAUDE.md, .gitignore
scripts/check_dist.py, scripts/check_release_floor.py   # ported
src/crud_views_adminlte/
example/              # Acme Roasters
tests/crud_views_adminlte/   # own settings with the full adminlte-django setup
docs/                 # index, installation, menu, theme_internals, demo, development
dev/
superpowers/{specs,plans,notes}/
```

The placeholder `src/django_crud_views_adminlte/`, its `[project.scripts]` entry and the `uv_build` backend go. The
directory is not a git repository yet; it becomes one at the start of the build.

### `crud_views_adminlte`

- **App order**: listed before `crud_views` and `crud_views_object_detail` so its templates shadow theirs (system check
  as CoreUI's E002). Where it sits relative to `django_adminlte4` is found out while building and documented.
- **`crud_views_adminlte/page.html`** (`CRUD_VIEWS_EXTENDS` target) extends `adminlte/page.html`:
  - `title` ← `cv_header`; `extra_css` / `extra_js` ← `cv_css` / `cv_js`;
    `content` ← `cv_filter`, `cv_content`, `cv_config`.
  - `messages`: left to the host (`adminlte/partials/messages.html`), so crud_views and non-crud pages show alerts
    alike; `cv_messages` is not used. Anything crud_views' message rendering adds that is lost this way (icons, alert
    classes) is a finding: there is no way to hand messages to a host. *(My call, from goal 2.)*
  - `breadcrumb` ← `cv_breadcrumb`. The host's block sits inside its own `<ol class="breadcrumb">`; whatever crud_views
    renders must fit inside that (likely an upstream finding: breadcrumb item-only rendering).
  - The host's `page_title` sits inside a fixed `<h3>` with no slot for subtitle, header icon or context actions. The
    theme overrides the host's `content_header` block (a block of `master.html`, so still extension) to place
    `cv_header_icon`/`cv_header`, `cv_paragraph` and `cv_context_actions`, using the host's `app-content-header`
    markup, and re-declares the nested `breadcrumb` block (it lives inside `content_header`). Logged against
    adminlte-django.
  - ViewSet Navigation (`cv_navbar`, `cv_navbar_items`): owner header and tabs at the top of the content header, as
    the CoreUI `page.html` does.
- **`ready()`** registers button classes (`buttons.ADMINLTE_BUTTON_CLASSES`, the same keys as the CoreUI table with
  AdminLTE/Bootstrap 5 values), label modes, icons (`bi:` names for crud_views' semantic icons), and theme assets
  (`crud_views_adminlte.css`, adapter JS only if needed: the host uses stock Bootstrap 5 JS and `data-bs-*`, so
  crud_views' default adapters should work).
- **Menu filter** in `crud_views_adminlte.menu`, added by the adopter to `ADMINLTE["filters"]`. adminlte-django runs
  all request-independent filters (`HrefFilter`, `SearchFilter`) once per process before any per-request one, whatever
  the list order (`split_filters` in `menu/builder.py`), so `HrefFilter` would set `href="#"` on a `viewset` entry
  first. The filter therefore sets `href` itself, or is split into a once-per-process URL part and a per-request
  permission/active part (builder's choice); logged against adminlte-django. Behaviour:
  - `{"viewset": "<name>"}` → `url` of the ViewSet's list view (or `{"viewset": ..., "view": "<key>"}`); unknown
    name → system check error, not a silent drop.
  - Permission: hidden when the user has no access to that view, using crud_views' own check, not a duplicated
    `can` string.
  - Active: on any URL of that ViewSet and its child ViewSets.
  - `text`/`icon` default from the ViewSet when the entry omits them (if crud_views exposes them).
  - Whatever this needs that crud_views does not expose publicly (`_REGISTRY` is private, for one) is a finding.
- **Templates**: start with zero crud_views overrides; stock Bootstrap 5 templates should render correctly under
  AdminLTE. Add an override only when the browser or a test shows a defect, logged. Tables: decide between crud_views'
  `crud_views/table/bootstrap5.html` and the host's `django_tables2/adminlte.html` (card wrapper) by what looks right
  and what crud_views' table features need (sorting, `aria-sort`, the bulk-select column); a conflict between the
  two is a finding.
- **Tables and bulk selection wait for #393** and are evaluated once, together: the table template choice, sorted
  column state, the `bulk:*` class keys and `bulk` label mode, the bulk toolbar and select column inside the chosen
  table and card markup, the bulk form page, and bulk result messages through the host's partial. Until then list
  pages use stock rendering untouched. If #393 has not landed when everything else is done, this work goes ahead on
  the current pin with no `table.thead` copy; the missing sorted-column state is logged as waiting on #393.

### Example (Acme Roasters)

- Copy `../../django-crud-views-core-ui/example/` (semantic icons, latest state), re-wired:
  - settings: full adminlte-django setup (above), `ADMINLTE` dict with brand "Acme Roasters", the menu as a Python
    list in `example/config/menu.py` using `viewset` entries, the filter pipeline, `assets_mode: "static"`,
    `sidebar_docs_url` off, footer text, `CRUD_VIEWS_EXTENDS = "project/crud_views.html"` (extends the theme page and
    adds "Show code"), `CRISPY_TEMPLATE_PACK = "bootstrap5"`.
  - The CoreUI demo's `acme_nav` tag library is replaced by the menu list.
  - Templates using CoreUI markup directly (dashboard, user list, order detail, packing slip, theming page, code panel,
    login extras) rewritten for AdminLTE. Where adminlte-django ships a matching component (cards, small boxes, info
    boxes, charts), the demo uses it, per goal 2; the demo then also shows crud_views next to django-components.
  - Login: the host's `registration/login.html`, extended (not replaced) for the demo-account buttons.
  - Brand colour sienna `#a0522d` through AdminLTE's/Bootstrap's CSS variables in `example/static/acme/acme.css`.
  - Demo accounts, `LoginRequiredMiddleware`, env settings, extensions widgets (datetimepicker, typeahead): as CoreUI.
  - Hosts from `DJANGO_ALLOWED_HOSTS`, default localhost.

### Testing

- Theme suite under `tests/crud_views_adminlte/` with settings carrying the full adminlte-django setup: block mapping,
  button classes, icons, the menu filter (URL, permission, active state, children, unknown name), system checks,
  drift tests against the host templates the theme relies on, and a flash message from a crud_views view rendering
  exactly once, through the host partial.
- Example app tests ported from the CoreUI demo; one test renders every example page as `alex` and fails on template
  errors.
- `manage.py check --fail-level WARNING`, `task test`, `task test:matrix` green.
- Browser pass over every page in light and dark mode, sidebar collapsed/mini, 375px: dropdowns, modals, tooltips,
  tabs, accordions, filters, formsets, ViewSet Navigation, menu active states for sam/kim/alex.

## Left to the builder

- Exact button classes per key; checked in the browser.
- Theme app position relative to `django_adminlte4` in `INSTALLED_APPS`.
- Whether the menu filter is one filter or a once-per-process + per-request pair.
- Which crud_views overrides turn out to be needed (aim: none or very few).
- Table template choice.
- Which demo pages use adminlte-django components.
- Phasing within the constraints above (the plan): setup and page template, then the menu filter, then the demo
  without tables, then tables + bulk (after #393), then the #394 bump, browser pass and tracker close-out.

## Decisions

From the user: build it as an extension of adminlte-django, not a new shell; demo on adminlte-django; same Acme
Roasters app; purpose is to find crud_views theming weaknesses before 1.0; work around adminlte-django gaps and log
them, file later; approach A; start on the #392 merge `75a42851`, then pin bumps for #391, #393, #394 in that
order, with tables + bulk gated on #393; a bulk-enabled orders list in the demo.

Calls made (not explicitly decided by the user): follow the host's conventions wherever it has one; tracker with two
sections; menu filter as the navigation integration; Django 6.0 + 6.1 matrix; adminlte-django pinned `<0.4` with drift
tests; `assets_mode: "static"`; override the host's `content_header` block; host renders flash messages;
crud_views read-only for this repo, tracker entries ready to file; host components in the demo where they
match; copy the CoreUI example as the starting point.
