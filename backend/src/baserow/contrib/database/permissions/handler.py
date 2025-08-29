"""
Granular permission handler for Baserow database.

This module provides the business logic for managing and evaluating
granular permissions at table, field, view, and row levels.
"""

import json
from typing import Dict, List, Optional, Set, Union

from django.contrib.auth import get_user_model
from django.db.models import Q, QuerySet
from django.utils import timezone

from baserow.contrib.database.fields.models import Field
from baserow.contrib.database.table.models import Table
from baserow.contrib.database.views.models import View
from baserow.core.exceptions import PermissionDenied
from baserow.core.models import Workspace

from .exceptions import (
    APIKeyExpired,
    APIKeyInactive,
    APIKeyNotFound,
    ConditionalPermissionEvaluationError,
    CustomRoleAlreadyExists,
    CustomRoleNotFound,
    InvalidPermissionLevel,
    PermissionNotFound,
)
from .models import (
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

User = get_user_model()


class GranularPermissionHandler:
    """
    Handler for managing granular permissions in Baserow.
    
    This handler provides methods for creating, updating, and evaluating
    permissions at various levels (table, field, view, row) and supports
    conditional permissions based on field values and user attributes.
    """

    def create_custom_role(
        self,
        workspace: Workspace,
        name: str,
        created_by: User,
        description: str = "",
        **permissions
    ) -> CustomRole:
        """
        Create a new custom role with specific permissions.
        
        :param workspace: The workspace to create the role in
        :param name: Name of the role
        :param created_by: User creating the role
        :param description: Optional description
        :param permissions: Permission flags (can_create_tables, etc.)
        :return: Created CustomRole instance
        :raises CustomRoleAlreadyExists: If role name already exists
        """
        if CustomRole.objects.filter(workspace=workspace, name=name).exists():
            raise CustomRoleAlreadyExists(f"Role '{name}' already exists in workspace")
        
        role = CustomRole.objects.create(
            workspace=workspace,
            name=name,
            description=description,
            created_by=created_by,
            **permissions
        )
        return role

    def update_custom_role(
        self,
        role: CustomRole,
        **updates
    ) -> CustomRole:
        """
        Update an existing custom role.
        
        :param role: The role to update
        :param updates: Fields to update
        :return: Updated CustomRole instance
        """
        for field, value in updates.items():
            if hasattr(role, field):
                setattr(role, field, value)
        role.save()
        return role

    def delete_custom_role(self, role: CustomRole) -> None:
        """
        Delete a custom role and all associated permissions.
        
        :param role: The role to delete
        """
        role.delete()

    def assign_role_to_user(
        self,
        user: User,
        role: CustomRole,
        workspace: Workspace,
        assigned_by: User
    ) -> UserRole:
        """
        Assign a custom role to a user.
        
        :param user: User to assign role to
        :param role: Role to assign
        :param workspace: Workspace context
        :param assigned_by: User making the assignment
        :return: Created UserRole instance
        """
        user_role, created = UserRole.objects.get_or_create(
            user=user,
            role=role,
            workspace=workspace,
            defaults={"assigned_by": assigned_by}
        )
        return user_role

    def remove_role_from_user(
        self,
        user: User,
        role: CustomRole,
        workspace: Workspace
    ) -> None:
        """
        Remove a role assignment from a user.
        
        :param user: User to remove role from
        :param role: Role to remove
        :param workspace: Workspace context
        """
        UserRole.objects.filter(
            user=user,
            role=role,
            workspace=workspace
        ).delete()

    def get_user_roles(self, user: User, workspace: Workspace) -> QuerySet[CustomRole]:
        """
        Get all custom roles assigned to a user in a workspace.
        
        :param user: User to get roles for
        :param workspace: Workspace context
        :return: QuerySet of CustomRole instances
        """
        return CustomRole.objects.filter(
            userrole__user=user,
            userrole__workspace=workspace
        )

    def set_table_permission(
        self,
        table: Table,
        user: Optional[User] = None,
        role: Optional[CustomRole] = None,
        permission_level: str = PermissionLevel.READ,
        **specific_permissions
    ) -> TablePermission:
        """
        Set table-level permissions for a user or role.
        
        :param table: Table to set permissions for
        :param user: User to set permissions for (mutually exclusive with role)
        :param role: Role to set permissions for (mutually exclusive with user)
        :param permission_level: Overall permission level
        :param specific_permissions: Specific permission flags
        :return: Created or updated TablePermission instance
        """
        if not user and not role:
            raise ValueError("Either user or role must be specified")
        if user and role:
            raise ValueError("Cannot specify both user and role")

        permission, created = TablePermission.objects.update_or_create(
            table=table,
            user=user,
            role=role,
            defaults={
                "permission_level": permission_level,
                **specific_permissions
            }
        )
        return permission

    def set_field_permission(
        self,
        field: Field,
        user: Optional[User] = None,
        role: Optional[CustomRole] = None,
        permission_level: str = PermissionLevel.READ,
        **specific_permissions
    ) -> FieldPermission:
        """
        Set field-level permissions for a user or role.
        
        :param field: Field to set permissions for
        :param user: User to set permissions for (mutually exclusive with role)
        :param role: Role to set permissions for (mutually exclusive with user)
        :param permission_level: Overall permission level
        :param specific_permissions: Specific permission flags
        :return: Created or updated FieldPermission instance
        """
        if not user and not role:
            raise ValueError("Either user or role must be specified")
        if user and role:
            raise ValueError("Cannot specify both user and role")

        permission, created = FieldPermission.objects.update_or_create(
            field=field,
            user=user,
            role=role,
            defaults={
                "permission_level": permission_level,
                **specific_permissions
            }
        )
        return permission

    def set_view_permission(
        self,
        view: View,
        user: Optional[User] = None,
        role: Optional[CustomRole] = None,
        permission_level: str = PermissionLevel.READ,
        **specific_permissions
    ) -> ViewPermission:
        """
        Set view-level permissions for a user or role.
        
        :param view: View to set permissions for
        :param user: User to set permissions for (mutually exclusive with role)
        :param role: Role to set permissions for (mutually exclusive with user)
        :param permission_level: Overall permission level
        :param specific_permissions: Specific permission flags
        :return: Created or updated ViewPermission instance
        """
        if not user and not role:
            raise ValueError("Either user or role must be specified")
        if user and role:
            raise ValueError("Cannot specify both user and role")

        permission, created = ViewPermission.objects.update_or_create(
            view=view,
            user=user,
            role=role,
            defaults={
                "permission_level": permission_level,
                **specific_permissions
            }
        )
        return permission

    def set_row_permission(
        self,
        table: Table,
        row_id: int,
        user: Optional[User] = None,
        role: Optional[CustomRole] = None,
        permission_level: str = PermissionLevel.READ,
        **specific_permissions
    ) -> RowPermission:
        """
        Set row-level permissions for a user or role.
        
        :param table: Table containing the row
        :param row_id: ID of the specific row
        :param user: User to set permissions for (mutually exclusive with role)
        :param role: Role to set permissions for (mutually exclusive with user)
        :param permission_level: Overall permission level
        :param specific_permissions: Specific permission flags
        :return: Created or updated RowPermission instance
        """
        if not user and not role:
            raise ValueError("Either user or role must be specified")
        if user and role:
            raise ValueError("Cannot specify both user and role")

        permission, created = RowPermission.objects.update_or_create(
            table=table,
            row_id=row_id,
            user=user,
            role=role,
            defaults={
                "permission_level": permission_level,
                **specific_permissions
            }
        )
        return permission

    def create_conditional_permission(
        self,
        name: str,
        table: Table,
        condition_field: Field,
        condition_operator: str,
        condition_value: str,
        user: Optional[User] = None,
        role: Optional[CustomRole] = None,
        granted_permission_level: str = PermissionLevel.READ,
        user_attribute_field: str = "",
        user_attribute_operator: str = "",
        user_attribute_value: str = "",
        **granted_permissions
    ) -> ConditionalPermission:
        """
        Create a conditional permission based on field values and user attributes.
        
        :param name: Name for the conditional permission
        :param table: Table to apply permission to
        :param condition_field: Field to evaluate for condition
        :param condition_operator: Operator for condition evaluation
        :param condition_value: Value to compare against
        :param user: User to apply permission to (mutually exclusive with role)
        :param role: Role to apply permission to (mutually exclusive with user)
        :param granted_permission_level: Permission level when condition is met
        :param user_attribute_field: Optional user attribute to check
        :param user_attribute_operator: Operator for user attribute condition
        :param user_attribute_value: Value for user attribute condition
        :param granted_permissions: Specific permissions when condition is met
        :return: Created ConditionalPermission instance
        """
        if not user and not role:
            raise ValueError("Either user or role must be specified")
        if user and role:
            raise ValueError("Cannot specify both user and role")

        conditional_permission = ConditionalPermission.objects.create(
            name=name,
            table=table,
            user=user,
            role=role,
            condition_field=condition_field,
            condition_operator=condition_operator,
            condition_value=condition_value,
            granted_permission_level=granted_permission_level,
            user_attribute_field=user_attribute_field,
            user_attribute_operator=user_attribute_operator,
            user_attribute_value=user_attribute_value,
            **granted_permissions
        )
        return conditional_permission

    def evaluate_conditional_permission(
        self,
        conditional_permission: ConditionalPermission,
        user: User,
        row_data: Dict
    ) -> bool:
        """
        Evaluate whether a conditional permission applies to a user and row.
        
        :param conditional_permission: The conditional permission to evaluate
        :param user: User to evaluate for
        :param row_data: Row data to evaluate condition against
        :return: True if condition is met and permission should be granted
        """
        try:
            # Evaluate field condition
            field_condition_met = self._evaluate_field_condition(
                conditional_permission.condition_field,
                conditional_permission.condition_operator,
                conditional_permission.condition_value,
                row_data
            )
            
            # Evaluate user attribute condition if specified
            user_condition_met = True
            if conditional_permission.user_attribute_field:
                user_condition_met = self._evaluate_user_condition(
                    conditional_permission.user_attribute_field,
                    conditional_permission.user_attribute_operator,
                    conditional_permission.user_attribute_value,
                    user
                )
            
            return field_condition_met and user_condition_met
            
        except Exception as e:
            raise ConditionalPermissionEvaluationError(
                f"Error evaluating conditional permission '{conditional_permission.name}': {str(e)}"
            )

    def _evaluate_field_condition(
        self,
        field: Field,
        operator: str,
        value: str,
        row_data: Dict
    ) -> bool:
        """
        Evaluate a field condition against row data.
        
        :param field: Field to evaluate
        :param operator: Comparison operator
        :param value: Value to compare against
        :param row_data: Row data containing field values
        :return: True if condition is met
        """
        field_key = f"field_{field.id}"
        field_value = row_data.get(field_key)
        
        # Handle different operators
        if operator == "equals":
            return str(field_value) == value
        elif operator == "not_equals":
            return str(field_value) != value
        elif operator == "contains":
            return value in str(field_value) if field_value else False
        elif operator == "not_contains":
            return value not in str(field_value) if field_value else True
        elif operator == "greater_than":
            try:
                return float(field_value) > float(value)
            except (ValueError, TypeError):
                return False
        elif operator == "less_than":
            try:
                return float(field_value) < float(value)
            except (ValueError, TypeError):
                return False
        elif operator == "is_empty":
            return not field_value or field_value == ""
        elif operator == "is_not_empty":
            return field_value and field_value != ""
        
        return False

    def _evaluate_user_condition(
        self,
        attribute_field: str,
        operator: str,
        value: str,
        user: User
    ) -> bool:
        """
        Evaluate a user attribute condition.
        
        :param attribute_field: User attribute to check
        :param operator: Comparison operator
        :param value: Value to compare against
        :param user: User to evaluate
        :return: True if condition is met
        """
        user_value = getattr(user, attribute_field, None)
        if user_value is None:
            return False
        
        user_value_str = str(user_value)
        
        if operator == "equals":
            return user_value_str == value
        elif operator == "contains":
            return value in user_value_str
        elif operator == "starts_with":
            return user_value_str.startswith(value)
        elif operator == "ends_with":
            return user_value_str.endswith(value)
        
        return False

    def check_table_permission(
        self,
        user: User,
        table: Table,
        operation: str,
        row_data: Optional[Dict] = None
    ) -> bool:
        """
        Check if a user has permission to perform an operation on a table.
        
        :param user: User to check permissions for
        :param table: Table to check permissions on
        :param operation: Operation to check (read, create, update, delete)
        :param row_data: Optional row data for conditional permissions
        :return: True if permission is granted
        """
        # Get user roles in the workspace
        user_roles = self.get_user_roles(user, table.database.workspace)
        
        # Check direct user permissions
        user_permissions = TablePermission.objects.filter(
            table=table,
            user=user
        ).first()
        
        # Check role-based permissions
        role_permissions = TablePermission.objects.filter(
            table=table,
            role__in=user_roles
        )
        
        # Evaluate permissions
        has_permission = False
        
        if user_permissions:
            has_permission = self._check_permission_level(
                user_permissions.permission_level,
                operation
            )
            if operation == "create" and hasattr(user_permissions, "can_create_rows"):
                has_permission = has_permission and user_permissions.can_create_rows
            elif operation == "update" and hasattr(user_permissions, "can_update_rows"):
                has_permission = has_permission and user_permissions.can_update_rows
            elif operation == "delete" and hasattr(user_permissions, "can_delete_rows"):
                has_permission = has_permission and user_permissions.can_delete_rows
        
        # Check role permissions (take highest permission)
        for role_permission in role_permissions:
            role_has_permission = self._check_permission_level(
                role_permission.permission_level,
                operation
            )
            if operation == "create" and hasattr(role_permission, "can_create_rows"):
                role_has_permission = role_has_permission and role_permission.can_create_rows
            elif operation == "update" and hasattr(role_permission, "can_update_rows"):
                role_has_permission = role_has_permission and role_permission.can_update_rows
            elif operation == "delete" and hasattr(role_permission, "can_delete_rows"):
                role_has_permission = role_has_permission and role_permission.can_delete_rows
            
            has_permission = has_permission or role_has_permission
        
        # Check conditional permissions if row data is provided
        if row_data:
            conditional_permissions = ConditionalPermission.objects.filter(
                table=table,
                is_active=True
            ).filter(
                Q(user=user) | Q(role__in=user_roles)
            )
            
            for conditional_permission in conditional_permissions:
                if self.evaluate_conditional_permission(conditional_permission, user, row_data):
                    conditional_has_permission = self._check_permission_level(
                        conditional_permission.granted_permission_level,
                        operation
                    )
                    if operation == "update" and hasattr(conditional_permission, "can_update"):
                        conditional_has_permission = conditional_has_permission and conditional_permission.can_update
                    elif operation == "delete" and hasattr(conditional_permission, "can_delete"):
                        conditional_has_permission = conditional_has_permission and conditional_permission.can_delete
                    
                    has_permission = has_permission or conditional_has_permission
        
        return has_permission

    def check_field_permission(
        self,
        user: User,
        field: Field,
        operation: str
    ) -> bool:
        """
        Check if a user has permission to perform an operation on a field.
        
        :param user: User to check permissions for
        :param field: Field to check permissions on
        :param operation: Operation to check (read, update)
        :return: True if permission is granted
        """
        # Get user roles in the workspace
        user_roles = self.get_user_roles(user, field.table.database.workspace)
        
        # Check direct user permissions
        user_permissions = FieldPermission.objects.filter(
            field=field,
            user=user
        ).first()
        
        # Check role-based permissions
        role_permissions = FieldPermission.objects.filter(
            field=field,
            role__in=user_roles
        )
        
        # Evaluate permissions
        has_permission = False
        
        if user_permissions:
            if user_permissions.is_hidden:
                return False
            has_permission = self._check_permission_level(
                user_permissions.permission_level,
                operation
            )
            if operation == "update" and hasattr(user_permissions, "can_update"):
                has_permission = has_permission and user_permissions.can_update
        
        # Check role permissions (take highest permission)
        for role_permission in role_permissions:
            if role_permission.is_hidden:
                continue
            role_has_permission = self._check_permission_level(
                role_permission.permission_level,
                operation
            )
            if operation == "update" and hasattr(role_permission, "can_update"):
                role_has_permission = role_has_permission and role_permission.can_update
            
            has_permission = has_permission or role_has_permission
        
        return has_permission

    def _check_permission_level(self, permission_level: str, operation: str) -> bool:
        """
        Check if a permission level allows a specific operation.
        
        :param permission_level: Permission level to check
        :param operation: Operation to check
        :return: True if operation is allowed
        """
        if permission_level == PermissionLevel.NONE:
            return False
        elif permission_level == PermissionLevel.READ:
            return operation == "read"
        elif permission_level == PermissionLevel.UPDATE:
            return operation in ["read", "update"]
        elif permission_level == PermissionLevel.CREATE:
            return operation in ["read", "update", "create"]
        elif permission_level == PermissionLevel.DELETE:
            return operation in ["read", "update", "create", "delete"]
        
        return False

    def create_api_key(
        self,
        workspace: Workspace,
        name: str,
        created_by: User,
        **permissions
    ) -> APIKey:
        """
        Create a new API key with granular scope control.
        
        :param workspace: Workspace for the API key
        :param name: Name for the API key
        :param created_by: User creating the API key
        :param permissions: Permission flags and scope settings
        :return: Created APIKey instance
        """
        import secrets
        
        # Generate a secure API key
        key = f"brow_{secrets.token_urlsafe(32)}"
        
        api_key = APIKey.objects.create(
            workspace=workspace,
            name=name,
            key=key,
            created_by=created_by,
            **permissions
        )
        return api_key

    def validate_api_key(self, key: str, ip_address: str = None) -> APIKey:
        """
        Validate an API key and check restrictions.
        
        :param key: API key to validate
        :param ip_address: IP address of the request
        :return: APIKey instance if valid
        :raises APIKeyNotFound: If key doesn't exist
        :raises APIKeyInactive: If key is inactive
        :raises APIKeyExpired: If key has expired
        :raises PermissionDenied: If IP address is not allowed
        """
        try:
            api_key = APIKey.objects.get(key=key)
        except APIKey.DoesNotExist:
            raise APIKeyNotFound("Invalid API key")
        
        if not api_key.is_active:
            raise APIKeyInactive("API key is inactive")
        
        if api_key.is_expired():
            raise APIKeyExpired("API key has expired")
        
        # Check IP address restrictions
        if ip_address and api_key.allowed_ip_addresses:
            allowed_ips = api_key.get_allowed_ip_list()
            if ip_address not in allowed_ips:
                raise PermissionDenied("IP address not allowed for this API key")
        
        # Update last used timestamp
        api_key.last_used_at = timezone.now()
        api_key.save(update_fields=["last_used_at"])
        
        return api_key

    def check_api_key_permission(
        self,
        api_key: APIKey,
        operation: str,
        table: Optional[Table] = None,
        view: Optional[View] = None
    ) -> bool:
        """
        Check if an API key has permission to perform an operation.
        
        :param api_key: API key to check
        :param operation: Operation to check (read, create, update, delete)
        :param table: Optional table context
        :param view: Optional view context
        :return: True if permission is granted
        """
        # Check basic operation permissions
        if operation == "read" and not api_key.can_read:
            return False
        elif operation == "create" and not api_key.can_create:
            return False
        elif operation == "update" and not api_key.can_update:
            return False
        elif operation == "delete" and not api_key.can_delete:
            return False
        
        # Check table scope
        if table:
            scope_tables = api_key.scope_tables.all()
            if scope_tables.exists() and table not in scope_tables:
                return False
        
        # Check view scope
        if view:
            scope_views = api_key.scope_views.all()
            if scope_views.exists() and view not in scope_views:
                return False
        
        return True

    def get_user_permissions_summary(
        self,
        user: User,
        workspace: Workspace
    ) -> Dict:
        """
        Get a comprehensive summary of a user's permissions in a workspace.
        
        :param user: User to get permissions for
        :param workspace: Workspace context
        :return: Dictionary containing permission summary
        """
        user_roles = self.get_user_roles(user, workspace)
        
        summary = {
            "user_id": user.id,
            "workspace_id": workspace.id,
            "roles": [
                {
                    "id": role.id,
                    "name": role.name,
                    "description": role.description,
                    "can_create_tables": role.can_create_tables,
                    "can_delete_tables": role.can_delete_tables,
                    "can_create_views": role.can_create_views,
                    "can_manage_workspace": role.can_manage_workspace,
                }
                for role in user_roles
            ],
            "table_permissions": [],
            "field_permissions": [],
            "view_permissions": [],
            "conditional_permissions": [],
        }
        
        # Get table permissions
        table_permissions = TablePermission.objects.filter(
            Q(user=user) | Q(role__in=user_roles),
            table__database__workspace=workspace
        )
        for perm in table_permissions:
            summary["table_permissions"].append({
                "table_id": perm.table.id,
                "table_name": perm.table.name,
                "permission_level": perm.permission_level,
                "can_create_rows": perm.can_create_rows,
                "can_update_rows": perm.can_update_rows,
                "can_delete_rows": perm.can_delete_rows,
            })
        
        # Get field permissions
        field_permissions = FieldPermission.objects.filter(
            Q(user=user) | Q(role__in=user_roles),
            field__table__database__workspace=workspace
        )
        for perm in field_permissions:
            summary["field_permissions"].append({
                "field_id": perm.field.id,
                "field_name": perm.field.name,
                "table_id": perm.field.table.id,
                "permission_level": perm.permission_level,
                "can_read": perm.can_read,
                "can_update": perm.can_update,
                "is_hidden": perm.is_hidden,
            })
        
        # Get view permissions
        view_permissions = ViewPermission.objects.filter(
            Q(user=user) | Q(role__in=user_roles),
            view__table__database__workspace=workspace
        )
        for perm in view_permissions:
            summary["view_permissions"].append({
                "view_id": perm.view.id,
                "view_name": perm.view.name,
                "table_id": perm.view.table.id,
                "permission_level": perm.permission_level,
                "can_read": perm.can_read,
                "can_update": perm.can_update,
                "is_hidden": perm.is_hidden,
            })
        
        # Get conditional permissions
        conditional_permissions = ConditionalPermission.objects.filter(
            Q(user=user) | Q(role__in=user_roles),
            table__database__workspace=workspace,
            is_active=True
        )
        for perm in conditional_permissions:
            summary["conditional_permissions"].append({
                "id": perm.id,
                "name": perm.name,
                "table_id": perm.table.id,
                "condition_field": perm.condition_field.name,
                "condition_operator": perm.condition_operator,
                "granted_permission_level": perm.granted_permission_level,
            })
        
        return summary