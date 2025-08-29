from django.apps import AppConfig


class SecurityConfig(AppConfig):
    name = "baserow.contrib.security"
    label = "baserow_security"

    def ready(self):
        from . import signals  # noqa: F401