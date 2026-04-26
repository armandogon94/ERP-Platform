from django.apps import AppConfig


class CalendarConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.calendar"
    label = "calendar_module"
    verbose_name = "Calendar"

    def ready(self):
        # Wire post_save handlers for outbound webhook emission (Slice 22).
        from modules.calendar import signals  # noqa: F401
