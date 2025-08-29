"""
API serializers for enhanced automation triggers.

This module contains serializers for the enhanced trigger system including
date-based triggers, linked record change triggers, webhook triggers,
conditional triggers, and trigger templates.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

from baserow.contrib.automation.nodes.enhanced_trigger_models import (
    DateBasedTriggerNode,
    LinkedRecordChangeTriggerNode,
    WebhookTriggerNode,
    ConditionalTriggerNode,
    TriggerTemplate,
)
from baserow.contrib.database.fields.models import Field, LinkRowField, DateField
from baserow.api.fields.serializers import FieldSerializer

User = get_user_model()


class DateBasedTriggerNodeSerializer(serializers.ModelSerializer):
    """Serializer for date-based trigger nodes."""
    
    date_field = FieldSerializer(read_only=True)
    date_field_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = DateBasedTriggerNode
        fields = [
            'id', 'date_field', 'date_field_id', 'condition_type', 
            'days_offset', 'recurring_pattern', 'check_time', 
            'additional_conditions', 'workflow', 'order'
        ]
        read_only_fields = ['id', 'workflow']
    
    def validate_date_field_id(self, value):
        """Validate that the field exists and is a date field."""
        try:
            field = Field.objects.get(id=value)
            if not isinstance(field.specific, DateField):
                raise serializers.ValidationError(
                    "Field must be a date field type."
                )
            return value
        except Field.DoesNotExist:
            raise serializers.ValidationError("Date field not found.")
    
    def validate_recurring_pattern(self, value):
        """Validate recurring pattern configuration."""
        if not value:
            return value
        
        frequency = value.get('frequency')
        if frequency not in ['daily', 'weekly', 'monthly', 'yearly']:
            raise serializers.ValidationError(
                "Frequency must be one of: daily, weekly, monthly, yearly"
            )
        
        if frequency == 'weekly' and 'weekday' not in value:
            raise serializers.ValidationError(
                "Weekly frequency requires 'weekday' (0-6, Monday=0)"
            )
        
        if frequency == 'monthly' and 'day_of_month' not in value:
            raise serializers.ValidationError(
                "Monthly frequency requires 'day_of_month' (1-31)"
            )
        
        return value
    
    def validate_additional_conditions(self, value):
        """Validate additional conditions format."""
        if not value:
            return value
        
        for field_name, condition in value.items():
            if not isinstance(condition, dict):
                raise serializers.ValidationError(
                    f"Condition for '{field_name}' must be a dictionary"
                )
            
            if 'operator' not in condition:
                raise serializers.ValidationError(
                    f"Condition for '{field_name}' must include 'operator'"
                )
            
            valid_operators = [
                'equals', 'not_equals', 'greater_than', 'less_than',
                'contains', 'is_empty', 'is_not_empty'
            ]
            
            if condition['operator'] not in valid_operators:
                raise serializers.ValidationError(
                    f"Invalid operator '{condition['operator']}' for '{field_name}'"
                )
        
        return value


class LinkedRecordChangeTriggerNodeSerializer(serializers.ModelSerializer):
    """Serializer for linked record change trigger nodes."""
    
    link_field = FieldSerializer(read_only=True)
    link_field_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = LinkedRecordChangeTriggerNode
        fields = [
            'id', 'link_field', 'link_field_id', 'change_type',
            'monitored_fields', 'linked_record_conditions', 'workflow', 'order'
        ]
        read_only_fields = ['id', 'workflow']
    
    def validate_link_field_id(self, value):
        """Validate that the field exists and is a link row field."""
        try:
            field = Field.objects.get(id=value)
            if not isinstance(field.specific, LinkRowField):
                raise serializers.ValidationError(
                    "Field must be a link row field type."
                )
            return value
        except Field.DoesNotExist:
            raise serializers.ValidationError("Link field not found.")
    
    def validate_monitored_fields(self, value):
        """Validate monitored fields list."""
        if not value:
            return value
        
        if not isinstance(value, list):
            raise serializers.ValidationError("Monitored fields must be a list")
        
        # Validate that field IDs exist (basic validation)
        for field_id in value:
            if not isinstance(field_id, int):
                raise serializers.ValidationError(
                    "Monitored field IDs must be integers"
                )
        
        return value


class WebhookTriggerNodeSerializer(serializers.ModelSerializer):
    """Serializer for webhook trigger nodes."""
    
    class Meta:
        model = WebhookTriggerNode
        fields = [
            'id', 'webhook_url_path', 'auth_type', 'auth_token',
            'signature_secret', 'allowed_methods', 'payload_mapping',
            'validation_rules', 'workflow', 'order'
        ]
        read_only_fields = ['id', 'workflow']
        extra_kwargs = {
            'auth_token': {'write_only': True},
            'signature_secret': {'write_only': True},
        }
    
    def validate_webhook_url_path(self, value):
        """Validate webhook URL path uniqueness."""
        if self.instance:
            # Update case - exclude current instance
            existing = WebhookTriggerNode.objects.filter(
                webhook_url_path=value
            ).exclude(id=self.instance.id)
        else:
            # Create case
            existing = WebhookTriggerNode.objects.filter(webhook_url_path=value)
        
        if existing.exists():
            raise serializers.ValidationError(
                "Webhook URL path must be unique"
            )
        
        return value
    
    def validate_allowed_methods(self, value):
        """Validate HTTP methods list."""
        if not value:
            return ['POST']  # Default to POST
        
        valid_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
        for method in value:
            if method.upper() not in valid_methods:
                raise serializers.ValidationError(
                    f"Invalid HTTP method: {method}"
                )
        
        return [method.upper() for method in value]
    
    def validate_payload_mapping(self, value):
        """Validate payload mapping configuration."""
        if not value:
            return value
        
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Payload mapping must be a dictionary"
            )
        
        return value


class ConditionalTriggerNodeSerializer(serializers.ModelSerializer):
    """Serializer for conditional trigger nodes."""
    
    class Meta:
        model = ConditionalTriggerNode
        fields = [
            'id', 'base_trigger', 'condition_groups', 'evaluation_mode',
            'custom_logic', 'time_conditions', 'workflow', 'order'
        ]
        read_only_fields = ['id', 'workflow']
    
    def validate_condition_groups(self, value):
        """Validate condition groups structure."""
        if not value:
            return value
        
        if not isinstance(value, list):
            raise serializers.ValidationError(
                "Condition groups must be a list"
            )
        
        for i, group in enumerate(value):
            if not isinstance(group, dict):
                raise serializers.ValidationError(
                    f"Condition group {i} must be a dictionary"
                )
            
            if 'conditions' not in group:
                raise serializers.ValidationError(
                    f"Condition group {i} must have 'conditions'"
                )
            
            conditions = group['conditions']
            if not isinstance(conditions, list):
                raise serializers.ValidationError(
                    f"Conditions in group {i} must be a list"
                )
            
            for j, condition in enumerate(conditions):
                self._validate_single_condition(condition, f"group {i}, condition {j}")
        
        return value
    
    def _validate_single_condition(self, condition, context):
        """Validate a single condition structure."""
        required_fields = ['field', 'operator', 'value']
        
        for field in required_fields:
            if field not in condition:
                raise serializers.ValidationError(
                    f"Condition in {context} missing required field: {field}"
                )
        
        valid_operators = [
            'equals', 'not_equals', 'greater_than', 'less_than',
            'contains', 'is_empty', 'is_not_empty'
        ]
        
        if condition['operator'] not in valid_operators:
            raise serializers.ValidationError(
                f"Invalid operator in {context}: {condition['operator']}"
            )
    
    def validate_custom_logic(self, value):
        """Validate custom logic expression."""
        if not value:
            return value
        
        # Basic validation - ensure it only contains allowed characters
        allowed_chars = set('0123456789()&|! group_')
        if not all(c in allowed_chars for c in value.replace(' ', '')):
            raise serializers.ValidationError(
                "Custom logic contains invalid characters"
            )
        
        return value


class TriggerTemplateSerializer(serializers.ModelSerializer):
    """Serializer for trigger templates."""
    
    class Meta:
        model = TriggerTemplate
        fields = [
            'id', 'name', 'description', 'category', 'trigger_config',
            'action_templates', 'required_field_types', 'is_active',
            'usage_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'usage_count', 'created_at', 'updated_at']
    
    def validate_trigger_config(self, value):
        """Validate trigger configuration structure."""
        if not value or not isinstance(value, dict):
            raise serializers.ValidationError(
                "Trigger config must be a non-empty dictionary"
            )
        
        if 'type' not in value:
            raise serializers.ValidationError(
                "Trigger config must include 'type'"
            )
        
        valid_types = [
            'date_based_trigger', 'linked_record_change_trigger',
            'webhook_trigger', 'conditional_trigger', 'rows_created',
            'rows_updated', 'rows_deleted'
        ]
        
        if value['type'] not in valid_types:
            raise serializers.ValidationError(
                f"Invalid trigger type: {value['type']}"
            )
        
        return value
    
    def validate_action_templates(self, value):
        """Validate action templates structure."""
        if not isinstance(value, list):
            raise serializers.ValidationError(
                "Action templates must be a list"
            )
        
        for i, action in enumerate(value):
            if not isinstance(action, dict):
                raise serializers.ValidationError(
                    f"Action template {i} must be a dictionary"
                )
            
            if 'type' not in action:
                raise serializers.ValidationError(
                    f"Action template {i} must include 'type'"
                )
        
        return value


class TriggerTemplateApplicationSerializer(serializers.Serializer):
    """Serializer for applying trigger templates to workflows."""
    
    template_id = serializers.IntegerField()
    field_mappings = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Mapping of template field names to actual field IDs"
    )
    
    def validate_template_id(self, value):
        """Validate that the template exists and is active."""
        try:
            template = TriggerTemplate.objects.get(id=value, is_active=True)
            return value
        except TriggerTemplate.DoesNotExist:
            raise serializers.ValidationError("Template not found or inactive")
    
    def validate_field_mappings(self, value):
        """Validate field mappings structure."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Field mappings must be a dictionary"
            )
        
        # Validate that all values are integers (field IDs)
        for field_name, field_id in value.items():
            if not isinstance(field_id, int):
                raise serializers.ValidationError(
                    f"Field ID for '{field_name}' must be an integer"
                )
        
        return value


class WebhookRequestSerializer(serializers.Serializer):
    """Serializer for incoming webhook requests."""
    
    webhook_path = serializers.CharField(max_length=255)
    method = serializers.CharField(max_length=10)
    headers = serializers.DictField(default=dict)
    payload = serializers.DictField(default=dict)
    
    def validate_method(self, value):
        """Validate HTTP method."""
        valid_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
        if value.upper() not in valid_methods:
            raise serializers.ValidationError(f"Invalid HTTP method: {value}")
        return value.upper()


class TriggerValidationSerializer(serializers.Serializer):
    """Serializer for trigger validation results."""
    
    trigger_id = serializers.IntegerField()
    trigger_type = serializers.CharField()
    is_valid = serializers.BooleanField()
    errors = serializers.ListField(
        child=serializers.CharField(),
        default=list
    )
    warnings = serializers.ListField(
        child=serializers.CharField(),
        default=list
    )