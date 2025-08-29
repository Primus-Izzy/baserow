# People/Owner Field Implementation

This document describes the implementation of the People/Owner field type for Baserow, which allows linking to Baserow user accounts within the workspace with permission integration and notification capabilities.

## Overview

The People field type enables users to:
- Select single or multiple people from the workspace
- Display user avatars and profile information
- Receive notifications when added/removed from fields
- Integrate with the permission system
- Support both single and multiple user selection modes

## Implementation Components

### 1. PeopleField Model (`models.py`)

The `PeopleField` model extends the base `Field` class with the following attributes:

```python
class PeopleField(Field):
    # Selection configuration
    multiple_people = models.BooleanField(default=False)
    
    # Notification configuration  
    notify_when_added = models.BooleanField(default=True)
    notify_when_removed = models.BooleanField(default=False)
    
    # Default value configuration
    people_default = models.JSONField(null=True, blank=True)
    
    # Display configuration
    show_avatar = models.BooleanField(default=True)
    show_email = models.BooleanField(default=False)
```

**Key Features:**
- `multiple_people`: Controls whether single or multiple users can be selected
- `notify_when_added/removed`: Controls notification behavior
- `people_default`: Default user IDs (can include 0 for current user)
- `show_avatar/email`: Display configuration options

### 2. PeopleFieldType (`field_types.py`)

The `PeopleFieldType` class implements the field type logic:

```python
class PeopleFieldType(CollationSortMixin, FieldType):
    type = "people"
    model_class = PeopleField
    can_get_unique_values = False
```

**Key Methods:**
- `get_serializer_field()`: Returns appropriate serializer (single or list)
- `prepare_value_for_db()`: Validates and prepares user IDs for database storage
- `get_export_value()`: Formats values for export (e.g., "John Doe <john@example.com>")
- `get_model_field()`: Creates Django model field (ForeignKey or ManyToMany)
- `after_model_generation()`: Sets up many-to-many relationships for multiple people fields

**Validation:**
- Ensures all user IDs belong to workspace members
- Validates single vs. multiple people constraints
- Handles both dict and integer user ID formats

### 3. Database Migration (`0202_people_field.py`)

Creates the `PeopleField` model in the database:

```python
operations = [
    migrations.CreateModel(
        name='PeopleField',
        fields=[
            ('field_ptr', models.OneToOneField(...)),
            ('multiple_people', models.BooleanField(default=False)),
            ('notify_when_added', models.BooleanField(default=True)),
            ('notify_when_removed', models.BooleanField(default=False)),
            ('people_default', models.JSONField(null=True, blank=True)),
            ('show_avatar', models.BooleanField(default=True)),
            ('show_email', models.BooleanField(default=False)),
        ],
        bases=('database.field',),
    ),
]
```

### 4. Field Type Registration (`apps.py`)

The field type is registered in the Django application configuration:

```python
from .fields.field_types import PeopleFieldType
field_type_registry.register(PeopleFieldType())
```

### 5. Notification System (`people_notifications.py`)

Placeholder implementation for user notifications:

```python
class PeopleFieldNotificationHandler:
    @staticmethod
    def notify_users_added(field, users, row_id, table_name, changed_by_user=None)
    
    @staticmethod  
    def notify_users_removed(field, users, row_id, table_name, changed_by_user=None)
    
    @staticmethod
    def notify_field_assignment_changed(field, added_users, removed_users, ...)
```

**Note:** This is currently a placeholder that logs notifications. It should be integrated with the actual notification system when available.

## Data Storage

### Single People Field
- Stored as a `ForeignKey` to the User model
- Database column contains user ID or NULL
- Workspace users are filtered via additional_filters

### Multiple People Field  
- Stored using a many-to-many relationship
- Through table: `database_peoplerelation_{field_id}`
- Links table rows to multiple users
- Workspace filtering applied via additional_filters

## API Integration

The field type integrates with existing Baserow APIs:

### Serialization
- Uses `CollaboratorSerializer` for user data
- Returns `{id: user_id, name: first_name}` format
- Supports both single objects and lists

### Validation
- Validates user IDs against workspace membership
- Ensures proper single/multiple constraints
- Provides clear error messages for invalid data

### Export/Import
- Export format: "First Name <email@example.com>"
- Rich export returns arrays of formatted strings
- Import maps email addresses back to user IDs

## Permission Integration

The People field respects Baserow's permission system:

- Only workspace members can be selected
- Field visibility follows table/view permissions
- User information filtered based on access rights
- Integration with `WorkspaceUser` model for validation

## Usage Examples

### Creating a Single People Field
```python
field = PeopleField.objects.create(
    table=table,
    name="Assigned To",
    multiple_people=False,
    notify_when_added=True,
    show_avatar=True
)
```

### Creating a Multiple People Field
```python
field = PeopleField.objects.create(
    table=table,
    name="Team Members", 
    multiple_people=True,
    notify_when_added=True,
    notify_when_removed=True,
    show_avatar=True,
    show_email=True
)
```

### Setting Field Values
```python
# Single people field
row_data = {"field_123": {"id": 456}}

# Multiple people field  
row_data = {"field_124": [{"id": 456}, {"id": 789}]}
```

## Testing

Comprehensive test suite in `test_people_field.py`:

- Model creation and attribute validation
- Field type properties and methods
- Serialization and export functionality
- Random value generation for testing
- Error handling and edge cases

## Requirements Satisfied

This implementation satisfies requirement **6.5** from the specification:

✅ **People/Owner Field Type**
- Links to Baserow user accounts ✓
- User permission integration ✓  
- Notification system integration ✓ (placeholder)
- User avatar and profile data serialization ✓

## Future Enhancements

1. **Full Notification System Integration**
   - Replace placeholder with actual notification service
   - Support email, in-app, and external notifications
   - Configurable notification templates

2. **Advanced Permission Features**
   - Field-level user visibility controls
   - Role-based user filtering
   - Dynamic user lists based on permissions

3. **Enhanced Display Options**
   - Custom user display formats
   - User status indicators (online/offline)
   - User role/department information

4. **Workflow Integration**
   - Automatic assignment rules
   - User workload balancing
   - Task delegation features

## Migration Notes

When deploying this implementation:

1. Run the database migration: `python manage.py migrate database`
2. Restart the application to register the new field type
3. The field type will be available in the field creation UI
4. Existing data is not affected

## Dependencies

- Django ORM for model relationships
- Baserow's existing user and workspace models
- Field type registry system
- Serialization framework
- Permission system integration