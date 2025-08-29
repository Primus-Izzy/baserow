"""
Notification System Handler

Provides comprehensive notification management including:
- Creating and sending notifications
- Managing user preferences
- Intelligent batching
- Template rendering
- Multi-channel delivery
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from django.utils import timezone
from django.template import Template, Context
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings

from .models import (
    Notification,
    NotificationType,
    NotificationTemplate,
    UserNotificationPreference,
    NotificationBatch,
    NotificationDeliveryLog
)
from .exceptions import NotificationError, TemplateRenderError
from .delivery import NotificationDeliveryService

User = get_user_model()
logger = logging.getLogger(__name__)


class NotificationHandler:
    """Main handler for the notification system."""
    
    def __init__(self):
        self.delivery_service = NotificationDeliveryService()
    
    def create_notification(
        self,
        notification_type: str,
        recipient: User,
        title: str,
        message: str,
        data: Optional[Dict] = None,
        content_object: Optional[Any] = None,
        workspace=None,
        delivery_methods: Optional[List[str]] = None
    ) -> List[Notification]:
        """
        Create and queue notifications for delivery.
        
        Args:
            notification_type: Type of notification
            recipient: User to receive the notification
            title: Notification title
            message: Notification message
            data: Additional context data
            content_object: Related object that triggered the notification
            workspace: Workspace context
            delivery_methods: Specific delivery methods to use
        
        Returns:
            List of created notification instances
        """
        try:
            # Get notification type
            notif_type = NotificationType.objects.get(name=notification_type)
            
            # Get user preferences
            preferences = self.get_user_preferences(recipient, notif_type, workspace)
            
            # Determine delivery methods
            if delivery_methods is None:
                delivery_methods = self._get_enabled_delivery_methods(preferences)
            
            notifications = []
            
            for method in delivery_methods:
                # Check if user has this method enabled
                if not self._is_delivery_method_enabled(preferences, method):
                    continue
                
                # Check quiet hours
                if self._is_in_quiet_hours(preferences):
                    continue
                
                # Create notification
                notification = Notification.objects.create(
                    recipient=recipient,
                    notification_type=notif_type,
                    title=title,
                    message=message,
                    data=data or {},
                    content_object=content_object,
                    delivery_method=method,
                    workspace=workspace
                )
                
                notifications.append(notification)
                
                # Handle batching or immediate delivery
                if self._should_batch(preferences, method):
                    self._add_to_batch(notification, preferences)
                else:
                    self._queue_for_immediate_delivery(notification)
            
            return notifications
            
        except Exception as e:
            logger.error(f"Error creating notification: {str(e)}")
            raise NotificationError(f"Failed to create notification: {str(e)}")
    
    def send_notification(self, notification: Notification) -> bool:
        """
        Send a single notification.
        
        Args:
            notification: Notification instance to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Render template
            rendered_content = self._render_notification_template(notification)
            
            # Send via delivery service
            success = self.delivery_service.send(
                notification.delivery_method,
                notification.recipient,
                rendered_content['subject'],
                rendered_content['body'],
                notification.data
            )
            
            # Log delivery attempt
            self._log_delivery_attempt(notification, success)
            
            if success:
                notification.mark_as_sent()
            else:
                notification.status = 'failed'
                notification.save(update_fields=['status'])
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending notification {notification.id}: {str(e)}")
            self._log_delivery_attempt(notification, False, str(e))
            notification.status = 'failed'
            notification.save(update_fields=['status'])
            return False
    
    def get_user_preferences(
        self, 
        user: User, 
        notification_type: NotificationType, 
        workspace=None
    ) -> UserNotificationPreference:
        """Get or create user notification preferences."""
        preferences, created = UserNotificationPreference.objects.get_or_create(
            user=user,
            notification_type=notification_type,
            workspace=workspace,
            defaults={
                'in_app_enabled': notification_type.default_enabled,
                'email_enabled': notification_type.default_enabled,
            }
        )
        return preferences
    
    def update_user_preferences(
        self,
        user: User,
        preferences_data: Dict,
        workspace=None
    ) -> Dict[str, UserNotificationPreference]:
        """Update user notification preferences."""
        updated_preferences = {}
        
        for notif_type_name, settings in preferences_data.items():
            try:
                notif_type = NotificationType.objects.get(name=notif_type_name)
                preferences = self.get_user_preferences(user, notif_type, workspace)
                
                # Update preferences
                for key, value in settings.items():
                    if hasattr(preferences, key):
                        setattr(preferences, key, value)
                
                preferences.save()
                updated_preferences[notif_type_name] = preferences
                
            except NotificationType.DoesNotExist:
                logger.warning(f"Unknown notification type: {notif_type_name}")
                continue
        
        return updated_preferences
    
    def get_unread_notifications(
        self, 
        user: User, 
        workspace=None, 
        limit: int = 50
    ) -> List[Notification]:
        """Get unread in-app notifications for a user."""
        queryset = Notification.objects.filter(
            recipient=user,
            delivery_method='in_app',
            read_at__isnull=True
        ).select_related('notification_type')
        
        if workspace:
            queryset = queryset.filter(workspace=workspace)
        
        return list(queryset.order_by('-created_at')[:limit])
    
    def mark_notifications_as_read(
        self, 
        user: User, 
        notification_ids: List[int]
    ) -> int:
        """Mark multiple notifications as read."""
        count = Notification.objects.filter(
            id__in=notification_ids,
            recipient=user,
            read_at__isnull=True
        ).update(read_at=timezone.now())
        
        return count
    
    def process_batched_notifications(self) -> int:
        """Process and send batched notifications that are due."""
        processed_count = 0
        
        # Get batches that are due for sending
        due_batches = NotificationBatch.objects.filter(
            scheduled_for__lte=timezone.now(),
            sent_at__isnull=True
        ).select_related('recipient', 'notification_type')
        
        for batch in due_batches:
            try:
                success = self._send_batch(batch)
                if success:
                    processed_count += 1
            except Exception as e:
                logger.error(f"Error processing batch {batch.id}: {str(e)}")
        
        return processed_count
    
    def cleanup_old_notifications(self, days: int = 90) -> int:
        """Clean up old notifications."""
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Delete old read notifications
        deleted_count, _ = Notification.objects.filter(
            created_at__lt=cutoff_date,
            read_at__isnull=False
        ).delete()
        
        # Delete old delivery logs
        NotificationDeliveryLog.objects.filter(
            attempted_at__lt=cutoff_date
        ).delete()
        
        return deleted_count
    
    def _get_enabled_delivery_methods(
        self, 
        preferences: UserNotificationPreference
    ) -> List[str]:
        """Get list of enabled delivery methods for user preferences."""
        methods = []
        
        if preferences.in_app_enabled:
            methods.append('in_app')
        if preferences.email_enabled:
            methods.append('email')
        if preferences.webhook_enabled:
            methods.append('webhook')
        if preferences.slack_enabled:
            methods.append('slack')
        if preferences.teams_enabled:
            methods.append('teams')
        
        return methods
    
    def _is_delivery_method_enabled(
        self, 
        preferences: UserNotificationPreference, 
        method: str
    ) -> bool:
        """Check if a delivery method is enabled for the user."""
        method_map = {
            'in_app': preferences.in_app_enabled,
            'email': preferences.email_enabled,
            'webhook': preferences.webhook_enabled,
            'slack': preferences.slack_enabled,
            'teams': preferences.teams_enabled,
        }
        return method_map.get(method, False)
    
    def _is_in_quiet_hours(self, preferences: UserNotificationPreference) -> bool:
        """Check if current time is within user's quiet hours."""
        if not preferences.quiet_hours_enabled:
            return False
        
        # This is a simplified implementation
        # In production, you'd want proper timezone handling
        now = timezone.now().time()
        start = preferences.quiet_hours_start
        end = preferences.quiet_hours_end
        
        if start and end:
            if start <= end:
                return start <= now <= end
            else:  # Quiet hours span midnight
                return now >= start or now <= end
        
        return False
    
    def _should_batch(
        self, 
        preferences: UserNotificationPreference, 
        method: str
    ) -> bool:
        """Determine if notification should be batched."""
        if method != 'email':
            return False
        
        return preferences.email_batch_frequency != 'immediate'
    
    def _add_to_batch(
        self, 
        notification: Notification, 
        preferences: UserNotificationPreference
    ):
        """Add notification to a batch."""
        # Calculate when batch should be sent
        scheduled_for = self._calculate_batch_time(preferences.email_batch_frequency)
        
        # Create batch key
        batch_key = f"{notification.notification_type.name}_{preferences.email_batch_frequency}"
        
        # Get or create batch
        batch, created = NotificationBatch.objects.get_or_create(
            recipient=notification.recipient,
            batch_key=batch_key,
            scheduled_for=scheduled_for,
            defaults={
                'notification_type': notification.notification_type,
                'delivery_method': 'email',
                'subject': f"Baserow Notifications - {notification.notification_type.name}",
                'content': "",
                'notification_count': 0
            }
        )
        
        # Update batch
        batch.notification_count += 1
        batch.content += f"• {notification.title}: {notification.message}\n"
        batch.save()
        
        # Update notification status
        notification.status = 'batched'
        notification.batch_group = batch_key
        notification.save(update_fields=['status', 'batch_group'])
    
    def _calculate_batch_time(self, frequency: str) -> datetime:
        """Calculate when a batch should be sent based on frequency."""
        now = timezone.now()
        
        if frequency == 'hourly':
            return now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        elif frequency == 'daily':
            return now.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
        elif frequency == 'weekly':
            days_ahead = 0 - now.weekday()  # Monday is 0
            if days_ahead <= 0:
                days_ahead += 7
            return now.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=days_ahead)
        
        return now
    
    def _queue_for_immediate_delivery(self, notification: Notification):
        """Queue notification for immediate delivery."""
        from .tasks import send_notification_task
        send_notification_task.delay(notification.id)
    
    def _render_notification_template(self, notification: Notification) -> Dict[str, str]:
        """Render notification template with context data."""
        try:
            # Get template
            template = NotificationTemplate.objects.filter(
                notification_type=notification.notification_type,
                delivery_method=notification.delivery_method,
                workspace=notification.workspace
            ).first()
            
            if not template:
                # Fall back to default template
                template = NotificationTemplate.objects.filter(
                    notification_type=notification.notification_type,
                    delivery_method=notification.delivery_method,
                    is_default=True
                ).first()
            
            if not template:
                # Use basic template
                return {
                    'subject': notification.title,
                    'body': notification.message
                }
            
            # Prepare context
            context_data = {
                'notification': notification,
                'recipient': notification.recipient,
                'title': notification.title,
                'message': notification.message,
                **notification.data
            }
            
            context = Context(context_data)
            
            # Render templates
            subject_template = Template(template.subject_template or notification.title)
            body_template = Template(template.body_template)
            
            return {
                'subject': subject_template.render(context),
                'body': body_template.render(context)
            }
            
        except Exception as e:
            logger.error(f"Error rendering template: {str(e)}")
            raise TemplateRenderError(f"Failed to render template: {str(e)}")
    
    def _send_batch(self, batch: NotificationBatch) -> bool:
        """Send a batched notification."""
        try:
            success = self.delivery_service.send(
                batch.delivery_method,
                batch.recipient,
                batch.subject,
                batch.content,
                {}
            )
            
            if success:
                batch.sent_at = timezone.now()
                batch.save(update_fields=['sent_at'])
                
                # Update individual notifications
                Notification.objects.filter(
                    batch_group=batch.batch_key,
                    recipient=batch.recipient,
                    status='batched'
                ).update(status='sent', sent_at=timezone.now())
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending batch {batch.id}: {str(e)}")
            return False
    
    def _log_delivery_attempt(
        self, 
        notification: Notification, 
        success: bool, 
        error_message: str = ""
    ):
        """Log a delivery attempt."""
        NotificationDeliveryLog.objects.create(
            notification=notification,
            delivery_method=notification.delivery_method,
            status='success' if success else 'failed',
            error_message=error_message
        )


# Singleton instance
notification_handler = NotificationHandler()