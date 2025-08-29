from django.apps import AppConfig


class CollaborationConfig(AppConfig):
    name = "baserow.contrib.database.collaboration"

    def ready(self):
        from baserow.contrib.database.collaboration.ws_pages import (
            CollaborationRowPageType,
            CollaborationTablePageType,
            CollaborationViewPageType,
        )
        from baserow.ws.registries import page_registry

        page_registry.register(CollaborationTablePageType())
        page_registry.register(CollaborationViewPageType())
        page_registry.register(CollaborationRowPageType())