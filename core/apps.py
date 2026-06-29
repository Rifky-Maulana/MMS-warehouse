from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "Inti Sistem"

    def ready(self):
        # Daftarkan signal login/logout → Catatan Audit.
        from . import signals  # noqa: F401
