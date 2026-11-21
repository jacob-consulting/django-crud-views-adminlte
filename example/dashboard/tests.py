import re
from io import StringIO
from pathlib import Path
from unittest import mock
from urllib.parse import urlencode

from django.apps import apps
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Permission
from django.contrib.staticfiles import finders
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase
from django.urls import get_resolver, reverse
from django.utils import timezone
from django_fsm import FSMFieldMixin
from lxml import html as lxml_html

User = get_user_model()


class AuthTests(TestCase):
    def test_pages_require_login(self):
        for name in ("dashboard:index", "dashboard:users"):
            response = self.client.get(reverse(name))
            self.assertRedirects(response, f"{reverse('login')}?next={reverse(name)}")

    def test_login_page_renders(self):
        response = self.client.get(reverse("login"))
        self.assertContains(response, "Sign in to start your session")  # adminlte-django's login card

    def test_wrong_password_shows_error(self):
        User.objects.create_user("ann", password="s3cret-pass")
        response = self.client.post(reverse("login"), {"username": "ann", "password": "nope"})
        self.assertContains(response, "alert-danger")

    def test_login_and_logout(self):
        User.objects.create_user("ann", password="s3cret-pass")
        response = self.client.post(reverse("login"), {"username": "ann", "password": "s3cret-pass"})
        self.assertRedirects(response, reverse("dashboard:index"))
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"))
        self.assertEqual(self.client.get(reverse("dashboard:index")).status_code, 302)


class DashboardTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("ann", first_name="Ann", last_name="Lee", password="s3cret-pass")
        self.client.force_login(self.user)

    def test_members_do_not_see_users_link(self):
        response = self.client.get(reverse("dashboard:index"))
        self.assertNotContains(response, reverse("dashboard:users"))


class DemoAccountTests(TestCase):
    def test_seed_creates_demo_accounts(self):
        call_command("seed_demo", stdout=StringIO())
        for name in ("alex", "sam", "kim"):
            self.assertTrue(User.objects.filter(username=name).exists())
        self.assertIsNotNone(authenticate(username="sam", password="demo"))
        self.assertTrue(User.objects.get(username="sam").groups.filter(name="Account managers").exists())

    def test_seed_demo_refuses_when_accounts_exist(self):
        call_command("seed_demo", stdout=StringIO())
        out = StringIO()
        call_command("seed_demo", stdout=out)
        self.assertEqual(out.getvalue().strip(), "Demo data already present; use --reset to rebuild.")
        self.assertEqual(User.objects.filter(username__in=("alex", "sam", "kim")).count(), 3)

    def test_login_page_lists_demo_accounts(self):
        html = self.client.get("/accounts/login/").content.decode()
        for name in ("Alex", "Sam", "Kim"):
            self.assertIn(name, html)
        self.assertIn('data-demo-user="sam"', html)

    def test_crud_views_extends_project_template(self):
        self.assertEqual(settings.CRUD_VIEWS_EXTENDS, "project/crud_views.html")


class DashboardIconTests(TestCase):
    def test_dashboard_icons_are_bootstrap_icons(self):
        self.client.force_login(User.objects.create_user("ann"))
        html = self.client.get(reverse("dashboard:index")).content.decode()
        self.assertIn('class="bi bi-currency-euro"', html)  # the revenue info box, from config.icons
        self.assertNotIn("<svg", html)


class DashboardWidgetTests(TestCase):
    """The KPIs are adminlte-django info boxes, the panels its cards; the chart stays ApexCharts (tracker A16)."""

    def setUp(self):
        call_command("seed_demo", stdout=StringIO())
        self.client.force_login(User.objects.get(username="alex"))
        self.root = lxml_html.fromstring(self.client.get(reverse("dashboard:index")).content.decode())

    def test_kpis_are_info_boxes(self):
        texts = [" ".join(e.text_content().split()) for e in self.root.cssselect(".info-box .info-box-text")]
        self.assertEqual(texts, ["Revenue (30 days)", "Open orders", "Active subscriptions", "Green stock"])
        number = self.root.cssselect(".info-box .info-box-number")[0].text_content()
        self.assertRegex(number, r"^€ [\d,]+\.\d\d$")
        self.assertEqual(len(self.root.cssselect(".info-box .progress .progress-bar")), 1)  # green stock

    def test_panels_are_cards(self):
        titles = [" ".join(e.text_content().split()) for e in self.root.cssselect(".card > .card-header .card-title")]
        self.assertEqual(titles, ["Revenue per week", "Orders to roast this week", "Recent cuppings"])
        self.assertEqual(len(self.root.cssselect("#chart-revenue")), 1)
        self.assertFalse(self.root.cssselect("[data-chartjs]"))  # the host's Chart.js component is not used


class UserListTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser("root", "root@example.com", "s3cret-pass")
        self.client.force_login(self.admin)

    def test_members_are_forbidden(self):
        self.client.force_login(User.objects.create_user("ann"))
        self.assertEqual(self.client.get(reverse("dashboard:users")).status_code, 403)

    def test_view_permission_is_enough_to_list(self):
        viewer = User.objects.create_user("viewer")
        viewer.user_permissions.add(Permission.objects.get(codename="view_user"))
        self.client.force_login(viewer)
        response = self.client.get(reverse("dashboard:users"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'id="modal-user"')
        self.assertNotContains(response, 'data-bs-target="#modal-user"')

    def test_search(self):
        User.objects.create_user("ann", email="ann@example.com")
        User.objects.create_user("bob", email="bob@example.com")
        response = self.client.get(reverse("dashboard:users"), {"q": "ann@"})
        self.assertEqual([u.username for u in response.context["page"]], ["ann"])

    def test_create_user(self):
        response = self.client.post(
            reverse("dashboard:user_create"),
            {
                "username": "carol",
                "email": "carol@example.com",
                "password1": "a-Long-pass-123",
                "password2": "a-Long-pass-123",
            },
            follow=True,
        )
        self.assertRedirects(response, reverse("dashboard:users"))
        self.assertContains(response, "was created")
        self.assertTrue(User.objects.get(username="carol").check_password("a-Long-pass-123"))

    def test_invalid_create_reopens_form_with_errors(self):
        response = self.client.post(
            reverse("dashboard:user_create"),
            {
                "username": "root",
                "password1": "x",
                "password2": "y",
            },
        )
        self.assertEqual(response.status_code, 400)
        modal = lxml_html.fromstring(response.content.decode()).cssselect("#modal-user")[0]
        self.assertIn("data-show-on-load", modal.attrib)  # adminlte-django's modal, reopened by the page script
        self.assertTrue(modal.cssselect("form#form-user .is-invalid"))  # crispy-bootstrap5's error markup
        self.assertTrue(modal.cssselect('.modal-footer button[type="submit"][form="form-user"]'))

    def test_modal_is_closed_on_a_plain_get(self):
        modal = lxml_html.fromstring(self.client.get(reverse("dashboard:users")).content.decode()).cssselect(
            "#modal-user"
        )[0]
        self.assertNotIn("data-show-on-load", modal.attrib)

    def test_create_requires_add_permission(self):
        viewer = User.objects.create_user("viewer")
        viewer.user_permissions.add(Permission.objects.get(codename="view_user"))
        self.client.force_login(viewer)
        response = self.client.post(reverse("dashboard:user_create"), {"username": "x"})
        self.assertEqual(response.status_code, 403)


class LayoutTests(TestCase):
    """adminlte-django's layout: one navbar, one sidebar, the colour-mode switch, the pre-built asset bundle."""

    def setUp(self):
        self.client.force_login(User.objects.create_user("switcher"))
        self.html = self.client.get(reverse("dashboard:index")).content.decode()
        self.root = lxml_html.fromstring(self.html)

    def test_page_renders_one_sidebar_and_one_header(self):
        self.assertEqual(len(self.root.cssselect("nav.app-header")), 1)
        self.assertEqual(len(self.root.cssselect("aside.app-sidebar")), 1)
        self.assertEqual(len(self.root.cssselect("main.app-main")), 1)

    def test_header_toggles_the_sidebar(self):
        self.assertEqual(len(self.root.cssselect('nav.app-header [data-lte-toggle="sidebar"]')), 1)

    def test_no_id_is_used_twice(self):
        ids = re.findall(r"\sid=\"([^\"]+)\"", self.html)
        self.assertEqual(sorted(ids), sorted(set(ids)))

    def test_one_colour_mode_switch_in_the_header(self):
        for mode in ("light", "dark", "auto"):
            with self.subTest(mode=mode):
                self.assertEqual(len(self.root.cssselect(f'nav.app-header [data-bs-theme-value="{mode}"]')), 1)

    def test_prebuilt_assets_are_loaded_and_exist(self):
        # ADMINLTE["assets_mode"] = "static": the package's bundle, no Vite dev server
        for path in ("adminlte/dist/css/adminlte.min.css", "adminlte/dist/js/adminlte.min.js"):
            with self.subTest(path=path):
                self.assertIn(f"/static/{path}", self.html)
                self.assertIsNotNone(finders.find(path))
        self.assertEqual(settings.ADMINLTE["assets_mode"], "static")

    def test_server_sets_no_colour_mode(self):
        # the shell's colour-mode switch keeps the user's pick in localStorage; the server renders no default
        self.assertIsNone(self.root.get("data-bs-theme"))


class LayoutBoundaryTests(SimpleTestCase):
    def test_example_overrides_the_site_name(self):
        self.assertEqual(settings.ADMINLTE["title"], "Acme Roasters")

    def test_boundary_scan_covers_only_the_theme(self):
        # Under nox the package lives in site-packages: the scan must not walk every installed distribution.
        root = _theme_dir()
        files = list(_package_sources())
        self.assertTrue(files)
        self.assertTrue(all(path.is_relative_to(root) for path in files))

    def test_src_does_not_import_the_example(self):
        pattern = re.compile(
            r"^\s*(from|import)\s+(catalog|customers|dashboard|config|sales|roastery|shipping|showcase)\b", re.MULTILINE
        )
        for path in _package_sources():
            with self.subTest(path=path):
                self.assertIsNone(pattern.search(path.read_text()))


def _counts():
    """Row counts of every demo model, by label."""
    from django.apps import apps

    labels = ("catalog", "sales", "roastery")
    models = [m for label in labels for m in apps.get_app_config(label).get_models()]
    counts = {m._meta.label: m._base_manager.count() for m in models}
    counts["auth.User"] = User.objects.count()
    return counts


class SeedWorldTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", stdout=StringIO())

    def test_seed_refuses_on_populated_db(self):
        before = _counts()
        out = StringIO()
        call_command("seed_demo", stdout=out)
        self.assertEqual(out.getvalue().strip(), "Demo data already present; use --reset to rebuild.")
        self.assertEqual(_counts(), before)

    def test_seed_reset_is_deterministic(self):
        from sales.models import Customer

        User.objects.create_superuser("admin", "a@example.com", "admin")
        call_command("seed_demo", "--reset", stdout=StringIO())
        first = (_counts(), Customer.objects.order_by("pk").first().name)
        call_command("seed_demo", "--reset", stdout=StringIO())
        self.assertEqual((_counts(), Customer.objects.order_by("pk").first().name), first)
        self.assertTrue(User.objects.filter(username="admin").exists())  # reset never touches other users
        self.assertEqual(User.objects.count(), 4)

    def test_seed_world_shape(self):

        from catalog.models import Beans, Equipment, Product, Subscription
        from django.db.models import Count
        from guardian.shortcuts import get_objects_for_user
        from roastery.models import GreenLot
        from sales.models import Customer, CustomerSubscription, Order, OrderState

        self.assertGreaterEqual(Customer.objects.count(), 20)
        self.assertGreaterEqual(Order.objects.count(), 60)
        self.assertEqual({o.state for o in Order.objects.all()}, {s.value for s in OrderState})
        self.assertGreaterEqual(Order.objects.filter(state=OrderState.DELIVERED).count(), 20)  # history, not all drafts
        self.assertLess(Order.objects.filter(state=OrderState.DRAFT).count(), 15)
        self.assertGreaterEqual(Product.objects.count(), 25)
        for model in (Beans, Equipment, Subscription):
            self.assertGreater(model.objects.count(), 0)
        lots = GreenLot.objects.annotate(n=Count("sessions__scores")).filter(n__gt=0)
        self.assertGreaterEqual(lots.count(), 6)
        sam = User.objects.get(username="sam")
        self.assertGreaterEqual(get_objects_for_user(sam, "sales.view_customer", Customer).count(), 3)
        dates = [o.created_at.date() for o in Order.objects.all()]
        today = timezone.localdate()
        self.assertGreaterEqual((today - min(dates)).days, 80)
        self.assertLessEqual((today - min(dates)).days, 92)
        for start in range(0, 90, 30):  # every month has orders
            window = [d for d in dates if start <= (today - d).days < start + 30]
            self.assertGreaterEqual(len(window), 10)
        self.assertGreaterEqual(CustomerSubscription.objects.filter(is_active=True).count(), 10)
        self.assertTrue(Order.objects.filter(roast_batches__isnull=False).exists())


class RoasteryDashboardTests(TestCase):
    """Known small world: exact numbers for the stat cards, scoped per user."""

    @classmethod
    def setUpTestData(cls):
        from datetime import timedelta
        from decimal import Decimal

        from catalog.models import Beans, Origin, Subscription
        from roastery.models import CuppingScore, CuppingSession, GreenLot, RoastBatch
        from sales.models import Customer, CustomerSubscription, Order, OrderLine
        from sales.permissions import grant_customer

        call_command("seed_demo", stdout=StringIO())  # accounts and groups only matter; wipe the rest
        for model in (RoastBatch, Order, CustomerSubscription, Customer, CuppingScore, CuppingSession, GreenLot):
            model.objects.all().delete()
        cls.alex, cls.sam, cls.kim = (User.objects.get(username=n) for n in ("alex", "sam", "kim"))

        origin = Origin.objects.first()
        beans = Beans.objects.create(
            name="Dash beans", slug="dash-beans", sku="D-1", price=Decimal("10.00"), origin=origin
        )
        sub = Subscription.objects.create(name="Dash sub", slug="dash-sub", sku="D-2", price=Decimal("30.00"))
        cls.consumer = Customer.objects.create(name="Consumer One", kind="consumer")
        cls.shop = Customer.objects.create(name="Shop Two", kind="wholesale", company="Shop", price_tier="B")  # 12%
        grant_customer(cls.sam, cls.consumer)

        today = timezone.localdate()
        now = timezone.now()

        def order(customer, state, qty, days_ago, roast_in=None):
            o = Order.objects.create(
                customer=customer,
                state=state,
                requested_roast_date=today + timedelta(days=roast_in) if roast_in is not None else None,
            )
            OrderLine.objects.create(order=o, product=beans, quantity=qty)
            Order.objects.filter(pk=o.pk).update(created_at=now - timedelta(days=days_ago))
            return o

        cls.to_roast = order(cls.consumer, "confirmed", 5, 5, roast_in=2)  # 50.00
        order(cls.shop, "shipped", 10, 10)  # 100.00 - 12.00 = 88.00
        order(cls.shop, "delivered", 10, 40)  # 88.00, previous 30 days
        order(cls.consumer, "draft", 100, 0)  # excluded
        order(cls.consumer, "cancelled", 100, 2)  # excluded
        order(cls.shop, "roasted", 1, 3)  # 10.00 - 1.20 = 8.80
        order(cls.shop, "confirmed", 2, 1, roast_in=20)  # 17.60, not due this week

        CustomerSubscription.objects.create(customer=cls.consumer, product=sub, next_delivery=today + timedelta(days=3))
        CustomerSubscription.objects.create(customer=cls.shop, product=sub, next_delivery=today + timedelta(days=1))
        CustomerSubscription.objects.create(customer=cls.shop, product=sub, next_delivery=today, is_active=False)

        cls.lot = GreenLot.objects.create(
            code="XX-24-001",
            origin=origin,
            producer="P",
            variety="V",
            harvest_year=2024,
            kg_purchased=Decimal("100"),
            kg_on_hand=Decimal("40.5"),
            price_per_kg=Decimal("8"),
            arrived_on=today,
        )
        GreenLot.objects.create(
            code="XX-24-002",
            origin=origin,
            producer="P",
            variety="V",
            harvest_year=2024,
            kg_purchased=Decimal("10"),
            kg_on_hand=Decimal("10"),
            price_per_kg=Decimal("8"),
            arrived_on=today,
        )
        cls.session = CuppingSession.objects.create(lot=cls.lot, held_on=today)
        for taster, value in ((cls.kim, "8"), (cls.alex, "7")):
            CuppingScore.objects.create(
                session=cls.session, taster=taster, **{a: Decimal(value) for a in CuppingScore.ATTRIBUTES}
            )

    def get(self, user):
        self.client.force_login(user)
        return self.client.get(reverse("dashboard:index"))

    def test_stats_match_data(self):
        from decimal import Decimal

        ctx = self.get(self.alex).context
        self.assertEqual(ctx["revenue_30d"], Decimal("164.40"))  # confirmed, roasted, shipped, delivered by created_at
        self.assertEqual(ctx["revenue_trend_pct"], Decimal("86.8"))  # vs 88.00 in the 30 days before
        self.assertEqual(ctx["open_orders"], 3)  # two confirmed, one roasted
        self.assertEqual(ctx["orders_waiting_to_roast"], 2)
        self.assertEqual(list(ctx["orders_to_roast"]), [self.to_roast])
        self.assertEqual(ctx["active_subscriptions"], 2)
        self.assertEqual(ctx["next_subscription_run"], timezone.localdate() + timezone.timedelta(days=1))
        self.assertEqual(ctx["green_stock_kg"], Decimal("50.5"))
        self.assertEqual([s.pk for s in ctx["recent_cuppings"]], [self.session.pk])
        self.assertEqual(ctx["recent_cuppings"][0].average, Decimal("82.5"))  # totals 30 + 7 * 8 and 30 + 7 * 7

    def test_revenue_by_week_has_12_points(self):
        from decimal import Decimal

        weeks = self.get(self.alex).context["revenue_by_week"]
        self.assertEqual(len(weeks), 12)
        self.assertTrue(all(label.startswith("W") for label, _ in weeks))
        self.assertEqual(sum(v for _, v in weeks), Decimal("252.40"))  # the delivered order of 40 days ago counts too

    def test_sam_dashboard_counts_only_granted_customers(self):
        from decimal import Decimal

        ctx = self.get(self.sam).context
        self.assertEqual(ctx["revenue_30d"], Decimal("50.00"))
        self.assertIsNone(ctx["revenue_trend_pct"])  # nothing in the previous period
        self.assertEqual(ctx["open_orders"], 1)
        self.assertEqual(ctx["active_subscriptions"], 1)
        self.assertEqual(ctx["next_subscription_run"], timezone.localdate() + timezone.timedelta(days=3))
        self.assertEqual(sum(v for _, v in ctx["revenue_by_week"]), Decimal("50.00"))
        self.assertEqual(list(ctx["orders_to_roast"]), [self.to_roast])
        self.assertNotContains(self.get(self.sam), "Shop Two")

    def test_kim_sees_all_sales_numbers_and_the_roastery(self):
        from decimal import Decimal

        ctx = self.get(self.kim).context
        self.assertEqual(ctx["revenue_30d"], Decimal("164.40"))
        self.assertEqual(ctx["green_stock_kg"], Decimal("50.5"))

    def test_rows_link_to_crud_pages(self):
        response = self.get(self.alex)
        self.assertContains(
            response, reverse("order-detail", kwargs={"customer_pk": self.consumer.pk, "pk": self.to_roast.pk})
        )
        self.assertContains(response, reverse("cupping-detail", kwargs={"lot_pk": self.lot.pk, "pk": self.session.pk}))

    def test_chart_assets_are_pinned_with_sri(self):
        html = self.get(self.alex).content.decode()
        self.assertRegex(
            html,
            r'"https://cdn.jsdelivr.net/npm/apexcharts@\d+\.\d+\.\d+/dist/apexcharts.min.js"[^>]*'
            r'integrity="sha384-[^"]+"[^>]*crossorigin="anonymous"',
        )
        # the only jsDelivr package: ApexCharts (the shell's assets are served from static, assets_mode "static")
        packages = set(re.findall(r'(?:href|src)="https://cdn\.jsdelivr\.net/npm/((?:@[\w-]+/)?[\w-]+)@', html))
        self.assertEqual(packages, {"apexcharts"})
        self.assertNotIn("@coreui", html)
        self.assertIn('id="revenue-data"', html)
        self.assertIsNotNone(finders.find("dashboard/revenue-chart.js"))


def _text(html):
    """The visible text of highlighted code: tags stripped, entities unescaped."""
    import html as html_lib

    return html_lib.unescape(re.sub(r"<[^>]+>", "", html))


class ShowCodeTests(TestCase):
    """The "Show code" panel on crud_views pages and the "How this is themed" page (config/showcode.py)."""

    def setUp(self):
        self.admin = User.objects.create_superuser("root", password="s3cret-pass")
        self.client.force_login(self.admin)

    def test_code_panel_on_crud_pages(self):
        """The page carries the empty shell; the sources come from the fragment endpoint."""
        html = self.client.get(reverse("customer-list")).content.decode()
        url = reverse("code-panel", kwargs={"app_label": "sales"})
        self.assertEqual(url, "/_code/sales/")
        self.assertIn('id="code-panel"', html)
        self.assertIn(f'data-code-url="{url}"', html)
        self.assertIn('data-code-active="sales/views/customers.py"', html)
        self.assertIn('href="#code-panel"', html)  # the "Show code" toggle in the page header
        self.assertIn("acme/code-panel.js", html)
        self.assertNotIn("GuardianViewSet", html)  # no source on the page itself
        fragment = self.client.get(url)
        self.assertEqual(fragment.status_code, 200)
        self.assertIn("cv_customer = GuardianViewSet", _text(fragment.content.decode()))
        self.assertIn('data-code-file="sales/views/customers.py"', fragment.content.decode())

    def test_code_panel_endpoint_rejects_other_labels(self):
        for label in ("auth", "nonexistent", "dashboard", "crud_views_adminlte", "django_adminlte4"):
            self.assertEqual(self.client.get(f"/_code/{label}/").status_code, 404, label)
        for path in ("/_code/../config/", "/_code/..%2Fconfig/", "/_code/config/settings.py/"):
            self.assertEqual(self.client.get(path).status_code, 404, path)

    def test_code_panel_endpoint_requires_login(self):
        self.client.logout()
        url = reverse("code-panel", kwargs={"app_label": "sales"})
        self.assertRedirects(self.client.get(url), f"{reverse('login')}?next={url}")

    def test_pygments_stylesheet_has_light_and_dark_colours(self):
        css = self.client.get(reverse("pygments-css"))
        self.assertEqual(css["Content-Type"], "text/css")
        text = css.content.decode()
        self.assertIn(":root:not([data-bs-theme=dark]) .code-block .k {", text)
        self.assertIn("[data-bs-theme=dark] .code-block .k {", text)
        self.assertNotIn("\npre {", "\n" + text)  # nothing unscoped
        self.assertIn(reverse("pygments-css"), self.client.get(reverse("theming")).content.decode())

    def test_settings_excerpt_handles_every_assignment_form(self):
        from config.showcode import settings_excerpt

        text = (
            "SECRET_KEY = 'x'\nINSTALLED_APPS = ['a']\nINSTALLED_APPS += ['b']\n"
            "CRUD_VIEWS_EXTENDS: str = 'p.html'\nDEBUG = True\n"
        )
        self.assertEqual(
            settings_excerpt(text),
            ["INSTALLED_APPS = ['a']", "INSTALLED_APPS += ['b']", "CRUD_VIEWS_EXTENDS: str = 'p.html'"],
        )

    def test_package_files_skip_binaries(self):
        import tempfile

        from config.showcode import _highlighted, _package_files

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "apps.py").write_text("x = 1\n")
            (root / "logo.png").write_bytes(b"\x89PNG\r\n\x1a\n\xff\xfe")
            (root / "bad.css").write_bytes(b"\xff\xfe\x00")
            self.assertEqual([p.name for p in _package_files(root)], ["apps.py", "bad.css"])  # png: no lexer
            bad = root / "bad.css"
            self.assertIsNone(_highlighted(bad, bad.stat().st_mtime_ns))  # not UTF-8: skipped, not a 500

    def test_code_panel_never_shows_theme_imports(self):
        from config.showcode import collect_sources_for_app

        for app in ("sales", "catalog", "roastery", "shipping"):
            sources = collect_sources_for_app(app)
            self.assertTrue(sources, app)
            for source in sources:
                for name in ("django_adminlte4", "crud_views_adminlte"):
                    self.assertNotIn(name, _text(source.html), source.label)

    def test_code_panel_lists_models_views_and_templates_but_not_seed(self):
        from config.showcode import collect_sources_for_app

        labels = [s.label for s in collect_sources_for_app("sales")]
        self.assertIn("sales/models.py", labels)
        self.assertIn("sales/views/customers.py", labels)
        self.assertIn("sales/templates/sales/order_detail.html", labels)
        self.assertNotIn("sales/seed.py", labels)
        self.assertFalse([label for label in labels if "/tests" in label])

    def test_code_panel_only_for_example_apps(self):
        from config.showcode import collect_app_sources, collect_sources_for_app

        class NotAnExampleView:
            pass

        NotAnExampleView.__module__ = "crud_views.lib.views"
        self.assertEqual(collect_app_sources(NotAnExampleView()), [])
        self.assertEqual(collect_sources_for_app("../config"), [])
        self.assertEqual(collect_sources_for_app("dashboard"), [])

    def test_panel_is_collapsed_by_default(self):
        html = self.client.get(reverse("customer-list")).content.decode()
        match = re.search(r'<div class="([^"]*)" id="code-panel"', html)
        self.assertIsNotNone(match)
        self.assertIn("collapse", match.group(1).split())
        self.assertNotIn("show", match.group(1).split())

    def test_theming_page_counts(self):
        from config.showcode import collect_theme_sources

        sources = collect_theme_sources()
        html = self.client.get(reverse("theming")).content.decode()
        lines = sum(s.lines for s in sources)
        self.assertIn(f"The whole theme is {len(sources)} files, {lines} lines.", html)
        self.assertIn("Your app code is unchanged.", html)
        for source in sources:
            self.assertIn(source.label, html)

    def test_theme_sources_cover_the_theme_app(self):
        from config.showcode import collect_theme_sources

        labels = [s.label for s in collect_theme_sources()]
        for label in (
            "crud_views_adminlte/apps.py",
            "crud_views_adminlte/buttons.py",
            "crud_views_adminlte/menu.py",
            "crud_views_adminlte/static/crud_views_adminlte/crud_views_adminlte.css",
            "crud_views_adminlte/templates/crud_views_adminlte/page.html",
            "example/config/settings.py (excerpt)",
        ):
            self.assertIn(label, labels)
        self.assertFalse([label for label in labels if "__pycache__" in label or "/tests" in label])

    def test_theming_page_shows_the_settings_but_not_the_secret_key(self):
        html = self.client.get(reverse("theming")).content.decode()
        text = _text(html)
        for name in (
            "INSTALLED_APPS",
            "ADMINLTE",
            "CRUD_VIEWS_EXTENDS",
            "CRUD_VIEWS_BREADCRUMB_PREFIX",
            "CRISPY_TEMPLATE_PACK",
            "DJANGO_TABLES2_TEMPLATE",
        ):
            self.assertIn(name, text)
        self.assertNotIn("SECRET_KEY", html)
        self.assertNotIn(settings.SECRET_KEY, html)
        self.assertNotIn("django-insecure", html)

    def test_theming_page_links_to_the_docs(self):
        html = self.client.get(reverse("theming")).content.decode()
        self.assertIn("https://django-crud-views.readthedocs.io/en/latest/reference/theme/", html)
        self.assertIn("https://django-crud-views-adminlte.readthedocs.io/en/latest/", html)

    def test_theming_page_names_the_host_and_its_version(self):
        from importlib.metadata import version

        text = " ".join(_text(self.client.get(reverse("theming")).content.decode()).split())
        self.assertIn(f"Not counted above: django_adminlte4, adminlte-django {version('adminlte-django')}", text)

    def test_theming_is_in_the_nav_for_every_user(self):
        User.objects.create_user("plain", password="s3cret-pass")
        self.client.force_login(User.objects.get(username="plain"))
        response = self.client.get(reverse("dashboard:index"))
        self.assertContains(response, reverse("theming"))
        self.assertContains(response, "How this is themed")
        self.assertEqual(self.client.get(reverse("theming")).status_code, 200)

    def test_theming_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("theming"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('theming')}")


