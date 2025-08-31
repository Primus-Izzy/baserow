# Integrations API Documentation

This document covers the API endpoints for external integrations, webhooks, and third-party service connections.

## Native Integrations

### List Available Integrations

```http
GET /api/integrations/
```

**Response:**
```json
{
  "integrations": [
    {
      "id": "google_drive",
      "name": "Google Drive",
      "description": "Connect to Google Drive for file storage",
      "category": "file_storage",
      "status": "available",
      "requires_oauth": true,
      "supported_features": ["file_upload", "file_sync", "folder_sync"]
    },
    {
      "id": "slack",
      "name": "Slack",
      "description": "Send notifications to Slack channels",
      "category": "communication",
      "status": "available",
      "requires_oauth": true,
      "supported_features": ["send_message", "create_channel", "user_lookup"]
    }
  ]
}
```

### Create Integration Connection

```http
POST /api/integrations/connections/
```

**Request Body:**
```json
{
  "integration_id": "google_drive",
  "name": "My Google Drive",
  "configuration": {
    "oauth_code": "authorization_code_from_oauth_flow",
    "scopes": ["https://www.googleapis.com/auth/drive.file"]
  },
  "workspace_id": 123
}
```

**Response:**
```json
{
  "id": 1001,
  "integration_id": "google_drive",
  "name": "My Google Drive",
  "status": "connected",
  "configuration": {
    "user_email": "user@example.com",
    "scopes": ["https://www.googleapis.com/auth/drive.file"],
    "expires_at": "2024-02-15T10:30:00Z"
  },
  "workspace_id": 123,
  "created_on": "2024-01-15T10:30:00Z",
  "last_sync": null
}
```

### List Integration Connections

```http
GET /api/integrations/connections/
```

**Query Parameters:**
- `integration_id`: Filter by integration type
- `workspace_id`: Filter by workspace
- `status`: Filter by connection status

### Update Integration Connection

```http
PATCH /api/integrations/connections/{connection_id}/
```

### Delete Integration Connection

```http
DELETE /api/integrations/connections/{connection_id}/
```

### Test Integration Connection

```http
POST /api/integrations/connections/{connection_id}/test/
```

**Response:**
```json
{
  "status": "success",
  "message": "Connection test successful",
  "details": {
    "response_time_ms": 150,
    "api_version": "v1",
    "user_info": {
      "email": "user@example.com",
      "name": "John Doe"
    }
  }
}
```

## Google Drive Integration

### OAuth Authorization

```http
GET /api/integrations/google-drive/oauth-url/
```

**Query Parameters:**
- `redirect_uri`: OAuth redirect URI
- `workspace_id`: Target workspace ID

**Response:**
```json
{
  "oauth_url": "https://accounts.google.com/oauth/authorize?client_id=...",
  "state": "random_state_string"
}
```

### Upload File to Google Drive

```http
POST /api/integrations/connections/{connection_id}/upload/
```

**Request Body (multipart/form-data):**
```
file: [binary file data]
folder_id: "google_drive_folder_id"
table_id: 123
field_id: 456
row_id: 1001
```

**Response:**
```json
{
  "file_id": "google_drive_file_id",
  "file_name": "document.pdf",
  "file_url": "https://drive.google.com/file/d/file_id/view",
  "mime_type": "application/pdf",
  "size": 1024000,
  "uploaded_at": "2024-01-15T10:30:00Z"
}
```

### Sync Google Drive Folder

```http
POST /api/integrations/connections/{connection_id}/sync-folder/
```

**Request Body:**
```json
{
  "folder_id": "google_drive_folder_id",
  "table_id": 123,
  "sync_direction": "bidirectional",
  "file_field_id": 456,
  "name_field_id": 457,
  "auto_sync": true
}
```

## Google Calendar Integration

### Create Calendar Sync

```http
POST /api/integrations/connections/{connection_id}/calendar-sync/
```

**Request Body:**
```json
{
  "calendar_id": "primary",
  "table_id": 123,
  "view_id": 456,
  "field_mappings": {
    "title": 789,
    "description": 790,
    "start_date": 791,
    "end_date": 792,
    "location": 793
  },
  "sync_direction": "bidirectional",
  "auto_sync": true
}
```

**Response:**
```json
{
  "id": 2001,
  "calendar_id": "primary",
  "calendar_name": "Primary Calendar",
  "table_id": 123,
  "view_id": 456,
  "field_mappings": {
    "title": 789,
    "description": 790,
    "start_date": 791,
    "end_date": 792,
    "location": 793
  },
  "sync_direction": "bidirectional",
  "auto_sync": true,
  "last_sync": null,
  "status": "active"
}
```

### Trigger Calendar Sync

```http
POST /api/integrations/calendar-sync/{sync_id}/sync/
```

**Response:**
```json
{
  "sync_id": "sync_123",
  "status": "in_progress",
  "started_at": "2024-01-15T10:30:00Z",
  "events_processed": 0,
  "total_events": 25
}
```

### Get Calendar Sync Status

```http
GET /api/integrations/calendar-sync/{sync_id}/status/
```

