# Granular Permission System

This module implements a comprehensive granular permission system for Baserow that extends the existing workspace-level permissions to provide fine-grained access control at table, field, view, and row levels.

## Features

### Custom Roles
- Create custom roles with specific permission sets
- Assign roles to users within workspaces
- Hierarchical permission inheritance

### Permission Levels
- **Table Level**: Control access to entire tables
- **Field Level**: Hide or restrict access to specific fields
- **View Level**: Control access to specific views
- **Row Level**: Control access to individual records

### Conditional Permissions
- Dynamic permissions based on field values
- User attribute-based conditions
- Complex condition evaluation

### API Key Management
- Granular scope control for API access
- Rate limiting and IP restrictions
- Expiration and usage tracking

## Models

### CustomRole
Defines custom roles with specific permissions:
- `can_create_tables`: Permission to create new tables
- `can_delete_tables`: Permission to delete tables
- `can_create_views`: Permission to create views
- `can_manage_workspace`: Permission to manage workspace settings

### TablePermission
Controls access to tables:
- `permission_level`: Overall permission level (NONE, READ, UPDATE, CREATE, DELETE)
- `can_create_rows`: Specific permission to create rows
- `can_update_rows`: Specific permission to update rows
- `can_delete_rows`: Specific permission to delete rows

### FieldPermission
Controls access to fields:
- `permission_level`: Overall permission level
- `can_read`: Permission to read field values
- `can_update`: Permission to update field values
- `is_hidden`: Hide field from user interface

### ViewPermission
Controls access to views:
- `permission_level`: Overall permission level
- `can_read`: Permission to view the view
- `can_update`: Permission to modify view settings
- `can_delete`: Permission to delete the view
- `is_hidden`: Hide view from user interface

### ConditionalPermission
Dynamic permissions based on conditions:
- `condition_field`: Field to evaluate
- `condition_operator`: Comparison operator
- `condition_value`: Value to compare against
- `user_attribute_field`: Optional user attribute condition
- `granted_permission_level`: Permission level when condition is met

### RowPermission
Controls access to specific rows:
- `row_id`: ID of the specific row
- `permission_level`: Overall permission level
- `can_read`: Permission to read the row
- `can_update`: Permission to update the row
- `can_delete`: Permission to delete the row
- `is_hidden`: Hide row from user interface

### APIKey
API keys with granular scope control:
- `scope_tables`: Tables this API key can access
- `scope_views`: Views this API key can access
- `can_read/create/update/delete`: Operation permissions
- `rate_limit_per_minute`: Rate limiting
- `allowed_ip_addresses`: IP restrictions
- `expires_at`: Optional expiration

## Usage

### Creating Custom Roles

```python
from baserow.contrib.database.permissions.handler import GranularPermissionHandler

handler = GranularPermissionHandler()

# Create a custom role
role = handler.create_custom_role(
    workspace=workspace,
    name="Editor",
    description="Can edit data but not structure",
    created_by=admin_user,
    can_create_tables=False,
    can_delete_tables=False,
    can_create_views=True
)

# Assign role to user
handler.assign_role_to_user(
    user=user,
    role=role,
    workspace=workspace,
    assigned_by=admin_user
)
```

### Setting Permissions

```python
# Set table permission
handler.set_table_permission(
    table=table,
    user=user,
    permission_level=PermissionLevel.UPDATE,
    can_create_rows=True,
    can_delete_rows=False
)

# Set field permission
handler.set_field_permission(
    field=field,
    user=user,
    permission_level=PermissionLevel.READ,
    is_hidden=False
)

# Create conditional permission
handler.create_conditional_permission(
    name="Owner Access",
    table=table,
    condition_field=owner_field,
    condition_operator="equals",
    condition_value=str(user.id),
    user=user,
    granted_permission_level=PermissionLevel.DELETE
)
```

### Checking Permissions

```python
# Check table permission
has_permission = handler.check_table_permission(
    user=user,
    table=table,
    operation="update"
)

# Check field permission
can_read_field = handler.check_field_permission(
    user=user,
    field=field,
    operation="read"
)
```

### API Key Management

```python
# Create API key
api_key = handler.create_api_key(
    workspace=workspace,
    name="Integration Key",
    created_by=admin_user,
    can_read=True,
    can_create=False,
    rate_limit_per_minute=100
)

# Set scope
api_key.scope_tables.set([table1, table2])

# Validate API key
validated_key = handler.validate_api_key(api_key.key)
```

## API Endpoints

The system provides REST API endpoints for managing permissions:

- `GET/POST /api/workspaces/{id}/permissions/custom-roles/` - Manage custom roles
- `GET/POST /api/workspaces/{id}/permissions/table-permissions/` - Manage table permissions
- `GET/POST /api/workspaces/{id}/permissions/field-permissions/` - Manage field permissions
- `GET/POST /api/workspaces/{id}/permissions/view-permissions/` - Manage view permissions
- `GET/POST /api/workspaces/{id}/permissions/conditional-permissions/` - Manage conditional permissions
- `GET/POST /api/workspaces/{id}/permissions/api-keys/` - Manage API keys
- `GET /api/workspaces/{id}/permissions/management/user-summary/` - Get user permission summary
- `POST /api/workspaces/{id}/permissions/management/bulk-update/` - Bulk update permissions

## Integration

The granular permission system integrates with Baserow's existing permission framework through the `GranularPermissionManagerType` class, which is registered with the permission manager registry.

### Permission Manager Integration

The system implements the `PermissionManagerType` interface and handles operations like:
- `check_multiple_permissions()`: Check multiple permissions at once
- `filter_queryset()`: Filter querysets based on permissions
- `get_permissions_object()`: Get permissions for frontend use

### Database Integration

The system uses Django's permission framework and integrates with Baserow's existing models:
- Extends workspace permissions
- Works with existing table, field, and view models
- Maintains backward compatibility

## Management Commands

### Initialize Permission System

```bash
python manage.py init_granular_permissions --create-default-roles
```

This command creates default roles in all workspaces:
- **Editor**: Can create, read, and update data
- **Viewer**: Can only view data
- **Commenter**: Can view data and add comments
- **Table Manager**: Can manage table structure

## Testing

Run the test suite:

```bash
python manage.py test baserow.contrib.database.permissions
```

The test suite covers:
- Custom role creation and management
- Permission setting and checking
- Conditional permission evaluation
- API key management
- Integration with existing permission system

## Security Considerations

- All permissions are checked server-side
- API keys support rate limiting and IP restrictions
- Conditional permissions are evaluated securely
- Audit logging tracks permission changes
- Row-level security prevents unauthorized data access

## Performance

The system is designed for performance:
- Efficient database queries with proper indexing
- Caching of permission evaluations
- Bulk operations for managing multiple permissions
- Optimized queryset filtering

## Migration

When upgrading existing Baserow installations:

1. Run the migration: `python manage.py migrate`
2. Initialize default roles: `python manage.py init_granular_permissions --create-default-roles`
3. Configure permissions as needed through the API or admin interface

The system maintains backward compatibility with existing workspace permissions.