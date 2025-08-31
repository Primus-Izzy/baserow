# Collaboration API Documentation

This document covers the API endpoints for collaboration features including real-time editing, comments, activity logs, and notifications.

## Real-Time Collaboration

### WebSocket Connection

Connect to the WebSocket endpoint for real-time updates:

```javascript
const ws = new WebSocket('wss://your-baserow-instance.com/ws/collaboration/');
ws.onopen = function() {
    // Send authentication
    ws.send(JSON.stringify({
        type: 'authenticate',
        token: 'your-jwt-token'
    }));
};
```

### Join Table/View Room

```javascript
ws.send(JSON.stringify({
    type: 'join_room',
    table_id: 123,
    view_id: 456 // optional
}));
```

### Real-Time Events

#### User Presence
```javascript
// Received when user joins/leaves
{
    type: 'user_presence',
    action: 'joined', // or 'left'
    user: {
        id: 123,
        email: 'user@example.com',
        first_name: 'John',
        last_name: 'Doe',
        avatar_url: 'https://example.com/avatar.jpg'
    },
    table_id: 123,
    view_id: 456
}
```

#### Live Cursors
```javascript
// Send cursor position
ws.send(JSON.stringify({
    type: 'cursor_position',
    table_id: 123,
    row_id: 1001,
    field_id: 789,
    position: { x: 100, y: 200 }
}));

// Receive cursor updates
{
    type: 'cursor_update',
    user_id: 124,
    table_id: 123,
    row_id: 1001,
    field_id: 789,
    position: { x: 150, y: 250 }
}
```

#### Typing Indicators
```javascript
// Send typing status
ws.send(JSON.stringify({
    type: 'typing',
    table_id: 123,
    row_id: 1001,
    field_id: 789,
    is_typing: true
}));

// Receive typing updates
{
    type: 'typing_indicator',
    user_id: 124,
    table_id: 123,
    row_id: 1001,
    field_id: 789,
    is_typing: true
}
```

#### Record Updates
```javascript
{
    type: 'record_updated',
    table_id: 123,
    row_id: 1001,
    updated_fields: {
        789: 'New Value',
        790: 'Another Value'
    },
    updated_by: 124,
    timestamp: '2024-01-15T10:30:00Z'
}
```

### Get Active Users

```http
GET /api/database/collaboration/active-users/
```

**Query Parameters:**
- `table_id`: Filter by table ID
- `view_id`: Filter by view ID

**Response:**
```json
{
  "active_users": [
    {
      "user_id": 123,
      "email": "user1@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "avatar_url": "https://example.com/avatar1.jpg",
      "last_seen": "2024-01-15T10:30:00Z",
      "current_location": {
        "table_id": 123,
        "view_id": 456,
        "row_id": 1001,
        "field_id": 789
      }
    }
  ]
}
```

## Comments System

### Create Comment

```http
POST /api/database/comments/
```

**Request Body:**
```json
{
  "table_id": 123,
  "row_id": 1001,
  "content": "This task needs more details. @john.doe can you help?",
  "parent_id": null,
  "mentions": [
    {
      "user_id": 124,
      "username": "john.doe",
      "position": 45
    }
  ]
}
```

**Response:**
```json
{
  "id": 2001,
  "table_id": 123,
  "row_id": 1001,
  "content": "This task needs more details. @john.doe can you help?",
  "content_html": "This task needs more details. <span class=\"mention\" data-user-id=\"124\">@john.doe</span> can you help?",
  "parent_id": null,
  "user": {
    "id": 123,
    "email": "user@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "avatar_url": "https://example.com/avatar.jpg"
  },
  "mentions": [
    {
      "user_id": 124,
      "username": "john.doe",
      "position": 45
    }
  ],
  "created_on": "2024-01-15T10:30:00Z",
  "updated_on": "2024-01-15T10:30:00Z",
  "replies_count": 0
}
```

### List Comments

```http
GET /api/database/comments/
```

