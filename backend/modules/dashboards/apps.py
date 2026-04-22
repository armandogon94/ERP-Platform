from django.apps import AppConfig


class DashboardsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.dashboards"
    label = "dashboards"
    verbose_name = "Dashboards"

    def ready(self):
        # Import the registry module so all @register_data_source decorators run.
        from modules.dashboards import data_sources  # noqa: F401
