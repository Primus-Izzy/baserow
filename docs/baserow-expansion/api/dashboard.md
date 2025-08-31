# Dashboard API Documentation

This document covers the API endpoints for dashboard and reporting features including widgets, charts, and data visualization.

## Dashboards

### Create Dashboard

```http
POST /api/dashboard/
```

**Request Body:**
```json
{
  "name": "Project Overview",
  "description": "Main project dashboard with key metrics",
  "workspace_id": 123,
  "layout": {
    "columns": 12,
    "row_height": 60,
    "widgets": []
  },
  "is_public": false,
  "theme": "light"
}
```

**Response:**
```json
{
  "id": 1001,
  "name": "Project Overview",
  "description": "Main project dashboard with key metrics",
  "workspace_id": 123,
  "layout": {
    "columns": 12,
    "row_height": 60,
    "widgets": []
  },
  "is_public": false,
  "theme": "light",
  "created_by": 123,
  "created_on": "2024-01-15T10:30:00Z",
  "updated_on": "2024-01-15T10:30:00Z"
}
```

### List Dashboards

```http
GET /api/dashboard/
```

**Query Parameters:**
- `workspace_id`: Filter by workspace ID
- `is_public`: Filter by public status
- `search`: Search by name or description

### Get Dashboard

```http
GET /api/dashboard/{dashboard_id}/
```

**Response:**
```json
{
  "id": 1001,
  "name": "Project Overview",
  "description": "Main project dashboard with key metrics",
  "workspace_id": 123,
  "layout": {
    "columns": 12,
    "row_height": 60,
    "widgets": [
      {
        "id": "widget_1",
        "type": "chart",
        "position": { "x": 0, "y": 0, "w": 6, "h": 4 },
        "configuration": {
          "chart_type": "bar",
          "title": "Tasks by Status",
          "data_source": {
            "table_id": 456,
            "view_id": 789
          }
        }
      }
    ]
  },
  "widgets": [
    {
      "id": 2001,
      "dashboard_id": 1001,
      "type": "chart",
      "configuration": {
        "chart_type": "bar",
        "title": "Tasks by Status",
        "data_source": {
          "table_id": 456,
          "view_id": 789,
          "group_by_field_id": 101,
          "aggregate_field_id": null,
          "aggregate_function": "count"
        },
        "styling": {
          "colors": ["#3498db", "#e74c3c", "#f39c12"],
          "show_legend": true,
          "show_grid": true
        }
      },
      "created_on": "2024-01-15T10:30:00Z"
    }
  ],
  "permissions": {
    "can_edit": true,
    "can_share": true,
    "can_delete": true
  }
}
```

### Update Dashboard

```http
PATCH /api/dashboard/{dashboard_id}/
```

### Delete Dashboard

```http
DELETE /api/dashboard/{dashboard_id}/
```

### Duplicate Dashboard

```http
POST /api/dashboard/{dashboard_id}/duplicate/
```

**Request Body:**
```json
{
  "name": "Project Overview Copy",
  "workspace_id": 124
}
```

## Widgets

### Create Widget

```http
POST /api/dashboard/widgets/
```

**Request Body:**
```json
{
  "dashboard_id": 1001,
  "type": "chart",
  "position": { "x": 0, "y": 0, "w": 6, "h": 4 },
  "configuration": {
    "chart_type": "pie",
    "title": "Task Distribution",
    "data_source": {
      "table_id": 456,
      "view_id": 789,
      "group_by_field_id": 101,
      "aggregate_function": "count",
      "filters": [
        {
          "field_id": 102,
          "type": "equal",
          "value": "Active"
        }
      ]
    },
    "styling": {
      "colors": ["#3498db", "#e74c3c", "#f39c12", "#2ecc71"],
      "show_legend": true,
      "show_values": true
    },
    "refresh_interval": 300
  }
}
```

**Response:**
```json
{
  "id": 2001,
  "dashboard_id": 1001,
  "type": "chart",
  "position": { "x": 0, "y": 0, "w": 6, "h": 4 },
  "configuration": {
    "chart_type": "pie",
    "title": "Task Distribution",
    "data_source": {
      "table_id": 456,
      "view_id": 789,
      "group_by_field_id": 101,
      "aggregate_function": "count",
      "filters": [
        {
          "field_id": 102,
          "type": "equal",
          "value": "Active"
        }
      ]
    },
    "styling": {
      "colors": ["#3498db", "#e74c3c", "#f39c12", "#2ecc71"],
      "show_legend": true,
      "show_values": true
    },
    "refresh_interval": 300
  },
  "created_on": "2024-01-15T10:30:00Z",
  "updated_on": "2024-01-15T10:30:00Z"
}
```

### Widget Types