**Query Parameters:**
- `table_id`: Filter by table ID (required)
- `row_id`: Filter by row ID
- `parent_id`: Filter by parent comment ID
- `user_id`: Filter by user ID
- `limit`: Number of comments to return (default: 50)
- `offset`: Pagination offset

**Response:**
```json
{
  "count": 25,
  "next": "https://api.example.com/database/comments/?offset=50",
  "previous": null,
  "results": [
    {
      "id": 2001,
      "table_id": 123,
      "row_id": 1001,
      "content": "This task needs more details.",
      "content_html": "This task needs more details.",
      "parent_id": null,
      "user": {
        "id": 123,
        "email": "user@example.com",
        "first_name": "Jane",
        "last_name": "Smith",
        "avatar_url": "https://example.com/avatar.jpg"
      },
      "created_on": "2024-01-15T10:30:00Z",
      "updated_on": "2024-01-15T10:30:00Z",
      "replies_count": 2,
      "replies": [
        {
          "id": 2002,
          "content": "I'll add more details shortly.",
          "user": {
            "id": 124,
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe"
          },
          "created_on": "2024-01-15T10:35:00Z"
        }
      ]
    }
  ]
}
```

### Update Comment

```http
PATCH /api/database/comments/{comment_id}/
```

**Request Body:**
```json
{
  "content": "Updated comment content"
}
```

### Delete Comment

```http
DELETE /api/database/comments/{comment_id}/
```

### React to Comment

```http
POST /api/database/comments/{comment_id}/reactions/
```

**Request Body:**
```json
{
  "emoji": "👍",
  "action": "add" // or "remove"
}
```

**Response:**
```json
{
  "reactions": {
    "👍": {
      "count": 3,
      "users": [123, 124, 125],
      "user_reacted": true
    },
    "❤️": {
      "count": 1,
      "users": [126],
      "user_reacted": false
    }
  }
}
```

## Activity Logs

### Get Activity Logs

```http
GET /api/database/activity/
```

**Query Parameters:**
- `table_id`: Filter by table ID
- `row_id`: Filter by row ID
- `user_id`: Filter by user ID
- `action_type`: Filter by action type
- `start_date`: Filter from date (ISO format)
- `end_date`: Filter to date (ISO format)
- `limit`: Number of activities to return (default: 50)
- `offset`: Pagination offset

**Response:**
```json
{
  "count": 150,
  "next": "https://api.example.com/database/activity/?offset=50",
  "previous": null,
  "results": [
    {
      "id": 3001,
      "user": {
        "id": 123,
        "email": "user@example.com",
        "first_name": "Jane",
        "last_name": "Smith",
        "avatar_url": "https://example.com/avatar.jpg"
      },
      "action_type": "record_updated",
      "table": {
        "id": 123,
        "name": "Tasks"
      },
      "row_id": 1001,
      "details": {
        "field_changes": {
          "789": {
            "field_name": "Status",
            "old_value": "In Progress",
            "new_value": "Complete"
          },
          "790": {
            "field_name": "Completion Date",
            "old_value": null,
            "new_value": "2024-01-15"
          }
        }
      },
      "timestamp": "2024-01-15T10:30:00Z",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0..."
    }
  ]
}
```

### Activity Types

| Action Type | Description |
|-------------|-------------|
| `record_created` | New record created |
| `record_updated` | Record fields updated |
| `record_deleted` | Record deleted |
| `field_created` | New field added to table |
| `field_updated` | Field configuration changed |
| `field_deleted` | Field removed from table |
| `view_created` | New view created |
| `view_updated` | View configuration changed |
| `view_deleted` | View deleted |
| `table_created` | New table created |
| `table_updated` | Table settings changed |
| `table_deleted` | Table deleted |
| `comment_created` | Comment added |
| `comment_updated` | Comment edited |
| `comment_deleted` | Comment removed |
| `automation_triggered` | Automation executed |
| `user_invited` | User invited to workspace |
| `user_removed` | User removed from workspace |
| `permission_changed` | User permissions modified |

### Export Activity Logs

```http
POST /api/database/activity/export/
```

**Request Body:**
```json
{
  "format": "csv",
  "filters": {
    "table_id": 123,
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  },
  "include_details": true
}
```

