# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

The distribution **django-crud-views-adminlte** (repo `jacob-consulting/django-crud-views-adminlte`): an AdminLTE 4 theme
for django-crud-views. One package under `src/`: `crud_views_adminlte`, which extends the third-party page shell
**adminlte-django** (PyPI `adminlte-django`, import `django_adminlte4`; not the unrelated `django-adminlte4`). There is
no shell package and no crispy pack here (crispy-bootstrap5 is used as is). Supported: Python 3.12-3.15 x Django 6.0,
6.1 (nox matrix; the Python 3.15 and the Django 6.0 x 3.15 cells run and are logged as unsupported); local development
runs Python 3.15 / Django 6.1.

State: scaffold (Task 1). `crud_views_adminlte/page.html` is a placeholder; `ready()` is empty. Design and plan:
`superpowers/specs/` and `superpowers/plans/`.

`../../django-crud-views` and `../../django-crud-views-extensions` are editable path sources (`[tool.uv.sources]`) and
read-only for this repo: gaps are worked around here and logged in `superpowers/notes/upstream-tracker.md`. nox installs
django-crud-views from GitHub at the commit in `PIN` (`noxfile.py`) until 1.0.0rc1 is on PyPI; the declared floor stays
lower and `scripts/check_release_floor.py` guards the publish step.

## Commands

```shell
unset VIRTUAL_ENV   # before every uv / uvx command, if the parent environment sets one
uv sync --extra examples --extra test --extra dev
# Always run test suites on all cores: pytest -n auto. Single-core only for one test or a -k selection.
uv run pytest -n auto tests/crud_views_adminlte --ds tests.crud_views_adminlte.settings
uv run ruff format . && uv run ruff check .
uvx nox            # tests, examples, package, docs matrix (Taskfile: task test:matrix)
```

`task` (Taskfile.yaml) drives the demo (`example/`, not created yet).

## Host setup (adminlte-django)

See `tests/crud_views_adminlte/settings.py`: `django_components` before `django_adminlte4` in `INSTALLED_APPS`,
`APP_DIRS=False` with explicit loaders (filesystem, app_directories, `django_components.template_loader.Loader`), the
`component_tags` builtin, the `adminlte` context processor, `COMPONENTS`, `STATICFILES_FINDERS` with
`ComponentsFileSystemFinder`, `ADMINLTE["assets_mode"] = "static"`, `CRUD_VIEWS_EXTENDS = "crud_views_adminlte/page.html"`,
`CRISPY_TEMPLATE_PACK = "bootstrap5"`. The theme app is listed before `crud_views`.

## Conventions

- No override of `adminlte/master.html`; an `adminlte/partials/*` override only as a logged last resort. No
  monkeypatching of crud_views or adminlte-django.
- **Upstream tracker rule:** every override, theme CSS rule or workaround gets an entry in
  `superpowers/notes/upstream-tracker.md` in the same commit and a `# tracker <ID>` / `{# tracker <ID> #}` comment at the
  workaround. IDs `C<n>` (django-crud-views), `A<n>` (adminlte-django).
- App code in `example/` never imports `crud_views_adminlte`.
- Demo: brand "Acme Roasters", primary sienna `#a0522d`; accounts `alex` / `sam` / `kim` (password `demo`), `admin`/`admin`
  from the Taskfile.
- Design specs, plans and notes live in `superpowers/{specs,plans,notes}/`; maintainer notes in `dev/` (not published).
- Ruff, line length 120; run `uv run ruff format . && uv run ruff check .` before committing.
