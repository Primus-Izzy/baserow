"""
Django app configuration for the granular permission system.
"""

from django.apps import AppConfig


class PermissionsConfig(AppConfig):
    """App configuration for granular permissions."""
    
    name = "baserow.contrib.database.permissions"
    label = "database_permissions"
    verbose_name = "Database Granular Permissions"
    
    def ready(self):
        """Register permission manager when app is ready."""
        from baserow.core.registries import permission_manager_type_registry
        from .permission_manager import GranularPermissionManagerType
        
        permission_manager_type_registry.register(GranularPermissionManagerType())