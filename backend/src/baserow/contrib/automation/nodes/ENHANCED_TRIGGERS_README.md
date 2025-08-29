# Enhanced Automation Trigger System

This document describes the enhanced automation trigger system implemented for Baserow, which extends the existing automation capabilities with new trigger types and advanced functionality.

## Overview

The enhanced trigger system adds four new trigger types to Baserow's automation system:

1. **Date-Based Triggers** - Fire based on date/time conditions
2. **Linked Record Change Triggers** - Fire when linked records change
3. **Webhook Triggers** - Fire when external webhooks are received
4. **Conditional Triggers** - Add complex conditions to existing triggers
5. **Trigger Templates** - Pre-built templates for common automation patterns

## New Trigger Types

### Date-Based Triggers

Date-based triggers monitor date fields and fire when specific date conditions are met.

**Features:**
- Date reached triggers
- Days before/after triggers
- Recurring patterns (daily, weekly, monthly)
- Overdue item detection
- Time-of-day scheduling
- Additional field conditions

**Use Cases:**
- Send reminders before due dates
- Daily/weekly status reports
- Overdue task alerts
- Recurring maintenance tasks

### Linked Record Change Triggers

These triggers monitor changes in related tables through link row fields.

**Features:**
- Monitor linked record creation, updates, deletion
- Track link additions/removals
- Field-specific monitoring
- Conditional filtering of linked records

**Use Cases:**
- Notify when project tasks are updated
- Sync data between related tables
- Cascade updates through relationships
- Track dependency changes

### Webhook Triggers

External webhook triggers allow external systems to trigger Baserow automations.

**Features:**
- Unique webhook URLs per trigger
- Multiple authentication methods (API key, Bearer token, signature)
- HTTP method filtering
- Payload mapping and validation
- Request logging

**Use Cases:**
- Integration with external services
- Real-time data synchronization
- Event-driven workflows
- Third-party system notifications

### Conditional Triggers

Conditional triggers add complex evaluation logic to existing triggers.

**Features:**
- Multiple condition groups with AND/OR logic
- Field-based conditions with various operators
- Custom logic expressions
- Time-based conditions
- Context-aware evaluation

**Use Cases:**
- Business hours only triggers
- Multi-criteria filtering
- Complex approval workflows
- Conditional notifications

## Trigger Templates

The template system provides pre-built automation patterns for common use cases.

**Features:**
- Categorized templates (project management, notifications, etc.)
- Field mapping for easy application
- Usage tracking and analytics
- Custom template creation
- Compatibility checking

**Default Templates:**
- Due Date Reminder
- New Task Assignment
- Status Change Notification
- Overdue Task Alert
- Weekly Status Report

## Implementation Details

### Models

The enhanced trigger system adds several new models:

- `DateBasedTriggerNode` - Date-based trigger configuration
- `LinkedRecordChangeTriggerNode` - Linked record change trigger configuration
- `WebhookTriggerNode` - Webhook trigger configuration
- `ConditionalTriggerNode` - Conditional trigger configuration
- `TriggerTemplate` - Template definitions
- `WebhookRequestLog` - Webhook request logging

### Service Types

Each trigger type has a corresponding service type that handles the trigger logic:

- `DateBasedTriggerServiceType` - Handles date condition evaluation
- `LinkedRecordChangeTriggerServiceType` - Monitors linked record changes
- `WebhookTriggerServiceType` - Processes webhook requests
- `ConditionalTriggerServiceType` - Evaluates complex conditions

### API Endpoints

New API endpoints are available for managing enhanced triggers:

- `/api/automation/triggers/date-triggers/` - Date-based triggers
- `/api/automation/triggers/link-triggers/` - Linked record triggers
- `/api/automation/triggers/webhook-triggers/` - Webhook triggers
- `/api/automation/triggers/conditional-triggers/` - Conditional triggers
- `/api/automation/triggers/templates/` - Trigger templates
- `/api/automation/webhooks/{path}/` - Public webhook endpoint