def _grant(user, *codenames):
    for codename in codenames:
        app_label, codename = codename.split(".")
        user.user_permissions.add(Permission.objects.get(content_type__app_label=app_label, codename=codename))


class NavigationTests(TestCase):
    """The sidebar (adminlte-django's menu, config/menu.py): the dashboard link, then one header per section."""

    def setUp(self):
        self.user = User.objects.create_user("navi")
        self.client.force_login(self.user)

    def sidebar(self, url):
        return lxml_html.fromstring(self.client.get(url).content.decode()).cssselect("aside.app-sidebar .sidebar-menu")[
            0
        ]

    @staticmethod
    def headers(menu):
        return [li.text_content().strip() for li in menu.cssselect("li.nav-header")]

    @staticmethod
    def links(menu):
        """{href: (text, classes of the link)} of the menu's links."""
        return {
            a.get("href"): (" ".join(a.text_content().split()), a.get("class").split())
            for a in menu.cssselect("a.nav-link")
        }

    def test_sections_are_headers_with_their_links(self):
        _grant(
            self.user,
            "sales.view_customer",
            "sales.view_order",
            "catalog.view_product",
            "catalog.view_category",
            "roastery.view_greenlot",
        )
        menu = self.sidebar(reverse("dashboard:index"))
        for section in ("Sales", "Catalog", "Roastery", "Developer"):
            self.assertIn(section, self.headers(menu))
        self.assertEqual(self.links(menu)["/customer/"][0], "Customers")
        self.assertFalse(menu.cssselect(".nav-treeview"))  # flat: no submenus

    def test_every_link_has_an_icon(self):
        links = self.sidebar(reverse("dashboard:index")).cssselect("a.nav-link")
        self.assertTrue(links)
        for link in links:
            with self.subTest(link=link.get("href")):
                self.assertTrue(link.cssselect("i.nav-icon.bi"))

    def test_active_entry_is_marked(self):
        _grant(self.user, "sales.view_customer", "sales.view_order")
        links = self.links(self.sidebar(reverse("orders-list")))
        self.assertIn("active", links["/orders/"][1])
        self.assertNotIn("active", links["/customer/"][1])

    def test_an_entry_is_active_on_its_child_pages(self):
        _grant(self.user, "sales.view_customer", "sales.view_order")
        from sales.models import Customer

        customer = Customer.objects.create(name="Navi Ltd")
        # the order list nested under a customer belongs to the customer's entry, not the top-level Orders ViewSet
        links = self.links(self.sidebar(reverse("order-list", kwargs={"customer_pk": customer.pk})))
        self.assertIn("active", links["/customer/"][1])
        self.assertNotIn("active", links["/orders/"][1])

    def test_a_section_with_one_entry_keeps_its_header(self):
        menu = self.sidebar(reverse("dashboard:index"))
        self.assertIn("Developer", self.headers(menu))
        self.assertIn("/theming/", self.links(menu))

    def test_sections_follow_the_permissions(self):
        # tracker A14: a section header stays when every entry under it is hidden, so the links are asserted
        menu = self.sidebar(reverse("dashboard:index"))
        for href in ("/product/", "/category/", "/lot/", "/batch/", "/shipment/", "/users/"):
            self.assertNotIn(href, self.links(menu))
        _grant(self.user, "sales.view_order")
        menu = self.sidebar(reverse("dashboard:index"))
        # Shipments live under Roastery and need only the order permission.
        self.assertIn("/shipment/", self.links(menu))
        self.assertNotIn("/lot/", self.links(menu))

    def test_customers_open_for_account_managers_without_a_global_view(self):
        _grant(self.user, "sales.add_customer")
        self.assertIn("/customer/", self.links(self.sidebar(reverse("dashboard:index"))))


