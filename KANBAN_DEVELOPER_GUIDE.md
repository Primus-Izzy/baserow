# Kanban View Developer Guide

## 🎯 Quick Start

### Creating a Kanban View
```python
from baserow.contrib.database.views.handler import ViewHandler
from baserow.contrib.database.fields.handler import FieldHandler

# Create a single select field for columns
field_handler = FieldHandler()
status_field = field_handler.create_field(
    user=user,
    table=table,
    type_name="single_select",
    name="Status",
)

# Add select options
data_fixture.create_select_option(field=status_field, value="To Do", color="blue")
data_fixture.create_select_option(field=status_field, value="In Progress", color="yellow")
data_fixture.create_select_option(field=status_field, value="Done", color="green")

# Create Kanban view
view_handler = ViewHandler()
kanban_view = view_handler.create_view(
    user=user,
    table=table,
    type_name="kanban",
    name="Project Board",
    single_select_field=status_field,
)
```

### Moving Cards Between Columns
```python
from baserow.contrib.database.views.kanban_handler import KanbanViewHandler

kanban_handler = KanbanViewHandler()
result = kanban_handler.move_card(
    user=user,
    kanban_view=kanban_view,
    row_id=123,
    to_column_value="In Progress",
)
```

### Getting Column Information
```python
columns = kanban_handler.get_kanban_columns(kanban_view)
# Returns: [
#   {"id": None, "value": None, "name": "No Status", "color": "#E0E0E0", "order": -1},
#   {"id": 1, "value": "To Do", "name": "To Do", "color": "blue", "order": 0},
#   {"id": 2, "value": "In Progress", "name": "In Progress", "color": "yellow", "order": 1},
#   {"id": 3, "value": "Done", "name": "Done", "color": "green", "order": 2}
# ]
```

## 🔧 API Usage

### List Kanban Rows
```http
GET /api/database/views/kanban/123/?include=field_options
```

### Move a Card
```http
PATCH /api/database/views/kanban/123/move-card/
Content-Type: application/json

{
  "row_id": 456,
  "to_column_value": "Done",
  "before_row_id": null
}
```

### Get Available Columns
```http
GET /api/database/views/kanban/123/columns/
```

## 🎨 Customization

### Card Configuration
```python
# Update card display settings
kanban_handler.update_card_configuration(
    user=user,
    kanban_view=kanban_view,
    configuration={
        "show_cover_image": True,
        "compact_mode": False,
        "show_field_names": True,
        "max_fields_visible": 5
    }
)
```

### Column Configuration
```python
# Update column behavior
kanban_handler.update_column_configuration(
    user=user,
    kanban_view=kanban_view,
    configuration={
        "allow_empty_column": True,
        "column_width": "auto",
        "show_card_count": True
    }
)
```

### Field Options for Cards
```python
from baserow.contrib.database.views.models import KanbanViewFieldOptions

# Configure which fields show on cards
field_option = KanbanViewFieldOptions.objects.get(
    kanban_view=kanban_view,
    field=some_field
)
field_option.show_in_card = True
field_option.card_display_style = "compact"
field_option.order = 1
field_option.save()
```

## 🧪 Testing

### Unit Tests
```python
import pytest
from baserow.contrib.database.views.models import KanbanView
from baserow.contrib.database.views.kanban_handler import KanbanViewHandler

@pytest.mark.django_db
def test_kanban_card_movement(data_fixture):
    # Test setup
    user = data_fixture.create_user()
    table = data_fixture.create_table_for_user(user=user)
    
    # Create kanban view with single select field
    # ... setup code ...
    
    # Test card movement
    result = kanban_handler.move_card(
        user=user,
        kanban_view=kanban_view,
        row_id=row.id,
        to_column_value="Done"
    )
    
    assert result["moved_to_column"] == "Done"
```

### API Tests
```python
def test_kanban_move_card_api(api_client, data_fixture):
    user, token = data_fixture.create_user_and_token()
    kanban_view = data_fixture.create_kanban_view(user=user)
    
    response = api_client.patch(
        f"/api/database/views/kanban/{kanban_view.id}/move-card/",
        {"row_id": 123, "to_column_value": "Done"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}"
    )
    
    assert response.status_code == 200
```

## 🔍 Debugging

### Common Issues

1. **Single Select Field Not Set**
   ```python
   if not kanban_view.single_select_field:
       raise ValueError("Kanban view must have a single select field configured")
   ```

2. **Invalid Column Value**
   ```python
   try:
       option = SelectOption.objects.get(
           field=kanban_view.single_select_field,
           value=column_value
       )
   except SelectOption.DoesNotExist:
       raise ValueError(f"Column option '{column_value}' does not exist")
   ```

3. **Permission Issues**
   ```python
   CoreHandler().check_permissions(
       user,
       ListRowsDatabaseTableOperationType.type,
       workspace=kanban_view.table.database.workspace,
       context=kanban_view.table,
   )
   ```

### Logging
```python
import logging
logger = logging.getLogger(__name__)

def move_card(self, user, kanban_view, row_id, to_column_value):
    logger.info(f"Moving card {row_id} to column '{to_column_value}'")
    # ... implementation ...
    logger.info(f"Card moved successfully")
```

## 🚀 Performance Tips

1. **Batch Operations**: Use bulk updates for multiple card moves
2. **Caching**: Cache column information for frequently accessed views
3. **Pagination**: Implement pagination for large card sets
4. **Indexing**: Ensure proper database indexes on single select fields

## 🔧 Extension Points

### Custom Card Renderers
```python
class CustomKanbanViewType(KanbanViewType):
    def get_card_renderer(self, view, field):
        if field.type == "custom_field":
            return CustomCardRenderer()
        return super().get_card_renderer(view, field)
```

### Custom Column Behaviors
```python
class CustomKanbanViewHandler(KanbanViewHandler):
    def get_kanban_columns(self, kanban_view):
        columns = super().get_kanban_columns(kanban_view)
        # Add custom column logic
        return self.enhance_columns(columns)
```

This guide provides everything needed to work with, extend, and debug the Kanban view backend implementation.