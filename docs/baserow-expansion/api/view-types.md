# View Types API Documentation

This document covers the API endpoints for all new view types introduced in the Baserow expansion.

## Kanban View

### Create Kanban View

```http
POST /api/database/views/
```

**Request Body:**
```json
{
  "type": "kanban",
  "name": "Project Board",
  "table_id": 123,
  "kanban_single_select_field_id": 456,
  "kanban_card_fields": [789, 790, 791],
  "kanban_color_field_id": 792,
  "kanban_cover_image_field_id": 793,
  "kanban_show_card_count": true
}
```

**Response:**
```json
{
  "id": 100,
  "type": "kanban",
  "name": "Project Board",
  "table_id": 123,
  "kanban_single_select_field_id": 456,
  "kanban_card_fields": [789, 790, 791],
  "kanban_color_field_id": 792,
  "kanban_cover_image_field_id": 793,
  "kanban_show_card_count": true,
  "created_on": "2024-01-15T10:30:00Z",
  "updated_on": "2024-01-15T10:30:00Z"
}
```

### Get Kanban View Data

```http
GET /api/database/views/kanban/{view_id}/
```

**Response:**
```json
{
  "columns": [
    {
      "id": "option_1",
      "value": "To Do",
      "color": "blue",
      "cards": [
        {
          "id": 1001,
          "fields": {
            "789": "Task Title",
            "790": "High",
            "791": "2024-01-20"
          }
        }
      ],
      "count": 5
    },
    {
      "id": "option_2", 
      "value": "In Progress",
      "color": "yellow",
      "cards": [],
      "count": 3
    }
  ],
  "total_count": 8
}
```

### Move Card Between Columns

```http
PATCH /api/database/views/kanban/{view_id}/move-card/
```

**Request Body:**
```json
{
  "row_id": 1001,
  "from_column": "option_1",
  "to_column": "option_2",
  "position": 0
}
```

## Timeline/Gantt View

### Create Timeline View

```http
POST /api/database/views/
```

**Request Body:**
```json
{
  "type": "timeline",
  "name": "Project Timeline",
  "table_id": 123,
  "timeline_start_date_field_id": 456,
  "timeline_end_date_field_id": 457,
  "timeline_color_field_id": 458,
  "timeline_show_dependencies": true,
  "timeline_zoom_level": "week",
  "timeline_show_milestones": true
}
```

**Response:**
```json
{
  "id": 101,
  "type": "timeline",
  "name": "Project Timeline",
  "table_id": 123,
  "timeline_start_date_field_id": 456,
  "timeline_end_date_field_id": 457,
  "timeline_color_field_id": 458,
  "timeline_show_dependencies": true,
  "timeline_zoom_level": "week",
  "timeline_show_milestones": true,
  "created_on": "2024-01-15T10:30:00Z",
  "updated_on": "2024-01-15T10:30:00Z"
}
```

### Get Timeline View Data

```http
GET /api/database/views/timeline/{view_id}/
```

**Query Parameters:**
- `start_date`: Start date for timeline range (ISO format)
- `end_date`: End date for timeline range (ISO format)
- `zoom_level`: `day`, `week`, `month`, `year`

**Response:**
```json
{
  "tasks": [
    {
      "id": 1001,
      "start_date": "2024-01-15",
      "end_date": "2024-01-25",
      "title": "Task 1",
      "color": "#3498db",
      "progress": 0.6,
      "dependencies": [1002, 1003]
    }
  ],
  "milestones": [
    {
      "id": 2001,
      "date": "2024-01-30",
      "title": "Project Milestone",
      "color": "#e74c3c"
    }
  ],
  "dependencies": [
    {
      "from_task": 1001,
      "to_task": 1002,
      "type": "finish_to_start"
    }
  ]
}
```

### Update Task Dependencies

```http
POST /api/database/views/timeline/{view_id}/dependencies/
```

**Request Body:**
```json
{
  "from_row_id": 1001,
  "to_row_id": 1002,
  "dependency_type": "finish_to_start"
}
```

### Update Task Dates via Drag

```http
PATCH /api/database/views/timeline/{view_id}/update-dates/
```

**Request Body:**
```json
{
  "row_id": 1001,
  "start_date": "2024-01-16",
  "end_date": "2024-01-26"
}
```

## Calendar View

### Create Calendar View

```http
POST /api/database/views/
```

**Request Body:**
```json
{
  "type": "calendar",
  "name": "Event Calendar",
  "table_id": 123,
  "calendar_date_field_id": 456,
  "calendar_end_date_field_id": 457,
  "calendar_color_field_id": 458,
  "calendar_default_view": "month",
  "calendar_show_weekends": true,
  "calendar_first_day_of_week": 1
}
```

