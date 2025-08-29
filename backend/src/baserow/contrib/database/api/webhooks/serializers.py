"""
Serializers for webhook API endpoints.
"""
from rest_framework import serializers
from baserow.contrib.database.webhooks.models import Webhook, WebhookDelivery, WebhookLog


class WebhookSerializer(serializers.ModelSerializer):
    """Serializer for webhook model."""
    
    class Meta:
        model = Webhook
        fields = [
            'id', 'name', 'url', 'table', 'triggers', 'headers', 'status',
            'max_retries', 'retry_delay', 'timeout', 'created_at', 'updated_at',
            'total_deliveries', 'successful_deliveries', 'failed_deliveries',
            'last_delivery_at', 'last_success_at', 'last_failure_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'total_deliveries',
            'successful_deliveries', 'failed_deliveries', 'last_delivery_at',
            'last_success_at', 'last_failure_at'
        ]
    
    def validate_triggers(self, value):
        """Validate webhook triggers."""
        valid_triggers = [choice[0] for choice in Webhook.TRIGGER_CHOICES]
        for trigger in value:
            if trigger not in valid_triggers:
                raise serializers.ValidationError(f"Invalid trigger: {trigger}")
        return value
    
    def validate_max_retries(self, value):
        """Validate max retries."""
        if value < 0 or value > 10:
            raise serializers.ValidationError("Max retries must be between 0 and 10")
        return value
    
    def validate_retry_delay(self, value):
        """Validate retry delay."""
        if value < 1 or value > 3600:
            raise serializers.ValidationError("Retry delay must be between 1 and 3600 seconds")
        return value
    
    def validate_timeout(self, value):
        """Validate timeout."""
        if value < 1 or value > 300:
            raise serializers.ValidationError("Timeout must be between 1 and 300 seconds")
        return value


class CreateWebhookSerializer(WebhookSerializer):
    """Serializer for creating webhooks."""
    secret = serializers.CharField(required=False, allow_blank=True, write_only=True)
    
    class Meta(WebhookSerializer.Meta):
        fields = WebhookSerializer.Meta.fields + ['secret']


class WebhookDeliverySerializer(serializers.ModelSerializer):
    """Serializer for webhook delivery model."""
    
    class Meta:
        model = WebhookDelivery
        fields = [
            'id', 'trigger_event', 'status', 'attempts', 'max_attempts',
            'next_retry_at', 'response_status_code', 'response_headers',
            'error_message', 'created_at', 'delivered_at'
        ]
        read_only_fields = fields


class WebhookLogSerializer(serializers.ModelSerializer):
    """Serializer for webhook log model."""
    
    class Meta:
        model = WebhookLog
        fields = [
            'id', 'event_type', 'message', 'details', 'created_at'
        ]
        read_only_fields = fields


class WebhookTestSerializer(serializers.Serializer):
    """Serializer for testing webhook endpoints."""
    test_payload = serializers.JSONField(required=False, default=dict)
    
    def validate_test_payload(self, value):
        """Validate test payload."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Test payload must be a JSON object")
        return value


class WebhookStatsSerializer(serializers.Serializer):
    """Serializer for webhook statistics."""
    total_webhooks = serializers.IntegerField()
    active_webhooks = serializers.IntegerField()
    total_deliveries = serializers.IntegerField()
    successful_deliveries = serializers.IntegerField()
    failed_deliveries = serializers.IntegerField()
    success_rate = serializers.FloatField()
    recent_deliveries = WebhookDeliverySerializer(many=True)