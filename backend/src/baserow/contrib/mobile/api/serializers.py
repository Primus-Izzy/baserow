"""
API serializers for mobile features
"""

from rest_framework import serializers
from ..models import PushSubscription, PushNotification, OfflineOperation, MobileSettings, CameraUpload


class PushSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for push notification subscriptions"""
    
    subscription = serializers.JSONField(write_only=True)
    
    class Meta:
        model = PushSubscription
        fields = ['id', 'subscription', 'user_agent', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def create(self, validated_data):
        subscription_data = validated_data.pop('subscription')
        
        # Extract subscription details
        endpoint = subscription_data.get('endpoint')
        keys = subscription_data.get('keys', {})
        p256dh_key = keys.get('p256dh', '')
        auth_key = keys.get('auth', '')
        
        # Create or update subscription
        subscription, created = PushSubscription.objects.update_or_create(
            user=validated_data['user'],
            endpoint=endpoint,
            defaults={
                'p256dh_key': p256dh_key,
                'auth_key': auth_key,
                'user_agent': validated_data.get('user_agent', ''),
                'is_active': True
            }
        )
        
        return subscription


class PushNotificationSerializer(serializers.ModelSerializer):
    """Serializer for push notifications"""
    
    class Meta:
        model = PushNotification
        fields = [
            'id', 'notification_type', 'title', 'body', 'data',
            'status', 'error_message', 'sent_at', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'error_message', 'sent_at', 'created_at']


class OfflineOperationSerializer(serializers.ModelSerializer):
    """Serializer for offline operations"""
    
    class Meta:
        model = OfflineOperation
        fields = [
            'id', 'operation_type', 'table_id', 'row_id', 'data',
            'status', 'retry_count', 'error_message', 'created_at', 'synced_at'
        ]
        read_only_fields = ['id', 'status', 'retry_count', 'error_message', 'synced_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class MobileSettingsSerializer(serializers.ModelSerializer):
    """Serializer for mobile settings"""
    
    class Meta:
        model = MobileSettings
        fields = [
            'notifications_enabled', 'comment_notifications', 'mention_notifications',
            'update_notifications', 'high_contrast', 'large_text', 'reduced_motion',
            'screen_reader_announcements', 'offline_mode_enabled', 'auto_sync_enabled',
            'sync_on_wifi_only', 'updated_at'
        ]
        read_only_fields = ['updated_at']


class CameraUploadSerializer(serializers.ModelSerializer):
    """Serializer for camera uploads"""
    
    file = serializers.FileField(write_only=True)
    
    class Meta:
        model = CameraUpload
        fields = [
            'id', 'file', 'file_name', 'file_size', 'mime_type',
            'table_id', 'row_id', 'field_id', 'processed', 'created_at'
        ]
        read_only_fields = ['id', 'file_name', 'file_size', 'mime_type', 'processed', 'created_at']
    
    def create(self, validated_data):
        file = validated_data.pop('file')
        
        validated_data.update({
            'user': self.context['request'].user,
            'file_name': file.name,
            'file_size': file.size,
            'mime_type': file.content_type or 'application/octet-stream'
        })
        
        camera_upload = super().create(validated_data)
        
        # Process the file (save to storage, create file record, etc.)
        self._process_uploaded_file(camera_upload, file)
        
        return camera_upload
    
    def _process_uploaded_file(self, camera_upload, file):
        """Process the uploaded file"""
        # This would integrate with Baserow's file handling system
        # For now, just mark as processed
        camera_upload.processed = True
        camera_upload.save()


class SyncStatusSerializer(serializers.Serializer):
    """Serializer for sync status information"""
    
    is_online = serializers.BooleanField()
    pending_operations = serializers.IntegerField()
    last_sync_time = serializers.DateTimeField(allow_null=True)
    sync_in_progress = serializers.BooleanField()


class NotificationTestSerializer(serializers.Serializer):
    """Serializer for testing notifications"""
    
    title = serializers.CharField(max_length=255, default="Test Notification")
    body = serializers.CharField(max_length=500, default="This is a test notification from Baserow")
    data = serializers.JSONField(default=dict, required=False)