#### Chart Widget
```json
{
  "type": "chart",
  "configuration": {
    "chart_type": "bar|line|pie|donut|area|scatter",
    "title": "Chart Title",
    "data_source": {
      "table_id": 456,
      "view_id": 789,
      "group_by_field_id": 101,
      "aggregate_field_id": 102,
      "aggregate_function": "sum|count|avg|min|max"
    },
    "styling": {
      "colors": ["#3498db", "#e74c3c"],
      "show_legend": true,
      "show_grid": true,
      "show_values": false
    }
  }
}
```

#### KPI Widget
```json
{
  "type": "kpi",
  "configuration": {
    "title": "Total Revenue",
    "data_source": {
      "table_id": 456,
      "aggregate_field_id": 102,
      "aggregate_function": "sum",
      "filters": []
    },
    "styling": {
      "color": "#2ecc71",
      "icon": "dollar-sign",
      "format": "currency",
      "show_trend": true,
      "trend_period": "month"
    }
  }
}
```

#### Table Widget
```json
{
  "type": "table",
  "configuration": {
    "title": "Recent Tasks",
    "data_source": {
      "table_id": 456,
      "view_id": 789,
      "limit": 10,
      "sorts": [
        {
          "field_id": 103,
          "order": "DESC"
        }
      ]
    },
    "styling": {
      "show_header": true,
      "striped_rows": true,
      "compact": false
    }
  }
}
```

#### Progress Widget
```json
{
  "type": "progress",
  "configuration": {
    "title": "Project Completion",
    "data_source": {
      "table_id": 456,
      "progress_field_id": 104,
      "aggregate_function": "avg"
    },
    "styling": {
      "color": "#3498db",
      "show_percentage": true,
      "show_value": true
    }
  }
}
```

#### Calendar Widget
```json
{
  "type": "calendar",
  "configuration": {
    "title": "Upcoming Deadlines",
    "data_source": {
      "table_id": 456,
      "date_field_id": 105,
      "title_field_id": 106,
      "color_field_id": 107
    },
    "styling": {
      "view_type": "month",
      "show_weekends": true
    }
  }
}
```

### Get Widget Data

```http
GET /api/dashboard/widgets/{widget_id}/data/
```

**Query Parameters:**
- `refresh`: Force refresh data (bypass cache)
- `date_range`: Custom date range for time-based data

**Response:**
```json
{
  "data": {
    "labels": ["To Do", "In Progress", "Done"],
    "datasets": [
      {
        "label": "Tasks",
        "data": [15, 8, 22],
        "backgroundColor": ["#3498db", "#f39c12", "#2ecc71"]
      }
    ]
  },
  "metadata": {
    "total_records": 45,
    "last_updated": "2024-01-15T10:30:00Z",
    "cache_expires": "2024-01-15T10:35:00Z"
  }
}
```

### Update Widget

```http
PATCH /api/dashboard/widgets/{widget_id}/
```

### Delete Widget

```http
DELETE /api/dashboard/widgets/{widget_id}/
```

### Update Widget Layout

```http
PATCH /api/dashboard/{dashboard_id}/layout/
```

**Request Body:**
```json
{
  "widgets": [
    {
      "id": "widget_1",
      "position": { "x": 0, "y": 0, "w": 6, "h": 4 }
    },
    {
      "id": "widget_2",
      "position": { "x": 6, "y": 0, "w": 6, "h": 4 }
    }
  ]
}
```

## Charts

### Chart Data Processing

```http
POST /api/dashboard/charts/process-data/
```

**Request Body:**
```json
{
  "data_source": {
    "table_id": 456,
    "view_id": 789,
    "group_by_field_id": 101,
    "aggregate_field_id": 102,
    "aggregate_function": "sum",
    "filters": [],
    "date_range": {
      "start_date": "2024-01-01",
      "end_date": "2024-01-31"
    }
  },
  "chart_type": "line",
  "time_grouping": "day"
}
```

**Response:**
```json
{
  "processed_data": {
    "labels": ["2024-01-01", "2024-01-02", "2024-01-03"],
    "datasets": [
      {
        "label": "Revenue",
        "data": [1200, 1500, 1800],
        "borderColor": "#3498db",
        "backgroundColor": "rgba(52, 152, 219, 0.1)"
      }
    ]
  },
  "statistics": {
    "total": 4500,
    "average": 1500,
    "min": 1200,
    "max": 1800,
    "trend": "increasing"
  }
}
```

### Chart Templates

```http
GET /api/dashboard/charts/templates/
```

**Response:**
```json
{
  "templates": [
    {
      "id": "template_1",
      "name": "Task Status Distribution",
      "description": "Pie chart showing task distribution by status",
      "chart_type": "pie",
      "required_fields": ["single_select"],
      "configuration": {
        "group_by_field_type": "single_select",
        "aggregate_function": "count"
      }
    }
  ]
}
```

