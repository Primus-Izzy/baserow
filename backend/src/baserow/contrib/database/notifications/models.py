# Notification System Models
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class NotificationType(models.Model):
    """Defines different types of notifications available in the system."""
    
    CATEGORY_CHOICES = [
        ('collaboration', 'Collaboration'),
        ('automation', 'Automation'),
        ('system', 'System'),
        ('security', 'Security'),
        ('integration', 'Integration'),
    ]
    
    DELIVERY_METHOD_CHOICES = [
        ('in_app', 'In-App'),
        ('email', 'Email'),
        ('webhook', 'Webhook'),
        ('slack', 'Slack'),
        ('teams', 'Microsoft Teams'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    default_enabled = models.BooleanField(default=True)
    supported_delivery_methods = models.JSONField(default=list)
    template_variables = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'database_notification_type'
    
    def __str__(self):
        return f"{self.name} ({self.category})"


class NotificationTemplate(models.Model):
    """Customizable templates for different notification types and delivery methods."""
    
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE)
    delivery_method = models.CharField(max_length=20)
    subject_template = models.TextField(blank=True)
    body_template = models.TextField()
    is_default = models.BooleanField(default=False)
    workspace = models.ForeignKey(
        'core.Workspace', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="If null, this is a system-wide template"
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'database_notification_template'
        unique_together = ['notification_type', 'delivery_method', 'workspace']
    
    def __str__(self):
        return f"{self.notification_type.name} - {self.delivery_method}"


class UserNotificationPreference(models.Model):
    """User-specific notification preferences."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE)
    workspace = models.ForeignKey('core.Workspace', on_delete=models.CASCADE, null=True, blank=True)
    
    # Delivery method preferences
    in_app_enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=True)
    webhook_enabled = models.BooleanField(default=False)
    slack_enabled = models.BooleanField(default=False)
    teams_enabled = models.BooleanField(default=False)
    
    # Batching preferences
    email_batch_frequency = models.CharField(
        max_length=20,
        choices=[
            ('immediate', 'Immediate'),
            ('hourly', 'Hourly'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
        ],
        default='immediate'
    )
    
    # Quiet hours
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    quiet_hours_timezone = models.CharField(max_length=50, default='UTC')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'database_user_notification_preference'
        unique_together = ['user', 'notification_type', 'workspace']
    
    def __str__(self):
        return f"{self.user.email} - {self.notification_type.name}"


class Notification(models.Model):
    """Individual notification instances."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('batched', 'Batched'),
        ('cancelled', 'Cancelled'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE)
    
    # Content object that triggered the notification
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Notification content
    title = models.CharField(max_length=255)
    message = models.TextField()
    data = models.JSONField(default=dict)  # Additional context data
    
    # Delivery tracking
    delivery_method = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Batching
    batch_group = models.CharField(max_length=100, null=True, blank=True)
    
    # Metadata
    workspace = models.ForeignKey('core.Workspace', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'database_notification'
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['batch_group']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} -> {self.recipient.email}"
    
    def mark_as_read(self):
        """Mark notification as read."""
        if not self.read_at:
            self.read_at = timezone.now()
            self.save(update_fields=['read_at'])
    
    def mark_as_sent(self):
        """Mark notification as sent."""
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at'])


class NotificationBatch(models.Model):
    """Batched notifications for efficient delivery."""
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE)
    delivery_method = models.CharField(max_length=20)
    batch_key = models.CharField(max_length=100)
    
    # Batch content
    subject = models.CharField(max_length=255)
    content = models.TextField()
    notification_count = models.PositiveIntegerField(default=0)
    
    # Scheduling
    scheduled_for = models.DateTimeField()
    sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'database_notification_batch'
        unique_together = ['recipient', 'batch_key', 'scheduled_for']
    
    def __str__(self):
        return f"Batch {self.batch_key} -> {self.recipient.email}"


class NotificationDeliveryLog(models.Model):
    """Log of notification delivery attempts."""
    
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    delivery_method = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    response_data = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    attempted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'database_notification_delivery_log'
    
    def __str__(self):
        return f"{self.notification.title} - {self.delivery_method} - {self.status}"