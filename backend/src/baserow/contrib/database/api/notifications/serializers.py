"""
API Serializers for Notification System
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

from baserow.contrib.database.notifications.models import (
    Notification,
    NotificationType,
    NotificationTemplate,
    UserNotificationPreference,
    NotificationBatch
)

User = get_user_model()


class NotificationTypeSerializer(serializers.ModelSerializer):
    """Serializer for notification types."""
    
    class Meta:
        model = NotificationType
        fields = [
            'id', 'name', 'category', 'description', 'default_enabled',
            'supported_delivery_methods', 'template_variables', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications."""
    
    notification_type = NotificationTypeSerializer(read_only=True)
    is_read = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message', 'data',
            'delivery_method', 'status', 'is_read', 'created_at', 'sent_at'
        ]
        read_only_fields = [
            'id', 'notification_type', 'status', 'created_at', 'sent_at'
        ]
    
    def get_is_read(self, obj):
        """Check if notification is read."""
        return obj.read_at is not None


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for notification templates."""
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'notification_type', 'delivery_method', 'subject_template',
            'body_template', 'is_default', 'workspace', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserNotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for user notification preferences."""
    
    notification_type_name = serializers.CharField(source='notification_type.name', read_only=True)
    notification_type_category = serializers.CharField(source='notification_type.category', read_only=True)
    
    class Meta:
        model = UserNotificationPreference
        fields = [
            'id', 'notification_type', 'notification_type_name', 'notification_type_category',
            'workspace', 'in_app_enabled', 'email_enabled', 'webhook_enabled',
            'slack_enabled', 'teams_enabled', 'email_batch_frequency',
            'quiet_hours_enabled', 'quiet_hours_start', 'quiet_hours_end',
            'quiet_hours_timezone', 'updated_at'
        ]
        read_only_fields = ['id', 'notification_type_name', 'notification_type_category', 'updated_at']


class BulkNotificationPreferenceUpdateSerializer(serializers.Serializer):
    """Serializer for bulk updating notification preferences."""
    
    preferences = serializers.DictField(
        child=serializers.DictField(),
        help_text="Dictionary of notification type names to preference settings"
    )
    workspace_id = serializers.IntegerField(required=False, allow_null=True)


class MarkNotificationsReadSerializer(serializers.Serializer):
    """Serializer for marking notifications as read."""
    
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of notification IDs to mark as read"
    )


class NotificationStatsSerializer(serializers.Serializer):
    """Serializer for notification statistics."""
    
    total_notifications = serializers.IntegerField()
    unread_notifications = serializers.IntegerField()
    notifications_by_type = serializers.DictField()
    recent_activity = serializers.ListField()


class CreateNotificationSerializer(serializers.Serializer):
    """Serializer for creating notifications (admin use)."""
    
    notification_type = serializers.CharField()
    recipient_ids = serializers.ListField(child=serializers.IntegerField())
    title = serializers.CharField(max_length=255)
    message = serializers.CharField()
    data = serializers.DictField(required=False, default=dict)
    delivery_methods = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    workspace_id = serializers.IntegerField(required=False, allow_null=True)