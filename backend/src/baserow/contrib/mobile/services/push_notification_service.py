"""
Push notification service for mobile devices
"""

import json
import logging
from typing import Dict, Any, Optional
from django.conf import settings
from django.utils import timezone
from pywebpush import webpush, WebPushException

from ..models import PushSubscription, PushNotification

logger = logging.getLogger(__name__)


class PushNotificationService:
    """Service for sending push notifications to mobile devices"""
    
    def __init__(self):
        self.vapid_private_key = getattr(settings, 'VAPID_PRIVATE_KEY', '')
        self.vapid_public_key = getattr(settings, 'VAPID_PUBLIC_KEY', '')
        self.vapid_claims = getattr(settings, 'VAPID_CLAIMS', {
            'sub': 'mailto:admin@baserow.io'
        })
    
    def send_notification(
        self,
        subscription: PushSubscription,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        notification_type: str = 'system'
    ) -> bool:
        """
        Send a push notification to a specific subscription
        
        Args:
            subscription: PushSubscription instance
            title: Notification title
            body: Notification body
            data: Additional data to include
            notification_type: Type of notification
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not subscription.is_active:
            logger.warning(f"Attempted to send notification to inactive subscription {subscription.id}")
            return False
        
        # Create notification record
        notification = PushNotification.objects.create(
            subscription=subscription,
            notification_type=notification_type,
            title=title,
            body=body,
            data=data or {}
        )
        
        try:
            # Prepare notification payload
            payload = {
                'title': title,
                'body': body,
                'icon': '/icon-192x192.png',
                'badge': '/badge-72x72.png',
                'tag': f'baserow-{notification_type}',
                'data': data or {},
                'actions': self._get_notification_actions(notification_type),
                'vibrate': [200, 100, 200],
                'requireInteraction': notification_type in ['mention', 'comment']
            }
            
            # Send push notification
            webpush(
                subscription_info={
                    'endpoint': subscription.endpoint,
                    'keys': {
                        'p256dh': subscription.p256dh_key,
                        'auth': subscription.auth_key
                    }
                },
                data=json.dumps(payload),
                vapid_private_key=self.vapid_private_key,
                vapid_claims=self.vapid_claims
            )
            
            # Mark as sent
            notification.status = 'sent'
            notification.sent_at = timezone.now()
            notification.save()
            
            logger.info(f"Push notification sent successfully to subscription {subscription.id}")
            return True
            
        except WebPushException as e:
            error_message = str(e)
            logger.error(f"WebPush error for subscription {subscription.id}: {error_message}")
            
            # Handle specific errors
            if e.response and e.response.status_code in [410, 413]:
                # Subscription is no longer valid
                subscription.is_active = False
                subscription.save()
                notification.status = 'expired'
            else:
                notification.status = 'failed'
            
            notification.error_message = error_message
            notification.save()
            return False
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"Unexpected error sending push notification: {error_message}")
            
            notification.status = 'failed'
            notification.error_message = error_message
            notification.save()
            return False
    
    def send_to_user(
        self,
        user,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        notification_type: str = 'system'
    ) -> int:
        """
        Send notification to all active subscriptions for a user
        
        Args:
            user: User instance
            title: Notification title
            body: Notification body
            data: Additional data to include
            notification_type: Type of notification
            
        Returns:
            int: Number of notifications sent successfully
        """
        subscriptions = PushSubscription.objects.filter(user=user, is_active=True)
        sent_count = 0
        
        for subscription in subscriptions:
            if self.send_notification(subscription, title, body, data, notification_type):
                sent_count += 1
        
        return sent_count
    
    def send_comment_notification(self, comment, mentioned_users=None):
        """Send notification for new comments"""
        from baserow.contrib.database.models import Table
        
        try:
            table = Table.objects.get(id=comment.table_id)
            
            # Notify table collaborators
            collaborators = table.database.workspace.users.exclude(id=comment.user_id)
            
            for user in collaborators:
                # Check user's notification preferences
                if hasattr(user, 'mobile_settings') and user.mobile_settings.comment_notifications:
                    self.send_to_user(
                        user=user,
                        title=f"New comment in {table.name}",
                        body=f"{comment.user.first_name or comment.user.email} commented: {comment.content[:100]}",
                        data={
                            'type': 'comment',
                            'tableId': comment.table_id,
                            'rowId': comment.row_id,
                            'commentId': comment.id,
                            'url': f'/database/{table.database_id}/table/{table.id}'
                        },
                        notification_type='comment'
                    )
            
            # Send mention notifications
            if mentioned_users:
                for user in mentioned_users:
                    if hasattr(user, 'mobile_settings') and user.mobile_settings.mention_notifications:
                        self.send_to_user(
                            user=user,
                            title=f"You were mentioned in {table.name}",
                            body=f"{comment.user.first_name or comment.user.email} mentioned you in a comment",
                            data={
                                'type': 'mention',
                                'tableId': comment.table_id,
                                'rowId': comment.row_id,
                                'commentId': comment.id,
                                'url': f'/database/{table.database_id}/table/{table.id}'
                            },
                            notification_type='mention'
                        )
        except Exception as e:
            logger.error(f"Failed to send comment notification: {e}")
    
    def send_update_notification(self, table, updated_by, changes):
        """Send notification for table updates"""
        try:
            # Notify table collaborators
            collaborators = table.database.workspace.users.exclude(id=updated_by.id)
            
            for user in collaborators:
                if hasattr(user, 'mobile_settings') and user.mobile_settings.update_notifications:
                    self.send_to_user(
                        user=user,
                        title=f"Updates in {table.name}",
                        body=f"{updated_by.first_name or updated_by.email} made changes to the table",
                        data={
                            'type': 'update',
                            'tableId': table.id,
                            'changes': changes,
                            'url': f'/database/{table.database_id}/table/{table.id}'
                        },
                        notification_type='update'
                    )
        except Exception as e:
            logger.error(f"Failed to send update notification: {e}")
    
    def _get_notification_actions(self, notification_type: str) -> list:
        """Get notification actions based on type"""
        actions = []
        
        if notification_type == 'comment':
            actions = [
                {
                    'action': 'reply',
                    'title': 'Reply',
                    'icon': '/icons/reply.png'
                },
                {
                    'action': 'view',
                    'title': 'View',
                    'icon': '/icons/view.png'
                }
            ]
        elif notification_type == 'mention':
            actions = [
                {
                    'action': 'view',
                    'title': 'View',
                    'icon': '/icons/view.png'
                }
            ]
        
        return actions
    
    def cleanup_expired_notifications(self, days_old: int = 30):
        """Clean up old notifications"""
        cutoff_date = timezone.now() - timezone.timedelta(days=days_old)
        
        expired_count = PushNotification.objects.filter(
            created_at__lt=cutoff_date
        ).delete()[0]
        
        logger.info(f"Cleaned up {expired_count} expired notifications")
        return expired_count
    
    def cleanup_inactive_subscriptions(self, days_old: int = 90):
        """Clean up inactive subscriptions"""
        cutoff_date = timezone.now() - timezone.timedelta(days=days_old)
        
        inactive_count = PushSubscription.objects.filter(
            is_active=False,
            updated_at__lt=cutoff_date
        ).delete()[0]
        
        logger.info(f"Cleaned up {inactive_count} inactive subscriptions")
        return inactive_count