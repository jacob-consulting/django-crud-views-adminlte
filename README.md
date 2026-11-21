# django-crud-views-adminlte

Current version: 0.1.0

An [AdminLTE](https://adminlte.io) 4 theme for [django-crud-views](https://github.com/jacob-consulting/django-crud-views),
built on the page shell of [adminlte-django](https://pypi.org/project/adminlte-django/) (import `django_adminlte4`; not
the unrelated `django-adminlte4` package). This distribution contains one Django app, `crud_views_adminlte`, and no shell
of its own.

Python 3.12-3.15, Django 6.0 and 6.1. Work in progress: the scaffold only, no theme templates yet and not released.

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
uvx nox   # the matrix, against the built package and the pinned django-crud-views commit
```

Everything the theme needs beyond upstream hooks is listed in
[`superpowers/notes/upstream-tracker.md`](superpowers/notes/upstream-tracker.md).
