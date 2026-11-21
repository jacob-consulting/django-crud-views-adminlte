from django.apps import AppConfig


class CrudViewsAdminlteConfig(AppConfig):
    """AdminLTE theme for django-crud-views, on top of the adminlte-django page shell (django_adminlte4).

    Listed before ``crud_views`` in INSTALLED_APPS so its templates shadow upstream's. Registration of icons, button
    classes and assets follows in later tasks.
    """

    name = "crud_views_adminlte"
    verbose_name = "django-crud-views AdminLTE theme"

    def ready(self):
        pass
