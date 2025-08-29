# Enhanced Automation Action System

This document describes the enhanced automation action system that extends Baserow's automation capabilities with advanced action types, multi-step workflows, conditional branching, and comprehensive error handling.

## Overview

The enhanced action system provides:

- **Advanced Action Types**: Notifications, webhooks, status changes, conditional branching, and delays
- **Multi-step Workflows**: Sequential action processing with proper error handling
- **Conditional Branching**: Dynamic workflow paths based on data conditions
- **Action Templates**: Reusable patterns for common automation scenarios
- **Comprehensive Logging**: Detailed execution tracking and monitoring
- **Retry Logic**: Robust error handling with configurable retry mechanisms

## Action Types

### 1. Notification Actions (`NotificationActionNode`)

Send notifications through various channels:

- **Email**: Send emails to specific users or roles
- **In-App**: Create in-app notifications
- **Slack**: Send messages to Slack channels via webhooks
- **Microsoft Teams**: Send messages to Teams channels
- **Custom Webhooks**: Send notifications to custom webhook endpoints

**Configuration:**
```python
{
    "notification_type": "email",
    "recipient_users": [1, 2, 3],
    "recipient_roles": ["admin", "editor"],
    "subject_template": "Task Update: {{ task_name }}",
    "message_template": "Task {{ task_name }} is now {{ status }}",
    "external_config": {
        "webhook_url": "https://hooks.slack.com/...",
        "headers": {"Authorization": "Bearer token"}
    }
}
```

### 2. Webhook Actions (`WebhookActionNode`)

Send HTTP requests to external systems:

- **Multiple HTTP Methods**: GET, POST, PUT, PATCH, DELETE
- **Template Payloads**: Dynamic payload generation using templates
- **Authentication**: Support for API keys, Bearer tokens, and custom headers
- **Retry Logic**: Configurable retry mechanisms with exponential backoff

**Configuration:**
```python
{
    "url": "https://api.example.com/webhook",
    "method": "POST",
    "headers": {"Content-Type": "application/json"},
    "payload_template": '{"event": "{{ event_type }}", "data": {{ data }}}',
    "authentication": {
        "type": "bearer",
        "token": "your-api-token"
    },
    "retry_config": {
        "max_retries": 3,
        "retry_delay": 1,
        "backoff_multiplier": 2
    }
}
```

### 3. Status Change Actions (`StatusChangeActionNode`)

Update field values based on conditions:

- **Field Updates**: Change any field value in the current or related records
- **Conditional Updates**: Only update if certain conditions are met
- **Template Values**: Use templates to generate dynamic values

**Configuration:**
```python
{
    "target_field_id": 123,
    "new_value_template": "{{ new_status }}",
    "condition_template": "{{ current_status == 'pending' }}"
}
```

### 4. Conditional Branch Actions (`ConditionalBranchNode`)

Create branching logic in workflows:

- **Multiple Condition Types**: equals, greater_than, contains, etc.
- **Template Conditions**: Dynamic condition evaluation
- **Branch Outputs**: Different paths for true/false results

**Configuration:**
```python
{
    "condition_template": "{{ amount }}",
    "condition_type": "greater_than",
    "comparison_value_template": "1000"
}
```

### 5. Delay Actions (`DelayActionNode`)

Add delays to workflow execution:

- **Fixed Delays**: Wait for a specific duration
- **Until Date**: Wait until a specific date/time
- **Conditional Delays**: Wait until a condition is met

**Configuration:**
```python
{
    "delay_type": "fixed",
    "delay_duration": "00:30:00",  # 30 minutes
    "max_wait_duration": "24:00:00"  # Maximum 24 hours
}
```

## Action Templates

Action templates provide reusable patterns for common automation scenarios:

### Built-in Templates

1. **Send Welcome Email**: Notify new users when they join
2. **Status Change Notification**: Alert team when task status changes
3. **Deadline Reminder**: Send reminders before task deadlines
4. **Data Sync Webhook**: Sync data changes to external systems
5. **Approval Workflow**: Route items for approval based on thresholds

### Creating Custom Templates

```python
from baserow.contrib.automation.nodes.action_template_handler import ActionTemplateHandler

handler = ActionTemplateHandler()
template = handler.create_template(
    name="Custom Notification",
    description="Send custom notifications",
    category="notification",
    template_config={
        "nodes": [
            {
                "type": "notification",
                "service": {
                    "notification_type": "email",
                    "subject_template": "{{ subject }}",
                    "message_template": "{{ message }}"
                }
            }
        ]
    },
    required_fields=["subject", "message", "recipient_email"],
    user=request.user
)
```

## Enhanced Workflow Runner

The enhanced workflow runner provides:

### Multi-step Processing

- **Sequential Execution**: Actions execute in proper order
- **Data Flow**: Output from one action becomes input to the next
- **Error Isolation**: Failures in one action don't necessarily stop the entire workflow

### Conditional Branching

- **Dynamic Paths**: Workflows can take different paths based on data
- **Branch Merging**: Multiple branches can converge back to common actions
- **Nested Conditions**: Support for complex conditional logic

### Error Handling

- **Retry Logic**: Configurable retry attempts with exponential backoff
- **Error Classification**: Distinguish between critical and non-critical errors
- **Graceful Degradation**: Continue execution when possible after non-critical failures

### Execution Logging

