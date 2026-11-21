"""Template filters of the demo's own host pages: initials avatars per user, and semantic icons as CSS classes."""

from config.icons import icon_class as _icon_class
from django import template
from sales.models import AVATAR_COLORS

register = template.Library()


@register.filter
def initials(user):
    """Two-letter initials from the user's name, falling back to the username."""
    name = user.get_full_name().split()
    if len(name) >= 2:
        return (name[0][0] + name[-1][0]).upper()
    return user.get_username()[:2].upper()


@register.filter
def avatar_color(user):
    """A stable Bootstrap theme colour per user (bg-<colour>-subtle text-<colour>-emphasis)."""
    return AVATAR_COLORS[(user.pk or 0) % len(AVATAR_COLORS)]


@register.filter
def icon_class(key):
    """The CSS class of a semantic icon (config.icons), for an adminlte-django widget's ``icon`` prop."""
    return _icon_class(key)
