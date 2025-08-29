"""
API serializers for enhanced automation actions.
"""

from rest_framework import serializers
from django.contrib.auth.models import AbstractUser

from baserow.contrib.automation.nodes.enhanced_action_models import (
    NotificationActionNode,
    WebhookActionNode,
    StatusChangeActionNode,
    ConditionalBranchNode,
    DelayActionNode,
    WorkflowExecutionLog,
    ActionTemplate,
)


class NotificationActionNodeSerializer(serializers.ModelSerializer):
    """Serializer for notification action nodes."""
    
    recipient_users = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=AbstractUser.objects.all(),
        required=False
    )
    
    class Meta:
        model = NotificationActionNode
        fields = [
            'id', 'notification_type', 'recipient_users', 'recipient_roles',
            'subject_template', 'message_template', 'external_config'
        ]


class WebhookActionNodeSerializer(serializers.ModelSerializer):
    """Serializer for webhook action nodes."""
    
    class Meta:
        model = WebhookActionNode
        fields = [
            'id', 'url', 'method', 'headers', 'payload_template',
            'authentication', 'retry_config'
        ]


class StatusChangeActionNodeSerializer(serializers.ModelSerializer):
    """Serializer for status change action nodes."""
    
    class Meta:
        model = StatusChangeActionNode
        fields = [
            'id', 'target_field_id', 'new_value_template', 'condition_template'
        ]


class ConditionalBranchNodeSerializer(serializers.ModelSerializer):
    """Serializer for conditional branch nodes."""
    
    class Meta:
        model = ConditionalBranchNode
        fields = [
            'id', 'condition_template', 'condition_type', 'comparison_value_template'
        ]


class DelayActionNodeSerializer(serializers.ModelSerializer):
    """Serializer for delay action nodes."""
    
    class Meta:
        model = DelayActionNode
        fields = [
            'id', 'delay_type', 'delay_duration', 'delay_until_template',
            'condition_template', 'max_wait_duration'
        ]

c
lass WorkflowExecutionLogSerializer(serializers.ModelSerializer):
    """Serializer for workflow execution logs."""
    
    class Meta:
        model = WorkflowExecutionLog
        fields = [
            'id', 'workflow', 'node', 'execution_id', 'status',
            'input_data', 'output_data', 'error_message',
            'execution_time_ms', 'retry_count', 'created_at'
        ]
        read_only_fields = ['created_at']


class ActionTemplateSerializer(serializers.ModelSerializer):
    """Serializer for action templates."""
    
    created_by_name = serializers.CharField(
        source='created_by.first_name',
        read_only=True
    )
    
    class Meta:
        model = ActionTemplate
        fields = [
            'id', 'name', 'description', 'category', 'template_config',
            'required_fields', 'is_system_template', 'usage_count',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['usage_count', 'created_at', 'updated_at']
    
    def validate_template_config(self, value):
        """Validate template configuration structure."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Template config must be a dictionary")
        
        if 'nodes' not in value:
            raise serializers.ValidationError("Template config must contain 'nodes' key")
        
        if not isinstance(value['nodes'], list):
            raise serializers.ValidationError("Template config 'nodes' must be a list")
        
        return value


class ActionTemplateCreateSerializer(ActionTemplateSerializer):
    """Serializer for creating action templates."""
    
    class Meta(ActionTemplateSerializer.Meta):
        fields = [
            'name', 'description', 'category', 'template_config',
            'required_fields'
        ]


class ActionTemplateApplySerializer(serializers.Serializer):
    """Serializer for applying action templates to workflows."""
    
    template_id = serializers.IntegerField()
    workflow_id = serializers.IntegerField()
    configuration_overrides = serializers.JSONField(default=dict)
    
    def validate_template_id(self, value):
        """Validate that template exists."""
        try:
            ActionTemplate.objects.get(id=value)
        except ActionTemplate.DoesNotExist:
            raise serializers.ValidationError("Template not found")
        return value
    
    def validate_workflow_id(self, value):
        """Validate that workflow exists."""
        from baserow.contrib.automation.workflows.models import AutomationWorkflow
        
        try:
            AutomationWorkflow.objects.get(id=value)
        except AutomationWorkflow.DoesNotExist:
            raise serializers.ValidationError("Workflow not found")
        return value