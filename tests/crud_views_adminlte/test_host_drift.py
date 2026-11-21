"""Drift tests: what crud_views_adminlte/page.html relies on in the adminlte-django shell and in crud_views.

A failure here means an upstream release changed a template the theme extends or copies; the message names the file
and the installed version, so the theme can be adapted (and the tracker entry updated).
"""

import re
from importlib.metadata import version
from pathlib import Path

import crud_views
import django_adminlte4
import pytest
from django.contrib.messages import constants
from django.contrib.messages.storage.base import Message
from django.template.loader import get_template, render_to_string
from django.template.loader_tags import BlockNode

import crud_views_adminlte

HOST = f"adminlte-django {version('adminlte-django')}"
CRUD_VIEWS = f"django-crud-views {version('django-crud-views')}"

MASTER_BLOCKS = {"title", "extra_css", "content_header", "messages", "content", "extra_js"}
PAGE_BLOCKS = {"page_title", "breadcrumb"}
THEME_BLOCKS = {"cv_navbar", "page_title", "cv_paragraph", "cv_context", "breadcrumb", "cv_filter", "cv_content"}


def block_names(name):
    return {node.name for node in get_template(name).template.nodelist.get_nodes_by_type(BlockNode)}


def source(name):
    return Path(get_template(name).origin.name).read_text()


@pytest.mark.parametrize(
    ("name", "blocks"), [("adminlte/master.html", MASTER_BLOCKS), ("adminlte/page.html", PAGE_BLOCKS)]
)
def test_host_blocks_exist(name, blocks):
    missing = blocks - block_names(name)
    assert not missing, f"{name} ({HOST}) no longer defines blocks {sorted(missing)}"


def test_host_breadcrumb_block_sits_inside_its_ol():
    # The theme re-declares the breadcrumb block inside the same <ol class="breadcrumb"> and renders items only.
    page = source("adminlte/page.html")
    assert re.search(r'<ol class="breadcrumb[^"]*">\s*\{% block breadcrumb %\}', page), (
        f'adminlte/page.html ({HOST}): the breadcrumb block is no longer inside <ol class="breadcrumb">'
    )


def test_host_content_header_markup():
    # The theme's content_header copies the host's app-content-header / container-fluid / row frame (tracker A7).
    page = source("adminlte/page.html")
    frame = (
        r'<div class="app-content-header \{\{ adminlte.classes_content_header \}\}">\s*'
        r'<div class="container-fluid">\s*<div class="row">'
    )
    assert re.search(frame, page), f"adminlte/page.html ({HOST}): content_header frame changed"
    assert '<h3 class="mb-0">{% block page_title %}{% endblock %}</h3>' in page, (
        f"adminlte/page.html ({HOST}): page_title is no longer a bare <h3> (tracker A7 may be fixed)"
    )


def test_theme_blocks_exist():
    missing = THEME_BLOCKS - block_names("crud_views_adminlte/page.html")
    assert not missing, f"crud_views_adminlte/page.html lost blocks {sorted(missing)}"


def test_theme_page_extends_host_page_without_overriding_master():
    page = source("crud_views_adminlte/page.html")
    assert '{% extends "adminlte/page.html" %}' in page
    host = Path(django_adminlte4.__file__).resolve().parent
    for name in ("adminlte/master.html", "adminlte/page.html"):
        assert Path(get_template(name).origin.name).resolve().is_relative_to(host), f"{name} is overridden"


def test_breadcrumb_copy_tracks_upstream():
    # tracker C1: the theme's crud_views/tags/breadcrumb.html is upstream's item loop without the <nav><ol> wrapper.
    # Fails as soon as upstream edits the file: refresh the copy, or drop it once upstream renders items only.
    upstream_path = Path(crud_views.__file__).resolve().parent / "templates/crud_views/tags/breadcrumb.html"
    theme_path = Path(crud_views_adminlte.__file__).resolve().parent / "templates/crud_views/tags/breadcrumb.html"
    assert Path(get_template("crud_views/tags/breadcrumb.html").origin.name) == theme_path

    def squash(text):
        return " ".join(text.split())

    upstream = squash(upstream_path.read_text())
    wrapped = re.fullmatch(
        r'\{% if items %\} <nav aria-label="breadcrumb"> <ol class="breadcrumb"> (.*) </ol> </nav> \{% endif %\}',
        upstream,
    )
    assert wrapped, f"crud_views/tags/breadcrumb.html ({CRUD_VIEWS}) changed: refresh the theme copy (tracker C1)"
    theme = squash(re.sub(r"\{#.*?#\}", "", theme_path.read_text(), flags=re.S))
    assert theme == f"{{% if items %}} {wrapped.group(1)} {{% endif %}}"


def test_host_messages_partial_drops_extra_tags():
    # tracker A9: the theme leaves the messages block to the host, whose partial ignores a message's extra_tags
    # ({% cv_messages %} appends them to the alert's classes). Fails once the host keeps them: update the tracker.
    messages = [Message(constants.WARNING, "Careful", extra_tags="cv-sticky")]
    html = render_to_string("adminlte/partials/messages.html", {"messages": messages})
    assert "Careful" in html
    assert "cv-sticky" not in html, f"adminlte/partials/messages.html ({HOST}) now renders extra_tags (tracker A9)"


def test_host_runs_static_filters_first():
    # tracker A2: split_filters moves every per_request=False filter (HrefFilter) ahead of the per-request ones,
    # whatever the configured order, so a per-request filter cannot set href before HrefFilter does. The theme splits
    # its menu filter in two. Fails once the host honours the configured order: update the tracker.
    from django_adminlte4.menu.builder import split_filters
    from django_adminlte4.menu.filters import ActiveFilter, GateFilter, HrefFilter

    static, dynamic = split_filters([GateFilter, ActiveFilter, HrefFilter])
    assert (static, dynamic) == ([HrefFilter], [GateFilter, ActiveFilter]), f"split_filters changed ({HOST}, A2)"


def test_host_gate_keeps_emptied_parent_after_href():
    # tracker A10: in the per-request half, GateFilter only drops a parent whose submenu it emptied when the parent has
    # no url/route/href, but HrefFilter (static half, run first) has already given it href="#". ViewSetGateFilter
    # drops such parents itself. Fails once the host drops them: update the tracker.
    from django.contrib.auth.models import AnonymousUser
    from django.test import RequestFactory
    from django_adminlte4.menu.builder import MenuBuilder
    from django_adminlte4.menu.filters import GateFilter, HrefFilter

    request = RequestFactory().get("/")
    request.user = AnonymousUser()
    menu = [{"text": "Library", "submenu": [{"text": "Secret", "url": "/secret/", "can": "app.view_secret"}]}]
    prefiltered = MenuBuilder(menu, [HrefFilter]).menu()
    (parent,) = MenuBuilder(prefiltered, [GateFilter], request).menu()
    assert parent["submenu"] == [] and parent["href"] == "#", f"GateFilter now drops the emptied parent ({HOST}, A10)"


def test_host_menu_check_rejects_custom_keys():
    # tracker A11: adminlte.W003 flags any menu-item key outside its fixed MENU_ITEM_KEYS, so the theme's "viewset" /
    # "view" keys warn and the test settings silence W003. Fails once the host accepts custom filter keys.
    from django.test import override_settings
    from django_adminlte4.checks import check_menu_items

    with override_settings(ADMINLTE={"menu": [{"viewset": "author", "view": "list", "text": "Authors"}]}):
        ids = [message.id for message in check_menu_items()]
    assert ids == ["adminlte.W003", "adminlte.W003"], f"adminlte.W003 now accepts custom keys ({HOST}, A11)"
