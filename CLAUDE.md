# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

The distribution **django-crud-views-adminlte** (repo `jacob-consulting/django-crud-views-adminlte`): an AdminLTE 4 theme
for django-crud-views. One package under `src/`: `crud_views_adminlte`, which extends the third-party page shell
**adminlte-django** (PyPI `adminlte-django`, import `django_adminlte4`; not the unrelated `django-adminlte4`). There is
no shell package and no crispy pack here (crispy-bootstrap5 is used as is). Supported: Python 3.12-3.15 x Django 6.0,
6.1 (nox matrix; the Python 3.15 and the Django 6.0 x 3.15 cells run and are logged as unsupported); local development
runs Python 3.15 / Django 6.1.

State: feature-complete, not released (0.1.0). Design and plan: `superpowers/specs/` and `superpowers/plans/`; user guide
in `docs/` (mkdocs, published later on Read the Docs).

`../django-crud-views` and `../django-crud-views-extensions` are editable path sources (`[tool.uv.sources]`) and
read-only for this repo: gaps are worked around here and logged in `superpowers/notes/upstream-tracker.md`. nox installs
django-crud-views from its GitHub `main` (`CRUD_VIEWS` in `noxfile.py`) until 1.0.0rc1 is on PyPI; the declared floor stays
lower and `scripts/check_release_floor.py` guards the publish step.

## Commands

```shell
unset VIRTUAL_ENV   # before every uv / uvx command, if the parent environment sets one
uv sync --extra examples --extra test --extra dev
# Always run test suites on all cores: pytest -n auto. Single-core only for one test or a -k selection.
uv run pytest -n auto tests/crud_views_adminlte --ds tests.crud_views_adminlte.settings
uv run ruff format . && uv run ruff check .
uvx nox            # tests, examples, package, docs matrix (Taskfile: task test:matrix)
uvx nox -s docs    # mkdocs build --strict from docs/requirements.txt (hashed; regenerate from docs/requirements.in)
cd example && uv run pytest -n auto   # the demo's tests; manage.py check --fail-level WARNING must stay clean
```

`task up` (Taskfile.yaml) installs, migrates, creates `admin`/`admin`, seeds and runs the demo (`example/`, Acme Roasters);
`task test` runs the theme suite, the demo's tests and the system check.

## Architecture

`src/crud_views_adminlte/`: `apps.py` (`ready()` registers icons, button classes, label-mode defaults and the stylesheet
through upstream's hooks), `buttons.py` (AdminLTE class keys), `icons.py` (Bootstrap Icons through upstream's `bi`
library), `checks.py` (E001 app order; E010-E015 menu entries and the filter pair), `menu.py` (`ViewSetHrefFilter`,
`ViewSetGateFilter`, `VIEWSET_FILTERS`), `templatetags/crud_views_adminlte.py`, `templates/crud_views_adminlte/page.html`
(`CRUD_VIEWS_EXTENDS`: extends the host's `adminlte/page.html`, overrides `content_header` only),
`templates/crud_views/tags/breadcrumb.html` (items-only breadcrumb, shadows upstream globally, C1) and one stylesheet.
`docs/theme_internals.md` lists every override with its tracker ID; `docs/installation.md` holds the settings block, which
`tests/crud_views_adminlte/test_docs.py` executes and compares with the test settings, so change both together.

## Host setup (adminlte-django)

Documented in `docs/installation.md`; see `tests/crud_views_adminlte/settings.py` and `example/config/settings.py`: `django_components` before `django_adminlte4` in `INSTALLED_APPS`,
`APP_DIRS=False` with explicit loaders (filesystem, app_directories, `django_components.template_loader.Loader`), the
`component_tags` builtin, the `adminlte` context processor, `COMPONENTS`, `STATICFILES_FINDERS` with
`ComponentsFileSystemFinder`, `ADMINLTE["assets_mode"] = "static"`, `CRUD_VIEWS_EXTENDS = "crud_views_adminlte/page.html"`,
`CRISPY_TEMPLATE_PACK = "bootstrap5"`, `CRUD_VIEWS_BREADCRUMB_PREFIX` (A8), `DJANGO_TABLES2_TEMPLATE =
"crud_views/table/bootstrap5.html"` (A19), `ADMINLTE["filters"] = [*VIEWSET_FILTERS, *DEFAULT_FILTERS]` (A2) and
`SILENCED_SYSTEM_CHECKS = ["adminlte.W003"]` (A11). The theme app is listed before `crud_views`.

## Conventions

- No override of `adminlte/master.html`; an `adminlte/partials/*` override only as a logged last resort. No
  monkeypatching of crud_views or adminlte-django.
- **Upstream tracker rule:** every override, theme CSS rule or workaround gets an entry in
  `superpowers/notes/upstream-tracker.md` in the same commit and a `# tracker <ID>` / `{# tracker <ID> #}` comment at the
  workaround. IDs `C<n>` (django-crud-views, C1-C11), `A<n>` (adminlte-django, A1-A19); the next free ID is the one after
the last in the tracker. Tests named in the tracker guard the copies and host assumptions against upstream drift.
- Menu `viewset` entries need `text` (C3) and no child or object views (E011, E015); access is `cv_has_access(user)`
  only (C6, C7).
- App code in `example/` never imports `crud_views_adminlte`.
- Demo: brand "Acme Roasters", primary sienna `#a0522d`; accounts `alex` / `sam` / `kim` (password `demo`), `admin`/`admin`
  from the Taskfile.
- Design specs, plans and notes live in `superpowers/{specs,plans,notes}/`; maintainer notes in `dev/` (not published).
- Ruff, line length 120; run `uv run ruff format . && uv run ruff check .` before committing.
