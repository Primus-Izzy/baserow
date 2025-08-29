# Baserow Notification System

A comprehensive notification framework that provides multi-channel notifications with intelligent batching, user preferences, and customizable templates.

## Features

### Core Capabilities
- **Multi-Channel Delivery**: In-app, email, webhook, Slack, and Microsoft Teams notifications
- **Intelligent Batching**: Configurable batching to prevent notification spam
- **User Preferences**: Granular control over notification types and delivery methods
- **Customizable Templates**: Template system for different notification types and channels
- **Real-time Updates**: WebSocket integration for instant in-app notifications
- **Quiet Hours**: User-configurable quiet periods
- **Audit Trail**: Complete logging of all notification delivery attempts

### Notification Types
- **Collaboration**: Comment mentions, replies, row assignments
- **Automation**: Automation failures and successes
- **System**: Form submissions, workspace invitations
- **Security**: Security alerts and suspicious activity
- **Integration**: External service notifications

## Architecture

### Backend Components

#### Models (`models.py`)
- `NotificationType`: Defines available notification categories and settings
- `Notification`: Individual notification instances
- `UserNotificationPreference`: User-specific notification settings
- `NotificationTemplate`: Customizable templates for different channels
- `NotificationBatch`: Batched notifications for efficient delivery
- `NotificationDeliveryLog`: Audit trail of delivery attempts

#### Handler (`handler.py`)
- `NotificationHandler`: Main business logic for creating and sending notifications
- Manages user preferences and batching logic
- Handles template rendering and delivery coordination

#### Delivery Service (`delivery.py`)
- `NotificationDeliveryService`: Multi-channel delivery implementation
- Supports in-app, email, webhook, Slack, and Teams delivery
- Extensible channel registry for custom delivery methods

#### Background Tasks (`tasks.py`)
- Celery tasks for asynchronous notification processing
- Batch processing and cleanup tasks
- Retry logic with exponential backoff

### Frontend Components

#### Store (`store/notifications.js`)
- Vuex store for notification state management
- Real-time updates via WebSocket integration
- Preference management and statistics

#### Services (`services/notifications.js`)
- API client for notification endpoints
- Handles all HTTP communication with backend

#### Components
- `NotificationCenter.vue`: Main notification panel with bell icon
- `NotificationItem.vue`: Individual notification display
- `NotificationSettings.vue`: User preference configuration modal

## API Endpoints

### Notifications
- `GET /api/database/notifications/` - List user notifications
- `POST /api/database/notifications/mark_read/` - Mark notifications as read
- `POST /api/database/notifications/mark_all_read/` - Mark all as read
- `GET /api/database/notifications/stats/` - Get notification statistics

### Preferences
- `GET /api/database/preferences/` - Get user preferences
- `POST /api/database/preferences/bulk_update/` - Update preferences
- `POST /api/database/preferences/reset_to_defaults/` - Reset to defaults

### Templates
- `GET /api/database/templates/` - List notification templates
- `POST /api/database/templates/` - Create custom template
- `PATCH /api/database/templates/{id}/` - Update template

### Admin
- `POST /api/database/admin/create_notification/` - Create notifications (admin)

## Installation and Setup

### 1. Database Migration
```bash
python manage.py migrate
```

### 2. Initialize System
```bash
python manage.py init_notification_system
```

This command creates:
- Default notification types
- System-wide templates for all delivery methods
- Initial configuration

### 3. Celery Configuration
Add to your Celery configuration:

```python
# settings.py
CELERY_BEAT_SCHEDULE = {
    'process-batched-notifications': {
        'task': 'baserow.contrib.database.notifications.tasks.process_batched_notifications_task',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'cleanup-old-notifications': {
        'task': 'baserow.contrib.database.notifications.tasks.cleanup_old_notifications_task',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}
```

### 4. Frontend Integration
Add the notification center to your main layout:

```vue
<template>
  <div class="app-header">
    <!-- Other header content -->
    <NotificationCenter />
  </div>
</template>

<script>
import NotificationCenter from '@/modules/database/components/notifications/NotificationCenter'

export default {
  components: {
    NotificationCenter
  }
}
</script>
```

## Usage Examples

### Creating Notifications

