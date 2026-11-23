# django-crud-views-adminlte

[![Tests](https://github.com/jacob-consulting/django-crud-views-adminlte/actions/workflows/tests.yml/badge.svg)](https://github.com/jacob-consulting/django-crud-views-adminlte/actions/workflows/tests.yml)
[![Lint](https://github.com/jacob-consulting/django-crud-views-adminlte/actions/workflows/lint.yml/badge.svg)](https://github.com/jacob-consulting/django-crud-views-adminlte/actions/workflows/lint.yml)
[![Coverage](https://codecov.io/gh/jacob-consulting/django-crud-views-adminlte/branch/main/graph/badge.svg)](https://codecov.io/gh/jacob-consulting/django-crud-views-adminlte)
[![Docs](https://readthedocs.org/projects/django-crud-views-adminlte/badge/?version=latest)](https://django-crud-views-adminlte.readthedocs.io/en/latest/)

Current version: 0.1.0

An [AdminLTE](https://adminlte.io) 4 theme for [django-crud-views](https://github.com/jacob-consulting/django-crud-views),
built on the page shell of [adminlte-django](https://pypi.org/project/adminlte-django/) (import `django_adminlte4`; not
the unrelated `django-adminlte4` package). This distribution contains one Django app, `crud_views_adminlte`, and no shell
of its own.

The theme extends the host's `adminlte/page.html`, shadows a few django-crud-views templates, registers Bootstrap Icons
and AdminLTE button classes through upstream's hooks, and adds sidebar menu entries that link a ViewSet
(`{"viewset": "author", "text": "Authors"}`), shown only to users who may open it. Your ViewSets and views need no
changes.

Python 3.12-3.15, Django 6.0 and 6.1, `adminlte-django >=0.3.3,<0.4`. Not released yet.

## Install

```shell
pip install django-crud-views-adminlte
```

Then follow the [installation guide](docs/installation.md): the complete settings block (the host's setup, the theme
before `crud_views` in `INSTALLED_APPS`, `CRUD_VIEWS_EXTENDS`, the menu filters
`[*VIEWSET_FILTERS, *DEFAULT_FILTERS]`, `DJANGO_TABLES2_TEMPLATE`, `SILENCED_SYSTEM_CHECKS = ["adminlte.W003"]`).

## Demo

Acme Roasters, a roastery back office (`example/`), runs locally:

```shell
task up      # install, migrate, superuser admin/admin, seed the demo data, runserver on http://127.0.0.1:8000/
```

Accounts: `alex`, `sam`, `kim` (password `demo`), and `admin` / `admin` (superuser from the Taskfile).

## Documentation

[`docs/`](docs/index.md): installation, menu, theme internals, demo, development (mkdocs; `uvx nox -s docs`).

- Published: https://django-crud-views-adminlte.readthedocs.io/
- Source and issues: https://github.com/jacob-consulting/django-crud-views-adminlte


## Development

Next to checkouts of [django-crud-views](https://github.com/jacob-consulting/django-crud-views) and
[django-crud-views-extensions](https://github.com/jacob-consulting/django-crud-views-extensions) at `../../` (local
development installs both from there):

```shell
unset VIRTUAL_ENV
uv sync --extra examples --extra test --extra dev
uv run pytest -n auto tests/crud_views_adminlte --ds tests.crud_views_adminlte.settings
uv run ruff format . && uv run ruff check .
uvx nox   # the matrix, against the built package and django-crud-views main
```

Everything the theme needs beyond upstream hooks is listed in
[`superpowers/notes/upstream-tracker.md`](superpowers/notes/upstream-tracker.md).
