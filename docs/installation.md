# Installation

```shell
pip install django-crud-views-adminlte
```

This installs django-crud-views and adminlte-django with it. Install django-crud-views' extras as usual
(`django-crud-views[guardian]`, ...). The setup is adminlte-django's own, plus a few theme lines; every adopter inherits
the host's requirements (tracker A4).

## Settings

The complete block, for a project that has the host's pieces and the theme. Names you recognise from
adminlte-django's installation guide are the host's; the lines marked "theme" are this package's.

```python
# settings.py
from django_adminlte4.conf import DEFAULT_FILTERS

from crud_views_adminlte.menu import VIEWSET_FILTERS

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django_components",  # host: before django_adminlte4
    "django_adminlte4",  # host: before django.contrib.admin, if you use the admin
    "crispy_forms",
    "crispy_bootstrap5",
    "django_tables2",
    "django_filters",
    "crud_views_adminlte",  # theme: before crud_views and crud_views_object_detail
    "crud_views.apps.CrudViewsConfig",
    "crud_views_object_detail",  # if you use it
    # crud_views_workflow, crud_views_polymorphic, crud_views_guardian, ... as you use them
]

COMPONENTS = {"dirs": [], "app_dirs": ["components"], "autodiscover": True}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": False,  # required by django-components: explicit loaders below (adminlte.E002)
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django_adminlte4.context_processors.adminlte",
            ],
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
                "django_components.template_loader.Loader",
            ],
            "builtins": ["django_components.templatetags.component_tags"],
        },
    },
]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "django_components.finders.ComponentsFileSystemFinder",
]

ADMINLTE = {
    "assets_mode": "static",
    "sidebar_docs_url": "",
    "menu": [
        {"text": "Dashboard", "route": "dashboard:index", "icon": "bi bi-speedometer2"},
        {"viewset": "author", "text": "Authors"},  # theme: a django-crud-views ViewSet
    ],
    # theme: the ViewSet filters in front of the host's
    "filters": [*VIEWSET_FILTERS, *DEFAULT_FILTERS],
}

# theme: see "Silenced check" below
SILENCED_SYSTEM_CHECKS = ["adminlte.W003"]

CRISPY_ALLOWED_TEMPLATE_PACKS = ("bootstrap5",)
CRISPY_TEMPLATE_PACK = "bootstrap5"
CRUD_VIEWS_EXTENDS = "crud_views_adminlte/page.html"
CRUD_VIEWS_BREADCRUMB_PREFIX = [{"title": "Home", "url_name": "dashboard:index"}]
DJANGO_TABLES2_TEMPLATE = "crud_views/table/bootstrap5.html"
```

This block is exercised by the test suite (`test_docs_settings_snippet`): it is executed and compared with the settings
the theme's tests run under, so it cannot drift from what works.

The rest of a settings module (database, middleware, `STATIC_URL`, `LOGIN_URL`) is yours. Use a real `LOGIN_URL`: the
host's sign-in page and the menu's gating assume signed-in users.

### Order of `INSTALLED_APPS`

The theme shadows templates of `crud_views` and `crud_views_object_detail`, and Django's app template loader takes the
first app that has a template, so `crud_views_adminlte` must come before both. Anything the theme does not override falls
through to the stock templates. A wrong order renders stock markup and breaks silently; the system check
`crud_views_adminlte.E001` turns it into an error.

`django_components` before `django_adminlte4`, `APP_DIRS=False` with the explicit loaders, the `component_tags` builtin,
`COMPONENTS` and `ComponentsFileSystemFinder` are adminlte-django's requirements (`adminlte.E002`).

### Assets

`ADMINLTE["assets_mode"] = "static"` serves AdminLTE, Bootstrap and Bootstrap Icons from the host package's static
files rather than a CDN. The theme adds one stylesheet (`crud_views_adminlte/crud_views_adminlte.css`) through
crud_views' asset registry, loaded by `{% cv_css %}`; it adds no scripts.

### Menu filters

`"filters": [*VIEWSET_FILTERS, *DEFAULT_FILTERS]` is required as soon as the menu has a `viewset` entry. Without it the
host would render `href="#"` for every ViewSet link; `crud_views_adminlte.E013` reports a missing or misordered pair. See
[Menu](menu.md).

### Table template

`DJANGO_TABLES2_TEMPLATE = "crud_views/table/bootstrap5.html"` keeps crud_views' own table markup. The host's
`django_tables2/adminlte.html` extends tables2's base template and cannot be pointed at another one, so under it lists
lose the sort icons and the pagination markup (tracker A19). See [Theme internals](theme_internals.md#tables).

### Breadcrumb Home

`CRUD_VIEWS_BREADCRUMB_PREFIX` supplies the "Home" crumb on crud_views pages, because the host's own breadcrumb (always
`Home` linking to `/`) is not shown there (tracker A8). Point it at the same page your dashboard is.

### Silenced check

`SILENCED_SYSTEM_CHECKS = ["adminlte.W003"]` is needed because the host's menu check warns about every menu key it does
not know, including the theme's `viewset` and `view`, so `manage.py check --fail-level WARNING` would fail
(tracker A11). The cost: the check also validated the keys of your other menu entries, so with it silenced a typo such as
`"rout"` is no longer reported. `crud_views_adminlte.E010`-`E015` check the `viewset` entries only.

## System checks

```shell
python manage.py check --fail-level WARNING
```

| Id | Level | Meaning |
|---|---|---|
| `crud_views_adminlte.E001` | Error | `crud_views_adminlte` is listed after `crud_views` or `crud_views_object_detail`. |
| `crud_views_adminlte.E010`-`E015` | Error | A `viewset` menu entry or the filter list is wrong; see [Menu](menu.md#system-checks). |

## Your own page layer

To add something to every crud_views page, point `CRUD_VIEWS_EXTENDS` at your own template that extends the theme's page
(the demo adds a "Show code" panel this way):

```django
{% extends "crud_views_adminlte/page.html" %}
{% block cv_context %}{{ block.super }}<a class="btn btn-outline-secondary" href="#help">Help</a>{% endblock %}
```

The theme's page provides `title`, `extra_css`, `content_header`, `page_title`, `breadcrumb`, `cv_navbar`,
`cv_paragraph`, `cv_context`, `cv_filter`, `cv_content` and `extra_js`; `messages` stays the host's.

## Pages outside django-crud-views

Any template can use the host directly (`{% extends "adminlte/page.html" %}`). The host's own breadcrumb shows there, with
its own Home.

## Breadcrumb

!!! warning "The theme shadows `crud_views/tags/breadcrumb.html` globally"
    The theme replaces the template behind `{% cv_breadcrumb %}` with upstream's item loop without its
    `<nav><ol class="breadcrumb">` wrapper, because the host's page already owns the `<ol>` (tracker C1). That replacement
    applies everywhere in the project: `{% cv_breadcrumb %}` always renders `<li>` items only. In the theme's page that is
    what you want; if you call the tag in a template of your own, wrap it yourself. A view without crud_views' breadcrumb
    mixin gives no items, so its page shows an empty `<ol class="breadcrumb">`.
