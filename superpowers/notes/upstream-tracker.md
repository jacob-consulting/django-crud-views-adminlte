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

None logged yet.

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

- Status: anticipated · Severity: annoyance
- Symptom: a menu entry whose URL is only known per request or per ViewSet is given `href="#"`, whatever order
  `ADMINLTE["filters"]` lists the filters in.
- Minimal repro: put a request-dependent filter before `HrefFilter` in `ADMINLTE["filters"]` and give it an item
  without `url`/`route`; `split_filters` in `menu/builder.py` runs the request-independent filters (`HrefFilter`,
  `SearchFilter`) once per process first, so the item is already `href="#"`.
- Workaround: none yet. The theme's menu filter sets `href` itself (or is split into a once-per-process URL part and a
  per-request part).
- Proposed upstream fix: honour the configured order, or document the split and expose a hook for custom
  request-independent filters.
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
