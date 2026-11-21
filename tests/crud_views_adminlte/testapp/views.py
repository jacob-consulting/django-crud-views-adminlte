import django_tables2 as tables
from crispy_forms.layout import Row
from crud_views.lib.breadcrumb import CrudViewBreadcrumbMixin
from crud_views.lib.crispy import Column6, CrispyDeleteForm, CrispyModelForm, CrispyViewMixin
from crud_views.lib.navbar import CrudViewNavBarMixin, NavBar, NavItem
from crud_views.lib.table import LinkChildColumn, LinkDetailColumn, Table
from crud_views.lib.views import (
    CreateViewParentMixin,
    CreateViewPermissionRequired,
    DeleteViewPermissionRequired,
    DetailViewPermissionRequired,
    ListViewPermissionRequired,
    ListViewTableMixin,
    MessageMixin,
    UpdateViewPermissionRequired,
)
from crud_views.lib.viewset import ParentViewSet, ViewSet

from .models import Author, Book

# --------------------------------------------------------------------------- Author (top level)

cv_author = ViewSet(model=Author, name="author", icon_header="bi:person-badge")

# ViewSet Navigation: the author's detail page and its books share an owner header with section tabs.
author_navbar = NavBar(viewset="author", items=[NavItem(key="detail"), NavItem(child="book")])


class AuthorNavbarMixin(CrudViewNavBarMixin):
    cv_navbar = author_navbar


class AuthorForm(CrispyModelForm):
    class Meta:
        model = Author
        fields = ["name", "country"]

    def get_layout_fields(self):
        return Row(Column6("name"), Column6("country"))


class AuthorTable(Table):
    id = LinkDetailColumn()
    name = tables.Column()
    country = tables.Column()
    books = LinkChildColumn(name="book", verbose_name="Books", attrs=Table.ca.w10)


class AuthorListView(CrudViewBreadcrumbMixin, ListViewTableMixin, ListViewPermissionRequired):
    cv_viewset = cv_author
    cv_paragraph_template_code = "Everyone who writes for us."
    table_class = AuthorTable


class AuthorDetailView(AuthorNavbarMixin, CrudViewBreadcrumbMixin, DetailViewPermissionRequired):
    cv_viewset = cv_author


class AuthorCreateView(CrudViewBreadcrumbMixin, CrispyViewMixin, MessageMixin, CreateViewPermissionRequired):
    cv_viewset = cv_author
    form_class = AuthorForm  # upstream's create message snippet: Created Author <strong>…</strong>


class AuthorUpdateView(CrudViewBreadcrumbMixin, CrispyViewMixin, MessageMixin, UpdateViewPermissionRequired):
    cv_viewset = cv_author
    form_class = AuthorForm
    cv_message_template_code = "Updated {{ object }}"


class AuthorDeleteView(CrudViewBreadcrumbMixin, CrispyViewMixin, MessageMixin, DeleteViewPermissionRequired):
    cv_viewset = cv_author
    form_class = CrispyDeleteForm
    cv_message_template_code = "Deleted {{ object }}"


# --------------------------------------------------------------------------- Book (child of Author)

cv_book = ViewSet(model=Book, name="book", parent=ParentViewSet(name="author"))


class BookForm(CrispyModelForm):
    class Meta:
        model = Book
        fields = ["title", "year"]

    def get_layout_fields(self):
        return Row(Column6("title"), Column6("year"))


class BookTable(Table):
    id = LinkDetailColumn()
    title = tables.Column()
    year = tables.Column()


class BookListView(AuthorNavbarMixin, CrudViewBreadcrumbMixin, ListViewTableMixin, ListViewPermissionRequired):
    cv_viewset = cv_book
    table_class = BookTable


class BookDetailView(CrudViewBreadcrumbMixin, DetailViewPermissionRequired):
    cv_viewset = cv_book


class BookCreateView(
    CrudViewBreadcrumbMixin, CrispyViewMixin, MessageMixin, CreateViewParentMixin, CreateViewPermissionRequired
):
    cv_viewset = cv_book
    form_class = BookForm
    cv_message_template_code = "Created {{ object }}"


class BookUpdateView(CrudViewBreadcrumbMixin, CrispyViewMixin, MessageMixin, UpdateViewPermissionRequired):
    cv_viewset = cv_book
    form_class = BookForm
    cv_message_template_code = "Updated {{ object }}"


class BookDeleteView(CrudViewBreadcrumbMixin, CrispyViewMixin, MessageMixin, DeleteViewPermissionRequired):
    cv_viewset = cv_book
    form_class = CrispyDeleteForm
    cv_message_template_code = "Deleted {{ object }}"
