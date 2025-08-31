# Automation API Documentation

This document covers the API endpoints for the automation system introduced in the Baserow expansion.

## Overview

The automation system allows users to create workflows that automatically respond to data changes, time-based events, and external triggers. The system consists of automations, triggers, actions, and workflows.

## Automations

### Create Automation

```http
POST /api/database/automations/
```

**Request Body:**
```json
{
  "name": "New Task Notification",
  "description": "Send notification when new task is created",
  "table_id": 123,
  "is_active": true,
  "trigger": {
    "type": "record_created",
    "configuration": {
      "table_id": 123
    }
  },
  "actions": [
    {
      "type": "send_notification",
      "configuration": {
        "message": "New task created: {{field_456}}",
        "recipients": ["user_123", "user_456"]
      }
    }
  ]
}
```

**Response:**
```json
{
  "id": 1001,
  "name": "New Task Notification",
  "description": "Send notification when new task is created",
  "table_id": 123,
  "is_active": true,
  "created_by": 123,
  "created_on": "2024-01-15T10:30:00Z",
  "updated_on": "2024-01-15T10:30:00Z",
  "trigger": {
    "id": 2001,
    "type": "record_created",
    "configuration": {
      "table_id": 123
    }
  },
  "actions": [
    {
      "id": 3001,
      "type": "send_notification",
      "order": 1,
      "configuration": {
        "message": "New task created: {{field_456}}",
        "recipients": ["user_123", "user_456"]
      }
    }
  ]
}
```

### List Automations

```http
GET /api/database/automations/
```

**Query Parameters:**
- `table_id`: Filter by table ID
- `is_active`: Filter by active status
- `search`: Search by name or description

### Get Automation

```http
GET /api/database/automations/{automation_id}/
```

### Update Automation

```http
PATCH /api/database/automations/{automation_id}/
```

### Delete Automation

```http
DELETE /api/database/automations/{automation_id}/
```

### Toggle Automation Status

```http
POST /api/database/automations/{automation_id}/toggle/
```

## Triggers

### Available Trigger Types

#### Record Created Trigger
```json
{
  "type": "record_created",
  "configuration": {
    "table_id": 123,
    "conditions": [
      {
        "field_id": 456,
        "operator": "equals",
        "value": "High Priority"
      }
    ]
  }
}
```

#### Record Updated Trigger
```json
{
  "type": "record_updated",
  "configuration": {
    "table_id": 123,
    "field_ids": [456, 457],
    "conditions": [
      {
        "field_id": 456,
        "operator": "changed_to",
        "value": "Complete"
      }
    ]
  }
}
```

#### Date/Time Trigger
```json
{
  "type": "scheduled",
  "configuration": {
    "schedule_type": "cron",
    "cron_expression": "0 9 * * 1-5",
    "timezone": "UTC"
  }
}
```

#### Field Value Trigger
```json
{
  "type": "field_value",
  "configuration": {
    "field_id": 456,
    "operator": "date_reached",
    "offset_days": -1
  }
}
```

#### Webhook Trigger
```json
{
  "type": "webhook",
  "configuration": {
    "webhook_url": "https://api.example.com/webhook/abc123",
    "authentication": {
      "type": "bearer_token",
      "token": "secret_token"
    }
  }
}
```

### Test Trigger

```http
POST /api/database/automations/triggers/{trigger_id}/test/
```

**Request Body:**
```json
{
  "test_data": {
    "field_456": "Test Value",
    "field_457": "2024-01-15"
  }
}
```

## Actions

### Available Action Types

#### Update Record Action
```json
{
  "type": "update_record",
  "configuration": {
    "table_id": 123,
    "row_id": "{{trigger.row_id}}",
    "field_updates": {
      "456": "{{trigger.field_457}} - Updated",
      "457": "{{now()}}"
    }
  }
}
```

#### Create Record Action
```json
{
  "type": "create_record",
  "configuration": {
    "table_id": 124,
    "field_values": {
      "456": "{{trigger.field_456}}",
      "457": "Auto-created from automation"
    }
  }
}
```

#### Send Notification Action
```json
{
  "type": "send_notification",
  "configuration": {
    "notification_type": "in_app",
    "message": "Task {{trigger.field_456}} is due soon",
    "recipients": ["{{trigger.field_assigned_to}}", "user_123"],
    "priority": "high"
  }
}
```

#### Send Email Action
```json
{
  "type": "send_email",
  "configuration": {
    "to": ["{{trigger.field_email}}", "admin@example.com"],
    "cc": [],
    "bcc": [],
    "subject": "Task Update: {{trigger.field_456}}",
    "body": "The task {{trigger.field_456}} has been updated.",
    "body_html": "<p>The task <strong>{{trigger.field_456}}</strong> has been updated.</p>"
  }
}
```

#### Webhook Action
```json
{
  "type": "webhook",
  "configuration": {
    "url": "https://api.external-service.com/webhook",
    "method": "POST",
    "headers": {
      "Authorization": "Bearer {{env.API_TOKEN}}",
      "Content-Type": "application/json"
    },
    "body": {
      "event": "record_updated",
      "data": "{{trigger.all_fields}}"
    }
  }
}
```

#### Slack Integration Action
```json
{
  "type": "slack_message",
  "configuration": {
    "channel": "#general",
    "message": "New task created: {{trigger.field_456}}",
    "username": "Baserow Bot",
    "icon_emoji": ":robot_face:"
  }
}
```

