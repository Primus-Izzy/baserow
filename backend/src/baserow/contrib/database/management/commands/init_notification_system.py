"""
Management command to initialize the notification system with default types and templates.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from baserow.contrib.database.notifications.models import (
    NotificationType,
    NotificationTemplate
)


class Command(BaseCommand):
    help = 'Initialize notification system with default types and templates'

    def handle(self, *args, **options):
        """Initialize the notification system."""
        
        self.stdout.write('Initializing notification system...')
        
        with transaction.atomic():
            # Create default notification types
            self._create_notification_types()
            
            # Create default templates
            self._create_default_templates()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully initialized notification system')
        )
    
    def _create_notification_types(self):
        """Create default notification types."""
        
        notification_types = [
            {
                'name': 'comment_mention',
                'category': 'collaboration',
                'description': 'User mentioned in a comment',
                'default_enabled': True,
                'supported_delivery_methods': ['in_app', 'email', 'slack', 'teams'],
                'template_variables': {
                    'commenter_name': 'Name of the person who made the comment',
                    'table_name': 'Name of the table',
                    'row_id': 'ID of the row',
                    'comment_text': 'Text of the comment'
                }
            },
            {
                'name': 'comment_reply',
                'category': 'collaboration',
                'description': 'Reply to user\'s comment',
                'default_enabled': True,
                'supported_delivery_methods': ['in_app', 'email', 'slack', 'teams'],
                'template_variables': {
                    'replier_name': 'Name of the person who replied',
                    'table_name': 'Name of the table',
                    'row_id': 'ID of the row',
                    'reply_text': 'Text of the reply'
                }
            },
            {
                'name': 'row_assigned',
                'category': 'collaboration',
                'description': 'User assigned to a row',
                'default_enabled': True,
                'supported_delivery_methods': ['in_app', 'email', 'slack', 'teams'],
                'template_variables': {
                    'assigner_name': 'Name of the person who made the assignment',
                    'table_name': 'Name of the table',
                    'row_id': 'ID of the row'
                }
            },
            {
                'name': 'automation_failed',
                'category': 'automation',
                'description': 'Automation execution failed',
                'default_enabled': True,
                'supported_delivery_methods': ['in_app', 'email'],
                'template_variables': {
                    'automation_name': 'Name of the automation',
                    'error_message': 'Error message',
                    'table_name': 'Name of the table'
                }
            },
            {
                'name': 'form_submission',
                'category': 'system',
                'description': 'New form submission received',
                'default_enabled': True,
                'supported_delivery_methods': ['in_app', 'email', 'webhook'],
                'template_variables': {
                    'form_name': 'Name of the form',
                    'submitter_email': 'Email of the submitter',
                    'table_name': 'Name of the table'
                }
            },
            {
                'name': 'workspace_invitation',
                'category': 'collaboration',
                'description': 'Invitation to join workspace',
                'default_enabled': True,
                'supported_delivery_methods': ['email'],
                'template_variables': {
                    'inviter_name': 'Name of the person who sent the invitation',
                    'workspace_name': 'Name of the workspace'
                }
            },
            {
                'name': 'security_alert',
                'category': 'security',
                'description': 'Security-related alerts',
                'default_enabled': True,
                'supported_delivery_methods': ['in_app', 'email'],
                'template_variables': {
                    'alert_type': 'Type of security alert',
                    'ip_address': 'IP address involved',
                    'timestamp': 'When the event occurred'
                }
            },
            {
                'name': 'digest',
                'category': 'system',
                'description': 'Daily/weekly activity digest',
                'default_enabled': False,
                'supported_delivery_methods': ['email'],
                'template_variables': {
                    'period': 'Time period (daily/weekly)',
                    'activity_summary': 'Summary of activities'
                }
            }
        ]
        
        for type_data in notification_types:
            notification_type, created = NotificationType.objects.get_or_create(
                name=type_data['name'],
                defaults=type_data
            )
            
            if created:
                self.stdout.write(f'Created notification type: {type_data["name"]}')
            else:
                self.stdout.write(f'Notification type already exists: {type_data["name"]}')
    
    def _create_default_templates(self):
        """Create default notification templates."""
        
        templates = [
            # Comment mention templates
            {
                'notification_type': 'comment_mention',
                'delivery_method': 'in_app',
                'subject_template': 'You were mentioned in a comment',
                'body_template': '{{ commenter_name }} mentioned you in a comment on {{ table_name }}: "{{ comment_text }}"',
                'is_default': True
            },
            {
                'notification_type': 'comment_mention',
                'delivery_method': 'email',
                'subject_template': 'You were mentioned in a Baserow comment',
                'body_template': '''Hi {{ recipient.first_name }},

{{ commenter_name }} mentioned you in a comment on the table "{{ table_name }}":

"{{ comment_text }}"

Click here to view the comment and respond.

Best regards,
The Baserow Team''',
                'is_default': True
            },
            
            # Comment reply templates
            {
                'notification_type': 'comment_reply',
                'delivery_method': 'in_app',
                'subject_template': 'New reply to your comment',
                'body_template': '{{ replier_name }} replied to your comment on {{ table_name }}: "{{ reply_text }}"',
                'is_default': True
            },
            {
                'notification_type': 'comment_reply',
                'delivery_method': 'email',
                'subject_template': 'New reply to your Baserow comment',
                'body_template': '''Hi {{ recipient.first_name }},

{{ replier_name }} replied to your comment on the table "{{ table_name }}":

"{{ reply_text }}"

Click here to view the conversation.

Best regards,
The Baserow Team''',
                'is_default': True
            },
            
            # Row assignment templates
            {
                'notification_type': 'row_assigned',
                'delivery_method': 'in_app',
                'subject_template': 'You have been assigned to a row',
                'body_template': '{{ assigner_name }} assigned you to a row in {{ table_name }}',
                'is_default': True
            },
            {
                'notification_type': 'row_assigned',
                'delivery_method': 'email',
                'subject_template': 'You have been assigned to a Baserow row',
                'body_template': '''Hi {{ recipient.first_name }},

{{ assigner_name }} has assigned you to a row in the table "{{ table_name }}".

Click here to view the row and take action.

Best regards,
The Baserow Team''',
                'is_default': True
            },
            
            # Automation failed templates
            {
                'notification_type': 'automation_failed',
                'delivery_method': 'in_app',
                'subject_template': 'Automation failed',
                'body_template': 'The automation "{{ automation_name }}" failed: {{ error_message }}',
                'is_default': True
            },
            {
                'notification_type': 'automation_failed',
                'delivery_method': 'email',
                'subject_template': 'Baserow automation failed',
                'body_template': '''Hi {{ recipient.first_name }},

The automation "{{ automation_name }}" in table "{{ table_name }}" has failed with the following error:

{{ error_message }}

Please check your automation configuration and try again.

Best regards,
The Baserow Team''',
                'is_default': True
            },
            
            # Form submission templates
            {
                'notification_type': 'form_submission',
                'delivery_method': 'in_app',
                'subject_template': 'New form submission',
                'body_template': 'New submission received for form "{{ form_name }}"',
                'is_default': True
            },
            {
                'notification_type': 'form_submission',
                'delivery_method': 'email',
                'subject_template': 'New Baserow form submission',
                'body_template': '''Hi {{ recipient.first_name }},

A new submission has been received for the form "{{ form_name }}" in table "{{ table_name }}".

{% if submitter_email %}Submitted by: {{ submitter_email }}{% endif %}

Click here to view the submission.

Best regards,
The Baserow Team''',
                'is_default': True
            },
            
            # Workspace invitation templates
            {
                'notification_type': 'workspace_invitation',
                'delivery_method': 'email',
                'subject_template': 'You\'ve been invited to join a Baserow workspace',
                'body_template': '''Hi there,

{{ inviter_name }} has invited you to join the workspace "{{ workspace_name }}" on Baserow.

Click the link below to accept the invitation and get started:

[Accept Invitation]

If you don't have a Baserow account yet, you'll be able to create one during the process.

Best regards,
The Baserow Team''',
                'is_default': True
            },
            
            # Security alert templates
            {
                'notification_type': 'security_alert',
                'delivery_method': 'in_app',
                'subject_template': 'Security Alert',
                'body_template': 'Security alert: {{ alert_type }}',
                'is_default': True
            },
            {
                'notification_type': 'security_alert',
                'delivery_method': 'email',
                'subject_template': 'Baserow Security Alert',
                'body_template': '''Hi {{ recipient.first_name }},

We detected a security event on your Baserow account:

Alert Type: {{ alert_type }}
IP Address: {{ ip_address }}
Time: {{ timestamp }}

If this was not you, please secure your account immediately by changing your password.

Best regards,
The Baserow Security Team''',
                'is_default': True
            }
        ]
        
        for template_data in templates:
            # Get the notification type
            try:
                notification_type = NotificationType.objects.get(
                    name=template_data['notification_type']
                )
                template_data['notification_type'] = notification_type
                
                template, created = NotificationTemplate.objects.get_or_create(
                    notification_type=notification_type,
                    delivery_method=template_data['delivery_method'],
                    workspace=None,  # System-wide template
                    defaults={
                        'subject_template': template_data['subject_template'],
                        'body_template': template_data['body_template'],
                        'is_default': template_data['is_default']
                    }
                )
                
                if created:
                    self.stdout.write(
                        f'Created template: {notification_type.name} - {template_data["delivery_method"]}'
                    )
                else:
                    self.stdout.write(
                        f'Template already exists: {notification_type.name} - {template_data["delivery_method"]}'
                    )
                    
            except NotificationType.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f'Notification type not found: {template_data["notification_type"]}'
                    )
                )