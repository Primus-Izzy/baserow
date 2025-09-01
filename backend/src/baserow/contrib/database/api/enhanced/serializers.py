"""
Serializers for enhanced API endpoints.
"""
import logging
from rest_framework import serializers
from django.contrib.auth import get_user_model
from baserow.core.models import Group
from baserow.contrib.database.models import Database, Table
from baserow.contrib.database.views.models import View

logger = logging.getLogger(__name__)
User = get_user_model()


class EnhancedUserSerializer(serializers.ModelSerializer):
    """Enhanced user serializer with additional details."""
    
    full_name = serializers.SerializerMethodField()
    groups_count = serializers.IntegerField(read_only=True)
    last_active = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'is_active', 'date_joined', 'last_login', 'last_active',
            'groups_count'
        ]
        read_only_fields = [
            'id', 'date_joined', 'last_login', 'last_active', 'groups_count'
        ]
    
    def get_full_name(self, obj):
        """Get user's full name."""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email


class EnhancedGroupSerializer(serializers.ModelSerializer):
    """Enhanced group serializer with additional details."""
    
    member_count = serializers.IntegerField(read_only=True)
    databases_count = serializers.SerializerMethodField()
    tables_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = [
            'id', 'name', 'created_on', 'updated_on',
            'member_count', 'databases_count', 'tables_count'
        ]
        read_only_fields = ['id', 'created_on', 'updated_on']
    
    def get_databases_count(self, obj):
        """Get count of databases in group."""
        return obj.database_set.count()
    
    def get_tables_count(self, obj):
        """Get count of tables in group."""
        return Table.objects.filter(database__group=obj).count()


class EnhancedDatabaseSerializer(serializers.ModelSerializer):
    """Enhanced database serializer with additional details."""
    
    group_name = serializers.CharField(source='group.name', read_only=True)
    tables_count = serializers.SerializerMethodField()
    last_modified = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Database
        fields = [
            'id', 'name', 'order', 'group', 'group_name',
            'created_on', 'updated_on', 'last_modified', 'tables_count'
        ]
        read_only_fields = [
            'id', 'created_on', 'updated_on', 'last_modified', 'tables_count'
        ]
    
    def get_tables_count(self, obj):
        """Get count of tables in database."""
        return obj.table_set.count()


class EnhancedTableSerializer(serializers.ModelSerializer):
    """Enhanced table serializer with additional details."""
    
    database_name = serializers.CharField(source='database.name', read_only=True)
    group_name = serializers.CharField(source='database.group.name', read_only=True)
    fields_count = serializers.SerializerMethodField()
    views_count = serializers.SerializerMethodField()
    rows_count = serializers.SerializerMethodField()
    last_modified = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Table
        fields = [
            'id', 'name', 'order', 'database', 'database_name', 'group_name',
            'created_on', 'updated_on', 'last_modified',
            'fields_count', 'views_count', 'rows_count'
        ]
        read_only_fields = [
            'id', 'created_on', 'updated_on', 'last_modified',
            'fields_count', 'views_count', 'rows_count'
        ]
    
    def get_fields_count(self, obj):
        """Get count of fields in table."""
        return obj.field_set.count()
    
    def get_views_count(self, obj):
        """Get count of views in table."""
        return obj.view_set.count()
    
    def get_rows_count(self, obj):
        """Get count of rows in table."""
        try:
            return obj.get_model().objects.count()
        except (AttributeError, Exception) as e:
            logger.warning(f"Failed to get rows count for table {obj.id}: {e}")
            return 0


class EnhancedViewSerializer(serializers.ModelSerializer):
    """Enhanced view serializer with additional details."""
    
    table_name = serializers.CharField(source='table.name', read_only=True)
    database_name = serializers.CharField(source='table.database.name', read_only=True)
    group_name = serializers.CharField(source='table.database.group.name', read_only=True)
    last_modified = serializers.DateTimeField(read_only=True)
    view_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = View
        fields = [
            'id', 'name', 'order', 'type', 'view_type_display',
            'table', 'table_name', 'database_name', 'group_name',
            'created_on', 'updated_on', 'last_modified',
            'public', 'slug'
        ]
        read_only_fields = [
            'id', 'created_on', 'updated_on', 'last_modified', 'view_type_display'
        ]
    
    def get_view_type_display(self, obj):
        """Get human-readable view type."""
        view_type_map = {
            'grid': 'Grid View',
            'gallery': 'Gallery View',
            'form': 'Form View',
            'kanban': 'Kanban View',
            'calendar': 'Calendar View',
            'timeline': 'Timeline View'
        }
        return view_type_map.get(obj.type, obj.type.title())


class APIKeySerializer(serializers.Serializer):
    """Serializer for API key management."""
    
    name = serializers.CharField(max_length=255)
    permissions = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of permissions for the API key"
    )
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    
    def validate_permissions(self, permissions):
        """Validate API key permissions."""
        valid_permissions = [
            'database.read', 'database.write',
            'table.read', 'table.write', 'table.create', 'table.delete',
            'row.read', 'row.write', 'row.create', 'row.delete',
            'field.read', 'field.write', 'field.create', 'field.delete',
            'view.read', 'view.write', 'view.create', 'view.delete',
            'webhook.read', 'webhook.write', 'webhook.create', 'webhook.delete',
            'integration.read', 'integration.write', 'integration.create', 'integration.delete'
        ]
        
        for permission in permissions:
            if permission not in valid_permissions:
                raise serializers.ValidationError(
                    f"Invalid permission: {permission}. "
                    f"Valid permissions are: {', '.join(valid_permissions)}"
                )
        
        return permissions