"""
Enhanced trigger models for the automation system.

This module contains new trigger node models that extend the automation system
with date-based triggers, linked record change triggers, external webhook triggers,
and conditional trigger evaluation.
"""

from django.db import models
from django.contrib.postgres.fields import JSONField

from baserow.contrib.automation.nodes.models import AutomationTriggerNode


class DateBasedTriggerNode(AutomationTriggerNode):
    """
    Trigger node that fires based on date/time conditions.
    Supports scheduled triggers, date reached triggers, and recurring patterns.
    """
    
    # Date field to monitor
    date_field = models.ForeignKey(
        'database.Field',
        on_delete=models.CASCADE,
        related_name='date_trigger_nodes',
        help_text="The date field to monitor for trigger conditions"
    )
    
    # Trigger condition type
    TRIGGER_CONDITIONS = [
        ('date_reached', 'Date Reached'),
        ('days_before', 'Days Before Date'),
        ('days_after', 'Days After Date'),
        ('recurring', 'Recurring Pattern'),
        ('overdue', 'Overdue Items'),
    ]
    
    condition_type = models.CharField(
        max_length=20,
        choices=TRIGGER_CONDITIONS,
        default='date_reached',
        help_text="Type of date condition to trigger on"
    )
    
    # Number of days for before/after conditions
    days_offset = models.IntegerField(
        default=0,
        help_text="Number of days before/after the date field value"
    )
    
    # Recurring pattern configuration
    recurring_pattern = JSONField(
        default=dict,
        blank=True,
        help_text="Configuration for recurring triggers (daily, weekly, monthly, etc.)"
    )
    
    # Time of day to check (for daily recurring triggers)
    check_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Time of day to check the trigger condition"
    )
    
    # Additional conditions
    additional_conditions = JSONField(
        default=dict,
        blank=True,
        help_text="Additional field-based conditions that must be met"
    )


class LinkedRecordChangeTriggerNode(AutomationTriggerNode):
    """
    Trigger node that fires when linked records change.
    Monitors changes in related tables through link row fields.
    """
    
    # Link row field to monitor
    link_field = models.ForeignKey(
        'database.Field',
        on_delete=models.CASCADE,
        related_name='link_trigger_nodes',
        help_text="The link row field to monitor for changes"
    )
    
    # What changes to monitor
    CHANGE_TYPES = [
        ('linked_record_created', 'Linked Record Created'),
        ('linked_record_updated', 'Linked Record Updated'),
        ('linked_record_deleted', 'Linked Record Deleted'),
        ('link_added', 'Link Added'),
        ('link_removed', 'Link Removed'),
        ('any_change', 'Any Change in Linked Records'),
    ]
    
    change_type = models.CharField(
        max_length=25,
        choices=CHANGE_TYPES,
        default='any_change',
        help_text="Type of change to monitor in linked records"
    )
    
    # Fields to monitor in linked table
    monitored_fields = JSONField(
        default=list,
        blank=True,
        help_text="Specific fields in the linked table to monitor for changes"
    )
    
    # Conditions for the linked records
    linked_record_conditions = JSONField(
        default=dict,
        blank=True,
        help_text="Conditions that linked records must meet to trigger"
    )


class WebhookTriggerNode(AutomationTriggerNode):
    """
    Trigger node that fires when external webhooks are received.
    Provides endpoints for external systems to trigger automations.
    """
    
    # Webhook configuration
    webhook_url_path = models.CharField(
        max_length=255,
        unique=True,
        help_text="Unique URL path for this webhook trigger"
    )
    
    # Authentication settings
    AUTH_TYPES = [
        ('none', 'No Authentication'),
        ('api_key', 'API Key'),
        ('bearer_token', 'Bearer Token'),
        ('signature', 'Signature Verification'),
    ]
    
    auth_type = models.CharField(
        max_length=15,
        choices=AUTH_TYPES,
        default='api_key',
        help_text="Authentication method for webhook requests"
    )
    
    # API key or token (encrypted)
    auth_token = models.CharField(
        max_length=255,
        blank=True,
        help_text="Authentication token for webhook requests"
    )
    
    # Signature secret for verification
    signature_secret = models.CharField(
        max_length=255,
        blank=True,
        help_text="Secret key for signature verification"
    )
    
    # HTTP methods allowed
    allowed_methods = JSONField(
        default=list,
        help_text="HTTP methods allowed for this webhook (GET, POST, PUT, etc.)"
    )
    
    # Payload processing configuration
    payload_mapping = JSONField(
        default=dict,
        blank=True,
        help_text="Mapping of webhook payload fields to automation context"
    )
    
    # Request validation rules
    validation_rules = JSONField(
        default=dict,
        blank=True,
        help_text="Rules to validate incoming webhook requests"
    )


class ConditionalTriggerNode(AutomationTriggerNode):
    """
    Trigger node that evaluates complex conditions before firing.
    Can be combined with other triggers to add conditional logic.
    """
    
    # Base trigger to extend
    base_trigger = models.ForeignKey(
        AutomationTriggerNode,
        on_delete=models.CASCADE,
        related_name='conditional_extensions',
        help_text="Base trigger node to add conditions to"
    )
    
    # Complex condition configuration
    condition_groups = JSONField(
        default=list,
        help_text="Groups of conditions with AND/OR logic"
    )
    
    # Condition evaluation mode
    EVALUATION_MODES = [
        ('all_must_match', 'All Conditions Must Match (AND)'),
        ('any_can_match', 'Any Condition Can Match (OR)'),
        ('custom_logic', 'Custom Logic Expression'),
    ]
    
    evaluation_mode = models.CharField(
        max_length=20,
        choices=EVALUATION_MODES,
        default='all_must_match',
        help_text="How to evaluate multiple condition groups"
    )
    
    # Custom logic expression for complex conditions
    custom_logic = models.TextField(
        blank=True,
        help_text="Custom logic expression using condition group IDs"
    )
    
    # Time-based conditions
    time_conditions = JSONField(
        default=dict,
        blank=True,
        help_text="Time-based conditions (business hours, weekdays, etc.)"
    )


class TriggerTemplate(models.Model):
    """
    Template system for common trigger patterns.
    Allows users to quickly set up common automation scenarios.
    """
    
    name = models.CharField(
        max_length=255,
        help_text="Display name for the trigger template"
    )
    
    description = models.TextField(
        help_text="Description of what this template does"
    )
    
    # Template category
    CATEGORIES = [
        ('project_management', 'Project Management'),
        ('notifications', 'Notifications'),
        ('data_sync', 'Data Synchronization'),
        ('reporting', 'Reporting'),
        ('approval_workflows', 'Approval Workflows'),
        ('maintenance', 'Maintenance Tasks'),
        ('custom', 'Custom'),
    ]
    
    category = models.CharField(
        max_length=25,
        choices=CATEGORIES,
        default='custom',
        help_text="Category for organizing templates"
    )
    
    # Template configuration
    trigger_config = JSONField(
        help_text="Configuration template for the trigger"
    )
    
    # Associated action templates
    action_templates = JSONField(
        default=list,
        help_text="Templates for actions that commonly go with this trigger"
    )
    
    # Required field types for this template
    required_field_types = JSONField(
        default=list,
        help_text="Field types required in the table to use this template"
    )
    
    # Template metadata
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this template is available for use"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Usage tracking
    usage_count = models.IntegerField(
        default=0,
        help_text="Number of times this template has been used"
    )
    
    class Meta:
        ordering = ['category', 'name']
        
    def __str__(self):
        return f"{self.name} ({self.category})"