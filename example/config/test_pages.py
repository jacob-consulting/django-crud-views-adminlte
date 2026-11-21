"""Every example page renders for the demo accounts, the breadcrumb has one Home, and the menu follows the roles."""

import re
from io import StringIO

from crud_views.lib.viewset import _REGISTRY
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.test import TestCase
from django.urls import NoReverseMatch, get_resolver, reverse

User = get_user_model()

# the views the brief asks to cover; object views take the first object, child ViewSets the parents of that object
PAGE_KEYS = ("list", "card", "detail", "create", "update")
NON_CRUD = ("dashboard:index", "theming", "dashboard:users")  # user_create is POST-only
# manage pages are not named per ViewSet in the registry's keys: the customer ViewSet's manage page stands for them
MANAGE_URL = "/customer/manage/"


def _kwargs(viewset, obj):
    """URL kwargs for an object view of ``viewset``: the parent pks (walked up from ``obj``) and ``pk``."""
    kwargs = {}
    current = obj
    for arg, attr in zip(viewset.get_parent_url_args(), viewset.get_parent_attributes(), strict=True):
        current = getattr(current, attr)
        kwargs[arg] = current.pk
    return kwargs


def page_urls():
    """(label, url) for the list, detail, create and update page of every registered ViewSet."""
    get_resolver().url_patterns  # noqa: B018 - ViewSets register when the URLconf imports their views
    urls = []
    for viewset in _REGISTRY.values():
        obj = None if viewset.is_resource else viewset.model._default_manager.first()
        for key in PAGE_KEYS:
            if not viewset.is_view_registered(key):
                continue
            view_class = viewset.get_view_class(key)
            router = viewset.get_router_name(key)
            if viewset.is_resource and (view_class.cv_object or viewset.has_parent):
                continue  # non-ORM rows carry no pk to read from the database
            if view_class.cv_object or viewset.has_parent:
                if obj is None:
                    continue
                kwargs = _kwargs(viewset, obj)
                if view_class.cv_object:
                    kwargs["pk"] = obj.pk
                urls.append((router, reverse(router, kwargs=kwargs)))
            else:
                try:
                    urls.append((router, reverse(router)))
                except NoReverseMatch:
                    # the polymorphic create takes the kind to create: the first object's
                    ctype = ContentType.objects.get_for_model(obj, for_concrete_model=False)
                    urls.append((router, reverse(router, kwargs={"polymorphic_ctype_id": ctype.pk})))
    return urls


class PagesTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", stdout=StringIO())
        call_command("seed_demo_showcase", stdout=StringIO())

    def login(self, username="alex"):
        self.assertTrue(self.client.login(username=username, password="demo"))

    def sidebar_links(self, html):
        sidebar = html[html.index('class="sidebar-wrapper"') : html.index("</aside>")]
        return re.findall(r'<a href="([^"#][^"]*)"[^>]*class="nav-link', sidebar) or re.findall(
            r'<a [^>]*class="nav-link[^"]*"[^>]*href="([^"#][^"]*)"', sidebar
        )


class EveryPageTests(PagesTestCase):
    def test_every_page_renders(self):
        self.login("alex")
        urls = page_urls() + [(name, reverse(name)) for name in NON_CRUD] + [("manage", MANAGE_URL)]
        self.assertGreater(len(urls), 40)
        failures = []
        # A TemplateSyntaxError (or any render error) surfaces as an exception from the test client. django.template
        # logs every failed variable lookup at DEBUG, also the ones `{% if %}` and `|default` expect (dozens per page),
        # and string_if_invalid breaks crud_views' own tags, so neither can be asserted: errors and status are.
        for label, url in urls:
            try:
                response = self.client.get(url)
            except Exception as exc:
                failures.append(f"{label} {url}: {type(exc).__name__}: {exc}")
                continue
            if response.status_code != 200:
                failures.append(f"{label} {url}: HTTP {response.status_code}")
        self.assertEqual(failures, [])


