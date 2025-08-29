"""
URL configuration for the granular permission system API.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    APIKeyViewSet,
    ConditionalPermissionViewSet,
    CustomRoleViewSet,
    FieldPermissionViewSet,
    PermissionManagementViewSet,
    TablePermissionViewSet,
    ViewPermissionViewSet,
)

app_name = "baserow.contrib.database.permissions.api"

router = DefaultRouter()
router.register("custom-roles", CustomRoleViewSet, basename="custom_roles")
router.register("table-permissions", TablePermissionViewSet, basename="table_permissions")
router.register("field-permissions", FieldPermissionViewSet, basename="field_permissions")
router.register("view-permissions", ViewPermissionViewSet, basename="view_permissions")
router.register("conditional-permissions", ConditionalPermissionViewSet, basename="conditional_permissions")
router.register("api-keys", APIKeyViewSet, basename="api_keys")
router.register("management", PermissionManagementViewSet, basename="permission_management")

urlpatterns = [
    path("", include(router.urls)),
]