"""Bulk selection on authors (upstream #392): a table and a card source and two destinations, on their own ViewSet so
the plain author pages stay as they are."""

import django_tables2 as tables
from crud_views.lib.bulk import BulkFormViewPermissionRequired, BulkSelectionMixin
from crud_views.lib.crispy import CrispyForm
from crud_views.lib.table import Table
from crud_views.lib.views import CardListViewPermissionRequired, ListViewPermissionRequired, ListViewTableMixin
from crud_views.lib.viewset import ViewSet
from django import forms

from .models import Author

cv_bulk_author = ViewSet(model=Author, name="bulk_author", prefix="bulk-author", icon_header="bi:person-badge")


class BulkAuthorTable(Table):
    name = tables.Column()
    country = tables.Column()

    class Meta:
        prefix = "a-"  # a prefixed table: its sort parameter is a-sort


class BulkAuthorListView(BulkSelectionMixin, ListViewTableMixin, ListViewPermissionRequired):
    cv_viewset = cv_bulk_author
    table_class = BulkAuthorTable
    cv_bulk_actions = ("clear_country", "set_country")
    cv_list_actions = []
    cv_context_actions = ["card"]


class BulkAuthorCardView(BulkSelectionMixin, CardListViewPermissionRequired):
    cv_viewset = cv_bulk_author
    cv_bulk_actions = ("clear_country",)
    cv_context_actions = ["list"]
    cv_card_actions = []


class ClearCountryView(BulkFormViewPermissionRequired):
    """No input: the review lists eligible and blocked authors, then Confirm."""

    cv_viewset = cv_bulk_author
    cv_key = "clear_country"
    cv_path = "clear-country"
    cv_permission = "change"
    cv_icon_action = "bi:eraser"
    cv_action_label_template_code = "Clear the country of the selected authors"
    cv_action_short_label_template_code = "Clear country"
    cv_success_key = "list"
    cv_success_keys = ["list", "card"]

    def cv_bulk_check(self, obj):
        return [] if obj.country else ["No country to clear."]

    def cv_form_valid(self, context):
        for author in self.cv_bulk_objects:
            author.country = ""
            author.save(using=self.cv_get_db_alias(), update_fields=["country"])


class SetCountryForm(CrispyForm):
    submit_label = "Set"
    country = forms.CharField(max_length=100)

    def get_layout_fields(self):
        return ["country"]


class SetCountryView(BulkFormViewPermissionRequired):
    """With input: the review shows the action form."""

    cv_viewset = cv_bulk_author
    cv_key = "set_country"
    cv_path = "set-country"
    cv_permission = "change"
    cv_icon_action = "bi:globe"
    cv_action_label_template_code = "Set the country of the selected authors"
    cv_action_short_label_template_code = "Set country"
    form_class = SetCountryForm
    cv_success_key = "list"
    cv_message_template_code = "Country set for {{ view.cv_bulk_objects|length }} authors."

    def cv_form_valid(self, context):
        country = context["form"].cleaned_data["country"]
        for author in self.cv_bulk_objects:
            author.country = country
            author.save(using=self.cv_get_db_alias(), update_fields=["country"])
