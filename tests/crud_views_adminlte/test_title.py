"""The page <title> built by cv_adminlte_title: markup from crud_views is reduced to text, plain names are kept."""

from types import SimpleNamespace

from django.utils.safestring import mark_safe

from crud_views_adminlte.templatetags.crud_views_adminlte import cv_adminlte_title


def test_markup_header_is_reduced_to_text():
    view = SimpleNamespace(cv_header=mark_safe('<i class="bi bi-eye"></i> Details'))
    assert cv_adminlte_title({"view": view}) == "Details"


def test_plain_owner_name_keeps_angle_brackets():
    # an object name is text: "<b>A & B</b>" is what the user typed, not markup to strip (the template escapes it)
    view = SimpleNamespace(cv_header=mark_safe("Details"))
    navbar = {"label": "<b>A & B</b>", "items": []}
    assert cv_adminlte_title({"view": view, "cv_navbar": navbar}) == "Details · <b>A & B</b>"