class FaviconTests(TestCase):
    def test_every_page_links_the_brand_favicon(self):
        # Without a <link rel="icon"> browsers ask for /favicon.ico, a 404 on every page.
        self.client.force_login(User.objects.create_user("fav"))
        for url in (reverse("dashboard:index"), reverse("theming")):
            with self.subTest(url=url):
                self.assertContains(
                    self.client.get(url), '<link rel="icon" href="/static/acme/favicon.svg" type="image/svg+xml" />'
                )
        self.client.logout()
        self.assertContains(self.client.get(reverse("login")), 'href="/static/acme/favicon.svg"')
        self.assertIn("#a0522d", Path(finders.find("acme/favicon.svg")).read_text())


class ManageViewsTests(TestCase):
    # Upstream #361: manage pages need an active member of CRUD_VIEWS_MANAGE_GROUP in every mode, DEBUG grants
    # nothing, and "no" closes them for everyone. The seed makes alex the only member.

    def setUp(self):
        call_command("seed_demo", stdout=StringIO())
        self.users = {name: User.objects.get(username=name) for name in ("alex", "sam", "kim")}

    def get(self, username, url):
        self.client.force_login(self.users[username])
        return self.client.get(url)

    def test_settings_default_to_yes_without_the_environment_variable(self):
        source = (Path(settings.BASE_DIR) / "config" / "settings.py").read_text()
        self.assertIn(
            'CRUD_VIEWS_MANAGE_VIEWS_ENABLED = os.environ.get("CRUD_VIEWS_MANAGE_VIEWS_ENABLED", "yes")', source
        )

    def test_alex_opens_the_manage_page(self):
        self.assertEqual(self.get("alex", "/customer/manage/").status_code, 200)
        self.assertContains(self.client.get("/customer/"), 'href="/customer/manage/"')
        from sales.models import Customer

        customer = Customer.objects.first()
        nested = reverse("address-manage", kwargs={"customer_pk": customer.pk})
        self.assertEqual(self.client.get(nested).status_code, 200)

    def test_sam_and_kim_are_refused(self):
        from sales.models import Customer

        nested = reverse("address-manage", kwargs={"customer_pk": Customer.objects.first().pk})
        for username, list_url in (("sam", "/customer/"), ("kim", "/batch/")):
            with self.subTest(username):
                self.assertEqual(self.get(username, "/customer/manage/").status_code, 403)
                self.assertEqual(self.client.get(nested).status_code, 403)
                self.assertNotContains(self.client.get(list_url), "/manage/")

    def test_shipment_resource_has_a_manage_page(self):
        # Upstream #372: Resource ViewSets get the manage page too; opening it never calls the courier API (D-03)
        with mock.patch("shipping.resources.fetch_shipments", side_effect=AssertionError("courier called")):
            response = self.get("alex", "/shipment/manage/")
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'class="badge bg-info-subtle text-info-emphasis"')  # manage:badge-resource
            for username in ("sam", "kim"):
                with self.subTest(username):
                    self.assertEqual(self.get(username, "/shipment/manage/").status_code, 403)

    def test_manage_matrix_lists_sams_object_grants(self):
        # Finding 35: user-level Guardian grants used to be invisible; CRUD_VIEWS_MANAGE_SHOW_USERS lists them
        html = self.get("alex", "/customer/manage/").content.decode()
        self.assertIn("sam", html, msg="sam missing from the matrix")
        self.assertIn("badge border border-secondary-subtle text-body-secondary", html)  # manage:badge-objects

    def test_access_check_traces_sam_on_customers(self):
        # Upstream #370, on in the demo (CRUD_VIEWS_MANAGE_ACCESS_TRACE): alex traces sam's access by path
        from guardian.shortcuts import get_objects_for_user
        from sales.models import Customer

        mine = get_objects_for_user(self.users["sam"], "sales.view_customer", accept_global_perms=False)
        cases = (
            (mine.first(), 'class="badge bg-success-subtle text-success-emphasis">Allowed<'),
            (
                Customer.objects.exclude(pk__in=mine).first(),
                'class="badge bg-danger-subtle text-danger-emphasis">Denied<',
            ),
        )
        for customer, outcome in cases:
            with self.subTest(customer=customer.pk):
                response = self.get(
                    "alex",
                    "/customer/manage/?"
                    + urlencode(
                        {
                            "cv_access_mode": "path",
                            "cv_access_user": "sam",
                            "cv_access_path": f"/customer/{customer.pk}/detail/",
                        }
                    ),
                )
                html = response.content.decode()
                self.assertIn('id="cv-manage-access-trace"', html)
                self.assertIn(outcome, html[html.index('id="cv-manage-access-trace"') :])

    def test_superuser_outside_the_group_is_refused(self):
        self.client.force_login(User.objects.create_superuser("root", password="x"))
        self.assertEqual(self.client.get("/customer/manage/").status_code, 403)
        self.assertNotContains(self.client.get("/customer/"), "/manage/")

    def test_no_mode_refuses_alex(self):
        # crud_views reads its settings once at import, so the value is patched on its settings object.
        from crud_views.lib.settings import crud_views_settings

        with mock.patch.object(crud_views_settings, "manage_views_enabled", "no"):
            self.assertEqual(self.get("alex", "/customer/manage/").status_code, 403)

    def test_reset_keeps_alex_in_the_manage_group(self):
        from crud_views.lib.settings import crud_views_settings

        call_command("seed_demo", "--reset", stdout=StringIO())
        alex = User.objects.get(username="alex")
        self.assertTrue(alex.groups.filter(name=crud_views_settings.manage_group).exists())


