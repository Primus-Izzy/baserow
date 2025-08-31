# API Overview

The Baserow API provides comprehensive access to all platform features through a RESTful interface. This expanded API supports the new Monday.com-style features while maintaining backward compatibility.

## 🚀 Quick Start

### Authentication

All API requests require authentication using either JWT tokens or API keys.

#### JWT Authentication
```bash
# Login to get JWT token
curl -X POST https://api.baserow.io/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Use token in subsequent requests
curl -H "Authorization: JWT your-jwt-token" \
  https://api.baserow.io/api/database/tables/
```

#### API Key Authentication
```bash
# Create API key in user settings
curl -H "Authorization: Token your-api-key" \
  https://api.baserow.io/api/database/tables/
```

### Base URL
- **Production**: `https://api.baserow.io`
- **Self-hosted**: `https://your-domain.com`

### API Versioning
- **Current Version**: `v2`
- **Legacy Support**: `v1` (deprecated, use v2)
- **Version Header**: `Accept: application/json; version=2`

## 📊 New API Endpoints

### View Types
- **Kanban Views**: `/api/database/views/kanban/`
- **Timeline Views**: `/api/database/views/timeline/`
- **Calendar Views**: `/api/database/views/calendar/`
- **Enhanced Forms**: `/api/database/views/form/`

### Field Types
- **Progress Bar**: `/api/database/fields/progress-bar/`
- **People Fields**: `/api/database/fields/people/`
- **Enhanced Formulas**: `/api/database/fields/formula/`

### Collaboration
- **Comments**: `/api/database/comments/`
- **Activity Log**: `/api/database/activity/`
- **Notifications**: `/api/notifications/`
- **User Presence**: `/api/presence/`

### Automation
- **Workflows**: `/api/automation/workflows/`
- **Triggers**: `/api/automation/triggers/`
- **Actions**: `/api/automation/actions/`

### Dashboards
- **Dashboards**: `/api/dashboards/`
- **Widgets**: `/api/dashboards/widgets/`
- **Charts**: `/api/dashboards/charts/`

## 🔧 Request/Response Format

### Request Headers
```http
Content-Type: application/json
Authorization: JWT your-jwt-token
Accept: application/json; version=2
X-Client-Version: 2.0.0
```

### Response Format
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Example Table",
    "created_on": "2024-01-01T00:00:00Z"
  },
  "meta": {
    "total_count": 100,
    "page": 1,
    "per_page": 20
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid field value",
    "details": {
      "field_name": ["This field is required"]
    }
  }
}
```

## 📈 Rate Limiting

### Default Limits
- **Authenticated Users**: 1000 requests/hour
- **API Keys**: 5000 requests/hour
- **Enterprise**: Custom limits available

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

### Handling Rate Limits
```javascript
// JavaScript example with retry logic
async function apiRequest(url, options) {
  const response = await fetch(url, options);
  
  if (response.status === 429) {
    const resetTime = response.headers.get('X-RateLimit-Reset');
    const waitTime = (resetTime * 1000) - Date.now();
    
    await new Promise(resolve => setTimeout(resolve, waitTime));
    return apiRequest(url, options); // Retry
  }
  
  return response;
}
```

## 🔄 Batch Operations

### Bulk Record Operations
```bash
# Create multiple records
curl -X POST https://api.baserow.io/api/database/tables/1/rows/batch/ \
  -H "Authorization: JWT your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"field_1": "Value 1", "field_2": "Value 2"},
      {"field_1": "Value 3", "field_2": "Value 4"}
    ]
  }'

# Update multiple records
curl -X PATCH https://api.baserow.io/api/database/tables/1/rows/batch/ \
  -H "Authorization: JWT your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"id": 1, "field_1": "Updated Value 1"},
      {"id": 2, "field_1": "Updated Value 2"}
    ]
  }'
```

### Batch Response
```json
{
  "success": true,
  "data": {
    "items": [
      {"id": 1, "field_1": "Value 1", "created_on": "2024-01-01T00:00:00Z"},
      {"id": 2, "field_1": "Value 3", "created_on": "2024-01-01T00:00:01Z"}
    ],
    "errors": []
  }
}
```

## 🔔 Webhooks

### Webhook Configuration
```bash
# Create webhook
curl -X POST https://api.baserow.io/api/database/webhooks/ \
  -H "Authorization: JWT your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.com/webhook",
    "events": ["row.created", "row.updated"],
    "table_id": 1,
    "active": true
  }'
