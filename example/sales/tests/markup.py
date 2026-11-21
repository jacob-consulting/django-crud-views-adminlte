"""Where the theme puts things on a crud_views page (crud_views_adminlte/page.html inside adminlte-django's page)."""

import re

from lxml import html as lxml_html

#: the view's subline under its heading (cv_paragraph)
SUBTITLE = '<p class="text-body-secondary mt-1 mb-0">'

HEADING = re.compile(r"<(h[1-6])\b[^>]*>(.*?)</\1>", re.S)


def header(html: str) -> str:
    """The page header: owner and tabs, the view's heading and subline, the breadcrumb and the context buttons."""
    start = html.index('<div class="app-content-header')
    return html[start : html.index('<div class="app-content ', start)]


def headings(html: str) -> list[str]:
    """The text of every heading in the page header, icons left out: the owner's h1 first, then the view's own."""
    root = lxml_html.fromstring(header(html))
    return [" ".join(h.text_content().split()) for h in root.cssselect("h1, h2, h3, h4, h5, h6")]


def page_heading(html: str) -> str | None:
    """The raw markup inside the view's own heading: the last heading of the page header."""
    found = HEADING.findall(header(html))
    return found[-1][1] if found else None