**Response:**
```json
{
  "sync_id": "sync_123",
  "status": "completed",
  "started_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:32:00Z",
  "events_processed": 25,
  "total_events": 25,
  "errors": []
}
```

## Slack Integration

### Send Message to Slack

```http
POST /api/integrations/connections/{connection_id}/send-message/
```

**Request Body:**
```json
{
  "channel": "#general",
  "message": "New task created: {{field_456}}",
  "username": "Baserow Bot",
  "icon_emoji": ":robot_face:",
  "attachments": [
    {
      "color": "good",
      "title": "Task Details",
      "fields": [
        {
          "title": "Priority",
          "value": "High",
          "short": true
        },
        {
          "title": "Due Date",
          "value": "2024-01-20",
          "short": true
        }
      ]
    }
  ]
}
```

**Response:**
```json
{
  "message_id": "slack_message_id",
  "channel": "#general",
  "timestamp": "1705312200.123456",
  "permalink": "https://workspace.slack.com/archives/C1234567890/p1705312200123456"
}
```

### List Slack Channels

```http
GET /api/integrations/connections/{connection_id}/channels/
```

**Response:**
```json
{
  "channels": [
    {
      "id": "C1234567890",
      "name": "general",
      "is_private": false,
      "is_member": true
    },
    {
      "id": "C0987654321",
      "name": "random",
      "is_private": false,
      "is_member": true
    }
  ]
}
```

### Create Slack Channel

```http
POST /api/integrations/connections/{connection_id}/create-channel/
```

**Request Body:**
```json
{
  "name": "project-updates",
  "is_private": false,
  "purpose": "Updates for the current project"
}
```

## Microsoft Teams Integration

### Send Teams Message

```http
POST /api/integrations/connections/{connection_id}/send-teams-message/
```

**Request Body:**
```json
{
  "team_id": "team_id",
  "channel_id": "channel_id",
  "message": {
    "type": "message",
    "attachments": [
      {
        "contentType": "application/vnd.microsoft.card.adaptive",
        "content": {
          "type": "AdaptiveCard",
          "version": "1.3",
          "body": [
            {
              "type": "TextBlock",
              "text": "New Task Created",
              "weight": "Bolder",
              "size": "Medium"
            },
            {
              "type": "FactSet",
              "facts": [
                {
                  "title": "Task:",
                  "value": "{{field_456}}"
                },
                {
                  "title": "Priority:",
                  "value": "{{field_457}}"
                }
              ]
            }
          ]
        }
      }
    ]
  }
}
```

## Email Integration

### Configure Email Service

```http
POST /api/integrations/connections/
```

**Request Body:**
```json
{
  "integration_id": "email_smtp",
  "name": "Company Email",
  "configuration": {
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "noreply@company.com",
    "smtp_password": "app_password",
    "use_tls": true,
    "from_email": "noreply@company.com",
    "from_name": "Company Notifications"
  },
  "workspace_id": 123
}
```

### Send Email

```http
POST /api/integrations/connections/{connection_id}/send-email/
```

**Request Body:**
```json
{
  "to": ["user@example.com"],
  "cc": [],
  "bcc": [],
  "subject": "Task Assignment: {{field_456}}",
  "body_text": "You have been assigned a new task: {{field_456}}",
  "body_html": "<p>You have been assigned a new task: <strong>{{field_456}}</strong></p>",
  "attachments": [
    {
      "filename": "task_details.pdf",
      "content": "base64_encoded_content",
      "content_type": "application/pdf"
    }
  ]
}
```

## Webhooks

### Create Webhook

```http
POST /api/webhooks/
```

**Request Body:**
```json
{
  "name": "Task Updates Webhook",
  "url": "https://api.external-service.com/webhook",
  "events": ["record_created", "record_updated", "record_deleted"],
  "table_id": 123,
  "headers": {
    "Authorization": "Bearer secret_token",
    "Content-Type": "application/json"
  },
  "active": true,
  "retry_config": {
    "max_retries": 3,
    "retry_delay_seconds": 60,
    "exponential_backoff": true
  }
}
```

**Response:**
```json
{
  "id": 3001,
  "name": "Task Updates Webhook",
  "url": "https://api.external-service.com/webhook",
  "events": ["record_created", "record_updated", "record_deleted"],
  "table_id": 123,
  "headers": {
    "Authorization": "[REDACTED]",
    "Content-Type": "application/json"
  },
  "active": true,
  "secret": "webhook_secret_key",
  "retry_config": {
    "max_retries": 3,
    "retry_delay_seconds": 60,
    "exponential_backoff": true
  },
  "created_on": "2024-01-15T10:30:00Z"
}
```

### List Webhooks

```http
GET /api/webhooks/
```

**Query Parameters:**
- `table_id`: Filter by table ID
- `active`: Filter by active status
- `event`: Filter by event type

### Update Webhook

```http
PATCH /api/webhooks/{webhook_id}/
```

### Delete Webhook

```http
DELETE /api/webhooks/{webhook_id}/
```

### Test Webhook

```http
POST /api/webhooks/{webhook_id}/test/
```

