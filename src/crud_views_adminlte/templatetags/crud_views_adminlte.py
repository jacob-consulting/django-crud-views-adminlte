"""Theme tags for crud_views_adminlte/page.html."""

from html import unescape

from django import template
from django.utils.html import strip_tags
from django.utils.safestring import SafeData
from django_adminlte4.templatetags.adminlte import adminlte_title

register = template.Library()


def _text(value) -> str:
    """Plain text of a snippet, whitespace collapsed: markup (a safe string) has its tags stripped and entities
    decoded; a plain string (an object's name) is text already and keeps any angle brackets it contains."""
    if isinstance(value, SafeData):
        value = unescape(strip_tags(str(value)))
    return " ".join(str(value).split())


@register.simple_tag(takes_context=True)
def cv_adminlte_heading_repeats_tab(context) -> bool:
    """True when a ViewSet Navigation bar is shown and the view's heading says the same as its active tab.

    Reads the documented ``cv_navbar`` mapping (``items``, ``active``, ``label``) and the view's ``cv_header``.
    Exact text after stripping tags and collapsing whitespace: a near miss keeps the heading.
    """
    navbar, view = context.get("cv_navbar"), context.get("view")
    if not navbar or view is None:
        return False
    active = [item for item in navbar["items"] if item["active"]]
    return bool(active) and _text(view.cv_header) == _text(active[0]["label"])


@register.simple_tag(takes_context=True)
def cv_adminlte_title(context) -> str:
    """The <title>: the view's header (plus the ViewSet Navigation owner), through the host's title prefix/postfix."""
    view = context.get("view")
    title = _text(view.cv_header) if view is not None else ""
    navbar = context.get("cv_navbar")
    if navbar:
        title = " · ".join(part for part in (title, _text(navbar["label"])) if part)
    return adminlte_title(title or None)
