"""
Handler for webhook system with reliable delivery.
"""
import json
import hmac
import hashlib
import requests
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from celery import shared_task

from .models import Webhook, WebhookDelivery, WebhookLog


class WebhookHandler:
    """Handler for managing webhooks and deliveries."""
    
    def create_webhook(self, user, group, name, url, triggers, **kwargs):
        """Create a new webhook."""
        webhook = Webhook.objects.create(
            name=name,
            url=url,
            group=group,
            triggers=triggers,
            created_by=user,
            **kwargs
        )
        
        self._log_webhook_event(
            webhook,
            'webhook_created',
            f"Webhook '{name}' created by {user.email}"
        )
        
        return webhook
    
    def update_webhook(self, webhook, **kwargs):
        """Update an existing webhook."""
        for key, value in kwargs.items():
            setattr(webhook, key, value)
        webhook.save()
        
        self._log_webhook_event(
            webhook,
            'webhook_updated',
            f"Webhook '{webhook.name}' updated"
        )
        
        return webhook
    
    def delete_webhook(self, webhook):
        """Delete a webhook."""
        webhook_name = webhook.name
        webhook.delete()
        
        # Note: Log entry will be deleted with webhook due to CASCADE
        
    def trigger_webhook(self, webhook, event_type, payload):
        """Trigger a webhook delivery."""
        if webhook.status != 'active':
            return None
        
        if event_type not in webhook.triggers:
            return None
        
        # Create delivery record
        delivery = WebhookDelivery.objects.create(
            webhook=webhook,
            trigger_event=event_type,
            payload=payload,
            max_attempts=webhook.max_retries
        )
        
        # Queue delivery task
        deliver_webhook.delay(delivery.id)
        
        return delivery
    
    def trigger_webhooks_for_event(self, group, event_type, payload, table=None):
        """Trigger all applicable webhooks for an event."""
        webhooks = Webhook.objects.filter(
            group=group,
            status='active',
            triggers__contains=[event_type]
        )
        
        if table:
            # Include webhooks for specific table or all tables
            webhooks = webhooks.filter(
                models.Q(table=table) | models.Q(table__isnull=True)
            )
        
        deliveries = []
        for webhook in webhooks:
            delivery = self.trigger_webhook(webhook, event_type, payload)
            if delivery:
                deliveries.append(delivery)
        
        return deliveries
    
    def retry_failed_deliveries(self):
        """Retry failed webhook deliveries that are due for retry."""
        now = timezone.now()
        
        failed_deliveries = WebhookDelivery.objects.filter(
            status__in=['failed', 'retrying'],
            next_retry_at__lte=now,
            attempts__lt=models.F('max_attempts')
        )
        
        for delivery in failed_deliveries:
            deliver_webhook.delay(delivery.id)
    
    def _log_webhook_event(self, webhook, event_type, message, details=None, delivery=None):
        """Log a webhook event."""
        WebhookLog.objects.create(
            webhook=webhook,
            delivery=delivery,
            event_type=event_type,
            message=message,
            details=details or {}
        )
    
    def _generate_signature(self, payload, secret):
        """Generate HMAC signature for webhook payload."""
        if not secret:
            return None
        
        payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
        signature = hmac.new(
            secret.encode('utf-8'),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        
        return f"sha256={signature}"


@shared_task(bind=True, max_retries=3)
def deliver_webhook(self, delivery_id):
    """Celery task to deliver webhook payload."""
    try:
        delivery = WebhookDelivery.objects.get(id=delivery_id)
        webhook = delivery.webhook
        handler = WebhookHandler()
        
        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': f'Baserow-Webhooks/1.0',
            'X-Baserow-Event': delivery.trigger_event,
            'X-Baserow-Delivery': str(delivery.id),
            'X-Baserow-Webhook': str(webhook.id),
        }
        
        # Add custom headers
        headers.update(webhook.headers)
        
        # Add signature if secret is configured
        signature = handler._generate_signature(delivery.payload, webhook.secret)
        if signature:
            headers['X-Baserow-Signature'] = signature
        
        # Update delivery attempt
        delivery.attempts += 1
        delivery.status = 'retrying' if delivery.attempts > 1 else 'pending'
        delivery.save()
        
        # Make HTTP request
        response = requests.post(
            webhook.url,
            json=delivery.payload,
            headers=headers,
            timeout=webhook.timeout,
            allow_redirects=True
        )
        
        # Update delivery with response
        delivery.response_status_code = response.status_code
        delivery.response_headers = dict(response.headers)
        delivery.response_body = response.text[:10000]  # Limit response body size
        delivery.delivered_at = timezone.now()
        
        if 200 <= response.status_code < 300:
            # Success
            delivery.status = 'success'
            webhook.successful_deliveries += 1
            webhook.last_success_at = timezone.now()
            
            handler._log_webhook_event(
                webhook,
                'delivery_success',
                f"Webhook delivered successfully (HTTP {response.status_code})",
                {'response_time': response.elapsed.total_seconds()},
                delivery
            )
        else:
            # HTTP error
            raise requests.HTTPError(f"HTTP {response.status_code}: {response.text}")
    
    except Exception as exc:
        delivery.error_message = str(exc)
        
        if delivery.attempts >= delivery.max_attempts:
            # Max attempts reached
            delivery.status = 'abandoned'
            webhook.failed_deliveries += 1
            webhook.last_failure_at = timezone.now()
            
            handler._log_webhook_event(
                webhook,
                'delivery_abandoned',
                f"Webhook delivery abandoned after {delivery.attempts} attempts",
                {'error': str(exc)},
                delivery
            )
        else:
            # Schedule retry
            delivery.status = 'failed'
            retry_delay = webhook.retry_delay * (2 ** (delivery.attempts - 1))  # Exponential backoff
            delivery.next_retry_at = timezone.now() + timedelta(seconds=retry_delay)
            
            handler._log_webhook_event(
                webhook,
                'delivery_failed',
                f"Webhook delivery failed (attempt {delivery.attempts}), retrying in {retry_delay}s",
                {'error': str(exc)},
                delivery
            )
            
            # Retry the task
            raise self.retry(exc=exc, countdown=retry_delay)
    
    finally:
        delivery.save()
        webhook.total_deliveries += 1
        webhook.last_delivery_at = timezone.now()
        webhook.save()