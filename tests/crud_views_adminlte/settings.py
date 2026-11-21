from pathlib import Path

from django_adminlte4.conf import DEFAULT_FILTERS

from crud_views_adminlte.menu import VIEWSET_FILTERS

BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY = "test-only-not-secret"
ROOT_URLCONF = "tests.crud_views_adminlte.urls"
ALLOWED_HOSTS = ["testserver"]

# adminlte-django's installation.md: django_components first, then django_adminlte4 (before django.contrib.admin if the
# admin is installed; the test project does not install it).
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django_components",
    "django_adminlte4",
    "crispy_forms",
    "crispy_bootstrap5",
    "django_tables2",
    "django_filters",
    # The theme overrides crud_views templates, so it must come before crud_views.
    "crud_views_adminlte",
    "crud_views.apps.CrudViewsConfig",
    "crud_views_object_detail",
    "tests.crud_views_adminlte.testapp",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
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

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

STATIC_URL = "static/"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard:index"
LOGOUT_REDIRECT_URL = "login"

ADMINLTE = {
    "assets_mode": "static",
    "sidebar_docs_url": "",
    "menu": [
        {"text": "Dashboard", "route": "dashboard:index", "icon": "bi bi-speedometer2"},
        {"viewset": "author", "text": "Authors"},
    ],
    # The theme's ViewSet filters before the host's (tracker A2; check crud_views_adminlte.E013).
    "filters": [*VIEWSET_FILTERS, *DEFAULT_FILTERS],
}

# tracker A11: the host's menu check warns about every key it does not know, including the theme's "viewset" / "view";
# crud_views_adminlte.E010-E015 check those entries instead.
SILENCED_SYSTEM_CHECKS = ["adminlte.W003"]

CRISPY_ALLOWED_TEMPLATE_PACKS = ("bootstrap5",)
CRISPY_TEMPLATE_PACK = "bootstrap5"
CRUD_VIEWS_EXTENDS = "crud_views_adminlte/page.html"
# The theme replaces the host's auto-derived breadcrumb on crud_views pages, so Home comes from here (tracker A8).
CRUD_VIEWS_BREADCRUMB_PREFIX = [{"title": "Home", "url_name": "dashboard:index"}]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
