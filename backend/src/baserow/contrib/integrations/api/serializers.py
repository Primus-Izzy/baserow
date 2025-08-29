from rest_framework import serializers
from ..models import (
    IntegrationProvider,
    IntegrationConnection,
    IntegrationSync,
    IntegrationWebhook,
    IntegrationLog
)


class IntegrationProviderSerializer(serializers.ModelSerializer):
    """Serializer for integration providers"""
    
    class Meta:
        model = IntegrationProvider
        fields = [
            'id', 'name', 'provider_type', 'display_name', 'description', 
            'icon_url', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class IntegrationConnectionSerializer(serializers.ModelSerializer):
    """Serializer for integration connections"""
    
    provider = IntegrationProviderSerializer(read_only=True)
    
    class Meta:
        model = IntegrationConnection
        fields = [
            'id', 'provider', 'external_user_id', 'external_user_email',
            'external_user_name', 'status', 'last_sync_at', 'error_message',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'external_user_id', 'external_user_email', 'external_user_name',
            'last_sync_at', 'created_at', 'updated_at'
        ]


class IntegrationSyncSerializer(serializers.ModelSerializer):
    """Serializer for integration syncs"""
    
    connection = IntegrationConnectionSerializer(read_only=True)
    
    class Meta:
        model = IntegrationSync
        fields = [
            'id', 'connection', 'table', 'sync_type', 'sync_direction',
            'external_resource_id', 'field_mappings', 'sync_filters',
            'auto_sync_enabled', 'sync_interval_minutes', 'is_active',
            'last_sync_at', 'last_sync_status', 'sync_error_message',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'last_sync_at', 'last_sync_status', 'sync_error_message',
            'created_at', 'updated_at'
        ]


class IntegrationWebhookSerializer(serializers.ModelSerializer):
    """Serializer for integration webhooks"""
    
    class Meta:
        model = IntegrationWebhook
        fields = [
            'id', 'webhook_url', 'event_types', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'webhook_url', 'created_at', 'updated_at']


class IntegrationLogSerializer(serializers.ModelSerializer):
    """Serializer for integration logs"""
    
    class Meta:
        model = IntegrationLog
        fields = ['id', 'level', 'message', 'details', 'created_at']
        read_only_fields = ['id', 'created_at']


class OAuthAuthorizationSerializer(serializers.Serializer):
    """Serializer for OAuth authorization request"""
    
    provider = serializers.CharField()
    workspace_id = serializers.IntegerField()
    state = serializers.CharField(required=False)


class OAuthCallbackSerializer(serializers.Serializer):
    """Serializer for OAuth callback"""
    
    code = serializers.CharField()
    state = serializers.CharField(required=False)
    error = serializers.CharField(required=False)


class SyncConfigurationSerializer(serializers.Serializer):
    """Serializer for sync configuration"""
    
    sync_type = serializers.ChoiceField(choices=IntegrationSync.SYNC_TYPES)
    sync_direction = serializers.ChoiceField(choices=IntegrationSync.SYNC_DIRECTIONS, default='bidirectional')
    external_resource_id = serializers.CharField()
    field_mappings = serializers.JSONField(default=dict)
    sync_filters = serializers.JSONField(default=dict)
    auto_sync_enabled = serializers.BooleanField(default=True)
    sync_interval_minutes = serializers.IntegerField(default=15, min_value=1, max_value=1440)