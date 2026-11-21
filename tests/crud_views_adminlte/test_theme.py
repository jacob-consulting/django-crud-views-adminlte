"""crud_views_adminlte/page.html rendered: crud_views pages inside the adminlte-django page shell."""

import lxml.html
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from tests.crud_views_adminlte.testapp.models import Author, Book

pytestmark = pytest.mark.django_db

HEADER = ".app-content-header"
HOST_ALERT = ".adminlte-messages .alert"  # adminlte/partials/messages.html


@pytest.fixture
def admin_client(client):
    user = get_user_model().objects.create_superuser("admin", "admin@example.com", "admin")
    client.force_login(user)
    return client


@pytest.fixture
def author():
    author = Author.objects.create(name="Ursula Le Guin", country="US")
    Book.objects.create(author=author, title="The Dispossessed", year=1974)
    return author


def page(response):
    assert response.status_code == 200
    return lxml.html.fromstring(response.content.decode())


def text(element):
    return " ".join(element.text_content().split())


def test_header(admin_client, author):
    doc = page(admin_client.get(reverse("author-list")))
    (header,) = doc.cssselect(HEADER)
    (heading,) = header.cssselect("h2.h3")
    assert heading.cssselect("i.bi.bi-person-badge")
    assert text(heading) == "Authors"
    assert "Everyone who writes for us." in text(header)
    assert header.cssselect(f'a[cv-key="create"][href^="{reverse("author-create")}?"]')
    assert not doc.cssselect(f"{HEADER} h3:empty")  # the host's bare page_title <h3> is not left behind


def test_page_title_uses_host_title_and_owner(admin_client, author):
    doc = page(admin_client.get(reverse("author-list")))
    assert doc.findtext(".//title").strip() == "Authors"
    doc = page(admin_client.get(reverse("book-list", kwargs={"author_pk": author.pk})))
    assert doc.findtext(".//title").strip() == "Books · Ursula Le Guin"


def test_breadcrumb_items_inside_host_ol(admin_client, author):
    url = reverse("book-detail", kwargs={"author_pk": author.pk, "pk": author.books.get().pk})
    doc = page(admin_client.get(url))
    (ol,) = doc.cssselect("ol.breadcrumb")
    assert doc.cssselect(f"{HEADER} ol.breadcrumb") == [ol]
    assert not ol.xpath(".//ol | .//nav")
    assert not ol.xpath("ancestor::nav")
    crumbs = [text(li) for li in ol.cssselect("li.breadcrumb-item")]
    assert crumbs == ["Home", "Authors", "Ursula Le Guin", "Books", "The Dispossessed"]
    assert ol.cssselect("li.breadcrumb-item.active[aria-current=page]")[-1] is ol.cssselect("li")[-1]


def test_breadcrumb_no_duplicate_home(admin_client, author):
    # CRUD_VIEWS_BREADCRUMB_PREFIX (test settings) supplies Home; the host's auto-derived Home is replaced, not added.
    for url in (reverse("author-list"), reverse("author-detail", kwargs={"pk": author.pk})):
        doc = page(admin_client.get(url))
        crumbs = [text(li) for li in doc.cssselect("ol.breadcrumb li")]
        assert crumbs.count("Home") == 1, crumbs
        (home,) = doc.cssselect("ol.breadcrumb li a")[:1]
        assert home.get("href") == reverse("dashboard:index")


def test_message_once_through_host(admin_client):
    response = admin_client.post(reverse("author-create"), {"name": "Octavia Butler", "country": "US"}, follow=True)
    doc = page(response)
    html = response.content.decode()
    assert html.count("Octavia Butler</strong>") == 1
    (alert,) = doc.cssselect(HOST_ALERT)
    assert "alert-success" in alert.get("class").split()
    assert text(alert) == "Created Author Octavia Butler"
    assert alert.cssselect("strong")  # the snippet's markup survives the host's {{ message }}
    second = admin_client.get(reverse("author-list"))
    assert "Created author" not in second.content.decode()
    assert not page(second).cssselect(HOST_ALERT)


def test_no_cv_messages_markup(admin_client):
    response = admin_client.post(reverse("author-create"), {"name": "Octavia Butler"}, follow=True)
    doc = page(response)
    assert doc.cssselect(HOST_ALERT)
    assert not doc.cssselect("[data-cv-alert-dismiss]")  # crud_views/tags/alert.html, i.e. {% cv_messages %}


def test_navbar_owner_header(admin_client, author):
    doc = page(admin_client.get(reverse("book-list", kwargs={"author_pk": author.pk})))
    (header,) = doc.cssselect(HEADER)
    (owner,) = doc.cssselect(".cv-adminlte-owner")
    assert owner.getparent().getparent() is header  # first thing in the header's container-fluid
    assert owner.getparent().index(owner) == 0
    (h1,) = doc.cssselect("h1")
    assert text(h1) == "Ursula Le Guin" and owner in h1.iterancestors()
    (nav,) = doc.cssselect('nav[aria-label="Sections for Ursula Le Guin"]')
    assert owner in nav.iterancestors()
    tabs = [text(a) for a in nav.cssselect("a.nav-link")]
    assert tabs == ["Detail", "Books"]
    (active,) = nav.cssselect("a.nav-link.active")
    assert text(active) == "Books"
    # the view's heading says the same as the active tab, so it is left out; context actions stay
    assert not header.cssselect("h2")
    assert header.cssselect('[cv-key="create"]')


def test_owner_page_keeps_heading_that_differs_from_tab(admin_client, author):
    doc = page(admin_client.get(reverse("author-detail", kwargs={"pk": author.pk})))
    (header,) = doc.cssselect(HEADER)
    assert len(doc.cssselect(".cv-adminlte-owner")) == 1
    assert [text(a) for a in header.cssselect("nav a.nav-link.active")] == ["Detail"]
    (heading,) = header.cssselect("h2.h3")
    assert text(heading) == "Author"


def test_page_without_navbar_has_no_owner_header(admin_client, author):
    doc = page(admin_client.get(reverse("author-list")))
    assert not doc.cssselect(".cv-adminlte-owner")
    assert not doc.cssselect("h1")


def test_theme_css_is_linked(admin_client):
    html = admin_client.get(reverse("author-list")).content.decode()
    assert "crud_views_adminlte/crud_views_adminlte.css" in html
    assert html.index("crud_views_adminlte/crud_views_adminlte.css") < html.index("</head>")


def test_content_and_scripts(admin_client, author):
    response = admin_client.get(reverse("author-list"))
    doc = page(response)
    (content,) = doc.cssselect(".app-content .container-fluid")
    assert content.cssselect("table")
    assert "Ursula Le Guin" in text(content)
    html = response.content.decode()
    assert "crud_views/js/" in html[html.index("</main>") :]
