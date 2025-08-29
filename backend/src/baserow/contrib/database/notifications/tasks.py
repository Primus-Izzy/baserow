"""
Celery tasks for notification system
"""

import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_notification_task(self, notification_id: int):
    """
    Celery task to send a single notification.
    
    Args:
        notification_id: ID of the notification to send
    """
    try:
        from .models import Notification
        from .handler import notification_handler
        
        notification = Notification.objects.get(id=notification_id)
        success = notification_handler.send_notification(notification)
        
        if not success:
            # Retry with exponential backoff
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        
        logger.info(f"Successfully sent notification {notification_id}")
        
    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found")
    except Exception as exc:
        logger.error(f"Error sending notification {notification_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def process_batched_notifications_task():
    """
    Celery task to process batched notifications that are due for sending.
    """
    try:
        from .handler import notification_handler
        
        processed_count = notification_handler.process_batched_notifications()
        logger.info(f"Processed {processed_count} batched notifications")
        
        return processed_count
        
    except Exception as exc:
        logger.error(f"Error processing batched notifications: {str(exc)}")
        raise


@shared_task
def cleanup_old_notifications_task(days: int = 90):
    """
    Celery task to clean up old notifications.
    
    Args:
        days: Number of days to keep notifications
    """
    try:
        from .handler import notification_handler
        
        deleted_count = notification_handler.cleanup_old_notifications(days)
        logger.info(f"Cleaned up {deleted_count} old notifications")
        
        return deleted_count
        
    except Exception as exc:
        logger.error(f"Error cleaning up notifications: {str(exc)}")
        raise


@shared_task
def send_digest_notifications_task():
    """
    Celery task to send digest notifications (daily/weekly summaries).
    """
    try:
        from .models import UserNotificationPreference, NotificationType
        from .handler import notification_handler
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Get users who want digest notifications
        digest_preferences = UserNotificationPreference.objects.filter(
            email_batch_frequency__in=['daily', 'weekly']
        ).select_related('user', 'notification_type')
        
        processed_count = 0
        
        for preference in digest_preferences:
            # Create digest notification
            # This would contain a summary of recent activity
            notification_handler.create_notification(
                notification_type='digest',
                recipient=preference.user,
                title=f"Your {preference.email_batch_frequency} Baserow digest",
                message="Here's what happened in your workspaces...",
                delivery_methods=['email']
            )
            processed_count += 1
        
        logger.info(f"Sent {processed_count} digest notifications")
        return processed_count
        
    except Exception as exc:
        logger.error(f"Error sending digest notifications: {str(exc)}")
        raise