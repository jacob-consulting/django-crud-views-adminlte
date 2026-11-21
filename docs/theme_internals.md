# Theme internals

How the theme maps django-crud-views onto adminlte-django. Task 9 completes this page (block mapping, overrides and
their tracker IDs); the sections below are recorded as they are decided.

## Tables

**Choice:** `DJANGO_TABLES2_TEMPLATE = "crud_views/table/bootstrap5.html"`, crud_views' own table template, not the
host's `django_tables2/adminlte.html`.

**Why:** adminlte-django's template wraps a table in a card (`card-body p-0 table-responsive`, pagination in the card
footer), but it extends django-tables2's `django_tables2/bootstrap5.html`, not crud_views' template, and cannot be
pointed at another base. Under it crud_views list pages lose the sort-direction icon of the sorted column, the
pagination icons and their hidden labels, the active page as `aria-current="page"` and the disabled previous/next
items (tracker A19, checked in the browser on the demo's orders list). The bulk select column, the toolbar, the empty
state and the absence of a card in a card were fine under either template; the lost sort and pagination markup
decided it.

**Consequences:**

- Adopters must set `DJANGO_TABLES2_TEMPLATE = "crud_views/table/bootstrap5.html"` in their settings (tracker A19);
  TODO Task 9: put this line in the installation page's settings block.

- List tables sit on the page background, as in crud_views' Bootstrap theme, not in an AdminLTE card.
- crud_views' wrapper `div.table-container` has no class key and is not `.table-responsive`; the theme's stylesheet
  lets it scroll sideways (`position: relative; overflow-x: auto`, tracker C9), so a wide list does not push the page
  sideways on a phone. Row action menus open with Popper's `fixed` strategy and are not clipped by the scroller.
- The sorted column has no `aria-sort`, and a table with a `prefix` shows no sort icon: both are fixed upstream by
  django-crud-views #393, not yet merged (tracker C8). The theme keeps no copy of the `table.thead` block meanwhile;
  `test_sorted_column_aria_sort` is a strict expected failure until the pin bump.
- Revisit after #393: if a card frame is wanted, a theme template extending `crud_views/table/bootstrap5.html` and
  overriding only `table-wrapper` with the host's card markup would combine both (logged with A19, not done).

## Bulk selection

Bulk selection (django-crud-views #392) needs nothing beyond the class registry:

- The seven `bulk:*` keys (`buttons.py`) are plain Bootstrap 5.3 classes, checked in the browser on table and cards,
  light and dark, at 375px; the `bulk` label mode stays upstream's default (`both`).
- The toolbar renders above the table wrapper or the card grid; `crud_views/js/bulk.js` comes with `{% cv_js %}`.
- The review page (`view_bulk_form.html`) renders in the theme's page like any custom form view; its blocked records
  are a `{% cv_alert "warning" %}`.
- Result and warning messages go through the host's messages partial, once, like every other message (tracker C2).