class MigrationsTests(TestCase):
    """The migrations were generated on Django 6.1; every supported Django (5.2 too) must see no model changes."""

    def test_models_match_migrations(self):
        out = StringIO()
        try:
            call_command("makemigrations", "--check", "--dry-run", stdout=out, stderr=out)
        except SystemExit:
            self.fail(f"makemigrations --check found changes:\n{out.getvalue()}")


def _theme_dir() -> Path:
    """The theme package's directory, wherever it is installed (the example never imports the theme)."""
    return Path(apps.get_app_config("crud_views_adminlte").path)


def _package_sources():
    """Every .py file of crud_views_adminlte: the theme's own code."""
    yield from _theme_dir().rglob("*.py")


def _bootstrap_icon_names() -> set[str]:
    """Every icon name of the Bootstrap Icons font adminlte-django ships (``.bi-<name>::before`` rules)."""
    css = Path(finders.find("adminlte/dist/css/bootstrap-icons.min.css")).read_text()
    return set(re.findall(r"\.bi-([a-z0-9-]+)::?before", css))


class IconVocabularyTests(SimpleTestCase):
    """The app names icons by domain meaning; only settings and config/icons.py know the library."""

    def test_example_code_names_no_library(self):
        root = Path(settings.BASE_DIR)
        allowed = {root / "config" / "settings.py", root / "config" / "icons.py"}
        offenders = [
            str(path.relative_to(root))
            for path in [*root.rglob("*.py"), *root.rglob("*.html")]
            if path not in allowed
            and "migrations" not in path.parts
            and re.search(r"[\"']bi:|\bbi bi-", path.read_text(encoding="utf-8"))
            and not path.name.startswith("test")
        ]
        self.assertEqual(offenders, [])

    def test_every_semantic_name_has_an_icon(self):
        from config.icons import ACME_ICONS
        from crud_views.lib.icons import resolve_icon

        names = _bootstrap_icon_names()
        self.assertTrue(ACME_ICONS)
        for key in ACME_ICONS:
            library, name = resolve_icon(key)
            self.assertEqual(library, "bi", key)
            self.assertIn(name, names, key)

    @staticmethod
    def _used_icons():
        """Every icon value the example's code names, as (where, value): views, property groups, workflow, models,
        courier events and the sidebar menu."""
        from catalog.models import Product
        from config.menu import MENU
        from crud_views.lib.viewset import _REGISTRY
        from shipping.courier import EVENT_PLAN

        _ = get_resolver().url_patterns  # importing the URLconf registers every ViewSet
        used = []

        def walk_groups(where, groups):
            for group in groups or []:
                if isinstance(group, dict) and group.get("icon"):
                    used.append((f"{where} group {group.get('title')}", group["icon"]))

        for name, viewset in _REGISTRY.items():
            used.append((f"ViewSet {name}.icon_header", viewset.icon_header))
            for key, view in viewset.get_all_views().items():
                for attr in ("cv_icon_action", "cv_icon_header"):
                    used.append((f"{name}.{key}.{attr}", getattr(view, attr, None)))
                display = getattr(view, "cv_property_display", None)
                if isinstance(display, dict):
                    for model, groups in display.items():
                        walk_groups(f"{name}.{key}[{model.__name__}]", groups)
                else:
                    walk_groups(f"{name}.{key}", display)

        def subclasses(cls):
            for sub in cls.__subclasses__():
                yield sub
                yield from subclasses(sub)

        for cls in (Product, *subclasses(Product)):
            if "card_icon" in vars(cls):
                used.append((f"{cls.__name__}.card_icon", cls.card_icon))
        for model in apps.get_models():
            for field in model._meta.get_fields():
                if isinstance(field, FSMFieldMixin):
                    for transition in field.get_all_transitions(model):
                        used.append(
                            (f"{model.__name__} transition {transition.name}", (transition.custom or {}).get("icon"))
                        )
        for description, _location, _hours, icon in EVENT_PLAN:
            used.append((f"courier event {description}", icon))
        # the sidebar takes CSS classes (config.icons.icon_class): "bi bi-<name>" back to the library's name
        for entry in MENU:
            if entry.get("icon"):
                used.append((f"menu {entry['text']}", "bi:" + entry["icon"].removeprefix("bi bi-")))
        return [(where, value) for where, value in used if value]

    def test_every_icon_used_in_code_resolves(self):
        from crud_views.lib.icons import resolve_icon

        names = _bootstrap_icon_names()
        used = self._used_icons()
        self.assertGreater(len(used), 40)
        self.assertTrue([w for w, _v in used if " transition " in w], "no workflow transition icon collected")
        for where, value in used:
            resolved = resolve_icon(value)
            self.assertIsNotNone(resolved, f"{where}: {value!r}")
            library, name = resolved
            self.assertEqual(library, "bi", f"{where}: {value!r} is not a table key (renders as a raw class)")
            self.assertIn(name, names, f"{where}: {value!r}")


