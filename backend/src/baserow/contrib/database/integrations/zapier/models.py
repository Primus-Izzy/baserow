"""
Models for Zapier integration support.
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from baserow.core.models import Group
from baserow.contrib.database.models import Table

User = get_user_model()


class ZapierIntegration(models.Model):
    """
    Model representing a Zapier integration configuration.
    """
    TRIGGER_TYPES = [
        ('new_row', 'New Row'),
        ('updated_row', 'Updated Row'),
        ('deleted_row', 'Deleted Row'),
        ('new_table', 'New Table'),
        ('updated_table', 'Updated Table'),
    ]
    
    ACTION_TYPES = [
        ('create_row', 'Create Row'),
        ('update_row', 'Update Row'),
        ('delete_row', 'Delete Row'),
        ('find_row', 'Find Row'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='zapier_integrations')
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='zapier_integrations')
    integration_type = models.CharField(
        max_length=20,
        choices=[('trigger', 'Trigger'), ('action', 'Action')]
    )
    trigger_type = models.CharField(
        max_length=50,
        choices=TRIGGER_TYPES,
        null=True,
        blank=True
    )
    action_type = models.CharField(
        max_length=50,
        choices=ACTION_TYPES,
        null=True,
        blank=True
    )
    configuration = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Statistics
    total_executions = models.PositiveIntegerField(default=0)
    successful_executions = models.PositiveIntegerField(default=0)
    failed_executions = models.PositiveIntegerField(default=0)
    last_execution_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'database_zapier_integration'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.integration_type})"


class ZapierExecution(models.Model):
    """
    Model tracking Zapier integration executions.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('retrying', 'Retrying'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    integration = models.ForeignKey(
        ZapierIntegration,
        on_delete=models.CASCADE,
        related_name='executions'
    )
    zapier_execution_id = models.CharField(max_length=255, null=True, blank=True)
    input_data = models.JSONField()
    output_data = models.JSONField(default=dict)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    error_message = models.TextField(blank=True)
    execution_time_ms = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'database_zapier_execution'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['integration', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Execution {self.id} for {self.integration.name}"


class MakeIntegration(models.Model):
    """
    Model representing a Make.com integration configuration.
    """
    WEBHOOK_TYPES = [
        ('instant', 'Instant'),
        ('polling', 'Polling'),
    ]
    
    MODULE_TYPES = [
        ('trigger', 'Trigger'),
        ('action', 'Action'),
        ('search', 'Search'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='make_integrations')
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='make_integrations')
    module_type = models.CharField(max_length=20, choices=MODULE_TYPES)
    webhook_type = models.CharField(
        max_length=20,
        choices=WEBHOOK_TYPES,
        default='instant'
    )
    webhook_url = models.URLField(max_length=2000, null=True, blank=True)
    configuration = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Statistics
    total_executions = models.PositiveIntegerField(default=0)
    successful_executions = models.PositiveIntegerField(default=0)
    failed_executions = models.PositiveIntegerField(default=0)
    last_execution_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'database_make_integration'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.module_type})"


class MakeExecution(models.Model):
    """
    Model tracking Make.com integration executions.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('retrying', 'Retrying'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    integration = models.ForeignKey(
        MakeIntegration,
        on_delete=models.CASCADE,
        related_name='executions'
    )
    make_execution_id = models.CharField(max_length=255, null=True, blank=True)
    input_data = models.JSONField()
    output_data = models.JSONField(default=dict)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    error_message = models.TextField(blank=True)
    execution_time_ms = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'database_make_execution'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['integration', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Execution {self.id} for {self.integration.name}"