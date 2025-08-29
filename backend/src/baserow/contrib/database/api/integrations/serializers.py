"""
Serializers for third-party integrations.
"""
from rest_framework import serializers
from baserow.contrib.database.integrations.zapier.models import (
    ZapierIntegration, ZapierExecution, MakeIntegration, MakeExecution
)
from baserow.contrib.database.api.tables.serializers import TableSerializer
from baserow.core.api.groups.serializers import GroupSerializer


class ZapierIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for Zapier integrations."""
    
    group = GroupSerializer(read_only=True)
    table = TableSerializer(read_only=True)
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    
    class Meta:
        model = ZapierIntegration
        fields = [
            'id', 'name', 'group', 'table', 'integration_type',
            'trigger_type', 'action_type', 'configuration', 'is_active',
            'created_by_email', 'created_at', 'updated_at',
            'total_executions', 'successful_executions', 'failed_executions',
            'last_execution_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'total_executions',
            'successful_executions', 'failed_executions', 'last_execution_at'
        ]


class CreateZapierIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for creating Zapier integrations."""
    
    group_id = serializers.IntegerField(write_only=True)
    table_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ZapierIntegration
        fields = [
            'name', 'group_id', 'table_id', 'integration_type',
            'trigger_type', 'action_type', 'configuration'
        ]
    
    def validate(self, data):
        """Validate integration configuration."""
        integration_type = data.get('integration_type')
        
        if integration_type == 'trigger' and not data.get('trigger_type'):
            raise serializers.ValidationError(
                "trigger_type is required for trigger integrations"
            )
        
        if integration_type == 'action' and not data.get('action_type'):
            raise serializers.ValidationError(
                "action_type is required for action integrations"
            )
        
        return data


class ZapierExecutionSerializer(serializers.ModelSerializer):
    """Serializer for Zapier execution records."""
    
    integration_name = serializers.CharField(source='integration.name', read_only=True)
    
    class Meta:
        model = ZapierExecution
        fields = [
            'id', 'integration_name', 'zapier_execution_id',
            'input_data', 'output_data', 'status', 'error_message',
            'execution_time_ms', 'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at', 'completed_at']


class MakeIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for Make.com integrations."""
    
    group = GroupSerializer(read_only=True)
    table = TableSerializer(read_only=True)
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    
    class Meta:
        model = MakeIntegration
        fields = [
            'id', 'name', 'group', 'table', 'module_type',
            'webhook_type', 'webhook_url', 'configuration', 'is_active',
            'created_by_email', 'created_at', 'updated_at',
            'total_executions', 'successful_executions', 'failed_executions',
            'last_execution_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'total_executions',
            'successful_executions', 'failed_executions', 'last_execution_at'
        ]


class CreateMakeIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for creating Make.com integrations."""
    
    group_id = serializers.IntegerField(write_only=True)
    table_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = MakeIntegration
        fields = [
            'name', 'group_id', 'table_id', 'module_type',
            'webhook_type', 'webhook_url', 'configuration'
        ]


class MakeExecutionSerializer(serializers.ModelSerializer):
    """Serializer for Make.com execution records."""
    
    integration_name = serializers.CharField(source='integration.name', read_only=True)
    
    class Meta:
        model = MakeExecution
        fields = [
            'id', 'integration_name', 'make_execution_id',
            'input_data', 'output_data', 'status', 'error_message',
            'execution_time_ms', 'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at', 'completed_at']


class ZapierTriggerTestSerializer(serializers.Serializer):
    """Serializer for testing Zapier triggers."""
    
    sample_data = serializers.JSONField(required=False)


class ZapierActionTestSerializer(serializers.Serializer):
    """Serializer for testing Zapier actions."""
    
    input_data = serializers.JSONField()


class MakeWebhookTestSerializer(serializers.Serializer):
    """Serializer for testing Make.com webhooks."""
    
    sample_data = serializers.JSONField(required=False)


class MakeModuleTestSerializer(serializers.Serializer):
    """Serializer for testing Make.com modules."""
    
    input_data = serializers.JSONField()


class IntegrationStatsSerializer(serializers.Serializer):
    """Serializer for integration statistics."""
    
    total_integrations = serializers.IntegerField()
    active_integrations = serializers.IntegerField()
    total_executions = serializers.IntegerField()
    successful_executions = serializers.IntegerField()
    failed_executions = serializers.IntegerField()
    success_rate = serializers.FloatField()
    zapier_integrations = serializers.IntegerField()
    make_integrations = serializers.IntegerField()
    recent_executions = serializers.ListField()