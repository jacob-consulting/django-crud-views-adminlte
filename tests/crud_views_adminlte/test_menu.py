"""ViewSet entries in ADMINLTE["menu"], built through the host's real context processor and filter pipeline."""

import os
import subprocess
import sys

import lxml.html
import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Permission
from django.template.loader import render_to_string
from django.test import RequestFactory, override_settings
from django.urls import reverse
from django_adminlte4.conf import DEFAULT_FILTERS
from django_adminlte4.context_processors import adminlte

from crud_views_adminlte.checks import check_menu
from crud_views_adminlte.menu import VIEWSET_FILTERS
from tests.crud_views_adminlte.testapp.models import Author

pytestmark = pytest.mark.django_db

FILTERS = [*VIEWSET_FILTERS, *DEFAULT_FILTERS]
DASHBOARD = {"text": "Dashboard", "route": "dashboard:index", "icon": "bi bi-speedometer2"}


def adminlte_settings(menu, filters=FILTERS):
    return override_settings(
        ADMINLTE={"assets_mode": "static", "sidebar_docs_url": "", "menu": menu, "filters": filters}
    )


def sidebar(user, path="/dashboard/"):
    """The sidebar menu as the host's context processor builds it for a request at ``path``."""
    request = RequestFactory().get(path)
    request.user = user
    return list(adminlte(request)["adminlte_menu_sidebar"])


def by_text(items):
    return {item["text"]: item for item in items}


def make_user(*codenames):
    username = "-".join(codenames) or "nobody"
    user = get_user_model().objects.create_user(username, password="demo")
    user.user_permissions.set(Permission.objects.filter(codename__in=codenames))
    return get_user_model().objects.get(pk=user.pk)  # fresh instance: no stale permission cache


@pytest.fixture
def viewer():
    return make_user("view_author")


@pytest.fixture
def editor():
    return make_user("view_author", "add_author")


def test_href_resolved(viewer):
    with adminlte_settings([DASHBOARD, {"viewset": "author", "text": "Authors"}]):
        items = by_text(sidebar(viewer))
    assert items["Authors"]["href"] == reverse("author-list")
    assert items["Dashboard"]["href"] == reverse("dashboard:index")  # host items untouched


def test_view_key(editor):
    with adminlte_settings([{"viewset": "author", "view": "create", "text": "New author"}]):
        (item,) = sidebar(editor)
    assert item["href"] == reverse("author-create")


def test_icon_from_viewset_and_entry_wins(viewer):
    menu = [
        {"viewset": "author", "text": "Authors"},
        {"viewset": "author", "text": "Writers", "icon": "bi bi-pen"},
    ]
    with adminlte_settings(menu):
        items = by_text(sidebar(viewer))
    assert items["Authors"]["icon"] == "bi bi-person-badge"  # ViewSet(icon_header="bi:person-badge")
    assert items["Writers"]["icon"] == "bi bi-pen"


def test_hidden_without_permission():
    user = make_user()
    menu = [DASHBOARD, {"viewset": "author", "text": "Authors"}]
    with adminlte_settings(menu):
        assert [item["text"] for item in sidebar(user)] == ["Dashboard"]


def test_shown_with_permission(viewer):
    menu = [{"viewset": "author", "text": "Authors"}, {"viewset": "author", "view": "create", "text": "New author"}]
    with adminlte_settings(menu):
        assert [item["text"] for item in sidebar(viewer)] == ["Authors"]  # view_author, no add_author


def test_anonymous_hides_entries():
    """Review Focus 1: login / error pages render the menu for AnonymousUser."""
    menu = [DASHBOARD, {"text": "Library", "submenu": [{"viewset": "author", "text": "Authors"}]}]
    with adminlte_settings(menu):
        assert [item["text"] for item in sidebar(AnonymousUser())] == ["Dashboard"]


def test_host_page_renders_for_anonymous():
    """An error page extending the host shell renders the sidebar for AnonymousUser (Review Focus 1)."""
    request = RequestFactory().get("/missing/")
    request.user = AnonymousUser()
    with adminlte_settings([DASHBOARD, {"viewset": "author", "text": "Authors"}]):
        html = render_to_string("adminlte/page.html", request=request)
    (menu,) = lxml.html.fromstring(html).cssselect(".sidebar-menu")
    assert [a.get("href") for a in menu.cssselect("a.nav-link")] == [reverse("dashboard:index")]


def test_active_on_child_pages(viewer):
    author = Author.objects.create(name="Ursula Le Guin")
    menu = [DASHBOARD, {"viewset": "author", "text": "Authors"}]
    with adminlte_settings(menu):
        items = by_text(sidebar(viewer, reverse("book-list", kwargs={"author_pk": author.pk})))
        assert items["Authors"]["active"] is True
        assert items["Dashboard"]["active"] is False
        assert by_text(sidebar(viewer, reverse("author-detail", kwargs={"pk": author.pk})))["Authors"]["active"]
        assert not by_text(sidebar(viewer, "/dashboard/"))["Authors"]["active"]


