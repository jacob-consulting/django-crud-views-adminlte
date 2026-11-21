"""List tables under the theme: crud_views' table template (DJANGO_TABLES2_TEMPLATE) inside the host's page shell.

The template choice and why: docs/theme_internals.md ("Tables"). The sorted-column state waits on django-crud-views
#393 (tracker C8).
"""

import lxml.html
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from tests.crud_views_adminlte.testapp.models import Author

pytestmark = pytest.mark.django_db

TABLE_TEMPLATE = "crud_views/table/bootstrap5.html"


@pytest.fixture
def admin_client(client):
    user = get_user_model().objects.create_superuser("admin", "admin@example.com", "admin")
    client.force_login(user)
    return client


@pytest.fixture
def authors():
    return [
        Author.objects.create(name="Ursula Le Guin", country="US"),
        Author.objects.create(name="Stanisław Lem", country="PL"),
    ]


def page(response):
    assert response.status_code == 200
    return lxml.html.fromstring(response.content.decode())


def test_table_template_setting(settings):
    assert settings.DJANGO_TABLES2_TEMPLATE == TABLE_TEMPLATE


@pytest.mark.parametrize("url_name", ["author-list", "bulk_author-list"])
def test_table_without_host_card(admin_client, authors, url_name):
    response = admin_client.get(reverse(url_name))
    assert TABLE_TEMPLATE in [t.name for t in response.templates]
    doc = page(response)
    (main,) = doc.cssselect("main.app-main")
    (table,) = main.cssselect("table")
    # crud_views' wrapper, once; no card around it and no card in a card (the host's tables2 template is not used)
    (wrapper,) = main.cssselect(".table-container")
    assert table.getparent() is wrapper
    assert not table.xpath("ancestor::*[contains(concat(' ', normalize-space(@class), ' '), ' card ')]")
    assert "table" in table.get("class").split()
    assert len(table.cssselect("tbody tr")) == 2


def test_sorted_column_icon(admin_client, authors):
    doc = page(admin_client.get(reverse("author-list") + "?sort=name"))
    (th,) = [th for th in doc.cssselect("thead th") if "Name" in th.text_content()]
    assert th.cssselect("i.bi")  # crud_views' table-sort-asc icon, lost under the host's tables2 template


# tracker C8: no table.thead copy on the fallback path; passes (and so fails strictly) once the pin brings #393
@pytest.mark.xfail(strict=True, raises=AssertionError, reason="waiting on django-crud-views #393")
@pytest.mark.parametrize(
    ("url_name", "param"),
    [("author-list", "sort"), ("bulk_author-list", "a-sort")],
    ids=["no-prefix", "prefix"],
)
def test_sorted_column_aria_sort(admin_client, authors, url_name, param):
    doc = page(admin_client.get(f"{reverse(url_name)}?{param}=name"))
    (th,) = [th for th in doc.cssselect("thead th") if "Name" in th.text_content()]
    assert th.get("aria-sort") == "ascending"


def test_table_container_scrolls_sideways():
    # tracker C9: crud_views' table wrapper is a bare div.table-container (no class key, not .table-responsive), so a
    # wide table pushed the page sideways at 375px; the theme lets the wrapper scroll instead
    from pathlib import Path

    import crud_views_adminlte

    css = (Path(crud_views_adminlte.__file__).parent / "static/crud_views_adminlte/crud_views_adminlte.css").read_text()
    rule = css[css.index(".table-container {") :]
    assert "overflow-x: auto;" in rule[: rule.index("}")]
    assert "position: relative;" in rule[: rule.index("}")]  # contains the visually-hidden labels
    assert "tracker C9" in css
