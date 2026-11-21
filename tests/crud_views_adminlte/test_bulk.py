"""Bulk selection (django-crud-views #392) under the theme: toolbar and checkboxes with the theme's bulk:* classes,
the review page in the page shell, result messages through the host's partial."""

import lxml.html
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from crud_views_adminlte.buttons import ADMINLTE_BUTTON_CLASSES
from tests.crud_views_adminlte.testapp.models import Author

pytestmark = pytest.mark.django_db

HOST_ALERT = ".adminlte-messages .alert"  # adminlte/partials/messages.html


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
        Author.objects.create(name="Anonymous", country=""),
    ]


def page(response):
    assert response.status_code == 200
    return lxml.html.fromstring(response.content.decode())


def text(element):
    return " ".join(element.text_content().split())


def css(key):
    """The theme's bulk:<key> classes as a CSS class selector."""
    return "".join(f".{c}" for c in ADMINLTE_BUTTON_CLASSES[f"bulk:{key}"].split())


def test_bulk_toolbar(admin_client, authors):
    doc = page(admin_client.get(reverse("bulk_author-list")))
    (main,) = doc.cssselect("main.app-main")
    (toolbar,) = main.cssselect(f"form[data-cv-bulk]{css('toolbar')}")
    assert toolbar.get("method") == "post"
    form_id = toolbar.get("id")
    # select-all and count, hidden until bulk.js reveals them
    (enhanced,) = toolbar.cssselect("[data-cv-bulk-enhanced][hidden]")
    (controls,) = enhanced.cssselect(css("controls"))
    (select_all,) = controls.cssselect(f"label{css('select-all')} input[type=checkbox][data-cv-bulk-all]")
    assert select_all.get("class") == ADMINLTE_BUTTON_CLASSES["bulk:checkbox"]
    assert controls.cssselect("[data-cv-bulk-count]")
    # one submit button per action, Bootstrap-styled, with icon and label (bulk label mode "both")
    (actions,) = toolbar.cssselect(css("actions"))
    buttons = actions.cssselect("button[data-cv-bulk-action]")
    assert [b.get("data-cv-bulk-action") for b in buttons] == ["clear_country", "set_country"]
    for button in buttons:
        assert "btn" in button.get("class").split()
        assert button.get("formaction")
        assert button.cssselect("i.bi")
    assert text(buttons[0]) == "Clear country"
    # per-row checkboxes in the first column, bound to the toolbar form
    rows = main.cssselect("table tbody tr")
    assert len(rows) == 3
    for row in rows:
        (box,) = row.cssselect("td:first-child input[type=checkbox][data-cv-bulk-item]")
        assert box.get("class") == ADMINLTE_BUTTON_CLASSES["bulk:checkbox"]
        assert box.get("form") == form_id
        assert box.get("name") == "cv_bulk_ids"
    # the toolbar sits above the table, outside its wrapper
    assert not toolbar.xpath("ancestor::*[contains(@class, 'table-container')]")
    # bulk.js is loaded by the page's {% cv_js %}
    assert any("crud_views/js/bulk.js" in (s.get("src") or "") for s in doc.cssselect("script"))


def test_bulk_card_view(admin_client, authors):
    doc = page(admin_client.get(reverse("bulk_author-card")))
    (main,) = doc.cssselect("main.app-main")
    (toolbar,) = main.cssselect(f"form[data-cv-bulk]{css('toolbar')}")
    assert toolbar.cssselect("[data-cv-bulk-all]")
    cells = main.cssselect(css("card-cell"))
    assert len(cells) == 3
    for cell in cells:
        (box,) = cell.cssselect("input[type=checkbox][data-cv-bulk-item]")
        assert box.get("class") == ADMINLTE_BUTTON_CLASSES["bulk:card-select"]
        assert box.get("form") == toolbar.get("id")
        assert cell.cssselect(".card")  # the card itself, next to its checkbox


def review(client, action, ids):
    url = reverse(f"bulk_author-{action}")
    return client.post(url, {"cv_bulk_stage": "review", "cv_bulk_ids": [str(pk) for pk in ids]})


def test_bulk_form_page_renders(admin_client, authors):
    doc = page(review(admin_client, "clear_country", [a.pk for a in authors]))
    (main,) = doc.cssselect("main.app-main")
    # in the theme's page: the full action label as the page heading
    (header,) = doc.cssselect(".app-content-header")
    assert "Clear the country of the selected authors" in text(header)
    (form,) = main.cssselect("form.cv-form")
    assert form.cssselect("input[type=hidden][name=cv_bulk_stage][value=execute]")
    assert len(form.cssselect("input[type=hidden][name=cv_bulk_ids]")) == 2
    assert len(form.cssselect("input[type=hidden][name=cv_bulk_blocked_ids]")) == 1
    # blocked: a Bootstrap warning alert with the name and the reason
    (blocked,) = form.cssselect(".alert.alert-warning")
    assert "1 record will be skipped" in text(blocked)
    assert "Anonymous: No country to clear." in text(blocked)
    # eligible: count and names
    assert "To process: 2" in text(form)
    assert {text(li) for li in form.xpath(".//ul[not(ancestor::div[contains(@class,'alert')])]/li")} == {
        "Ursula Le Guin",
        "Stanisław Lem",
    }
    assert form.cssselect("button[type=submit].btn.btn-primary")


def test_bulk_form_page_all_blocked(admin_client, authors):
    doc = page(review(admin_client, "clear_country", [authors[2].pk]))
    (form,) = doc.cssselect("main.app-main form.cv-form")
    assert "None of the selected records can be processed." in text(form)
    assert not form.cssselect("button[type=submit].btn-primary")  # no execution button, only the way back


def test_bulk_form_page_with_input(admin_client, authors):
    doc = page(review(admin_client, "set_country", [authors[0].pk]))
    (form,) = doc.cssselect("main.app-main form.cv-form")
    assert form.cssselect("input[name=country].form-control")


def test_bulk_result_message_through_host(admin_client, authors):
    url = reverse("bulk_author-set_country")
    data = {"cv_bulk_stage": "execute", "cv_bulk_ids": [str(a.pk) for a in authors[:2]], "country": "XX"}
    response = admin_client.post(url, data, follow=True)
    assert response.redirect_chain[-1][0].startswith(reverse("bulk_author-list"))
    doc = page(response)
    alerts = doc.cssselect(HOST_ALERT)
    assert [text(a) for a in alerts if "Country set" in text(a)] == ["Country set for 2 authors."]
    (alert,) = alerts
    assert "alert-success" in alert.get("class").split()
    assert not doc.cssselect("[data-cv-alert-dismiss]")  # crud_views' own message markup is not rendered as well
    assert Author.objects.filter(country="XX").count() == 2
    # shown once: the next page has no message left
    assert not page(admin_client.get(reverse("bulk_author-list"))).cssselect(HOST_ALERT)


def test_bulk_default_message_through_host(admin_client, authors):
    url = reverse("bulk_author-clear_country")
    data = {"cv_bulk_stage": "execute", "cv_bulk_ids": [str(authors[0].pk)]}
    doc = page(admin_client.post(url, data, follow=True))
    assert [text(a) for a in doc.cssselect(HOST_ALERT)] == ["1 record processed."]


def test_bulk_empty_selection_warning_through_host(admin_client, authors):
    url = reverse("bulk_author-clear_country")
    doc = page(admin_client.post(url, {"cv_bulk_stage": "review"}, follow=True))
    (alert,) = doc.cssselect(HOST_ALERT)
    assert "alert-warning" in alert.get("class").split()