def test_submenu_parent_dropped_when_all_children_hidden(viewer):
    library = {
        "text": "Library",
        "icon": "bi bi-book",
        "submenu": [{"viewset": "author", "text": "Authors"}, {"viewset": "author", "view": "create", "text": "New"}],
    }
    with adminlte_settings([DASHBOARD, library]):
        assert [item["text"] for item in sidebar(make_user())] == ["Dashboard"]
        (parent,) = [item for item in sidebar(viewer) if item["text"] == "Library"]
        assert [child["text"] for child in parent["submenu"]] == ["Authors"]


def test_sidebar_rendered_on_crud_page(viewer, client):
    client.force_login(viewer)
    with adminlte_settings([DASHBOARD, {"viewset": "author", "text": "Authors"}]):
        response = client.get(reverse("author-list"))
    assert response.status_code == 200
    doc = lxml.html.fromstring(response.content.decode())
    (link,) = doc.cssselect(f'.sidebar-menu a.nav-link[href="{reverse("author-list")}"]')
    assert "active" in link.classes
    assert link.cssselect("i.nav-icon.bi.bi-person-badge")


@pytest.mark.parametrize(
    ("entry", "filters", "error_id"),
    [
        ({"viewset": "nope", "text": "Nope"}, FILTERS, "crud_views_adminlte.E010"),
        ({"viewset": "book", "text": "Books"}, FILTERS, "crud_views_adminlte.E011"),  # Review Focus 2
        ({"viewset": "author", "view": "nope", "text": "Nope"}, FILTERS, "crud_views_adminlte.E012"),
        ({"viewset": "author", "text": "Authors"}, DEFAULT_FILTERS, "crud_views_adminlte.E013"),  # Review Focus 3
        ({"viewset": "author", "text": "Authors"}, [*DEFAULT_FILTERS, *VIEWSET_FILTERS], "crud_views_adminlte.E013"),
        ({"viewset": "author", "text": "Authors"}, [VIEWSET_FILTERS[0], *DEFAULT_FILTERS], "crud_views_adminlte.E013"),
        ({"viewset": "author"}, FILTERS, "crud_views_adminlte.E014"),
        ({"viewset": "author", "view": "detail", "text": "Detail"}, FILTERS, "crud_views_adminlte.E015"),
    ],
)
def test_checks(entry, filters, error_id):
    with adminlte_settings([DASHBOARD, {"text": "Library", "submenu": [entry]}], filters):
        assert [error.id for error in check_menu()] == [error_id]


def test_checks_clean():
    with adminlte_settings([DASHBOARD, {"viewset": "author", "text": "Authors"}]):
        assert check_menu() == []
    with adminlte_settings([DASHBOARD], DEFAULT_FILTERS):  # no viewset entries: host defaults are fine
        assert check_menu() == []


def test_test_settings_pass_checks():
    assert check_menu() == []


def test_cache_survives_settings_change(viewer):
    with adminlte_settings([{"viewset": "author", "text": "Authors"}]):
        first = sidebar(viewer)
    with adminlte_settings([{"viewset": "author", "view": "create", "text": "New author"}]):
        second = sidebar(make_superuser())
    assert [(item["text"], item["href"]) for item in first] == [("Authors", reverse("author-list"))]
    assert [(item["text"], item["href"]) for item in second] == [("New author", reverse("author-create"))]


def make_superuser():
    return get_user_model().objects.create_superuser("admin", "admin@example.com", "admin")


FRESH_PROCESS = """
import django
django.setup()
from django_adminlte4.menu.builder import MenuBuilder
from crud_views_adminlte.menu import ViewSetHrefFilter
print(MenuBuilder([{"viewset": "author", "text": "Authors"}], [ViewSetHrefFilter]).menu())
"""


def test_menu_built_before_first_url_resolution():
    # tracker C5: in a fresh process nothing has imported the views module (which registers the ViewSets) yet
    env = {**os.environ, "DJANGO_SETTINGS_MODULE": "tests.crud_views_adminlte.settings"}
    result = subprocess.run([sys.executable, "-c", FRESH_PROCESS], capture_output=True, text=True, env=env, check=True)
    assert "'href': '/author/'" in result.stdout


@pytest.mark.parametrize("template", ["{nope}", "{0}", "{", "{name.nope}"])
def test_icon_class_broken_library_gives_no_icon(template):
    from crud_views_adminlte.menu import icon_class

    with override_settings(CRUD_VIEWS_ICON_LIBRARIES={"xx": {"renderer": "font", "class": template}}):
        assert icon_class("xx:rocket") is None
    assert icon_class("bi:rocket") == "bi bi-rocket"