**Response:**
```json
{
  "id": 102,
  "type": "calendar",
  "name": "Event Calendar", 
  "table_id": 123,
  "calendar_date_field_id": 456,
  "calendar_end_date_field_id": 457,
  "calendar_color_field_id": 458,
  "calendar_default_view": "month",
  "calendar_show_weekends": true,
  "calendar_first_day_of_week": 1,
  "created_on": "2024-01-15T10:30:00Z",
  "updated_on": "2024-01-15T10:30:00Z"
}
```

### Get Calendar View Data

```http
GET /api/database/views/calendar/{view_id}/
```

**Query Parameters:**
- `start_date`: Start date for calendar range
- `end_date`: End date for calendar range
- `view_type`: `month`, `week`, `day`

**Response:**
```json
{
  "events": [
    {
      "id": 1001,
      "title": "Team Meeting",
      "start_date": "2024-01-15T10:00:00Z",
      "end_date": "2024-01-15T11:00:00Z",
      "all_day": false,
      "color": "#3498db",
      "recurring": {
        "pattern": "weekly",
        "interval": 1,
        "end_date": "2024-12-31"
      }
    }
  ],
  "calendar_info": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "view_type": "month"
  }
}
```

### Move Event via Drag

```http
PATCH /api/database/views/calendar/{view_id}/move-event/
```

**Request Body:**
```json
{
  "row_id": 1001,
  "new_start_date": "2024-01-16T10:00:00Z",
  "new_end_date": "2024-01-16T11:00:00Z"
}
```

### External Calendar Integration

```http
POST /api/database/views/calendar/{view_id}/external-sync/
```

**Request Body:**
```json
{
  "provider": "google_calendar",
  "calendar_id": "primary",
  "sync_direction": "bidirectional",
  "field_mappings": {
    "title": 456,
    "description": 457,
    "start_date": 458,
    "end_date": 459
  }
}
```

## Enhanced Form View

### Create Enhanced Form View

```http
POST /api/database/views/
```

**Request Body:**
```json
{
  "type": "form",
  "name": "Customer Feedback Form",
  "table_id": 123,
  "form_title": "We'd love your feedback!",
  "form_description": "Please share your thoughts",
  "form_cover_image": "https://example.com/cover.jpg",
  "form_logo_image": "https://example.com/logo.jpg",
  "form_submit_text": "Submit Feedback",
  "form_success_message": "Thank you for your feedback!",
  "form_success_url": "https://example.com/thank-you",
  "form_public": true,
  "form_password_protected": false,
  "form_limit_submissions": false,
  "form_conditional_logic": true
}
```

### Form Conditional Logic

```http
POST /api/database/views/form/{view_id}/conditional-logic/
```

**Request Body:**
```json
{
  "rules": [
    {
      "condition_field_id": 456,
      "condition_operator": "equals",
      "condition_value": "Yes",
      "action": "show_field",
      "target_field_id": 457
    }
  ]
}
```

### Form Validation Rules

```http
POST /api/database/views/form/{view_id}/validation-rules/
```

**Request Body:**
```json
{
  "field_id": 456,
  "rules": [
    {
      "type": "required",
      "message": "This field is required"
    },
    {
      "type": "min_length",
      "value": 10,
      "message": "Must be at least 10 characters"
    }
  ]
}
```

## View Filters and Sorts

All view types support advanced filtering and sorting:

### Apply Filters

```http
POST /api/database/views/{view_id}/filters/
```

**Request Body:**
```json
{
  "filters": [
    {
      "field_id": 456,
      "type": "equal",
      "value": "Active"
    },
    {
      "field_id": 457,
      "type": "date_after",
      "value": "2024-01-01"
    }
  ],
  "filter_type": "AND"
}
```

### Apply Sorts

```http
POST /api/database/views/{view_id}/sorts/
```

**Request Body:**
```json
{
  "sorts": [
    {
      "field_id": 456,
      "order": "ASC"
    },
    {
      "field_id": 457,
      "order": "DESC"
    }
  ]
}
```

## View Sharing and Permissions

### Create Public View Link

```http
POST /api/database/views/{view_id}/public-link/
```

**Request Body:**
```json
{
  "password": "optional_password",
  "expires_at": "2024-12-31T23:59:59Z",
  "allow_downloads": true
}
```

**Response:**
```json
{
  "public_url": "https://baserow.io/public/view/abc123def456",
  "password_protected": true,
  "expires_at": "2024-12-31T23:59:59Z"
}
```

### Update View Permissions

```http
PATCH /api/database/views/{view_id}/permissions/
```

**Request Body:**
```json
{
  "permissions": {
    "user_123": "editor",
    "user_456": "viewer"
  },
  "public_access": "none"
}
```

## View Export

### Export View Data

```http
POST /api/database/views/{view_id}/export/
```

**Request Body:**
```json
{
  "format": "csv",
  "include_headers": true,
  "filters": [],
  "sorts": []
}
```

**Response:**
```json
{
  "export_id": "export_123",
  "download_url": "https://baserow.io/exports/export_123.csv",
  "expires_at": "2024-01-16T10:30:00Z"
}
```