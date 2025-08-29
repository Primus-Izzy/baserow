"""
Models for webhook system with reliable delivery.
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from baserow.contrib.database.models import Table
from baserow.core.models import Group

User = get_user_model()


class Webhook(models.Model):
    """
    Model representing a webhook endpoint for real-time notifications.
    """
    TRIGGER_CHOICES = [
        ('row_created', 'Row Created'),
        ('row_updated', 'Row Updated'),
        ('row_deleted', 'Row Deleted'),
        ('table_created', 'Table Created'),
        ('table_updated', 'Table Updated'),
        ('table_deleted', 'Table Deleted'),
        ('field_created', 'Field Created'),
        ('field_updated', 'Field Updated'),
        ('field_deleted', 'Field Deleted'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('disabled', 'Disabled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    url = models.URLField(max_length=2000)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='webhooks')
    table = models.ForeignKey(
        Table, 
        on_delete=models.CASCADE, 
        related_name='webhooks',
        null=True,
        blank=True,
        help_text="If specified, webhook only triggers for this table"
    )
    triggers = models.JSONField(
        default=list,
        help_text="List of trigger events that activate this webhook"
    )
    headers = models.JSONField(
        default=dict,
        help_text="Custom headers to include in webhook requests"
    )
    secret = models.CharField(
        max_length=255,
        blank=True,
        help_text="Secret for webhook signature verification"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    max_retries = models.PositiveIntegerField(default=3)
    retry_delay = models.PositiveIntegerField(
        default=60,
        help_text="Delay in seconds between retries"
    )
    timeout = models.PositiveIntegerField(
        default=30,
        help_text="Request timeout in seconds"
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Statistics
    total_deliveries = models.PositiveIntegerField(default=0)
    successful_deliveries = models.PositiveIntegerField(default=0)
    failed_deliveries = models.PositiveIntegerField(default=0)
    last_delivery_at = models.DateTimeField(null=True, blank=True)
    last_success_at = models.DateTimeField(null=True, blank=True)
    last_failure_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'database_webhook'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.url})"


class WebhookDelivery(models.Model):
    """
    Model tracking individual webhook delivery attempts.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('retrying', 'Retrying'),
        ('abandoned', 'Abandoned'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    webhook = models.ForeignKey(
        Webhook, 
        on_delete=models.CASCADE, 
        related_name='deliveries'
    )
    trigger_event = models.CharField(max_length=50)
    payload = models.JSONField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=3)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    
    # Response details
    response_status_code = models.PositiveIntegerField(null=True, blank=True)
    response_headers = models.JSONField(default=dict)
    response_body = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'database_webhook_delivery'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['webhook', 'status']),
            models.Index(fields=['next_retry_at']),
        ]
    
    def __str__(self):
        return f"Delivery {self.id} for {self.webhook.name}"


class WebhookLog(models.Model):
    """
    Model for webhook activity logging.
    """
    webhook = models.ForeignKey(
        Webhook, 
        on_delete=models.CASCADE, 
        related_name='logs'
    )
    delivery = models.ForeignKey(
        WebhookDelivery,
        on_delete=models.CASCADE,
        related_name='logs',
        null=True,
        blank=True
    )
    event_type = models.CharField(max_length=50)
    message = models.TextField()
    details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'database_webhook_log'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['webhook', 'created_at']),
        ]