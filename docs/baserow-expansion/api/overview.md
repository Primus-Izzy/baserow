# API Overview - Baserow Expansion

This document provides a comprehensive overview of all new API endpoints and capabilities added in the Baserow Monday.com expansion.

## API Architecture

The expanded Baserow API maintains full backward compatibility while adding powerful new endpoints for enhanced functionality. All new endpoints follow RESTful principles and use the same authentication and error handling patterns as the core Baserow API.

### Base URL Structure
```
https://your-baserow-instance.com/api/
├── database/                    # Core database operations
│   ├── fields/                  # Field management (enhanced)
│   ├── views/                   # View management (enhanced)
│   ├── rows/                    # Row operations (enhanced)
│   ├── comments/                # NEW: Comments system
│   ├── activity/                # NEW: Activity logging
│   ├── presence/                # NEW: User presence
│   ├── automations/             # NEW: Automation system
│   └── batch/                   # NEW: Batch operations
├── dashboard/                   # NEW: Dashboard system
│   ├── dashboards/              # Dashboard management
│   ├── widgets/                 # Widget configuration
│   ├── charts/                  # Chart data and configuration
│   └── exports/                 # Dashboard exports
├── integrations/                # NEW: External integrations
│   ├── services/                # Integration services
│   ├── oauth/                   # OAuth authentication
│   └── webhooks/                # Webhook management
├── permissions/                 # NEW: Enhanced permissions
│   ├── roles/                   # Role management
│   ├── assignments/             # Permission assignments
│   └── api-keys/                # API key management
└── notifications/               # NEW: Notification system
    ├── preferences/             # User preferences
    ├── channels/                # Notification channels
    └── history/                 # Notification history
```

## Authentication

All new endpoints support the same authentication methods as core Baserow:

### JWT Token Authentication
```http
Authorization: JWT <your-jwt-token>
```

### API Key Authentication
```http
Authorization: Token <your-api-key>
```

### Enhanced API Key Features
- **Granular Permissions**: API keys can be scoped to specific tables, operations, and features
- **Rate Limiting**: Configurable rate limits per API key
- **Usage Tracking**: Monitor API key usage and performance
- **Expiration**: Set expiration dates for API keys

## New Field Types API

### Progress Bar Fields
Visual progress indicators with customizable ranges and colors.

**Endpoints:**
- `POST /api/database/fields/` - Create progress bar field
- `GET /api/database/fields/{id}/` - Get field configuration
- `PATCH /api/database/fields/{id}/` - Update field settings

**Key Features:**
- Multiple data sources (numeric fields, formulas, manual)
- Customizable color schemes and ranges
- Percentage display options

### People Fields
User assignment and collaboration features.

**Endpoints:**
- `POST /api/database/fields/` - Create people field
- `GET /api/database/fields/{id}/users/` - Get available users
- `POST /api/database/fields/{id}/notify/` - Send notifications

**Key Features:**
- Single or multiple user assignment
- Automatic notifications on changes
- Integration with permission system

### Formula Fields
Excel-like calculated fields with comprehensive function library.

**Endpoints:**
- `POST /api/database/fields/` - Create formula field
- `POST /api/database/fields/formula/validate/` - Validate formula syntax
- `GET /api/database/fields/{id}/dependencies/` - Get field dependencies

**Key Features:**
- Rich formula syntax with 50+ functions
- Dependency tracking and automatic recalculation
- Real-time validation and error reporting

### Rollup and Lookup Fields
Aggregate and reference data from linked tables.

**Endpoints:**
- `POST /api/database/fields/` - Create rollup/lookup field
- `GET /api/database/fields/{id}/preview/` - Preview calculated values
- `POST /api/database/fields/{id}/recalculate/` - Force recalculation

**Key Features:**
- Multiple aggregation functions (sum, count, average, etc.)
- Efficient query optimization
- Real-time updates when linked data changes

## New View Types API

### Kanban Views
Visual boards with drag-and-drop functionality.

**Endpoints:**
- `POST /api/database/views/` - Create Kanban view
- `GET /api/database/views/kanban/{id}/` - Get Kanban data
- `PATCH /api/database/views/kanban/{id}/move-card/` - Move cards between columns

**Key Features:**
- Configurable columns based on single-select fields
- Customizable card display and colors
- Real-time drag-and-drop updates

### Timeline/Gantt Views
Project scheduling with dependencies and milestones.

**Endpoints:**
- `POST /api/database/views/` - Create timeline view
- `GET /api/database/views/timeline/{id}/` - Get timeline data
- `POST /api/database/views/timeline/{id}/dependencies/` - Manage task dependencies

**Key Features:**
- Multiple zoom levels (day, week, month, year)
- Task dependencies and milestone tracking
- Drag-and-drop date adjustments

### Calendar Views
Event management with multiple display modes.

