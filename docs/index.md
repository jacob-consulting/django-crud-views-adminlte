# Django CRUD Views AdminLTE

Current version: 0.1.0

An [AdminLTE](https://adminlte.io) 4 theme for [django-crud-views](https://django-crud-views.readthedocs.io/), built on
the page shell of [adminlte-django](https://pypi.org/project/adminlte-django/) (import `django_adminlte4`; not the
unrelated `django-adminlte4` package). The distribution `django-crud-views-adminlte` contains one Django app,
`crud_views_adminlte`, and no shell of its own: the host owns the layout, the sidebar, the footer and the sign-in page,
and the theme maps django-crud-views' pages onto the host's blocks.

The theme extends the host's `adminlte/page.html` (no override of `adminlte/master.html`), shadows a few
django-crud-views templates, registers Bootstrap Icons and AdminLTE button classes through upstream's hooks, and adds
two menu filters so the sidebar can link ViewSets. Your ViewSets and views need no changes. Everything it needs beyond
upstream's hooks is listed in the
[upstream tracker](https://github.com/jacob-consulting/django-crud-views-adminlte/blob/main/superpowers/notes/upstream-tracker.md)
(IDs `C<n>` for django-crud-views, `A<n>` for adminlte-django).

Supported: Python 3.12-3.15, Django 6.0 and 6.1, `adminlte-django >=0.3.3,<0.4`, django-crud-views >=0.30. The theme
tracks django-crud-views `main` until 1.0.0rc1 is on PyPI. adminlte-django declares Python 3.12-3.14 only (tracker
A5), so the Python 3.15 cells are run and marked unsupported.

- [Installation](installation.md): the complete settings block, in the order it matters.
- [Menu](menu.md): `viewset` entries for the sidebar, who sees them, and the system checks.
- [Theme internals](theme_internals.md): what is overridden and why, with the tracker ID of each workaround.
- [Demo](demo.md): Acme Roasters, a back office for a coffee roastery.
- [Development](development.md): repository layout, tests, the nox matrix.