### Background Tasks

The system uses Celery tasks for background processing:

- `check_date_based_triggers` - Periodic date trigger evaluation
- `process_webhook_trigger` - Asynchronous webhook processing
- `evaluate_conditional_triggers` - Conditional trigger evaluation
- `validate_trigger_configurations` - System integrity checks

## Usage Examples

### Creating a Date-Based Trigger

```python
from baserow.contrib.automation.nodes.enhanced_trigger_models import DateBasedTriggerNode

trigger = DateBasedTriggerNode.objects.create(
    workflow=workflow,
    date_field=due_date_field,
    condition_type='days_before',
    days_offset=1,
    additional_conditions={
        'status': {
            'operator': 'not_equals',
            'value': 'completed'
        }
    }
)
```

### Creating a Webhook Trigger

```python
from baserow.contrib.automation.nodes.enhanced_trigger_models import WebhookTriggerNode

trigger = WebhookTriggerNode.objects.create(
    workflow=workflow,
    webhook_url_path='project_updates',
    auth_type='api_key',
    auth_token='secret_key_123',
    allowed_methods=['POST'],
    payload_mapping={
        'project_id': 'data.project.id',
        'status': 'data.status'
    }
)
```

### Applying a Template

```python
from baserow.contrib.automation.nodes.trigger_template_handler import TriggerTemplateHandler

handler = TriggerTemplateHandler()
result = handler.apply_template(
    template_id=1,
    workflow=workflow,
    field_mappings={
        'due_date': due_date_field.id,
        'assigned_to': assigned_to_field.id
    },
    user=user
)
```

## Configuration

### Celery Settings

Add the following to your Celery configuration:

```python
CELERY_BEAT_SCHEDULE = {
    'check-date-triggers': {
        'task': 'baserow.contrib.automation.tasks.check_date_based_triggers',
        'schedule': crontab(minute=0),  # Every hour
    },
    'validate-triggers': {
        'task': 'baserow.contrib.automation.tasks.validate_trigger_configurations',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}
```

### Webhook Security

For production deployments, ensure webhook endpoints are properly secured:

1. Use HTTPS for all webhook URLs
2. Implement signature verification for sensitive webhooks
3. Rate limit webhook endpoints
4. Monitor webhook request logs for suspicious activity

## Migration

The enhanced trigger system is added via migration `0014_enhanced_trigger_system.py`. This migration:

1. Creates new trigger node models
2. Creates the trigger template model
3. Creates webhook request log model
4. Adds database indexes for performance

## Testing

Run the enhanced trigger tests:

```bash
pytest backend/tests/baserow/contrib/automation/nodes/test_enhanced_triggers.py
```

## Management Commands

Initialize default trigger templates:

```bash
python manage.py init_trigger_templates
```

Force recreation of templates:

```bash
python manage.py init_trigger_templates --force
```

## Performance Considerations

1. **Date Triggers**: Use database indexes on date fields for efficient querying
2. **Webhook Triggers**: Process webhooks asynchronously to avoid blocking
3. **Conditional Triggers**: Optimize condition evaluation for large datasets
4. **Template Usage**: Cache template configurations for better performance

## Security Considerations

1. **Webhook Authentication**: Always use authentication for webhook triggers
2. **Payload Validation**: Validate webhook payloads to prevent injection attacks
3. **Rate Limiting**: Implement rate limiting for webhook endpoints
4. **Access Control**: Ensure proper permissions for trigger management
5. **Audit Logging**: Log all trigger activities for security monitoring

## Future Enhancements

Potential future improvements to the enhanced trigger system:

1. **Advanced Scheduling**: More sophisticated scheduling options
2. **Trigger Chaining**: Link triggers together for complex workflows
3. **Performance Monitoring**: Built-in performance metrics and alerting
4. **Visual Builder**: Drag-and-drop trigger configuration interface
5. **Integration Hub**: Pre-built integrations with popular services