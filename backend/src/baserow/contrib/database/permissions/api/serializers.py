"""
API serializers for the granular permission system.
"""

from rest_framework import serializers

from baserow.contrib.database.fields.models import Field
from baserow.contrib.database.table.models import Table
from baserow.contrib.database.views.models import View
from baserow.core.models import Workspace

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


class CustomRoleSerializer(serializers.ModelSerializer):
    """Serializer for custom roles."""
    
    class Meta:
        model = CustomRole
        fields = [
            "id",
            "name", 
            "description",
            "can_create_tables",
            "can_delete_tables",
            "can_create_views",
            "can_manage_workspace",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on"]


class CustomRoleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating custom roles."""
    
    class Meta:
        model = CustomRole
        fields = [
            "name",
            "description", 
            "can_create_tables",
            "can_delete_tables",
            "can_create_views",
            "can_manage_workspace",
        ]


class UserRoleSerializer(serializers.ModelSerializer):
    """Serializer for user role assignments."""
    
    role_name = serializers.CharField(source="role.name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)
    assigned_by_email = serializers.CharField(source="assigned_by.email", read_only=True)
    
    class Meta:
        model = UserRole
        fields = [
            "id",
            "user",
            "role",
            "role_name",
            "user_email", 
            "assigned_by_email",
            "assigned_at",
        ]
        read_only_fields = ["id", "assigned_at", "role_name", "user_email", "assigned_by_email"]


class TablePermissionSerializer(serializers.ModelSerializer):
    """Serializer for table permissions."""
    
    table_name = serializers.CharField(source="table.name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True, allow_null=True)
    role_name = serializers.CharField(source="role.name", read_only=True, allow_null=True)
    
    class Meta:
        model = TablePermission
        fields = [
            "id",
            "table",
            "table_name",
            "user",
            "user_email",
            "role", 
            "role_name",
            "permission_level",
            "can_create_rows",
            "can_update_rows",
            "can_delete_rows",
            "can_create_fields",
            "can_update_fields",
            "can_delete_fields",
            "can_create_views",
            "can_update_views",
            "can_delete_views",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on", "table_name", "user_email", "role_name"]


class FieldPermissionSerializer(serializers.ModelSerializer):
    """Serializer for field permissions."""
    
    field_name = serializers.CharField(source="field.name", read_only=True)
    table_name = serializers.CharField(source="field.table.name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True, allow_null=True)
    role_name = serializers.CharField(source="role.name", read_only=True, allow_null=True)
    
    class Meta:
        model = FieldPermission
        fields = [
            "id",
            "field",
            "field_name",
            "table_name",
            "user",
            "user_email",
            "role",
            "role_name", 
            "permission_level",
            "can_read",
            "can_update",
            "is_hidden",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on", "field_name", "table_name", "user_email", "role_name"]


class ViewPermissionSerializer(serializers.ModelSerializer):
    """Serializer for view permissions."""
    
    view_name = serializers.CharField(source="view.name", read_only=True)
    table_name = serializers.CharField(source="view.table.name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True, allow_null=True)
    role_name = serializers.CharField(source="role.name", read_only=True, allow_null=True)
    
    class Meta:
        model = ViewPermission
        fields = [
            "id",
            "view",
            "view_name",
            "table_name",
            "user",
            "user_email",
            "role",
            "role_name",
            "permission_level", 
            "can_read",
            "can_update",
            "can_delete",
            "is_hidden",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on", "view_name", "table_name", "user_email", "role_name"]


class ConditionalPermissionSerializer(serializers.ModelSerializer):
    """Serializer for conditional permissions."""
    
    table_name = serializers.CharField(source="table.name", read_only=True)
    condition_field_name = serializers.CharField(source="condition_field.name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True, allow_null=True)
    role_name = serializers.CharField(source="role.name", read_only=True, allow_null=True)
    
    class Meta:
        model = ConditionalPermission
        fields = [
            "id",
            "name",
            "table",
            "table_name",
            "user",
            "user_email",
            "role",
            "role_name",
            "condition_field",
            "condition_field_name",
            "condition_operator",
            "condition_value",
            "user_attribute_field",
            "user_attribute_operator", 
            "user_attribute_value",
            "granted_permission_level",
            "can_read",
            "can_update",
            "can_delete",
            "is_active",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on", "table_name", "condition_field_name", "user_email", "role_name"]


class RowPermissionSerializer(serializers.ModelSerializer):
    """Serializer for row permissions."""
    
    table_name = serializers.CharField(source="table.name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True, allow_null=True)
    role_name = serializers.CharField(source="role.name", read_only=True, allow_null=True)
    
    class Meta:
        model = RowPermission
        fields = [
            "id",
            "table",
            "table_name",
            "row_id",
            "user",
            "user_email",
            "role",
            "role_name",
            "permission_level",
            "can_read",
            "can_update",
            "can_delete",
            "is_hidden",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on", "table_name", "user_email", "role_name"]


class APIKeySerializer(serializers.ModelSerializer):
    """Serializer for API keys."""
    
    workspace_name = serializers.CharField(source="workspace.name", read_only=True)
    created_by_email = serializers.CharField(source="created_by.email", read_only=True)
    scope_table_names = serializers.SerializerMethodField()
    scope_view_names = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = APIKey
        fields = [
            "id",
            "name",
            "key",
            "workspace",
            "workspace_name",
            "created_by_email",
            "scope_table_names",
            "scope_view_names",
            "can_read",
            "can_create",
            "can_update",
            "can_delete",
            "rate_limit_per_minute",
            "allowed_ip_addresses",
            "is_active",
            "is_expired",
            "expires_at",
            "last_used_at",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "key", "created_on", "updated_on", "workspace_name", "created_by_email", "is_expired", "last_used_at"]
    
    def get_scope_table_names(self, obj):
        """Get names of tables in scope."""
        return list(obj.scope_tables.values_list("name", flat=True))
    
    def get_scope_view_names(self, obj):
        """Get names of views in scope."""
        return list(obj.scope_views.values_list("name", flat=True))
    
    def get_is_expired(self, obj):
        """Check if API key is expired."""
        return obj.is_expired()


class APIKeyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating API keys."""
    
    scope_tables = serializers.PrimaryKeyRelatedField(
        queryset=Table.objects.all(),
        many=True,
        required=False
    )
    scope_views = serializers.PrimaryKeyRelatedField(
        queryset=View.objects.all(),
        many=True,
        required=False
    )
    
    class Meta:
        model = APIKey
        fields = [
            "name",
            "scope_tables",
            "scope_views",
            "can_read",
            "can_create",
            "can_update",
            "can_delete",
            "rate_limit_per_minute",
            "allowed_ip_addresses",
            "expires_at",
        ]


class PermissionLevelChoicesSerializer(serializers.Serializer):
    """Serializer for permission level choices."""
    
    value = serializers.CharField()
    label = serializers.CharField()


class PermissionSummarySerializer(serializers.Serializer):
    """Serializer for user permission summary."""
    
    user_id = serializers.IntegerField()
    workspace_id = serializers.IntegerField()
    roles = CustomRoleSerializer(many=True)
    table_permissions = TablePermissionSerializer(many=True)
    field_permissions = FieldPermissionSerializer(many=True)
    view_permissions = ViewPermissionSerializer(many=True)
    conditional_permissions = ConditionalPermissionSerializer(many=True)


class BulkPermissionUpdateSerializer(serializers.Serializer):
    """Serializer for bulk permission updates."""
    
    permissions = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of permission objects to update"
    )
    
    def validate_permissions(self, value):
        """Validate permission objects."""
        for permission in value:
            if "type" not in permission:
                raise serializers.ValidationError("Each permission must have a 'type' field")
            if permission["type"] not in ["table", "field", "view", "row"]:
                raise serializers.ValidationError("Invalid permission type")
        return value