#: Classes left from django-crud-views-tabler and the CoreUI demo this one was copied from, which Bootstrap 5.3 and
#: AdminLTE 4 do not have: light badges, components, avatars, ghost buttons, sidebar and header classes, and the
#: CoreUI theme's own cv-coreui-* classes.
NON_ADMINLTE_CLASS = re.compile(
    r"^(?:bg-\w+-lt|(?:bg|text|border)-(?:azure|blue|cyan|green|indigo|lime|orange|pink|purple|red|teal|yellow)"
    r"|avatar(?:-\w+)?|badge-outline|btn-list|card-actions|card-lg|card-md|card-sm|card-status-\w+|card-table|"
    r"datagrid(?:-\w+)?|form-fieldset|form-footer|input-icon(?:-addon)?|list-group-header|modal-blur|"
    r"nav-link-icon|nav-link-title|navbar-vertical|page-body|page-wrapper|row-cards|row-deck|status-dot|step-item|"
    r"steps(?:-\w+)?|subheader|table-transparent|table-vcenter|timeline(?:-\w+)?|w-1"
    r"|btn-ghost(?:-\w+)?|border-(?:top|bottom|start|end)-[1-5]|nav-title|sidebar-nav|sidebar-fixed|sidebar-dark"
    r"|header-nav|header-toggler|progress-thin|page-header|page-title|page-subtitle|cv-coreui-[\w-]+)$"
)


