"""What CrudViewsAdminlteConfig.ready() registers: button classes, icons, label modes, assets, the app-order check."""

from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from crud_views.lib.assets import get_registered
from crud_views.lib.button_classes import DEFAULT_BUTTON_CLASSES, get_button_classes
from crud_views.lib.icons import DEFAULT_ICONS, get_icons
from crud_views.lib.icons import render_icon as cv_render_icon
from crud_views.lib.view.label_mode import default_label_mode
from django.apps import apps
from django.core.checks import Error, run_checks

import crud_views_adminlte
from crud_views_adminlte.buttons import ADMINLTE_BUTTON_CLASSES
from crud_views_adminlte.checks import check_app_order
from crud_views_adminlte.icons import ADMINLTE_ICONS

STATIC = Path(crud_views_adminlte.__file__).parent / "static"


def test_button_keys_cover_upstream():
    assert set(DEFAULT_BUTTON_CLASSES) - set(ADMINLTE_BUTTON_CLASSES) == set()


def test_button_classes_registered():
    classes = get_button_classes()
    assert classes["list:primary"] == ADMINLTE_BUTTON_CLASSES["list:primary"]
    for key, value in ADMINLTE_BUTTON_CLASSES.items():
        if not key.startswith("workflow:"):
            assert classes[key] == value, key


def test_no_non_bootstrap_button_classes():
    for key, value in ADMINLTE_BUTTON_CLASSES.items():
        classes = (value or "").split()
        assert not {"btn-xs", "btn-ghost-primary", "btn-icon", "btn-list"} & set(classes), key
        assert not any(c.startswith("cv-coreui-") or c.endswith("-lt") for c in classes), key


def test_workflow_keys_only_with_workflow_app():
    registered = {k for k in get_button_classes() if k.startswith("workflow:")}
    own = {k for k in ADMINLTE_BUTTON_CLASSES if k.startswith("workflow:")}
    assert own
    if apps.is_installed("crud_views_workflow"):
        assert own <= registered
    else:
        assert not own & registered


def test_icons_registered():
    icons = get_icons()
    assert set(DEFAULT_ICONS) - set(ADMINLTE_ICONS) == set()
    for key in DEFAULT_ICONS:
        assert icons[key].startswith("bi:"), key
        assert icons[key] == ADMINLTE_ICONS[key]


def test_icons_render_with_builtin_bootstrap_icons_font():
    html = str(cv_render_icon("update"))
    assert "bi bi-pencil-square" in html


def test_label_mode_defaults():
    assert default_label_mode("form") == "both"
    assert default_label_mode("bulk") == "both"


def test_assets_registered():
    bundle = {b.key: b for b in get_registered()}["crud_views_adminlte"]
    assert [a.path for a in bundle.css] == ["crud_views_adminlte/crud_views_adminlte.css"]
    assert not bundle.js
    assert (STATIC / bundle.css[0].path).is_file()


def test_app_order_check():
    # override_settings(INSTALLED_APPS=...) would re-run every ready() and fail on the duplicate asset bundle, so the
    # app list is mocked.
    names = ["django_adminlte4", "crud_views", "crud_views_adminlte", "crud_views_object_detail"]
    with mock.patch(
        "crud_views_adminlte.checks.apps.get_app_configs", return_value=[SimpleNamespace(name=n) for n in names]
    ):
        messages = check_app_order()
    assert len(messages) == 1
    assert isinstance(messages[0], Error)
    assert messages[0].id == "crud_views_adminlte.E001"
    assert "'crud_views'" in messages[0].msg


def test_app_order_check_passes_and_is_registered():
    assert check_app_order() == []
    assert [m for m in run_checks() if m.id == "crud_views_adminlte.E001"] == []