class BreadcrumbTests(PagesTestCase):
    def crumbs(self, html):
        ol = re.search(r'<ol class="breadcrumb[^"]*">(.*?)</ol>', html, re.S).group(1)
        return [re.sub(r"<[^>]+>|\s+", " ", li).strip() for li in re.findall(r"<li[^>]*>(.*?)</li>", ol, re.S)]

    def test_dashboard_breadcrumb_single_home(self):
        # Review Focus 5, host page: the host's own breadcrumb, one Home
        self.login("alex")
        crumbs = self.crumbs(self.client.get(reverse("dashboard:index")).content.decode())
        self.assertEqual(crumbs.count("Home"), 1, crumbs)

    def test_crud_page_breadcrumb_single_home(self):
        self.login("alex")
        crumbs = self.crumbs(self.client.get(reverse("customer-list")).content.decode())
        self.assertEqual(crumbs.count("Home"), 1, crumbs)


class FlashMessageTests(PagesTestCase):
    def test_message_once_across_crud_redirect_and_host_page(self):
        # Review Focus 4, host-page variant: create (crud_views), follow the redirect, then GET a non-crud host page.
        self.login("alex")
        first = self.client.post(reverse("category-create"), {"name": "Flash test"})
        self.assertEqual(first.status_code, 302)
        seen = []
        for url in (first["Location"], reverse("dashboard:index")):
            html = self.client.get(url).content.decode()
            seen.append(re.findall(r'<div class="alert alert-success[^"]*"[^>]*>.*?Flash test.*?</div>', html, re.S))
        total = sum(len(found) for found in seen)
        self.assertEqual(total, 1, seen)
        self.assertEqual(len(seen[0]), 1)  # the first page after the redirect shows it, in the host's markup


class MenuPerRoleTests(PagesTestCase):
    """The menu follows the permissions the seed gives each role (dashboard/seed.py and the apps' seeds).

    The roles differ less than their names suggest: Sam (account manager) and Kim (head roaster) both hold the view
    permissions of the catalog, the roastery and sales (Sam through ``add_customer``, Kim through ``view_customer``),
    so both see those sections; only Alex (owner) has the user and showcase permissions.
    """

    CRUD = ("/customer/", "/orders/", "/subscriptions/", "/product/", "/category/", "/lot/", "/batch/", "/shipment/")
    OWNER_ONLY = ("/showcase/", "/users/")

    def links(self, username):
        self.login(username)
        return self.sidebar_links(self.client.get(reverse("dashboard:index")).content.decode())

    def test_alex_sees_everything(self):
        links = self.links("alex")
        for prefix in (*self.CRUD, *self.OWNER_ONLY):
            self.assertTrue([u for u in links if u.startswith(prefix)], (prefix, links))

    def test_sam_and_kim_do_not_see_the_owner_entries(self):
        for username in ("sam", "kim"):
            links = self.links(username)
            for prefix in self.OWNER_ONLY:
                self.assertFalse([u for u in links if u.startswith(prefix)], (username, prefix, links))
            for prefix in self.CRUD:
                self.assertTrue([u for u in links if u.startswith(prefix)], (username, prefix, links))

    def test_every_menu_link_opens_for_the_role(self):
        for username in ("alex", "sam", "kim"):
            for url in self.links(username):
                with self.subTest(user=username, url=url):
                    self.assertEqual(self.client.get(url).status_code, 200)

    def test_a_user_without_permissions_sees_no_crud_entries(self):
        User.objects.create_user("nobody", password="demo")
        links = self.links("nobody")
        # tracker C7: the Customers entry (a Guardian ViewSet) stays for everyone, its list is open to any signed-in
        # user and shows only the objects they hold grants for
        shown = [u for u in links if u.startswith(self.CRUD + self.OWNER_ONLY)]
        self.assertEqual(shown, ["/customer/"])
