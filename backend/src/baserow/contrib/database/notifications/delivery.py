"""
Notification Delivery Service

Handles delivery of notifications through various channels:
- In-app notifications (stored in database)
- Email notifications
- Webhook notifications
- Slack notifications
- Microsoft Teams notifications
"""

import logging
import requests
from typing import Dict, Any, Optional
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


class NotificationDeliveryService:
    """Service for delivering notifications through various channels."""
    
    def send(
        self,
        delivery_method: str,
        recipient: User,
        subject: str,
        content: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Send notification through specified delivery method.
        
        Args:
            delivery_method: Method to use for delivery
            recipient: User receiving the notification
            subject: Notification subject
            content: Notification content
            data: Additional data for the notification
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            if delivery_method == 'in_app':
                return self._send_in_app(recipient, subject, content, data)
            elif delivery_method == 'email':
                return self._send_email(recipient, subject, content, data)
            elif delivery_method == 'webhook':
                return self._send_webhook(recipient, subject, content, data)
            elif delivery_method == 'slack':
                return self._send_slack(recipient, subject, content, data)
            elif delivery_method == 'teams':
                return self._send_teams(recipient, subject, content, data)
            else:
                logger.warning(f"Unknown delivery method: {delivery_method}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending notification via {delivery_method}: {str(e)}")
            return False
    
    def _send_in_app(
        self, 
        recipient: User, 
        subject: str, 
        content: str, 
        data: Dict[str, Any]
    ) -> bool:
        """Send in-app notification (already stored in database)."""
        # In-app notifications are already stored when created
        # This method is called for consistency but doesn't need to do anything
        return True
    
    def _send_email(
        self, 
        recipient: User, 
        subject: str, 
        content: str, 
        data: Dict[str, Any]
    ) -> bool:
        """Send email notification."""
        try:
            # Get email settings
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@baserow.io')
            
            # Send email
            send_mail(
                subject=subject,
                message=content,
                from_email=from_email,
                recipient_list=[recipient.email],
                fail_silently=False
            )
            
            logger.info(f"Email sent to {recipient.email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {recipient.email}: {str(e)}")
            return False
    
    def _send_webhook(
        self, 
        recipient: User, 
        subject: str, 
        content: str, 
        data: Dict[str, Any]
    ) -> bool:
        """Send webhook notification."""
        try:
            # Get webhook URL from user profile or workspace settings
            webhook_url = data.get('webhook_url')
            if not webhook_url:
                # Try to get from user profile
                webhook_url = getattr(recipient, 'webhook_url', None)
            
            if not webhook_url:
                logger.warning(f"No webhook URL configured for user {recipient.email}")
                return False
            
            # Prepare payload
            payload = {
                'type': 'notification',
                'recipient': {
                    'id': recipient.id,
                    'email': recipient.email,
                    'first_name': recipient.first_name,
                    'last_name': recipient.last_name,
                },
                'subject': subject,
                'content': content,
                'data': data,
                'timestamp': data.get('timestamp')
            }
            
            # Send webhook
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                logger.info(f"Webhook sent to {webhook_url}: {subject}")
                return True
            else:
                logger.error(f"Webhook failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send webhook: {str(e)}")
            return False
    
    def _send_slack(
        self, 
        recipient: User, 
        subject: str, 
        content: str, 
        data: Dict[str, Any]
    ) -> bool:
        """Send Slack notification."""
        try:
            # Get Slack webhook URL or bot token
            slack_webhook = data.get('slack_webhook')
            if not slack_webhook:
                slack_webhook = getattr(settings, 'SLACK_WEBHOOK_URL', None)
            
            if not slack_webhook:
                logger.warning("No Slack webhook configured")
                return False
            
            # Prepare Slack message
            slack_message = {
                'text': subject,
                'attachments': [
                    {
                        'color': 'good',
                        'fields': [
                            {
                                'title': 'Message',
                                'value': content,
                                'short': False
                            }
                        ],
                        'footer': 'Baserow Notifications',
                        'ts': data.get('timestamp')
                    }
                ]
            }
            
            # Send to Slack
            response = requests.post(
                slack_webhook,
                json=slack_message,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Slack notification sent: {subject}")
                return True
            else:
                logger.error(f"Slack notification failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {str(e)}")
            return False
    
    def _send_teams(
        self, 
        recipient: User, 
        subject: str, 
        content: str, 
        data: Dict[str, Any]
    ) -> bool:
        """Send Microsoft Teams notification."""
        try:
            # Get Teams webhook URL
            teams_webhook = data.get('teams_webhook')
            if not teams_webhook:
                teams_webhook = getattr(settings, 'TEAMS_WEBHOOK_URL', None)
            
            if not teams_webhook:
                logger.warning("No Teams webhook configured")
                return False
            
            # Prepare Teams message (Adaptive Card format)
            teams_message = {
                '@type': 'MessageCard',
                '@context': 'http://schema.org/extensions',
                'themeColor': '0076D7',
                'summary': subject,
                'sections': [
                    {
                        'activityTitle': subject,
                        'activitySubtitle': f'Notification for {recipient.first_name} {recipient.last_name}',
                        'text': content,
                        'facts': [
                            {
                                'name': 'Recipient',
                                'value': recipient.email
                            },
                            {
                                'name': 'Time',
                                'value': data.get('timestamp', 'Now')
                            }
                        ]
                    }
                ]
            }
            
            # Send to Teams
            response = requests.post(
                teams_webhook,
                json=teams_message,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                logger.info(f"Teams notification sent: {subject}")
                return True
            else:
                logger.error(f"Teams notification failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send Teams notification: {str(e)}")
            return False


class NotificationChannelRegistry:
    """Registry for custom notification channels."""
    
    def __init__(self):
        self._channels = {}
    
    def register_channel(self, name: str, handler_class):
        """Register a custom notification channel."""
        self._channels[name] = handler_class
    
    def get_channel(self, name: str):
        """Get a notification channel handler."""
        return self._channels.get(name)
    
    def list_channels(self) -> list:
        """List all registered channels."""
        return list(self._channels.keys())


# Global registry instance
channel_registry = NotificationChannelRegistry()