**Response:**
```json
{
  "export_id": "activity_export_123",
  "download_url": "https://baserow.io/exports/activity_export_123.csv",
  "expires_at": "2024-01-16T10:30:00Z"
}
```

## Notifications System

### Get Notifications

```http
GET /api/database/notifications/
```

**Query Parameters:**
- `unread_only`: Show only unread notifications
- `notification_type`: Filter by type
- `limit`: Number of notifications to return
- `offset`: Pagination offset

**Response:**
```json
{
  "count": 25,
  "unread_count": 5,
  "results": [
    {
      "id": 4001,
      "type": "comment_mention",
      "title": "You were mentioned in a comment",
      "message": "Jane Smith mentioned you in a comment on Task #1001",
      "data": {
        "comment_id": 2001,
        "table_id": 123,
        "row_id": 1001,
        "mentioned_by": {
          "id": 123,
          "name": "Jane Smith"
        }
      },
      "is_read": false,
      "created_on": "2024-01-15T10:30:00Z",
      "read_on": null
    }
  ]
}
```

### Mark Notification as Read

```http
PATCH /api/database/notifications/{notification_id}/
```

**Request Body:**
```json
{
  "is_read": true
}
```

### Mark All Notifications as Read

```http
POST /api/database/notifications/mark-all-read/
```

### Notification Preferences

```http
GET /api/database/notifications/preferences/
```

**Response:**
```json
{
  "email_notifications": {
    "comment_mentions": true,
    "record_assignments": true,
    "automation_failures": true,
    "daily_digest": false
  },
  "in_app_notifications": {
    "comment_mentions": true,
    "record_assignments": true,
    "automation_failures": true,
    "real_time_updates": true
  },
  "push_notifications": {
    "comment_mentions": true,
    "record_assignments": false,
    "automation_failures": true
  }
}
```

### Update Notification Preferences

```http
PATCH /api/database/notifications/preferences/
```

**Request Body:**
```json
{
  "email_notifications": {
    "comment_mentions": true,
    "daily_digest": true
  }
}
```

### Send Custom Notification

```http
POST /api/database/notifications/send/
```

**Request Body:**
```json
{
  "recipients": [123, 124],
  "type": "custom",
  "title": "Custom Notification",
  "message": "This is a custom notification message",
  "data": {
    "custom_field": "custom_value"
  },
  "channels": ["in_app", "email"]
}
```

## Conflict Resolution

### Get Conflicted Records

```http
GET /api/database/conflicts/
```

**Query Parameters:**
- `table_id`: Filter by table ID
- `resolved`: Filter by resolution status

**Response:**
```json
{
  "conflicts": [
    {
      "id": 5001,
      "table_id": 123,
      "row_id": 1001,
      "field_id": 789,
      "conflict_type": "simultaneous_edit",
      "versions": [
        {
          "user_id": 123,
          "value": "Version A",
          "timestamp": "2024-01-15T10:30:00Z"
        },
        {
          "user_id": 124,
          "value": "Version B",
          "timestamp": "2024-01-15T10:30:05Z"
        }
      ],
      "resolved": false,
      "created_on": "2024-01-15T10:30:10Z"
    }
  ]
}
```

### Resolve Conflict

```http
POST /api/database/conflicts/{conflict_id}/resolve/
```

**Request Body:**
```json
{
  "resolution_type": "choose_version",
  "chosen_version": 0,
  "custom_value": null
}
```

## Collaboration Settings

### Get Table Collaboration Settings

```http
GET /api/database/tables/{table_id}/collaboration-settings/
```

**Response:**
```json
{
  "real_time_editing": true,
  "show_cursors": true,
  "show_typing_indicators": true,
  "comment_permissions": "all_users",
  "activity_log_retention_days": 90,
  "conflict_resolution": "manual"
}
```

### Update Collaboration Settings

```http
PATCH /api/database/tables/{table_id}/collaboration-settings/
```

**Request Body:**
```json
{
  "show_cursors": false,
  "comment_permissions": "editors_only"
}
```