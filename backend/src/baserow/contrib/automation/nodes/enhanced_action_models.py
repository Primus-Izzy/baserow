"""
Enhanced automation action models for the expanded action system.

This module provides models for advanced action types including notifications,
webhooks, status changes, and multi-step workflows with conditional branching.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from baserow.contrib.automation.nodes.models import AutomationActionNode
from baserow.core.mixins import CreatedAndUpdatedOnMixin


class NotificationActionNode(AutomationActionNode):
    """
    Action node for sending notifications to users or external systems.
    """
    
    notification_type = models.CharField(
        max_length=50,
        choices=[
            ('email', 'Email'),
            ('in_app', 'In-App Notification'),
            ('slack', 'Slack'),
            ('teams', 'Microsoft Teams'),
            ('webhook', 'Webhook'),
        ],
        default='email'
    )
    
    # Recipients configuration
    recipient_users = models.ManyToManyField(
        AbstractUser,
        blank=True,
        help_text="Specific users to notify"
    )
    
    recipient_roles = models.JSONField(
        default=list,
        help_text="Roles to notify (e.g., ['admin', 'editor'])"
    )
    
    # Message configuration
    subject_template = models.TextField(
        blank=True,
        help_text="Template for notification subject/title"
    )
    
    message_template = models.TextField(
        help_text="Template for notification message body"
    )
    
    # External service configuration
    external_config = models.JSONField(
        default=dict,
        help_text="Configuration for external notification services"
    )


class WebhookActionNode(AutomationActionNode):
    """
    Action node for sending HTTP webhooks to external systems.
    """
    
    url = models.URLField(
        help_text="Webhook URL to send the request to"
    )
    
    method = models.CharField(
        max_length=10,
        choices=[
            ('GET', 'GET'),
            ('POST', 'POST'),
            ('PUT', 'PUT'),
            ('PATCH', 'PATCH'),
            ('DELETE', 'DELETE'),
        ],
        default='POST'
    )
    
    headers = models.JSONField(
        default=dict,
        help_text="HTTP headers to include in the request"
    )
    
    payload_template = models.TextField(
        blank=True,
        help_text="JSON template for the webhook payload"
    )
    
    authentication = models.JSONField(
        default=dict,
        help_text="Authentication configuration (API keys, OAuth, etc.)"
    )
    
    retry_config = models.JSONField(
        default=dict,
        help_text="Retry configuration for failed webhook calls"
    )


class StatusChangeActionNode(AutomationActionNode):
    """
    Action node for changing status fields or other field values.
    """
    
    target_field_id = models.PositiveIntegerField(
        help_text="ID of the field to update"
    )
    
    new_value_template = models.TextField(
        help_text="Template for the new field value"
    )
    
    condition_template = models.TextField(
        blank=True,
        help_text="Optional condition template to check before updating"
    )


class ConditionalBranchNode(AutomationActionNode):
    """
    Action node for conditional branching in workflows.
    """
    
    condition_template = models.TextField(
        help_text="Template for the condition to evaluate"
    )
    
    condition_type = models.CharField(
        max_length=50,
        choices=[
            ('equals', 'Equals'),
            ('not_equals', 'Not Equals'),
            ('greater_than', 'Greater Than'),
            ('less_than', 'Less Than'),
            ('contains', 'Contains'),
            ('starts_with', 'Starts With'),
            ('ends_with', 'Ends With'),
            ('is_empty', 'Is Empty'),
            ('is_not_empty', 'Is Not Empty'),
            ('custom', 'Custom Expression'),
        ],
        default='equals'
    )
    
    comparison_value_template = models.TextField(
        blank=True,
        help_text="Template for the value to compare against"
    )


class DelayActionNode(AutomationActionNode):
    """
    Action node for adding delays in workflow execution.
    """
    
    delay_type = models.CharField(
        max_length=20,
        choices=[
            ('fixed', 'Fixed Duration'),
            ('until_date', 'Until Specific Date'),
            ('until_condition', 'Until Condition Met'),
        ],
        default='fixed'
    )
    
    delay_duration = models.DurationField(
        null=True,
        blank=True,
        help_text="Fixed delay duration"
    )
    
    delay_until_template = models.TextField(
        blank=True,
        help_text="Template for date/time to delay until"
    )
    
    condition_template = models.TextField(
        blank=True,
        help_text="Template for condition to wait for"
    )
    
    max_wait_duration = models.DurationField(
        null=True,
        blank=True,
        help_text="Maximum time to wait for condition"
    )


class WorkflowExecutionLog(CreatedAndUpdatedOnMixin, models.Model):
    """
    Log of workflow execution steps for debugging and monitoring.
    """
    
    workflow = models.ForeignKey(
        'automation.AutomationWorkflow',
        on_delete=models.CASCADE,
        related_name='execution_logs'
    )
    
    node = models.ForeignKey(
        'automation.AutomationNode',
        on_delete=models.CASCADE,
        related_name='execution_logs'
    )
    
    execution_id = models.UUIDField(
        help_text="Unique identifier for this workflow execution"
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('running', 'Running'),
            ('success', 'Success'),
            ('failed', 'Failed'),
            ('skipped', 'Skipped'),
            ('timeout', 'Timeout'),
        ],
        default='pending'
    )
    
    input_data = models.JSONField(
        default=dict,
        help_text="Input data for this execution step"
    )
    
    output_data = models.JSONField(
        default=dict,
        help_text="Output data from this execution step"
    )
    
    error_message = models.TextField(
        blank=True,
        help_text="Error message if execution failed"
    )
    
    execution_time_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Execution time in milliseconds"
    )
    
    retry_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of retry attempts"
    )


class ActionTemplate(CreatedAndUpdatedOnMixin, models.Model):
    """
    Template for common automation action patterns.
    """
    
    name = models.CharField(
        max_length=255,
        help_text="Display name for the template"
    )
    
    description = models.TextField(
        help_text="Description of what this template does"
    )
    
    category = models.CharField(
        max_length=100,
        choices=[
            ('notification', 'Notifications'),
            ('data_management', 'Data Management'),
            ('integration', 'Integrations'),
            ('workflow_control', 'Workflow Control'),
            ('reporting', 'Reporting'),
        ],
        default='notification'
    )
    
    template_config = models.JSONField(
        help_text="Configuration template for the action"
    )
    
    required_fields = models.JSONField(
        default=list,
        help_text="List of required field configurations"
    )
    
    is_system_template = models.BooleanField(
        default=False,
        help_text="Whether this is a built-in system template"
    )
    
    created_by = models.ForeignKey(
        AbstractUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="User who created this template"
    )
    
    usage_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this template has been used"
    )
    
    class Meta:
        ordering = ['-usage_count', 'name']