def _crawl(client, start):
    """GET the start URLs, then every page linked from a page already fetched, one URL per view name.

    Returns {url: response}. Leaves out the admin, sign-in/out, static and media files.
    """
    from django.urls import Resolver404, resolve

    pages, queue, names = {}, list(start), set()
    while queue:
        url = queue.pop(0)
        if url in pages:
            continue
        response = pages[url] = client.get(url)
        if response.status_code != 200 or not response["Content-Type"].startswith("text/html"):
            continue
        for href in re.findall(r'href="(/[^"#?]*)', response.content.decode()):
            if href.startswith(("/admin/", "/accounts/", "/static/", "/media/")) or href in pages:
                continue
            try:
                name = resolve(href).view_name
            except Resolver404:
                continue
            if name not in names:
                names.add(name)
                queue.append(href)
    return pages


class AdminltePagesTests(TestCase):
    """Every page of the demo, as alex (who may open everything): AdminLTE / Bootstrap 5.3 markup only.

    The crawl starts at the dashboard, the theming, users and a manage page and the "Show code" fragment, and follows
    every link (sidebar, tables, buttons, tabs) to one page per view name, so it reaches a list, detail, update and
    create page of every ViewSet; ``test_every_viewset_view_is_reached`` checks that.
    """

    START = ("/", "/theming/", "/users/", "/customer/manage/", "/_code/sales/", "/_code/showcase/")

    @classmethod
    def setUpTestData(cls):
        from django.test import Client

        call_command("seed_demo", stdout=StringIO())
        call_command("seed_demo_showcase", stdout=StringIO())
        from catalog.models import Beans, Equipment, Subscription
        from django.contrib.contenttypes.models import ContentType

        client = Client()
        client.force_login(User.objects.get(username="alex"))
        # a polymorphic create page is reached through its type select (a form), so its URLs are started from here
        creates = [
            reverse("product-create", kwargs={"polymorphic_ctype_id": ContentType.objects.get_for_model(model).pk})
            for model in (Beans, Equipment, Subscription)
        ]
        from sales.models import Order, OrderState

        # a cancelled order's detail page shows the cancel note instead of the steps; crawling picks any one order
        cancelled = Order.objects.filter(state=OrderState.CANCELLED).first()
        cancelled_url = reverse("order-detail", kwargs={"customer_pk": cancelled.customer_id, "pk": cancelled.pk})
        pages = _crawl(client, (*cls.START, *creates, cancelled_url))
        cls.pages = {url: (r.status_code, r.content.decode()) for url, r in pages.items()}
        # a crispy create form posted empty: the error markup of the form pack
        invalid = client.post(reverse("showcaseitem-create"), {})
        cls.pages["POST " + reverse("showcaseitem-create")] = (invalid.status_code, invalid.content.decode())

    def test_every_page_renders(self):
        self.assertGreater(len(self.pages), 60)
        self.assertEqual({url: status for url, (status, _html) in self.pages.items() if status != 200}, {})

    def test_sweep_covers_a_form_with_errors_and_a_cancelled_order(self):
        _status, html = self.pages["POST " + reverse("showcaseitem-create")]
        self.assertIn("is-invalid", html)
        self.assertIn("invalid-feedback", html)
        self.assertTrue([url for url, (_s, html) in self.pages.items() if "This order was cancelled." in html])

    def test_every_viewset_view_is_reached(self):
        from crud_views.lib.viewset import _REGISTRY
        from django.urls import resolve

        reached = {resolve(url.split("?")[0]).view_name for url in self.pages if url.startswith("/")}
        missing = [
            viewset.get_router_name(key)
            for viewset in _REGISTRY.values()
            for key in ("list", "detail", "update", "create")
            if viewset.has_view(key) and viewset.get_router_name(key) not in reached
        ]
        self.assertEqual(missing, [])
        self.assertIn("showcaseitem-list", reached)

    def test_every_page_has_no_data_coreui(self):
        # an attribute inside a tag; the theming page and the code panel show source text
        attribute = re.compile(r"<[^>]*\sdata-coreui-")
        for url, (_status, html) in self.pages.items():
            with self.subTest(url=url):
                self.assertIsNone(attribute.search(html))

    def test_every_page_uses_adminlte_classes_only(self):
        for url, (_status, html) in self.pages.items():
            classes = {c for value in re.findall(r'\sclass="([^"]*)"', html) for c in value.split()}
            with self.subTest(url=url):
                self.assertEqual(sorted(c for c in classes if NON_ADMINLTE_CLASS.match(c)), [])

    def test_sign_in_page_has_no_data_coreui_and_adminlte_classes_only(self):
        from django.test import Client

        html = Client().get(reverse("login")).content.decode()
        self.assertIsNone(re.search(r"<[^>]*\sdata-coreui-", html))
        classes = {c for value in re.findall(r'\sclass="([^"]*)"', html) for c in value.split()}
        self.assertEqual(sorted(c for c in classes if NON_ADMINLTE_CLASS.match(c)), [])


