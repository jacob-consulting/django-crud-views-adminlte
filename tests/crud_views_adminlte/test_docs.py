"""The settings block of docs/installation.md must stay the setup the theme's tests run under."""

import re
from pathlib import Path

from django.conf import settings

DOCS = Path(__file__).resolve().parents[2] / "docs" / "installation.md"

# Settings the docs block states in full; the rest of a settings module (database, ...) is the host project's.
SAME_AS_TEST_SETTINGS = [
    "COMPONENTS",
    "TEMPLATES",
    "STATICFILES_FINDERS",
    "SILENCED_SYSTEM_CHECKS",
    "CRISPY_ALLOWED_TEMPLATE_PACKS",
    "CRISPY_TEMPLATE_PACK",
    "CRUD_VIEWS_EXTENDS",
    "CRUD_VIEWS_BREADCRUMB_PREFIX",
    "DJANGO_TABLES2_TEMPLATE",
]


def docs_settings() -> dict:
    blocks = re.findall(r"```python\n(.*?)```", DOCS.read_text(), flags=re.DOTALL)
    (block,) = [b for b in blocks if b.startswith("# settings.py")]
    namespace: dict = {}
    exec(compile(block, str(DOCS), "exec"), namespace)
    return namespace


def test_docs_settings_snippet():
    snippet = docs_settings()
    for key in SAME_AS_TEST_SETTINGS:
        assert snippet[key] == getattr(settings, key), key

    # The apps the docs list, in the order they matter, are those of the test settings (which add its own test app).
    docs_apps = list(snippet["INSTALLED_APPS"])
    test_apps = [app for app in settings.INSTALLED_APPS if app in docs_apps or not app.startswith("tests.")]
    assert [app for app in test_apps if app in docs_apps] == [app for app in docs_apps if app in test_apps]
    for app in settings.INSTALLED_APPS:
        if not app.startswith("tests."):
            assert app in docs_apps, app

    adminlte = snippet["ADMINLTE"]
    for key in ("assets_mode", "sidebar_docs_url", "menu", "filters"):
        assert adminlte[key] == settings.ADMINLTE[key], key
