# Permissions API Documentation

This document covers the API endpoints for the enhanced permission system in the Baserow expansion.

## Overview

The enhanced permission system provides granular access control at workspace, database, table, view, field, and row levels. It supports both predefined and custom roles with conditional permissions based on field values and user attributes.

## Permission Levels

### Hierarchy
1. **Workspace Level** - Overall workspace access
2. **Database Level** - Database-specific permissions  
3. **Table Level** - Table access and modification
4. **View Level** - View-specific visibility and editing
5. **Field Level** - Individual field permissions
6. **Row Level** - Record-specific access control

## Role Management

### Get Available Roles

```http
GET /api/permissions/roles/
```

**Response:**
```json
{
  "predefined_roles": [
    {
      "id": "admin",
      "name": "Administrator",
      "description": "Full access to all features",
      "permissions": ["create", "read", "update", "delete", "manage_permissions"]
    },
    {
      "id": "editor", 
      "name": "Editor",
      "description": "Can create and edit content",
      "permissions": ["create", "read", "update"]
    },
    {
      "id": "viewer",
      "name": "Viewer", 
      "description": "Read-only access",
      "permissions": ["read"]
    },
    {
      "id": "commenter",
      "name": "Commenter",
      "description": "Can view and comment",
      "permissions": ["read", "comment"]
    }
  ],
  "custom_roles": [
    {
      "id": 123,
      "name": "Data Analyst",
      "description": "Can view and export data",
      "permissions": ["read", "export"],
      "created_by": 456,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Create Custom Role

```http
POST /api/permissions/roles/
```

**Request Body:**
```json
{
  "name": "Project Manager",
  "description": "Can manage projects and assign tasks",
  "permissions": ["create", "read", "update", "assign_users", "manage_automation"],
  "workspace_id": 123
}
```

**Response:**
```json
{
  "id": 124,
  "name": "Project Manager",
  "description": "Can manage projects and assign tasks", 
  "permissions": ["create", "read", "update", "assign_users", "manage_automation"],
  "workspace_id": 123,
  "created_by": 456,
  "created_at": "2024-01-15T10:30:00Z"
}
```

## Permission Assignment

### Assign User Permissions

```http
POST /api/permissions/assign/
```

**Request Body:**
```json
{
  "user_id": 789,
  "resource_type": "table",
  "resource_id": 123,
  "role": "editor",
  "conditions": {
    "field_456": "Department A",
    "user_attribute": "department"
  },
  "expires_at": "2024-12-31T23:59:59Z"
}
```

**Response:**
```json
{
  "id": 1001,
  "user_id": 789,
  "resource_type": "table",
  "resource_id": 123,
  "role": "editor",
  "conditions": {
    "field_456": "Department A",
    "user_attribute": "department"
  },
  "expires_at": "2024-12-31T23:59:59Z",
  "assigned_by": 456,
  "assigned_at": "2024-01-15T10:30:00Z"
}
```

### Get User Permissions

```http
GET /api/permissions/user/{user_id}/
```

**Query Parameters:**
- `resource_type`: Filter by resource type (workspace, database, table, view, field)
- `resource_id`: Filter by specific resource ID

**Response:**
```json
{
  "user_id": 789,
  "permissions": [
    {
      "resource_type": "workspace",
      "resource_id": 1,
      "role": "member",
      "permissions": ["read", "create_tables"],
      "inherited": false
    },
    {
      "resource_type": "table", 
      "resource_id": 123,
      "role": "editor",
      "permissions": ["create", "read", "update"],
      "conditions": {
        "field_456": "Department A"
      },
      "inherited": false
    }
  ]
}
```

## Field-Level Permissions

### Set Field Permissions

```http
POST /api/permissions/field/{field_id}/
```

**Request Body:**
```json
{
  "permissions": [
    {
      "user_id": 789,
      "permission": "read"
    },
    {
      "role": "editor",
      "permission": "update"
    },
    {
      "user_id": 790,
      "permission": "none"
    }
  ]
}
```

### Get Field Permissions

```http
GET /api/permissions/field/{field_id}/
```

**Response:**
```json
{
  "field_id": 456,
  "permissions": [
    {
      "user_id": 789,
      "permission": "read",
      "assigned_by": 123,
      "assigned_at": "2024-01-15T10:30:00Z"
    },
    {
      "role": "editor", 
      "permission": "update",
      "assigned_by": 123,
      "assigned_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

## Row-Level Permissions

### Set Row Permissions

```http
POST /api/permissions/row/
```

**Request Body:**
```json
{
  "table_id": 123,
  "row_id": 1001,
  "permissions": [
    {
      "user_id": 789,
      "permission": "read"
    },
    {
      "user_id": 790,
      "permission": "update"
    }
  ]
}
```

### Conditional Row Permissions

```http
POST /api/permissions/row/conditional/
```

**Request Body:**
```json
{
  "table_id": 123,
  "conditions": {
    "field_456": "{{user.department}}",
    "field_789": "Active"
  },
  "permissions": [
    {
      "user_attribute": "department",
      "permission": "update"
    }
  ]
}
```

## API Key Management

### Create API Key

```http
POST /api/permissions/api-keys/
```

**Request Body:**
```json
{
  "name": "Mobile App Integration",
  "description": "API key for mobile application",
  "permissions": {
    "tables": [123, 124],
    "operations": ["read", "create", "update"],
    "rate_limit": 1000
  },
  "expires_at": "2024-12-31T23:59:59Z"
}
```

**Response:**
```json
{
  "id": 2001,
  "name": "Mobile App Integration",
  "key": "brow_1234567890abcdef",
  "permissions": {
    "tables": [123, 124],
    "operations": ["read", "create", "update"],
    "rate_limit": 1000
  },
  "expires_at": "2024-12-31T23:59:59Z",
  "created_at": "2024-01-15T10:30:00Z",
  "last_used": null
}
```

### List API Keys

```http
GET /api/permissions/api-keys/
```

**Response:**
```json
{
  "api_keys": [
    {
      "id": 2001,
      "name": "Mobile App Integration",
      "key_preview": "brow_1234...cdef",
      "permissions": {
        "tables": [123, 124],
        "operations": ["read", "create", "update"],
        "rate_limit": 1000
      },
      "expires_at": "2024-12-31T23:59:59Z",
      "created_at": "2024-01-15T10:30:00Z",
      "last_used": "2024-01-15T14:22:00Z",
      "usage_count": 1547
    }
  ]
}
```

### Revoke API Key

```http
DELETE /api/permissions/api-keys/{key_id}/
```

## Permission Validation

### Check User Permission

```http
POST /api/permissions/check/
```

**Request Body:**
```json
{
  "user_id": 789,
  "resource_type": "table",
  "resource_id": 123,
  "permission": "update",
  "context": {
    "row_id": 1001,
    "field_id": 456
  }
}
```

**Response:**
```json
{
  "allowed": true,
  "reason": "User has editor role on table",
  "conditions_met": true,
  "effective_permission": "update"
}
```

### Bulk Permission Check

```http
POST /api/permissions/check/bulk/
```

**Request Body:**
```json
{
  "user_id": 789,
  "checks": [
    {
      "resource_type": "table",
      "resource_id": 123,
      "permission": "read"
    },
    {
      "resource_type": "field",
      "resource_id": 456,
      "permission": "update"
    }
  ]
}
```

**Response:**
```json
{
  "results": [
    {
      "resource_type": "table",
      "resource_id": 123,
      "permission": "read",
      "allowed": true
    },
    {
      "resource_type": "field", 
      "resource_id": 456,
      "permission": "update",
      "allowed": false,
      "reason": "Field is read-only for this user"
    }
  ]
}
```

## Audit and Logging

### Get Permission Audit Log

```http
GET /api/permissions/audit/
```

**Query Parameters:**
- `user_id`: Filter by user
- `resource_type`: Filter by resource type
- `action`: Filter by action (grant, revoke, check)
- `start_date`: Start date for log entries
- `end_date`: End date for log entries

**Response:**
```json
{
  "audit_entries": [
    {
      "id": 3001,
      "user_id": 789,
      "action": "permission_granted",
      "resource_type": "table",
      "resource_id": 123,
      "permission": "editor",
      "granted_by": 456,
      "timestamp": "2024-01-15T10:30:00Z",
      "details": {
        "previous_permission": "viewer",
        "reason": "Promoted to project lead"
      }
    }
  ],
  "pagination": {
    "count": 150,
    "next": "/api/permissions/audit/?page=2",
    "previous": null
  }
}
```

## Security Features

### Enable Two-Factor Authentication

```http
POST /api/permissions/2fa/enable/
```

**Request Body:**
```json
{
  "user_id": 789,
  "method": "totp",
  "backup_codes": true
}
```

### IP Restrictions

```http
POST /api/permissions/ip-restrictions/
```

**Request Body:**
```json
{
  "user_id": 789,
  "allowed_ips": [
    "192.168.1.0/24",
    "10.0.0.100"
  ],
  "blocked_ips": [
    "192.168.2.50"
  ]
}
```

## Error Responses

### Permission Denied
```json
{
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "You don't have permission to perform this action",
    "details": {
      "required_permission": "update",
      "current_permission": "read",
      "resource_type": "table",
      "resource_id": 123
    }
  }
}
```

### Invalid Role
```json
{
  "error": {
    "code": "INVALID_ROLE",
    "message": "The specified role does not exist",
    "details": {
      "role": "invalid_role",
      "available_roles": ["admin", "editor", "viewer", "commenter"]
    }
  }
}
```

### Conditional Permission Failed
```json
{
  "error": {
    "code": "CONDITION_NOT_MET",
    "message": "Permission conditions not satisfied",
    "details": {
      "failed_conditions": {
        "field_456": {
          "required": "Department A",
          "actual": "Department B"
        }
      }
    }
  }
}
```

This permissions API provides comprehensive access control capabilities while maintaining security and auditability throughout the system.