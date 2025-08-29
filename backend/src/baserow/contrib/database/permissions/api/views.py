"""
API views for the granular permission system.
"""

from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from baserow.api.decorators import validate_body
from baserow.api.pagination import PageNumberPagination
from baserow.api.schemas import get_error_schema
from baserow.contrib.database.fields.models import Field
from baserow.contrib.database.table.models import Table
from baserow.contrib.database.views.models import View
from baserow.core.models import Workspace

from ..exceptions import (
    CustomRoleAlreadyExists,
    CustomRoleNotFound,
)
from ..handler import GranularPermissionHandler
from ..models import (
    APIKey,
    ConditionalPermission,
    CustomRole,
    FieldPermission,
    PermissionLevel,
    RowPermission,
    TablePermission,
    UserRole,
    ViewPermission,
)
from .serializers import (
    APIKeyCreateSerializer,
    APIKeySerializer,
    BulkPermissionUpdateSerializer,
    ConditionalPermissionSerializer,
    CustomRoleCreateSerializer,
    CustomRoleSerializer,
    FieldPermissionSerializer,
    PermissionLevelChoicesSerializer,
    PermissionSummarySerializer,
    RowPermissionSerializer,
    TablePermissionSerializer,
    UserRoleSerializer,
    ViewPermissionSerializer,
)

User = get_user_model()


