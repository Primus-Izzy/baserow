"""
Granular permission manager that integrates with Baserow's permission system.

This module provides a permission manager that extends Baserow's existing
permission framework to support granular permissions at table, field, view, and row levels.
"""

from typing import Dict, List, Union

from django.contrib.auth import get_user_model
from django.db.models import Q, QuerySet

from baserow.contrib.database.fields.models import Field
from baserow.contrib.database.table.models import Table
from baserow.contrib.database.views.models import View
from baserow.core.exceptions import PermissionDenied
from baserow.core.models import Workspace
from baserow.core.registries import PermissionManagerType
from baserow.core.subjects import UserSubjectType
from baserow.core.types import PermissionCheck

from .exceptions import (
    InsufficientFieldPermission,
    InsufficientRowPermission,
    InsufficientTablePermission,
    InsufficientViewPermission,
)
from .handler import GranularPermissionHandler
from .models import (
    APIKey,
    ConditionalPermission,
    CustomRole,
    FieldPermission,
    RowPermission,
    TablePermission,
    ViewPermission,
)

User = get_user_model()


class GranularPermissionManagerType(PermissionManagerType):
    """
    Permission manager for granular database permissions.
    
    This manager handles table, field, view, and row-level permissions
    that extend beyond the basic workspace-level permissions.
    """
    
    type = "granular_database"
    supported_actor_types = [UserSubjectType.type]
    
    def __init__(self):
        self.handler = GranularPermissionHandler()
    
    # Operations that require granular permission checks
    GRANULAR_OPERATIONS = [
        # Table operations
        "database.table.read",
        "database.table.update", 
        "database.table.delete",
        "database.table.create_row",
        "database.table.update_row",
        "database.table.delete_row",
        "database.table.create_field",
        "database.table.update_field",
        "database.table.delete_field",
        
        # Field operations
        "database.field.read",
        "database.field.update",
        "database.field.delete",
        
        # View operations
        "database.view.read",
        "database.view.update",
        "database.view.delete",
        "database.view.create",
        
        # Row operations
        "database.row.read",
        "database.row.update",
        "database.row.delete",
        "database.row.create",
    ]

    def check_multiple_permissions(
        self,
        checks: List[PermissionCheck],
        workspace: Workspace = None,
        include_trash: bool = False
    ) -> Dict[PermissionCheck, Union[bool, Exception]]:
        """
        Check multiple permissions using granular permission system.
        
        :param checks: List of permission checks to perform
        :param workspace: Workspace context
        :param include_trash: Whether to include trashed items
        :return: Dictionary mapping checks to results
        """
        result = {}
        
        for check in checks:
            if check.operation_name not in self.GRANULAR_OPERATIONS:
                continue
                
            try:
                # Extract operation details
                operation_parts = check.operation_name.split(".")
                if len(operation_parts) < 3:
                    continue
                    
                resource_type = operation_parts[1]  # table, field, view, row
                operation = operation_parts[2]      # read, update, delete, etc.
                
                # Handle different resource types
                if resource_type == "table":
                    result[check] = self._check_table_permission(
                        check.actor, check.context, operation, workspace
                    )
                elif resource_type == "field":
                    result[check] = self._check_field_permission(
                        check.actor, check.context, operation, workspace
                    )
                elif resource_type == "view":
                    result[check] = self._check_view_permission(
                        check.actor, check.context, operation, workspace
                    )
                elif resource_type == "row":
                    result[check] = self._check_row_permission(
                        check.actor, check.context, operation, workspace
                    )
                    
            except Exception as e:
                result[check] = e
                
        return result

    def _check_table_permission(
        self,
        user: User,
        context,
        operation: str,
        workspace: Workspace
    ) -> Union[bool, Exception]:
        """
        Check table-level permissions.
        
        :param user: User to check permissions for
        :param context: Table or table-related context
        :param operation: Operation to check
        :param workspace: Workspace context
        :return: True if allowed, Exception if denied
        """
        table = self._extract_table_from_context(context)
        if not table:
            return True  # Let other permission managers handle
            
        try:
            # Map operation names to handler operations
            operation_map = {
                "read": "read",
                "update": "update",
                "delete": "delete",
                "create_row": "create",
                "update_row": "update",
                "delete_row": "delete",
                "create_field": "create",
                "update_field": "update",
                "delete_field": "delete",
            }
            
            handler_operation = operation_map.get(operation, operation)
            
            # Get row data if available for conditional permissions
            row_data = getattr(context, 'row_data', None) if hasattr(context, 'row_data') else None
            
            has_permission = self.handler.check_table_permission(
                user, table, handler_operation, row_data
            )
            
            if not has_permission:
                return InsufficientTablePermission(
                    f"User {user.email} lacks {operation} permission on table {table.name}"
                )
                
            return True
            
        except Exception as e:
            return e

    def _check_field_permission(
        self,
        user: User,
        context,
        operation: str,
        workspace: Workspace
    ) -> Union[bool, Exception]:
        """
        Check field-level permissions.
        
        :param user: User to check permissions for
        :param context: Field or field-related context
        :param operation: Operation to check
        :param workspace: Workspace context
        :return: True if allowed, Exception if denied
        """
        field = self._extract_field_from_context(context)
        if not field:
            return True  # Let other permission managers handle
            
        try:
            # Map operation names to handler operations
            operation_map = {
                "read": "read",
                "update": "update",
                "delete": "delete",
            }
            
            handler_operation = operation_map.get(operation, operation)
            
            has_permission = self.handler.check_field_permission(
                user, field, handler_operation
            )
            
            if not has_permission:
                return InsufficientFieldPermission(
                    f"User {user.email} lacks {operation} permission on field {field.name}"
                )
                
            return True
            
        except Exception as e:
            return e

    def _check_view_permission(
        self,
        user: User,
        context,
        operation: str,
        workspace: Workspace
    ) -> Union[bool, Exception]:
        """
        Check view-level permissions.
        
        :param user: User to check permissions for
        :param context: View or view-related context
        :param operation: Operation to check
        :param workspace: Workspace context
        :return: True if allowed, Exception if denied
        """
        view = self._extract_view_from_context(context)
        if not view:
            return True  # Let other permission managers handle
            
        try:
            # Check view permissions using existing ViewPermission model
            user_roles = self.handler.get_user_roles(user, workspace)
            
            # Check direct user permissions
            user_permissions = ViewPermission.objects.filter(
                view=view,
                user=user
            ).first()
            
            # Check role-based permissions
            role_permissions = ViewPermission.objects.filter(
                view=view,
                role__in=user_roles
            )
            
            has_permission = False
            
            if user_permissions:
                if user_permissions.is_hidden:
                    return InsufficientViewPermission(
                        f"View {view.name} is hidden from user {user.email}"
                    )
                has_permission = self._check_view_operation_permission(
                    user_permissions, operation
                )
            
            # Check role permissions
            for role_permission in role_permissions:
                if role_permission.is_hidden:
                    continue
                role_has_permission = self._check_view_operation_permission(
                    role_permission, operation
                )
                has_permission = has_permission or role_has_permission
            
            if not has_permission:
                return InsufficientViewPermission(
                    f"User {user.email} lacks {operation} permission on view {view.name}"
                )
                
            return True
            
        except Exception as e:
            return e

    def _check_row_permission(
        self,
        user: User,
        context,
        operation: str,
        workspace: Workspace
    ) -> Union[bool, Exception]:
        """
        Check row-level permissions.
        
        :param user: User to check permissions for
        :param context: Row or row-related context
        :param operation: Operation to check
        :param workspace: Workspace context
        :return: True if allowed, Exception if denied
        """
        table, row_id = self._extract_row_from_context(context)
        if not table or not row_id:
            return True  # Let other permission managers handle
            
        try:
            user_roles = self.handler.get_user_roles(user, workspace)
            
            # Check row-specific permissions
            row_permissions = RowPermission.objects.filter(
                table=table,
                row_id=row_id
            ).filter(
                Q(user=user) | Q(role__in=user_roles)
            )
            
            has_permission = False
            
            for row_permission in row_permissions:
                if row_permission.is_hidden:
                    return InsufficientRowPermission(
                        f"Row {row_id} is hidden from user {user.email}"
                    )
                
                permission_granted = self._check_row_operation_permission(
                    row_permission, operation
                )
                has_permission = has_permission or permission_granted
            
            # If no specific row permissions, fall back to table permissions
            if not row_permissions.exists():
                return self._check_table_permission(user, table, operation, workspace)
            
            if not has_permission:
                return InsufficientRowPermission(
                    f"User {user.email} lacks {operation} permission on row {row_id}"
                )
                
            return True
            
        except Exception as e:
            return e

    def _check_view_operation_permission(
        self,
        view_permission: ViewPermission,
        operation: str
    ) -> bool:
        """
        Check if a view permission allows a specific operation.
        
        :param view_permission: ViewPermission instance
        :param operation: Operation to check
        :return: True if operation is allowed
        """
        if operation == "read":
            return view_permission.can_read
        elif operation == "update":
            return view_permission.can_update
        elif operation == "delete":
            return view_permission.can_delete
        
        return False

    def _check_row_operation_permission(
        self,
        row_permission: RowPermission,
        operation: str
    ) -> bool:
        """
        Check if a row permission allows a specific operation.
        
        :param row_permission: RowPermission instance
        :param operation: Operation to check
        :return: True if operation is allowed
        """
        if operation == "read":
            return row_permission.can_read
        elif operation == "update":
            return row_permission.can_update
        elif operation == "delete":
            return row_permission.can_delete
        
        return False

    def _extract_table_from_context(self, context) -> Table:
        """Extract Table instance from context."""
        if isinstance(context, Table):
            return context
        elif hasattr(context, 'table'):
            return context.table
        elif hasattr(context, 'database') and hasattr(context.database, 'table_set'):
            # Handle database context
            return None
        return None

    def _extract_field_from_context(self, context) -> Field:
        """Extract Field instance from context."""
        if isinstance(context, Field):
            return context
        elif hasattr(context, 'field'):
            return context.field
        return None

    def _extract_view_from_context(self, context) -> View:
        """Extract View instance from context."""
        if isinstance(context, View):
            return context
        elif hasattr(context, 'view'):
            return context.view
        return None

    def _extract_row_from_context(self, context) -> tuple:
        """Extract table and row_id from context."""
        if hasattr(context, 'table') and hasattr(context, 'row_id'):
            return context.table, context.row_id
        elif hasattr(context, 'table') and hasattr(context, 'id'):
            return context.table, context.id
        return None, None

    def get_permissions_object(self, actor: User, workspace: Workspace = None):
        """
        Get permissions object for frontend use.
        
        :param actor: User to get permissions for
        :param workspace: Workspace context
        :return: Permissions object for frontend
        """
        if not workspace:
            return None
            
        try:
            permissions_summary = self.handler.get_user_permissions_summary(
                actor, workspace
            )
            
            return {
                "granular_permissions": permissions_summary,
                "supported_operations": self.GRANULAR_OPERATIONS,
            }
            
        except Exception:
            return None

    def filter_queryset(
        self,
        actor: User,
        operation_name: str,
        queryset: QuerySet,
        workspace: Workspace = None,
    ) -> QuerySet:
        """
        Filter queryset based on granular permissions.
        
        :param actor: User to filter for
        :param operation_name: Operation being performed
        :param queryset: Queryset to filter
        :param workspace: Workspace context
        :return: Filtered queryset
        """
        if operation_name not in self.GRANULAR_OPERATIONS or not workspace:
            return queryset
            
        try:
            # Extract resource type from operation
            operation_parts = operation_name.split(".")
            if len(operation_parts) < 3:
                return queryset
                
            resource_type = operation_parts[1]
            
            # Apply filters based on resource type
            if resource_type == "table":
                return self._filter_table_queryset(actor, queryset, workspace)
            elif resource_type == "field":
                return self._filter_field_queryset(actor, queryset, workspace)
            elif resource_type == "view":
                return self._filter_view_queryset(actor, queryset, workspace)
            elif resource_type == "row":
                return self._filter_row_queryset(actor, queryset, workspace)
                
        except Exception:
            pass
            
        return queryset

    def _filter_table_queryset(
        self,
        user: User,
        queryset: QuerySet,
        workspace: Workspace
    ) -> QuerySet:
        """Filter table queryset based on permissions."""
        user_roles = self.handler.get_user_roles(user, workspace)
        
        # Get tables with explicit permissions
        permitted_table_ids = set()
        
        # Direct user permissions
        user_table_permissions = TablePermission.objects.filter(
            user=user,
            table__database__workspace=workspace
        ).values_list('table_id', flat=True)
        permitted_table_ids.update(user_table_permissions)
        
        # Role-based permissions
        role_table_permissions = TablePermission.objects.filter(
            role__in=user_roles,
            table__database__workspace=workspace
        ).values_list('table_id', flat=True)
        permitted_table_ids.update(role_table_permissions)
        
        if permitted_table_ids:
            return queryset.filter(id__in=permitted_table_ids)
        
        return queryset

    def _filter_field_queryset(
        self,
        user: User,
        queryset: QuerySet,
        workspace: Workspace
    ) -> QuerySet:
        """Filter field queryset based on permissions."""
        user_roles = self.handler.get_user_roles(user, workspace)
        
        # Exclude hidden fields
        hidden_field_ids = FieldPermission.objects.filter(
            Q(user=user) | Q(role__in=user_roles),
            field__table__database__workspace=workspace,
            is_hidden=True
        ).values_list('field_id', flat=True)
        
        if hidden_field_ids:
            return queryset.exclude(id__in=hidden_field_ids)
        
        return queryset

    def _filter_view_queryset(
        self,
        user: User,
        queryset: QuerySet,
        workspace: Workspace
    ) -> QuerySet:
        """Filter view queryset based on permissions."""
        user_roles = self.handler.get_user_roles(user, workspace)
        
        # Exclude hidden views
        hidden_view_ids = ViewPermission.objects.filter(
            Q(user=user) | Q(role__in=user_roles),
            view__table__database__workspace=workspace,
            is_hidden=True
        ).values_list('view_id', flat=True)
        
        if hidden_view_ids:
            return queryset.exclude(id__in=hidden_view_ids)
        
        return queryset

    def _filter_row_queryset(
        self,
        user: User,
        queryset: QuerySet,
        workspace: Workspace
    ) -> QuerySet:
        """Filter row queryset based on permissions."""
        # Row-level filtering is complex and depends on the specific table
        # This would need to be implemented based on the table model structure
        return queryset