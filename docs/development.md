# Development

## Layout of the repository

| Path | What |
|---|---|
| `src/crud_views_adminlte/` | the theme: app config, templates, menu filters, checks, button classes, icons, one stylesheet |
| `tests/crud_views_adminlte/` | the theme's tests and their settings, a test app with ViewSets |
| `example/` | the Acme Roasters demo project and its tests |
| `docs/` | this documentation |
| `dev/` | maintainer notes, not published |
| `superpowers/` | design specs, plans and the upstream tracker (`superpowers/notes/upstream-tracker.md`; maintainer notes, not on this site) |
| `scripts/` | `check_dist.py`, `check_release_floor.py` |

## Local setup

Local development installs django-crud-views and django-crud-views-extensions from sibling checkouts at `../../`
(`[tool.uv.sources]` in `pyproject.toml`):

```shell
git clone https://github.com/jacob-consulting/django-crud-views.git
git clone https://github.com/jacob-consulting/django-crud-views-extensions.git
git clone https://github.com/jacob-consulting/django-crud-views-adminlte.git
cd django-crud-views-adminlte
task up      # install, migrate, superuser admin/admin, seed, runserver
```

Without [Task](https://taskfile.dev):

```shell
uv sync --extra examples --extra test --extra dev
uv run python example/manage.py migrate
uv run python example/manage.py cv_manage_group
uv run python example/manage.py seed_demo            # accounts alex, sam, kim (password demo)
uv run python example/manage.py seed_demo_showcase   # not idempotent: run once
uv run python example/manage.py runserver
```

Run `unset VIRTUAL_ENV` before `uv` commands if your shell sets one.

## Tests

```shell
task test          # theme suite, the demo's tests and the system check
task test:matrix   # the nox matrix
uv run pytest -n auto tests/crud_views_adminlte --ds tests.crud_views_adminlte.settings
uv run ruff format . && uv run ruff check .
```

Run suites on all cores (`pytest -n auto`). The nox sessions (`noxfile.py`) build and install the distribution, so a
packaging mistake fails the tests:

- `tests-<python>(django='<version>')`: the theme suite, with coverage;
- `examples-<python>(django='<version>')`: the demo's tests and its system check;
- `package`: builds wheel and sdist and runs `scripts/check_dist.py`;
- `docs`: `mkdocs build --strict` with the hashed `docs/requirements.txt`.

```shell
uvx nox -s docs    # the documentation, strict
```

The matrix is Python 3.12-3.15 x Django 6.0, 6.1. Cells outside the declared support (Django 6.0 on Python 3.15;
adminlte-django on Python 3.15) run and are logged as unsupported, never dropped. Until django-crud-views 1.0.0rc1 is
on PyPI, nox installs it from a pinned GitHub commit (`PIN` in `noxfile.py`).

To regenerate the docs requirements after editing `docs/requirements.in`, see the command at its top.

## Conventions

- Every override, theme CSS rule or workaround gets an entry in the upstream tracker in the same commit, and a
  `tracker <ID>` comment at the workaround.
- No override of `adminlte/master.html`; an `adminlte/partials/*` override only as a logged last resort. No
  monkeypatching of crud_views or adminlte-django.
- App code in `example/` never imports `crud_views_adminlte`.
- The docs' settings block (`docs/installation.md`) is tested; change it and the test settings together.

## Releasing

1. Once django-crud-views 1.0.0rc1 is on PyPI: remove `CRUD_VIEWS` from `noxfile.py`, raise the floor in
   `pyproject.toml`. `scripts/check_release_floor.py` refuses a release while the floor is lower.
2. Update `CHANGELOG.md`, tag `v<version>`.

CI workflows, Read the Docs and a hosted demo are not set up yet.