**Request Body:**
```json
{
  "test_data": {
    "event": "record_created",
    "table_id": 123,
    "row_id": 1001,
    "data": {
      "field_456": "Test Task",
      "field_457": "High"
    }
  }
}
```

**Response:**
```json
{
  "status": "success",
  "response_code": 200,
  "response_body": "OK",
  "response_time_ms": 250,
  "delivered_at": "2024-01-15T10:30:00Z"
}
```

### Webhook Delivery Logs

```http
GET /api/webhooks/{webhook_id}/deliveries/
```

**Query Parameters:**
- `start_date`: Filter from date
- `end_date`: Filter to date
- `status`: Filter by delivery status
- `limit`: Number of deliveries to return

**Response:**
```json
{
  "deliveries": [
    {
      "id": "delivery_123",
      "webhook_id": 3001,
      "event": "record_created",
      "payload": {
        "event": "record_created",
        "table_id": 123,
        "row_id": 1001,
        "data": {
          "field_456": "New Task",
          "field_457": "Medium"
        },
        "timestamp": "2024-01-15T10:30:00Z"
      },
      "status": "success",
      "response_code": 200,
      "response_body": "OK",
      "response_time_ms": 180,
      "attempts": 1,
      "delivered_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Retry Failed Webhook

```http
POST /api/webhooks/deliveries/{delivery_id}/retry/
```

## Zapier Integration

### Create Zapier Trigger

```http
POST /api/integrations/zapier/triggers/
```

**Request Body:**
```json
{
  "name": "New Task Created",
  "table_id": 123,
  "trigger_event": "record_created",
  "filters": [
    {
      "field_id": 456,
      "operator": "equals",
      "value": "High Priority"
    }
  ],
  "webhook_url": "https://hooks.zapier.com/hooks/catch/123456/abcdef/"
}
```

### List Zapier Connections

```http
GET /api/integrations/zapier/connections/
```

### Zapier Field Mapping

```http
GET /api/integrations/zapier/field-mapping/
```

**Query Parameters:**
- `table_id`: Table ID for field mapping

**Response:**
```json
{
  "fields": [
    {
      "id": 456,
      "name": "Task Name",
      "type": "text",
      "zapier_type": "unicode"
    },
    {
      "id": 457,
      "name": "Priority",
      "type": "single_select",
      "zapier_type": "unicode",
      "options": ["Low", "Medium", "High"]
    }
  ]
}
```

## Make.com (Integromat) Integration

### Create Make.com Webhook

```http
POST /api/integrations/make/webhooks/
```

**Request Body:**
```json
{
  "name": "Task Updates to Make",
  "table_id": 123,
  "events": ["record_created", "record_updated"],
  "webhook_url": "https://hook.integromat.com/123456789",
  "data_format": "json",
  "include_metadata": true
}
```

## API Keys for Integrations

### Create Integration API Key

```http
POST /api/integrations/api-keys/
```

**Request Body:**
```json
{
  "name": "External Service API Key",
  "permissions": {
    "tables": [123, 124],
    "operations": ["read", "write"],
    "integrations": ["webhook", "zapier"]
  },
  "expires_at": "2024-12-31T23:59:59Z",
  "rate_limit": {
    "requests_per_hour": 1000,
    "burst_limit": 100
  }
}
```

**Response:**
```json
{
  "id": 4001,
  "name": "External Service API Key",
  "key": "brow_1234567890abcdef",
  "permissions": {
    "tables": [123, 124],
    "operations": ["read", "write"],
    "integrations": ["webhook", "zapier"]
  },
  "expires_at": "2024-12-31T23:59:59Z",
  "rate_limit": {
    "requests_per_hour": 1000,
    "burst_limit": 100
  },
  "created_on": "2024-01-15T10:30:00Z",
  "last_used": null
}
```

### List API Keys

```http
GET /api/integrations/api-keys/
```

### Revoke API Key

```http
DELETE /api/integrations/api-keys/{key_id}/
```

## Integration Monitoring

### Get Integration Health

```http
GET /api/integrations/health/
```

**Response:**
```json
{
  "overall_status": "healthy",
  "integrations": [
    {
      "integration_id": "google_drive",
      "status": "healthy",
      "last_check": "2024-01-15T10:30:00Z",
      "response_time_ms": 150,
      "error_rate": 0.01
    },
    {
      "integration_id": "slack",
      "status": "degraded",
      "last_check": "2024-01-15T10:30:00Z",
      "response_time_ms": 2500,
      "error_rate": 0.05,
      "issues": ["High response time"]
    }
  ]
}
```

### Integration Usage Statistics

```http
GET /api/integrations/usage/
```

**Query Parameters:**
- `integration_id`: Filter by integration type
- `start_date`: Statistics start date
- `end_date`: Statistics end date

**Response:**
```json
{
  "usage": [
    {
      "integration_id": "google_drive",
      "total_requests": 1500,
      "successful_requests": 1485,
      "failed_requests": 15,
      "avg_response_time_ms": 200,
      "data_transferred_mb": 250.5
    }
  ]
}
```