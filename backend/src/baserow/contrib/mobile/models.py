"""
Mobile-specific models for push notifications and offline sync
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class PushSubscription(models.Model):
    """
    Store push notification subscriptions for mobile devices
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_subscriptions')
    endpoint = models.URLField(max_length=500)
    p256dh_key = models.CharField(max_length=255)
    auth_key = models.CharField(max_length=255)
    user_agent = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'endpoint']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Push subscription for {self.user.email}"


class PushNotification(models.Model):
    """
    Track sent push notifications
    """
    NOTIFICATION_TYPES = [
        ('comment', 'Comment'),
        ('mention', 'Mention'),
        ('update', 'Update'),
        ('reminder', 'Reminder'),
        ('system', 'System'),
    ]
    
    DELIVERY_STATUS = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('expired', 'Expired'),
    ]
    
    subscription = models.ForeignKey(PushSubscription, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    body = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=DELIVERY_STATUS, default='pending')
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['subscription', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['notification_type']),
        ]
    
    def __str__(self):
        return f"{self.notification_type} notification: {self.title}"


class OfflineOperation(models.Model):
    """
    Store operations performed while offline for later sync
    """
    OPERATION_TYPES = [
        ('create_row', 'Create Row'),
        ('update_row', 'Update Row'),
        ('delete_row', 'Delete Row'),
        ('update_field', 'Update Field'),
        ('create_view', 'Create View'),
        ('update_view', 'Update View'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('synced', 'Synced'),
        ('failed', 'Failed'),
        ('expired', 'Expired'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    operation_type = models.CharField(max_length=20, choices=OPERATION_TYPES)
    table_id = models.PositiveIntegerField(null=True, blank=True)
    row_id = models.PositiveIntegerField(null=True, blank=True)
    data = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    retry_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['table_id']),
        ]
    
    def __str__(self):
        return f"{self.operation_type} operation for user {self.user.email}"
    
    def mark_synced(self):
        """Mark operation as successfully synced"""
        self.status = 'synced'
        self.synced_at = timezone.now()
        self.save()
    
    def mark_failed(self, error_message):
        """Mark operation as failed with error message"""
        self.status = 'failed'
        self.error_message = error_message
        self.retry_count += 1
        self.save()


class MobileSettings(models.Model):
    """
    Store mobile-specific user settings
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mobile_settings')
    
    # Notification preferences
    notifications_enabled = models.BooleanField(default=True)
    comment_notifications = models.BooleanField(default=True)
    mention_notifications = models.BooleanField(default=True)
    update_notifications = models.BooleanField(default=False)
    
    # Accessibility preferences
    high_contrast = models.BooleanField(default=False)
    large_text = models.BooleanField(default=False)
    reduced_motion = models.BooleanField(default=False)
    screen_reader_announcements = models.BooleanField(default=True)
    
    # Offline preferences
    offline_mode_enabled = models.BooleanField(default=True)
    auto_sync_enabled = models.BooleanField(default=True)
    sync_on_wifi_only = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Mobile Settings'
        verbose_name_plural = 'Mobile Settings'
    
    def __str__(self):
        return f"Mobile settings for {self.user.email}"


class CameraUpload(models.Model):
    """
    Track files uploaded via camera
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    mime_type = models.CharField(max_length=100)
    table_id = models.PositiveIntegerField(null=True, blank=True)
    row_id = models.PositiveIntegerField(null=True, blank=True)
    field_id = models.PositiveIntegerField(null=True, blank=True)
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['table_id', 'row_id']),
        ]
    
    def __str__(self):
        return f"Camera upload: {self.file_name}"