```

### Webhook Payload
```json
{
  "event": "row.created",
  "table_id": 1,
  "row_id": 123,
  "data": {
    "id": 123,
    "field_1": "New Value",
    "created_on": "2024-01-01T00:00:00Z"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "webhook_id": 456
}
```

### Webhook Security
```javascript
// Verify webhook signature
const crypto = require('crypto');

function verifyWebhook(payload, signature, secret) {
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');
  
  return signature === `sha256=${expectedSignature}`;
}
```

## 🔍 Filtering and Searching

### Advanced Filtering
```bash
# Complex filter example
curl "https://api.baserow.io/api/database/tables/1/rows/?filters=field_1__contains,John&filters=field_2__higher_than,100&filter_type=AND"
```

### Available Filter Types
- `equal` - Exact match
- `not_equal` - Not equal
- `contains` - Contains text
- `contains_not` - Does not contain
- `higher_than` - Greater than
- `lower_than` - Less than
- `date_equal` - Date equals
- `date_before` - Date before
- `date_after` - Date after
- `empty` - Field is empty
- `not_empty` - Field is not empty

### Search Across Fields
```bash
# Full-text search
curl "https://api.baserow.io/api/database/tables/1/rows/?search=project%20management"
```

## 📊 Pagination

### Cursor-based Pagination
```bash
# First page
curl "https://api.baserow.io/api/database/tables/1/rows/?size=20"

# Next page using cursor
curl "https://api.baserow.io/api/database/tables/1/rows/?size=20&cursor=eyJpZCI6MjB9"
```

### Pagination Response
```json
{
  "success": true,
  "data": {
    "results": [...],
    "next": "eyJpZCI6NDB9",
    "previous": null,
    "count": 1000
  }
}
```

## 🚀 Real-time Updates

### WebSocket Connection
```javascript
// Connect to WebSocket for real-time updates
const ws = new WebSocket('wss://api.baserow.io/ws/table/1/');

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Real-time update:', data);
};

// Subscribe to specific events
ws.send(JSON.stringify({
  type: 'subscribe',
  events: ['row_created', 'row_updated', 'row_deleted']
}));
```

### WebSocket Message Format
```json
{
  "type": "row_updated",
  "table_id": 1,
  "row_id": 123,
  "data": {
    "id": 123,
    "field_1": "Updated Value"
  },
  "user_id": 456,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 🔐 Security Best Practices

### API Key Management
- Store API keys securely (environment variables)
- Use different keys for different environments
- Rotate keys regularly
- Limit key permissions to minimum required

### Request Security
```bash
# Always use HTTPS
curl -X GET https://api.baserow.io/api/database/tables/ \
  -H "Authorization: JWT your-token" \
  -H "User-Agent: YourApp/1.0"
```

### Input Validation
```javascript
// Validate input before sending to API
function validateRowData(data) {
  const errors = {};
  
  if (!data.field_1 || data.field_1.length < 1) {
    errors.field_1 = 'Field 1 is required';
  }
  
  if (data.field_2 && data.field_2 > 1000) {
    errors.field_2 = 'Field 2 must be less than 1000';
  }
  
  return Object.keys(errors).length === 0 ? null : errors;
}
```

## 📚 SDK and Libraries

### Official SDKs
- **JavaScript/TypeScript**: `@baserow/sdk`
- **Python**: `baserow-client`
- **PHP**: `baserow/php-sdk`

### JavaScript SDK Example
```javascript
import { BaserowClient } from '@baserow/sdk';

const client = new BaserowClient({
  baseUrl: 'https://api.baserow.io',
  token: 'your-jwt-token'
});

// Get table data
const rows = await client.table(1).rows.list();

// Create new row
const newRow = await client.table(1).rows.create({
  field_1: 'New Value',
  field_2: 100
});
```

### Python SDK Example
```python
from baserow_client import BaserowClient

client = BaserowClient(
    base_url='https://api.baserow.io',
    token='your-jwt-token'
)

# Get table data
rows = client.table(1).rows.list()

# Create new row
new_row = client.table(1).rows.create({
    'field_1': 'New Value',
    'field_2': 100
})
```

## 🐛 Error Handling

### Common Error Codes
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `429` - Too Many Requests (rate limited)
- `500` - Internal Server Error

### Error Response Examples
```json
{
  "success": false,
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "You don't have permission to access this resource",
    "details": {
      "required_permission": "table.read",
      "user_permissions": ["workspace.read"]
    }
  }
}
```

### Retry Logic
```javascript
async function apiRequestWithRetry(url, options, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url, options);
      
      if (response.ok) {
        return response;
      }
      
      if (response.status >= 500 && i < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, i)));
        continue;
      }
      
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, i)));
    }
  }
}
```

## 📈 Performance Optimization

### Efficient Queries
```bash
# Use field selection to reduce payload size
curl "https://api.baserow.io/api/database/tables/1/rows/?include=field_1,field_2"

# Use pagination for large datasets
curl "https://api.baserow.io/api/database/tables/1/rows/?size=100"
```

### Caching Strategies
```javascript
// Client-side caching example
class BaserowCache {
  constructor(ttl = 300000) { // 5 minutes
    this.cache = new Map();
    this.ttl = ttl;
  }
  
  get(key) {
    const item = this.cache.get(key);
    if (!item) return null;
    
    if (Date.now() > item.expiry) {
      this.cache.delete(key);
      return null;
    }
    
    return item.data;
  }
  
  set(key, data) {
    this.cache.set(key, {
      data,
      expiry: Date.now() + this.ttl
    });
  }
}
```

## 🔗 Related Documentation

- [View Endpoints](views.md) - Detailed view API documentation
- [Field Endpoints](fields.md) - Field management APIs
- [Automation API](automation.md) - Workflow and automation APIs
- [Dashboard API](dashboards.md) - Dashboard and widget APIs
- [Collaboration API](collaboration.md) - Comments and activity APIs

---

**Next Steps**: Explore specific API endpoints or check out our [SDK documentation](../developer/sdks.md) for easier integration.