```python
from baserow.contrib.database.notifications.handler import notification_handler

# Simple notification
notification_handler.create_notification(
    notification_type='comment_mention',
    recipient=user,
    title='You were mentioned in a comment',
    message='John mentioned you in a comment on the Projects table',
    data={
        'table_id': 123,
        'row_id': 456,
        'commenter_name': 'John Doe'
    }
)

# Notification with specific delivery methods
notification_handler.create_notification(
    notification_type='security_alert',
    recipient=user,
    title='Suspicious login detected',
    message='A login from an unknown location was detected',
    delivery_methods=['in_app', 'email'],
    data={
        'ip_address': '192.168.1.1',
        'location': 'Unknown'
    }
)
```

### Updating User Preferences

```python
# Update preferences via handler
notification_handler.update_user_preferences(
    user=user,
    preferences_data={
        'comment_mention': {
            'email_enabled': True,
            'slack_enabled': False,
            'email_batch_frequency': 'daily'
        }
    }
)
```

### Custom Templates

```python
from baserow.contrib.database.notifications.models import NotificationTemplate, NotificationType

# Create custom email template
template = NotificationTemplate.objects.create(
    notification_type=NotificationType.objects.get(name='comment_mention'),
    delivery_method='email',
    subject_template='{{ commenter_name }} mentioned you in {{ table_name }}',
    body_template='''
    Hi {{ recipient.first_name }},
    
    {{ commenter_name }} mentioned you in a comment:
    "{{ comment_text }}"
    
    Click here to view: {{ comment_url }}
    ''',
    workspace=workspace  # Optional: workspace-specific template
)
```

## Configuration

### Environment Variables

```bash
# Email settings (required for email notifications)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password
DEFAULT_FROM_EMAIL=noreply@baserow.io

# Slack integration (optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# Microsoft Teams integration (optional)
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...
```

### Notification Types Configuration

Each notification type supports:
- `supported_delivery_methods`: List of available delivery channels
- `default_enabled`: Whether enabled by default for new users
- `template_variables`: Available variables for template rendering

## Real-time Integration

The notification system integrates with Baserow's WebSocket system:

```javascript
// Frontend real-time handling
this.$realtime.subscribe('notifications', (data) => {
  if (data.type === 'notification_created') {
    // Handle new notification
    this.$store.dispatch('database/notifications/handleRealtimeNotification', data.notification)
  }
})
```

## Customization

### Adding Custom Delivery Channels

```python
from baserow.contrib.database.notifications.delivery import channel_registry

class CustomDeliveryChannel:
    def send(self, recipient, subject, content, data):
        # Custom delivery logic
        return True

# Register the channel
channel_registry.register_channel('custom', CustomDeliveryChannel)
```

### Custom Notification Types

```python
# Add via management command or admin interface
NotificationType.objects.create(
    name='custom_event',
    category='system',
    description='Custom application event',
    supported_delivery_methods=['in_app', 'email'],
    template_variables={
        'event_name': 'Name of the event',
        'event_data': 'Event-specific data'
    }
)
```

## Performance Considerations

### Batching Strategy
- **Immediate**: For urgent notifications (security, mentions)
- **Hourly**: For moderate-priority updates
- **Daily**: For digest-style notifications
- **Weekly**: For summary reports

### Database Optimization
- Indexes on recipient, status, and created_at fields
- Automatic cleanup of old notifications
- Efficient querying with select_related and prefetch_related

### Caching
- User preferences cached in Redis
- Template rendering cached for frequently used templates
- Notification counts cached per user

## Monitoring and Debugging

### Delivery Logs
All delivery attempts are logged in `NotificationDeliveryLog`:
- Success/failure status
- Error messages
- Response data from external services

### Metrics
Track key metrics:
- Notification delivery rates
- User engagement with notifications
- Template performance
- Batch processing efficiency

### Debugging
Enable debug logging:

```python
LOGGING = {
    'loggers': {
        'baserow.contrib.database.notifications': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    }
}
```

## Security Considerations

### Data Protection
- Notification content respects user permissions
- Sensitive data not included in external webhooks
- Audit trail for all notification activities

### Rate Limiting
- Built-in protection against notification spam
- Configurable limits per user and notification type
- Exponential backoff for failed deliveries

### Privacy
- Users control their notification preferences
- Opt-out mechanisms for all notification types
- GDPR-compliant data handling and deletion