## Dashboard Sharing

### Create Public Dashboard Link

```http
POST /api/dashboard/{dashboard_id}/public-link/
```

**Request Body:**
```json
{
  "password": "optional_password",
  "expires_at": "2024-12-31T23:59:59Z",
  "allow_downloads": true,
  "branding": {
    "show_baserow_branding": false,
    "custom_logo": "https://example.com/logo.png",
    "custom_title": "Company Dashboard"
  }
}
```

**Response:**
```json
{
  "public_url": "https://baserow.io/public/dashboard/abc123def456",
  "password_protected": true,
  "expires_at": "2024-12-31T23:59:59Z",
  "created_on": "2024-01-15T10:30:00Z"
}
```

### Dashboard Permissions

```http
PATCH /api/dashboard/{dashboard_id}/permissions/
```

**Request Body:**
```json
{
  "permissions": {
    "user_123": "editor",
    "user_456": "viewer"
  },
  "public_access": "none",
  "workspace_access": "viewer"
}
```

### Embed Widget

```http
GET /api/dashboard/widgets/{widget_id}/embed/
```

**Query Parameters:**
- `theme`: light|dark
- `show_title`: true|false
- `width`: Widget width in pixels
- `height`: Widget height in pixels

**Response:**
```json
{
  "embed_url": "https://baserow.io/embed/widget/abc123",
  "iframe_code": "<iframe src=\"https://baserow.io/embed/widget/abc123\" width=\"400\" height=\"300\"></iframe>",
  "javascript_code": "<script src=\"https://baserow.io/embed/widget/abc123.js\"></script>"
}
```

## Dashboard Export

### Export Dashboard

```http
POST /api/dashboard/{dashboard_id}/export/
```

**Request Body:**
```json
{
  "format": "pdf|png|html",
  "layout": "portrait|landscape",
  "include_data": true,
  "date_range": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  }
}
```

**Response:**
```json
{
  "export_id": "dashboard_export_123",
  "download_url": "https://baserow.io/exports/dashboard_export_123.pdf",
  "expires_at": "2024-01-16T10:30:00Z",
  "status": "processing"
}
```

### Schedule Dashboard Report

```http
POST /api/dashboard/{dashboard_id}/schedule-report/
```

**Request Body:**
```json
{
  "name": "Weekly Project Report",
  "schedule": {
    "frequency": "weekly",
    "day_of_week": 1,
    "time": "09:00",
    "timezone": "UTC"
  },
  "format": "pdf",
  "recipients": ["manager@example.com", "team@example.com"],
  "include_data": true,
  "active": true
}
```

### Export Widget Data

```http
POST /api/dashboard/widgets/{widget_id}/export-data/
```

**Request Body:**
```json
{
  "format": "csv|xlsx|json",
  "include_metadata": true
}
```

## Dashboard Analytics

### Get Dashboard Usage

```http
GET /api/dashboard/{dashboard_id}/analytics/
```

**Query Parameters:**
- `start_date`: Analytics start date
- `end_date`: Analytics end date
- `metric`: views|users|exports

**Response:**
```json
{
  "metrics": {
    "total_views": 150,
    "unique_users": 25,
    "avg_session_duration": 180,
    "most_viewed_widget": {
      "widget_id": 2001,
      "title": "Task Distribution",
      "views": 45
    }
  },
  "timeline": [
    {
      "date": "2024-01-15",
      "views": 12,
      "unique_users": 5
    }
  ]
}
```

### Widget Performance

```http
GET /api/dashboard/widgets/{widget_id}/performance/
```

**Response:**
```json
{
  "performance": {
    "avg_load_time_ms": 250,
    "cache_hit_rate": 0.85,
    "data_freshness_minutes": 5,
    "error_rate": 0.02
  },
  "optimization_suggestions": [
    {
      "type": "cache_optimization",
      "message": "Consider increasing cache duration for this widget",
      "impact": "medium"
    }
  ]
}
```

## Real-Time Dashboard Updates

### WebSocket Connection for Dashboards

```javascript
const ws = new WebSocket('wss://your-baserow-instance.com/ws/dashboard/');

// Subscribe to dashboard updates
ws.send(JSON.stringify({
    type: 'subscribe_dashboard',
    dashboard_id: 1001
}));

// Receive real-time updates
{
    type: 'widget_data_updated',
    widget_id: 2001,
    data: {
        // Updated widget data
    },
    timestamp: '2024-01-15T10:30:00Z'
}
```

### Manual Refresh

```http
POST /api/dashboard/widgets/{widget_id}/refresh/
```

**Response:**
```json
{
  "status": "refreshed",
  "last_updated": "2024-01-15T10:30:00Z",
  "cache_expires": "2024-01-15T10:35:00Z"
}
```