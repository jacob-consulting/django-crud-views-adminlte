# Demo

**Acme Roasters** is a back office for a specialty coffee roastery, built with django-crud-views and themed by this
package on top of adminlte-django. It covers customers with per-object permissions (Guardian), addresses, orders with a
workflow, a line formset and bulk actions, subscriptions, polymorphic products, ordered categories, green coffee lots,
cupping sessions with score formsets, roast batches and shipments from a fake courier API. Every crud_views page has a
"Show code" panel, and `/theming/` shows how the theme is built.

The app code never imports the theme: it is a plain django-crud-views project with `crud_views_adminlte` in
`INSTALLED_APPS`, a sidebar in `ADMINLTE["menu"]` (`example/config/menu.py`) that uses `viewset` entries, and the brand
(sienna `#a0522d`) in `example/static/acme/acme.css`, the one place the host's compiled stylesheet needs a rule per
component (tracker A13).

There is no public demo yet: run it locally.

## Locally

```shell
git clone https://github.com/jacob-consulting/django-crud-views-adminlte.git
cd django-crud-views-adminlte
task up      # uv sync, migrate, superuser admin/admin, seed the demo data, runserver
```

Open <http://127.0.0.1:8000/> and sign in. See [Development](development.md) for running it without Task, and for the
sibling checkouts of django-crud-views that local development uses.

## Accounts

| Account | Password | Role |
|---|---|---|
| `alex` | `demo` | Owner: everything, including django-crud-views' manage pages |
| `sam` | `demo` | Account manager: only the customers granted to them |
| `kim` | `demo` | Head roaster: lots, cupping and roasting; customers read-only |
| `admin` | `admin` | Superuser created by `task up`: everything, plus `/admin/` |

Compare the sidebars of the accounts: it shows what each may open. Sam still sees Customers without holding a view
permission (tracker C7). Kim is offered only the bulk action "Mark roasted", not "Cancel orders" (tracker C10, fixed
upstream).

## Demo data

`seed_demo` builds one coherent world from a fixed random seed. It refuses to run when the demo accounts already exist;
`seed_demo --reset` rebuilds it. `seed_demo_showcase` adds forty items for the form showcase and is not safely
re-runnable (the Taskfile guards it).

## Settings from the environment

`DJANGO_SECRET_KEY`, `DJANGO_DEBUG` (`1`/`0`, default `1`), `DJANGO_ALLOWED_HOSTS` (comma-separated, default
`localhost,127.0.0.1`) and `CRUD_VIEWS_MANAGE_VIEWS_ENABLED` (default `yes`: only active members of the
`CRUD_VIEWS_MANAGE` group, `alex` after seeding, may open the manage pages). The built-in secret key is for local
development only.