class OriginTests(SimpleTestCase):
    """The example was copied from the Tabler demo; nothing of Tabler may be left but comments that credit it."""

    #: a comment line that names where something came from
    CREDIT = re.compile(r"^\s*(#|//|/?\*|\{#).*\b(from|after|as in|like)\b.*\bdjango-crud-views-tabler\b", re.I)

    def test_no_tabler_left(self):
        import inspect

        root = Path(settings.BASE_DIR)
        own_lines, own_start = inspect.getsourcelines(OriginTests)
        own = range(own_start, own_start + len(own_lines))
        offenders = []
        for path in sorted(root.rglob("*")):
            # catalog's first migration keeps FlavorNote's old help text as history; 0003 replaces it
            if (
                path.suffix not in {".py", ".html", ".css", ".js"}
                or path == root / "catalog/migrations/0001_initial.py"
            ):
                continue
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if path == Path(__file__).resolve() and number in own:
                    continue
                if "tabler" in line.lower() and not self.CREDIT.match(line):
                    offenders.append(f"{path.relative_to(root)}:{number}: {line.strip()}")
        self.assertEqual(offenders, [])


class CoreuiOriginTests(SimpleTestCase):
    """The example was copied from the CoreUI demo; nothing of CoreUI may be left but comments that credit it."""

    #: a line that credits the demo this one was copied from ("copied from / after / replacing the CoreUI demo"),
    #: not one that describes something as CoreUI's ("styled like CoreUI's sidebar")
    CREDIT = re.compile(r"\b(copied from|from|after|replacing)\s+the CoreUI demo\b")

    def test_no_coreui_left(self):
        root = Path(settings.BASE_DIR)
        offenders = []
        for path in sorted(root.rglob("*")):
            # migrations keep old help texts as history; this file names CoreUI's classes to assert they are gone
            if (
                path.suffix not in {".py", ".html", ".css", ".js"}
                or "migrations" in path.parts
                or path == Path(__file__).resolve()
            ):
                continue
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if "coreui" in line.lower() and not self.CREDIT.search(line):
                    offenders.append(f"{path.relative_to(root)}:{number}: {line.strip()}")
        self.assertEqual(offenders, [])


class BrandTests(SimpleTestCase):
    """acme.css: the compiled stylesheet keeps Bootstrap's blue in some rules; the brand restates them (A13)."""

    def css(self):
        return Path(finders.find("acme/acme.css")).read_text()

    def test_compiled_primary_rules_are_restated(self):
        css = self.css()
        for selector in (
            ".btn-primary",
            ".btn-outline-primary",
            '[data-bs-theme="dark"] .btn-outline-primary',
            ".form-control:focus",
            ".form-select:focus",
            ".form-check-input:focus",
            ".form-check-input:checked",
            ".nav-link:focus-visible",
            ".app-sidebar .nav-link.active",
        ):
            with self.subTest(selector=selector):
                self.assertRegex(css, rf"(?m)^{re.escape(selector)}(,| \{{)")
        self.assertNotIn("13, 110, 253", css)  # Bootstrap's blue
        self.assertNotIn("0d6efd", css.lower())

    def test_focus_ring_follows_the_colour_mode(self):
        css = self.css()
        light = css[css.index(":root,") :]
        dark = css[css.index('[data-bs-theme="dark"] {') :]
        self.assertIn("--bs-focus-ring-color: rgba(160, 82, 45, 0.25);", light[: light.index("}")])
        self.assertIn("--bs-focus-ring-color: rgba(198, 151, 129, 0.25);", dark[: dark.index("}")])