class CustomRoleViewSet(ModelViewSet):
    """ViewSet for managing custom roles."""
    
    serializer_class = CustomRoleSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        """Get custom roles for the user's workspaces."""
        workspace_id = self.kwargs.get("workspace_id")
        if workspace_id:
            return CustomRole.objects.filter(workspace_id=workspace_id)
        return CustomRole.objects.filter(
            workspace__workspaceuser__user=self.request.user
        )
    
    def get_serializer_class(self):
        """Get appropriate serializer class."""
        if self.action == "create":
            return CustomRoleCreateSerializer
        return CustomRoleSerializer
    
    @validate_body(CustomRoleCreateSerializer)
    def create(self, request, workspace_id):
        """Create a new custom role."""
        workspace = get_object_or_404(Workspace, id=workspace_id)
        
        # Check if user has permission to manage workspace
        # This would integrate with existing workspace permission checks
        
        handler = GranularPermissionHandler()
        
        try:
            role = handler.create_custom_role(
                workspace=workspace,
                created_by=request.user,
                **request.data
            )
            serializer = CustomRoleSerializer(role)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except CustomRoleAlreadyExists as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, pk=None, workspace_id=None):
        """Update a custom role."""
        role = self.get_object()
        handler = GranularPermissionHandler()
        
        updated_role = handler.update_custom_role(role, **request.data)
        serializer = CustomRoleSerializer(updated_role)
        return Response(serializer.data)
    
    def destroy(self, request, pk=None, workspace_id=None):
        """Delete a custom role."""
        role = self.get_object()
        handler = GranularPermissionHandler()
        
        handler.delete_custom_role(role)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=["post"])
    def assign_user(self, request, pk=None, workspace_id=None):
        """Assign role to a user."""
        role = self.get_object()
        workspace = get_object_or_404(Workspace, id=workspace_id)
        user_id = request.data.get("user_id")
        
        if not user_id:
            return Response(
                {"error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = get_object_or_404(User, id=user_id)
        handler = GranularPermissionHandler()
        
        user_role = handler.assign_role_to_user(
            user=user,
            role=role,
            workspace=workspace,
            assigned_by=request.user
        )
        
        serializer = UserRoleSerializer(user_role)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=["post"])
    def remove_user(self, request, pk=None, workspace_id=None):
        """Remove role from a user."""
        role = self.get_object()
        workspace = get_object_or_404(Workspace, id=workspace_id)
        user_id = request.data.get("user_id")
        
        if not user_id:
            return Response(
                {"error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = get_object_or_404(User, id=user_id)
        handler = GranularPermissionHandler()
        
        handler.remove_role_from_user(
            user=user,
            role=role,
            workspace=workspace
        )
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class TablePermissionViewSet(ModelViewSet):
    """ViewSet for managing table permissions."""
    
    serializer_class = TablePermissionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        """Get table permissions for the workspace."""
        workspace_id = self.kwargs.get("workspace_id")
        if workspace_id:
            return TablePermission.objects.filter(
                table__database__workspace_id=workspace_id
            )
        return TablePermission.objects.none()
    
    @validate_body(TablePermissionSerializer)
    def create(self, request, workspace_id):
        """Create a table permission."""
        handler = GranularPermissionHandler()
        
        table_id = request.data.get("table")
        table = get_object_or_404(Table, id=table_id)
        
        user_id = request.data.get("user")
        role_id = request.data.get("role")
        
        user = get_object_or_404(User, id=user_id) if user_id else None
        role = get_object_or_404(CustomRole, id=role_id) if role_id else None
        
        permission = handler.set_table_permission(
            table=table,
            user=user,
            role=role,
            **{k: v for k, v in request.data.items() if k not in ["table", "user", "role"]}
        )
        
        serializer = TablePermissionSerializer(permission)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FieldPermissionViewSet(ModelViewSet):
    """ViewSet for managing field permissions."""
    
    serializer_class = FieldPermissionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        """Get field permissions for the workspace."""
        workspace_id = self.kwargs.get("workspace_id")
        if workspace_id:
            return FieldPermission.objects.filter(
                field__table__database__workspace_id=workspace_id
            )
        return FieldPermission.objects.none()
    
    @validate_body(FieldPermissionSerializer)
    def create(self, request, workspace_id):
        """Create a field permission."""
        handler = GranularPermissionHandler()
        
        field_id = request.data.get("field")
        field = get_object_or_404(Field, id=field_id)
        
        user_id = request.data.get("user")
        role_id = request.data.get("role")
        
        user = get_object_or_404(User, id=user_id) if user_id else None
        role = get_object_or_404(CustomRole, id=role_id) if role_id else None
        
        permission = handler.set_field_permission(
            field=field,
            user=user,
            role=role,
            **{k: v for k, v in request.data.items() if k not in ["field", "user", "role"]}
        )
        
        serializer = FieldPermissionSerializer(permission)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ViewPermissionViewSet(ModelViewSet):
    """ViewSet for managing view permissions."""
    
    serializer_class = ViewPermissionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        """Get view permissions for the workspace."""
        workspace_id = self.kwargs.get("workspace_id")
        if workspace_id:
            return ViewPermission.objects.filter(
                view__table__database__workspace_id=workspace_id
            )
        return ViewPermission.objects.none()
    
    @validate_body(ViewPermissionSerializer)
    def create(self, request, workspace_id):
        """Create a view permission."""
        handler = GranularPermissionHandler()
        
        view_id = request.data.get("view")
        view = get_object_or_404(View, id=view_id)
        
        user_id = request.data.get("user")
        role_id = request.data.get("role")
        
        user = get_object_or_404(User, id=user_id) if user_id else None
        role = get_object_or_404(CustomRole, id=role_id) if role_id else None
        
        permission = handler.set_view_permission(
            view=view,
            user=user,
            role=role,
            **{k: v for k, v in request.data.items() if k not in ["view", "user", "role"]}
        )
        
        serializer = ViewPermissionSerializer(permission)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ConditionalPermissionViewSet(ModelViewSet):
    """ViewSet for managing conditional permissions."""
    
    serializer_class = ConditionalPermissionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        """Get conditional permissions for the workspace."""
        workspace_id = self.kwargs.get("workspace_id")
        if workspace_id:
            return ConditionalPermission.objects.filter(
                table__database__workspace_id=workspace_id
            )
        return ConditionalPermission.objects.none()
    
    @validate_body(ConditionalPermissionSerializer)
    def create(self, request, workspace_id):
        """Create a conditional permission."""
        handler = GranularPermissionHandler()
        
        table_id = request.data.get("table")
        table = get_object_or_404(Table, id=table_id)
        
        condition_field_id = request.data.get("condition_field")
        condition_field = get_object_or_404(Field, id=condition_field_id)
        
        user_id = request.data.get("user")
        role_id = request.data.get("role")
        
        user = get_object_or_404(User, id=user_id) if user_id else None
        role = get_object_or_404(CustomRole, id=role_id) if role_id else None
        
        permission = handler.create_conditional_permission(
            table=table,
            condition_field=condition_field,
            user=user,
            role=role,
            **{k: v for k, v in request.data.items() 
               if k not in ["table", "condition_field", "user", "role"]}
        )
        
        serializer = ConditionalPermissionSerializer(permission)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class APIKeyViewSet(ModelViewSet):
    """ViewSet for managing API keys."""
    
    serializer_class = APIKeySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        """Get API keys for the workspace."""
        workspace_id = self.kwargs.get("workspace_id")
        if workspace_id:
            return APIKey.objects.filter(workspace_id=workspace_id)
        return APIKey.objects.none()
    
    def get_serializer_class(self):
        """Get appropriate serializer class."""
        if self.action == "create":
            return APIKeyCreateSerializer
        return APIKeySerializer
    
    @validate_body(APIKeyCreateSerializer)
    def create(self, request, workspace_id):
        """Create a new API key."""
        workspace = get_object_or_404(Workspace, id=workspace_id)
        handler = GranularPermissionHandler()
        
        api_key = handler.create_api_key(
            workspace=workspace,
            created_by=request.user,
            **request.data
        )
        
        # Set scope tables and views if provided
        if "scope_tables" in request.data:
            api_key.scope_tables.set(request.data["scope_tables"])
        if "scope_views" in request.data:
            api_key.scope_views.set(request.data["scope_views"])
        
        serializer = APIKeySerializer(api_key)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PermissionManagementViewSet(ModelViewSet):
    """ViewSet for general permission management operations."""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=["get"])
    def permission_levels(self, request, workspace_id=None):
        """Get available permission levels."""
        choices = [
            {"value": choice[0], "label": choice[1]}
            for choice in PermissionLevel.choices
        ]
        serializer = PermissionLevelChoicesSerializer(choices, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def user_summary(self, request, workspace_id=None):
        """Get comprehensive permission summary for a user."""
        workspace = get_object_or_404(Workspace, id=workspace_id)
        user_id = request.query_params.get("user_id")
        
        if not user_id:
            return Response(
                {"error": "user_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = get_object_or_404(User, id=user_id)
        handler = GranularPermissionHandler()
        
        summary = handler.get_user_permissions_summary(user, workspace)
        serializer = PermissionSummarySerializer(summary)
        return Response(serializer.data)
    
    @action(detail=False, methods=["post"])
    @validate_body(BulkPermissionUpdateSerializer)
    def bulk_update(self, request, workspace_id=None):
        """Bulk update permissions."""
        workspace = get_object_or_404(Workspace, id=workspace_id)
        permissions = request.data.get("permissions", [])
        
        handler = GranularPermissionHandler()
        results = []
        
        with transaction.atomic():
            for permission_data in permissions:
                try:
                    permission_type = permission_data.get("type")
                    
                    if permission_type == "table":
                        # Handle table permission update
                        table = get_object_or_404(Table, id=permission_data.get("table_id"))
                        user = get_object_or_404(User, id=permission_data.get("user_id")) if permission_data.get("user_id") else None
                        role = get_object_or_404(CustomRole, id=permission_data.get("role_id")) if permission_data.get("role_id") else None
                        
                        permission = handler.set_table_permission(
                            table=table,
                            user=user,
                            role=role,
                            **{k: v for k, v in permission_data.items() 
                               if k not in ["type", "table_id", "user_id", "role_id"]}
                        )
                        results.append({"type": "table", "id": permission.id, "status": "success"})
                        
                    elif permission_type == "field":
                        # Handle field permission update
                        field = get_object_or_404(Field, id=permission_data.get("field_id"))
                        user = get_object_or_404(User, id=permission_data.get("user_id")) if permission_data.get("user_id") else None
                        role = get_object_or_404(CustomRole, id=permission_data.get("role_id")) if permission_data.get("role_id") else None
                        
                        permission = handler.set_field_permission(
                            field=field,
                            user=user,
                            role=role,
                            **{k: v for k, v in permission_data.items() 
                               if k not in ["type", "field_id", "user_id", "role_id"]}
                        )
                        results.append({"type": "field", "id": permission.id, "status": "success"})
                        
                    # Add similar handling for view and row permissions
                    
                except Exception as e:
                    results.append({
                        "type": permission_data.get("type"),
                        "status": "error",
                        "error": str(e)
                    })
        
        return Response({"results": results})
    
    @action(detail=False, methods=["post"])
    def check_permission(self, request, workspace_id=None):
        """Check if a user has a specific permission."""
        workspace = get_object_or_404(Workspace, id=workspace_id)
        user_id = request.data.get("user_id")
        operation = request.data.get("operation")
        resource_type = request.data.get("resource_type")
        resource_id = request.data.get("resource_id")
        
        if not all([user_id, operation, resource_type, resource_id]):
            return Response(
                {"error": "user_id, operation, resource_type, and resource_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = get_object_or_404(User, id=user_id)
        handler = GranularPermissionHandler()
        
        has_permission = False
        
        if resource_type == "table":
            table = get_object_or_404(Table, id=resource_id)
            has_permission = handler.check_table_permission(user, table, operation)
        elif resource_type == "field":
            field = get_object_or_404(Field, id=resource_id)
            has_permission = handler.check_field_permission(user, field, operation)
        # Add similar checks for view and row permissions
        
        return Response({"has_permission": has_permission})