### Test Action

```http
POST /api/database/automations/actions/{action_id}/test/
```

**Request Body:**
```json
{
  "context_data": {
    "trigger": {
      "row_id": 1001,
      "field_456": "Test Task",
      "field_457": "2024-01-15"
    }
  }
}
```

## Workflows

### Create Multi-Step Workflow

```http
POST /api/database/automations/
```

**Request Body:**
```json
{
  "name": "Complex Task Workflow",
  "table_id": 123,
  "is_active": true,
  "trigger": {
    "type": "record_created",
    "configuration": {
      "table_id": 123
    }
  },
  "workflow": {
    "steps": [
      {
        "id": "step_1",
        "type": "condition",
        "configuration": {
          "condition": "{{trigger.field_456}} == 'High Priority'",
          "true_path": "step_2",
          "false_path": "step_4"
        }
      },
      {
        "id": "step_2",
        "type": "action",
        "action": {
          "type": "send_notification",
          "configuration": {
            "message": "High priority task created",
            "recipients": ["manager_123"]
          }
        },
        "next_step": "step_3"
      },
      {
        "id": "step_3",
        "type": "delay",
        "configuration": {
          "delay_type": "minutes",
          "delay_value": 30
        },
        "next_step": "step_5"
      },
      {
        "id": "step_4",
        "type": "action",
        "action": {
          "type": "update_record",
          "configuration": {
            "field_updates": {
              "457": "Standard Priority"
            }
          }
        },
        "next_step": "step_5"
      },
      {
        "id": "step_5",
        "type": "action",
        "action": {
          "type": "send_email",
          "configuration": {
            "to": ["{{trigger.field_assigned_to}}"],
            "subject": "Task Assignment",
            "body": "You have been assigned a new task"
          }
        }
      }
    ]
  }
}
```

### Workflow Execution Status

```http
GET /api/database/automations/{automation_id}/executions/
```

**Response:**
```json
{
  "executions": [
    {
      "id": "exec_123",
      "automation_id": 1001,
      "trigger_data": {
        "row_id": 2001,
        "field_456": "Test Task"
      },
      "status": "completed",
      "started_at": "2024-01-15T10:30:00Z",
      "completed_at": "2024-01-15T10:32:15Z",
      "steps": [
        {
          "step_id": "step_1",
          "status": "completed",
          "result": "true_path",
          "duration_ms": 150
        },
        {
          "step_id": "step_2",
          "status": "completed",
          "result": "notification_sent",
          "duration_ms": 2000
        }
      ]
    }
  ]
}
```

## Automation Templates

### List Templates

```http
GET /api/database/automations/templates/
```

**Response:**
```json
{
  "templates": [
    {
      "id": "template_1",
      "name": "Task Due Date Reminder",
      "description": "Send reminder when task due date approaches",
      "category": "notifications",
      "trigger_type": "field_value",
      "action_types": ["send_notification", "send_email"]
    }
  ]
}
```

### Create Automation from Template

```http
POST /api/database/automations/from-template/
```

**Request Body:**
```json
{
  "template_id": "template_1",
  "table_id": 123,
  "configuration": {
    "due_date_field_id": 456,
    "reminder_days": 2,
    "notification_recipients": ["user_123"]
  }
}
```

## Variable System

### Available Variables

#### Trigger Variables
- `{{trigger.row_id}}` - ID of the triggered row
- `{{trigger.field_NAME}}` - Value of specific field
- `{{trigger.all_fields}}` - All field values as JSON
- `{{trigger.table_id}}` - ID of the table
- `{{trigger.user_id}}` - ID of user who triggered the automation

#### System Variables
- `{{now()}}` - Current timestamp
- `{{today()}}` - Current date
- `{{user.email}}` - Current user's email
- `{{user.name}}` - Current user's name
- `{{env.VARIABLE_NAME}}` - Environment variable

#### Utility Functions
- `{{format_date(date, 'YYYY-MM-DD')}}` - Format date
- `{{upper(text)}}` - Convert to uppercase
- `{{lower(text)}}` - Convert to lowercase
- `{{concat(text1, text2)}}` - Concatenate strings

## Error Handling

### Automation Errors

```json
{
  "error": {
    "code": "AUTOMATION_EXECUTION_FAILED",
    "message": "Action failed to execute",
    "details": {
      "automation_id": 1001,
      "step_id": "step_2",
      "error_type": "network_timeout",
      "retry_count": 3
    }
  }
}
```

### Retry Configuration

```http
PATCH /api/database/automations/{automation_id}/retry-config/
```

**Request Body:**
```json
{
  "max_retries": 3,
  "retry_delay_seconds": 60,
  "exponential_backoff": true
}
```

## Monitoring and Logs

### Get Automation Logs

```http
GET /api/database/automations/{automation_id}/logs/
```

**Query Parameters:**
- `start_date`: Filter logs from date
- `end_date`: Filter logs to date
- `status`: Filter by execution status
- `limit`: Number of logs to return

### Automation Metrics

```http
GET /api/database/automations/{automation_id}/metrics/
```

**Response:**
```json
{
  "total_executions": 150,
  "successful_executions": 145,
  "failed_executions": 5,
  "average_execution_time_ms": 2500,
  "last_execution": "2024-01-15T10:30:00Z",
  "execution_rate_per_hour": 12.5
}
```