**Endpoints:**
- `POST /api/database/views/` - Create calendar view
- `GET /api/database/views/calendar/{id}/` - Get calendar events
- `POST /api/database/views/calendar/{id}/external-sync/` - External calendar integration

**Key Features:**
- Month, week, and day view modes
- External calendar synchronization
- Recurring event support

### Enhanced Form Views
Advanced forms with conditional logic and branding.

**Endpoints:**
- `POST /api/database/views/` - Create enhanced form view
- `POST /api/database/views/form/{id}/conditional-logic/` - Configure conditional fields
- `POST /api/database/views/form/{id}/validation-rules/` - Set validation rules

**Key Features:**
- Conditional field display logic
- Custom branding and styling
- Advanced validation rules

## Collaboration API

### Comments System
Threaded comments with mentions and rich text.

**Endpoints:**
- `GET /api/database/comments/` - List comments
- `POST /api/database/comments/` - Create comment
- `PATCH /api/database/comments/{id}/` - Update comment
- `DELETE /api/database/comments/{id}/` - Delete comment
- `POST /api/database/comments/{id}/resolve/` - Mark as resolved

**Key Features:**
- Threaded conversations
- @mention notifications
- Rich text formatting
- Permission-based visibility

### Activity Logging
Comprehensive audit trail of all user actions.

**Endpoints:**
- `GET /api/database/activity/` - Get activity log
- `GET /api/database/activity/export/` - Export activity data
- `GET /api/database/activity/stats/` - Activity statistics

**Key Features:**
- Detailed action tracking
- Advanced filtering and search
- Export capabilities
- Performance optimized queries

### User Presence
Real-time user activity and cursor tracking.

**Endpoints:**
- `GET /api/database/presence/` - Get active users
- `POST /api/database/presence/update/` - Update user presence
- `GET /api/database/presence/history/` - Presence history

**Key Features:**
- Live cursor positions
- Active user indicators
- Session management
- Real-time WebSocket updates

## Automation API

### Automation Management
Visual workflow builder with triggers and actions.

**Endpoints:**
- `GET /api/database/automations/` - List automations
- `POST /api/database/automations/` - Create automation
- `PATCH /api/database/automations/{id}/` - Update automation
- `POST /api/database/automations/{id}/test/` - Test automation

**Key Features:**
- Visual workflow designer
- Multiple trigger types
- Extensive action library
- Error handling and retry logic

### Triggers and Actions
Configurable automation components.

**Endpoints:**
- `GET /api/database/automations/triggers/` - Available trigger types
- `GET /api/database/automations/actions/` - Available action types
- `POST /api/database/automations/{id}/execute/` - Manual execution

**Key Features:**
- Record-based triggers
- Date and time triggers
- External webhook triggers
- Email, Slack, and webhook actions

### Execution Monitoring
Track automation performance and errors.

**Endpoints:**
- `GET /api/database/automations/{id}/executions/` - Execution history
- `GET /api/database/automations/{id}/logs/` - Detailed logs
- `GET /api/database/automations/stats/` - Performance statistics

**Key Features:**
- Detailed execution logs
- Performance metrics
- Error tracking and alerting
- Success/failure statistics

## Dashboard API

### Dashboard Management
Create and manage interactive dashboards.

**Endpoints:**
- `GET /api/dashboard/dashboards/` - List dashboards
- `POST /api/dashboard/dashboards/` - Create dashboard
- `PATCH /api/dashboard/dashboards/{id}/` - Update dashboard
- `POST /api/dashboard/dashboards/{id}/share/` - Share dashboard

**Key Features:**
- Drag-and-drop layout system
- Public sharing capabilities
- Permission-based access control
- Mobile-responsive designs

### Widget System
Configurable dashboard widgets.

**Endpoints:**
- `GET /api/dashboard/widgets/` - Available widget types
- `POST /api/dashboard/widgets/` - Create widget
- `GET /api/dashboard/widgets/{id}/data/` - Get widget data
- `POST /api/dashboard/widgets/{id}/refresh/` - Refresh widget data

**Key Features:**
- Multiple chart types
- KPI and counter widgets
- Real-time data updates
- Custom data sources

### Export and Sharing
Dashboard export and embedding capabilities.

**Endpoints:**
- `POST /api/dashboard/exports/` - Export dashboard
- `GET /api/dashboard/exports/{id}/` - Download export
- `POST /api/dashboard/embed/` - Generate embed code

**Key Features:**
- PDF and PNG exports
- Scheduled report delivery
- Widget embedding
- Public dashboard links

## Integration API

### External Services
Connect with popular external services.

**Endpoints:**
- `GET /api/integrations/services/` - Available services
- `POST /api/integrations/services/{service}/connect/` - Connect service
- `GET /api/integrations/services/{service}/status/` - Connection status
- `POST /api/integrations/services/{service}/sync/` - Sync data

**Supported Services:**
- Google Workspace (Drive, Calendar, Gmail)
- Microsoft 365 (OneDrive, Outlook, Teams)
- Slack and Discord
- Zapier and Make.com
- Dropbox and Box

