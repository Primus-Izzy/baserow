# API Documentation

This section provides comprehensive API documentation for all new endpoints and features added in the Baserow Monday.com expansion.

## Overview

The Baserow expansion maintains the existing RESTful API design while adding new endpoints for enhanced functionality. All new endpoints follow the same authentication, pagination, and error handling patterns as the core Baserow API.

## Base URL

```
https://your-baserow-instance.com/api/
```

## Authentication

All API endpoints require authentication using one of the following methods:

### JWT Token Authentication
```http
Authorization: JWT <your-jwt-token>
```

### API Key Authentication
```http
Authorization: Token <your-api-key>
```

## New API Endpoints Overview

### View Types
- **Kanban Views**: `/api/database/views/kanban/`
- **Timeline Views**: `/api/database/views/timeline/`
- **Calendar Views**: `/api/database/views/calendar/`
- **Enhanced Form Views**: `/api/database/views/form/enhanced/`

### Field Types
- **Progress Bar Fields**: `/api/database/fields/progress-bar/`
- **People Fields**: `/api/database/fields/people/`
- **Formula Fields**: `/api/database/fields/formula/`
- **Rollup Fields**: `/api/database/fields/rollup/`
- **Lookup Fields**: `/api/database/fields/lookup/`

### Automation System
- **Automations**: `/api/database/automations/`
- **Triggers**: `/api/database/automations/triggers/`
- **Actions**: `/api/database/automations/actions/`
- **Workflows**: `/api/database/automations/workflows/`

### Collaboration Features
- **Comments**: `/api/database/comments/`
- **Activity Logs**: `/api/database/activity/`
- **User Presence**: `/api/database/presence/`
- **Notifications**: `/api/database/notifications/`

### Dashboard & Reporting
- **Dashboards**: `/api/dashboard/`
- **Widgets**: `/api/dashboard/widgets/`
- **Charts**: `/api/dashboard/charts/`
- **Exports**: `/api/dashboard/exports/`

### Integrations
- **Native Integrations**: `/api/integrations/`
- **Webhooks**: `/api/webhooks/`
- **External Services**: `/api/integrations/services/`

### Enhanced API Features
- **Batch Operations**: `/api/database/batch/`
- **Advanced Permissions**: `/api/permissions/`
- **Security Features**: `/api/security/`

## Common Response Formats

### Success Response
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "meta": {
    "pagination": {
      "count": 100,
      "next": "https://api.example.com/endpoint/?page=2",
      "previous": null
    }
  }
}
```

### Error Response
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {
      // Additional error details
    }
  }
}
```

## Rate Limiting

API requests are rate limited to prevent abuse:
- **Authenticated users**: 1000 requests per hour
- **API keys**: Configurable per key (default: 5000 requests per hour)
- **Batch operations**: 100 requests per hour

Rate limit headers are included in all responses:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Pagination

All list endpoints support pagination using the following parameters:
- `page`: Page number (default: 1)
- `size`: Items per page (default: 100, max: 200)

## Filtering and Sorting

Enhanced filtering and sorting capabilities are available on most endpoints:
- `filters`: JSON object with filter conditions
- `sorts`: Array of sort specifications
- `search`: Full-text search query

Example:
```
GET /api/database/rows/123/?filters={"field_456": "value"}&sorts=[{"field": "field_789", "order": "ASC"}]
```

## WebSocket API

Real-time features use WebSocket connections:
- **Connection URL**: `wss://your-baserow-instance.com/ws/`
- **Authentication**: Include JWT token in connection headers
- **Room-based updates**: Subscribe to specific table/view updates

## Detailed Endpoint Documentation

For detailed documentation of specific endpoints, see:
- [Field Types API](./field-types.md)
- [View Types API](./view-types.md)
- [Automation API](./automation.md)
- [Collaboration API](./collaboration.md)
- [Dashboard API](./dashboard.md)
- [Integration API](./integrations.md)