- **Comprehensive Tracking**: Log every step of workflow execution
- **Performance Metrics**: Track execution times and success rates
- **Debugging Support**: Detailed error messages and execution context

## API Endpoints

### Action Management

- `GET /api/automation/actions/notification-actions/` - List notification actions
- `POST /api/automation/actions/notification-actions/` - Create notification action
- `GET /api/automation/actions/webhook-actions/` - List webhook actions
- `POST /api/automation/actions/webhook-actions/` - Create webhook action

### Template Management

- `GET /api/automation/actions/action-templates/` - List action templates
- `POST /api/automation/actions/action-templates/` - Create action template
- `GET /api/automation/actions/action-templates/popular/` - Get popular templates
- `POST /api/automation/actions/action-templates/{id}/apply/` - Apply template to workflow

### Execution Monitoring

- `GET /api/automation/actions/execution-logs/` - List execution logs
- `GET /api/automation/actions/execution-logs/?workflow_id=123` - Filter by workflow

## Usage Examples

### Basic Notification Workflow

```python
# Create a notification when a task is completed
workflow = AutomationWorkflow.objects.create(name="Task Completion Notification")

# Trigger: When task status changes to "completed"
trigger = create_status_change_trigger(workflow, field="status", value="completed")

# Action: Send email notification
notification_action = NotificationActionNode.objects.create(
    workflow=workflow,
    notification_type="email",
    subject_template="Task Completed: {{ task_name }}",
    message_template="The task '{{ task_name }}' has been completed by {{ user_name }}."
)
```

### Conditional Approval Workflow

```python
# Create an approval workflow based on amount
workflow = AutomationWorkflow.objects.create(name="Expense Approval")

# Trigger: When expense is created
trigger = create_record_created_trigger(workflow, table="expenses")

# Condition: Check if amount > $1000
condition = ConditionalBranchNode.objects.create(
    workflow=workflow,
    condition_template="{{ amount }}",
    condition_type="greater_than",
    comparison_value_template="1000"
)

# True branch: Require approval
approval_action = StatusChangeActionNode.objects.create(
    workflow=workflow,
    target_field_id=status_field.id,
    new_value_template="pending_approval"
)

# False branch: Auto-approve
auto_approve_action = StatusChangeActionNode.objects.create(
    workflow=workflow,
    target_field_id=status_field.id,
    new_value_template="approved"
)
```

### External Integration Workflow

```python
# Sync data to external CRM when contact is updated
workflow = AutomationWorkflow.objects.create(name="CRM Sync")

# Trigger: When contact is updated
trigger = create_record_updated_trigger(workflow, table="contacts")

# Action: Send webhook to CRM
webhook_action = WebhookActionNode.objects.create(
    workflow=workflow,
    url="https://api.crm.com/contacts/sync",
    method="POST",
    payload_template='{"id": {{ contact_id }}, "data": {{ contact_data }}}',
    authentication={
        "type": "api_key",
        "key_name": "X-API-Key",
        "key_value": "your-api-key"
    }
)
```

## Configuration

### Celery Tasks

The enhanced action system uses Celery for background processing:

```python
# settings.py
CELERY_BEAT_SCHEDULE = {
    'cleanup-execution-logs': {
        'task': 'baserow.contrib.automation.tasks.cleanup_workflow_execution_logs',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'validate-action-configurations': {
        'task': 'baserow.contrib.automation.tasks.validate_action_configurations',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
    },
}
```

### Email Configuration

For email notifications:

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.example.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'noreply@yourbaserow.com'
```

## Management Commands

### Initialize Action Templates

```bash
python manage.py init_action_templates
```

### Initialize with Force (recreate existing)

```bash
python manage.py init_action_templates --force
```

## Testing

Run the enhanced action system tests:

```bash
python manage.py test backend.tests.baserow.contrib.automation.nodes.test_enhanced_actions
```

## Performance Considerations

1. **Async Processing**: All actions run asynchronously to avoid blocking
2. **Batch Operations**: Group similar operations for efficiency
3. **Caching**: Cache frequently accessed templates and configurations
4. **Log Rotation**: Regularly clean up old execution logs
5. **Rate Limiting**: Implement rate limiting for external API calls

## Security Considerations

1. **Template Validation**: Validate all templates to prevent code injection
2. **Permission Checks**: Ensure users can only access authorized data
3. **Secure Storage**: Store API keys and tokens securely
4. **Audit Logging**: Log all configuration changes and executions
5. **Input Sanitization**: Sanitize all user inputs in templates

## Troubleshooting

### Common Issues

1. **Template Rendering Errors**: Check template syntax and available variables
2. **Webhook Failures**: Verify URLs, authentication, and network connectivity
3. **Permission Errors**: Ensure proper user permissions for field updates
4. **Performance Issues**: Check execution logs for bottlenecks

### Debugging

1. **Enable Debug Logging**: Set log level to DEBUG for detailed information
2. **Check Execution Logs**: Review WorkflowExecutionLog entries
3. **Test Templates**: Use the template testing endpoints
4. **Monitor Celery**: Check Celery worker status and queue lengths

## Future Enhancements

1. **Visual Workflow Builder**: Drag-and-drop interface for creating workflows
2. **Advanced Conditions**: Support for complex logical expressions
3. **Loop Actions**: Support for iterating over collections
4. **Parallel Execution**: Execute multiple actions simultaneously
5. **Workflow Versioning**: Track and manage workflow versions