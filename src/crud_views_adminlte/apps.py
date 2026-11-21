from django.apps import AppConfig


class CrudViewsAdminlteConfig(AppConfig):
    """AdminLTE theme for django-crud-views, on top of the adminlte-django page shell (django_adminlte4).

    Listed before ``crud_views`` in INSTALLED_APPS so its templates shadow upstream's. Registration of icons, button
    classes and assets are registered in ``ready()``; the icons are Bootstrap Icons through upstream's built-in ``bi``
    library, so no renderer is registered.
    """

    name = "crud_views_adminlte"
    verbose_name = "django-crud-views AdminLTE theme"

    def ready(self):
        from crud_views.lib.assets import register_assets
        from crud_views.lib.button_classes import register_button_classes
        from crud_views.lib.icons import register_icons
        from crud_views.lib.view.label_mode import register_label_mode_defaults

        import crud_views_adminlte.checks  # noqa: F401
        from crud_views_adminlte.buttons import ADMINLTE_BUTTON_CLASSES
        from crud_views_adminlte.icons import ADMINLTE_ICONS

        register_icons(ADMINLTE_ICONS)
        register_label_mode_defaults({"form": "both"})
        register_button_classes(
            {
                key: value
                for key, value in ADMINLTE_BUTTON_CLASSES.items()
                if not key.startswith("workflow:") or self.apps.is_installed("crud_views_workflow")
            }
        )
        # Stock Bootstrap 5 provides the JS; the theme adds no scripts.
        register_assets("crud_views_adminlte", css=["crud_views_adminlte/crud_views_adminlte.css"])