### Webhook System
Reliable webhook delivery with retry logic.

**Endpoints:**
- `GET /api/integrations/webhooks/` - List webhooks
- `POST /api/integrations/webhooks/` - Create webhook
- `GET /api/integrations/webhooks/{id}/logs/` - Delivery logs
- `POST /api/integrations/webhooks/{id}/test/` - Test webhook

**Key Features:**
- Event filtering
- Retry mechanisms
- Signature verification
- Delivery tracking

## Enhanced Permissions API

### Role Management
Flexible role-based access control.

**Endpoints:**
- `GET /api/permissions/roles/` - List roles
- `POST /api/permissions/roles/` - Create custom role
- `PATCH /api/permissions/roles/{id}/` - Update role
- `GET /api/permissions/roles/{id}/users/` - Users with role

**Key Features:**
- Predefined and custom roles
- Hierarchical permissions
- Conditional access rules
- Time-based permissions

### Permission Assignment
Granular permission control at multiple levels.

**Endpoints:**
- `POST /api/permissions/assign/` - Assign permissions
- `GET /api/permissions/user/{id}/` - User permissions
- `POST /api/permissions/check/` - Check permissions
- `GET /api/permissions/audit/` - Permission audit log

**Key Features:**
- Workspace, table, view, field, and row-level permissions
- Conditional permissions based on data
- Comprehensive audit trails
- Bulk permission operations

## Batch Operations API

### Bulk Data Operations
Efficient processing of large datasets.

**Endpoints:**
- `POST /api/database/batch/create/` - Bulk create records
- `POST /api/database/batch/update/` - Bulk update records
- `POST /api/database/batch/delete/` - Bulk delete records
- `GET /api/database/batch/{id}/status/` - Operation status

**Key Features:**
- Transaction support
- Progress tracking
- Error handling
- Performance optimization

## WebSocket API

### Real-Time Updates
Live collaboration and data synchronization.

**Connection:**
```
wss://your-baserow-instance.com/ws/
```

**Message Types:**
- `table_updated` - Table data changes
- `view_updated` - View configuration changes
- `user_presence` - User activity updates
- `comment_added` - New comments
- `automation_executed` - Automation results

**Key Features:**
- Room-based subscriptions
- Automatic reconnection
- Message queuing
- Conflict resolution

## Rate Limiting

### Default Limits
- **Authenticated Users**: 1,000 requests per hour
- **API Keys**: 5,000 requests per hour (configurable)
- **Batch Operations**: 100 requests per hour
- **WebSocket Connections**: 10 concurrent connections per user

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
X-RateLimit-Retry-After: 3600
```

## Error Handling

### Standard Error Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {
      "field": "Additional error context"
    },
    "request_id": "req_1234567890"
  }
}
```

### Common Error Codes
- `PERMISSION_DENIED` - Insufficient permissions
- `VALIDATION_ERROR` - Invalid input data
- `RESOURCE_NOT_FOUND` - Requested resource doesn't exist
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `AUTOMATION_ERROR` - Automation execution failed
- `INTEGRATION_ERROR` - External service error

## API Versioning

### Version Strategy
- **Current Version**: v2 (expansion features)
- **Legacy Support**: v1 (core Baserow features)
- **Version Header**: `Accept: application/json; version=2`
- **URL Versioning**: `/api/v2/` (optional)

### Backward Compatibility
- All v1 endpoints remain functional
- New features only available in v2
- Gradual migration path provided
- Deprecation notices for removed features

## SDK and Libraries

### Official SDKs
- **Python SDK**: Full API coverage with async support
- **JavaScript SDK**: Browser and Node.js compatible
- **REST Client**: OpenAPI specification available

### Community Libraries
- **PHP SDK**: Community-maintained
- **Ruby Gem**: Community-maintained
- **Go Client**: Community-maintained

## Getting Started

### Quick Start Example
```javascript
// Initialize client
const baserow = new BaserowClient({
  apiUrl: 'https://your-baserow.com/api/',
  token: 'your-jwt-token'
});

// Create a Kanban view
const kanbanView = await baserow.views.create({
  type: 'kanban',
  name: 'Project Board',
  table_id: 123,
  kanban_single_select_field_id: 456
});

// Add automation
const automation = await baserow.automations.create({
  name: 'Task Assignment',
  table_id: 123,
  triggers: [{
    type: 'record_updated',
    field_id: 789
  }],
  actions: [{
    type: 'send_email',
    template: 'task_assigned'
  }]
});

// Create dashboard
const dashboard = await baserow.dashboards.create({
  name: 'Project Overview',
  widgets: [{
    type: 'chart',
    chart_type: 'bar',
    data_source: { table_id: 123, view_id: kanbanView.id }
  }]
});
```

This expanded API provides comprehensive functionality for building sophisticated applications on top of Baserow while maintaining the simplicity and flexibility that makes Baserow powerful.