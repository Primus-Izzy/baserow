from django.apps import AppConfig


class IntegrationsConfig(AppConfig):
    name = "baserow.contrib.integrations"
    
    def ready(self):
        from . import signals  # noqa: F401