import pytest

from baserow.contrib.database.fields.handler import FieldHandler
from baserow.contrib.database.fields.models import SingleSelectField
from baserow.contrib.database.views.handler import ViewHandler
from baserow.contrib.database.views.models import KanbanView
from baserow.contrib.database.views.kanban_handler import KanbanViewHandler


@pytest.mark.django_db
def test_create_kanban_view(data_fixture):
    """Test creating a Kanban view."""
    user = data_fixture.create_user()
    table = data_fixture.create_table_for_user(user=user)
    
    # Create a single select field for the Kanban columns
    field_handler = FieldHandler()
    single_select_field = field_handler.create_field(
        user=user,
        table=table,
        type_name="single_select",
        name="Status",
    )
    
    # Add some options to the single select field
    data_fixture.create_select_option(
        field=single_select_field,
        value="To Do",
        color="blue",
        order=0,
    )
    data_fixture.create_select_option(
        field=single_select_field,
        value="In Progress",
        color="yellow",
        order=1,
    )
    data_fixture.create_select_option(
        field=single_select_field,
        value="Done",
        color="green",
        order=2,
    )
    
    # Create the Kanban view
    view_handler = ViewHandler()
    kanban_view = view_handler.create_view(
        user=user,
        table=table,
        type_name="kanban",
        name="Kanban View",
        single_select_field=single_select_field,
    )
    
    assert isinstance(kanban_view, KanbanView)
    assert kanban_view.single_select_field == single_select_field
    assert kanban_view.name == "Kanban View"


@pytest.mark.django_db
def test_kanban_view_get_columns(data_fixture):
    """Test getting columns for a Kanban view."""
    user = data_fixture.create_user()
    table = data_fixture.create_table_for_user(user=user)
    
    # Create a single select field
    field_handler = FieldHandler()
    single_select_field = field_handler.create_field(
        user=user,
        table=table,
        type_name="single_select",
        name="Status",
    )
    
    # Add options
    option1 = data_fixture.create_select_option(
        field=single_select_field,
        value="To Do",
        color="blue",
        order=0,
    )
    option2 = data_fixture.create_select_option(
        field=single_select_field,
        value="Done",
        color="green",
        order=1,
    )
    
    # Create Kanban view
    view_handler = ViewHandler()
    kanban_view = view_handler.create_view(
        user=user,
        table=table,
        type_name="kanban",
        name="Kanban View",
        single_select_field=single_select_field,
    )
    
    # Test getting columns
    kanban_handler = KanbanViewHandler()
    columns = kanban_handler.get_kanban_columns(kanban_view)
    
    # Should have 3 columns: null column + 2 options
    assert len(columns) == 3
    
    # Check null column
    null_column = columns[0]
    assert null_column["id"] is None
    assert null_column["value"] is None
    assert null_column["name"] == "No Status"
    
    # Check option columns
    option_columns = columns[1:]
    assert len(option_columns) == 2
    assert option_columns[0]["value"] == "To Do"
    assert option_columns[1]["value"] == "Done"


@pytest.mark.django_db
def test_kanban_view_move_card(data_fixture):
    """Test moving a card between columns."""
    user = data_fixture.create_user()
    table = data_fixture.create_table_for_user(user=user)
    
    # Create a single select field
    field_handler = FieldHandler()
    single_select_field = field_handler.create_field(
        user=user,
        table=table,
        type_name="single_select",
        name="Status",
    )
    
    # Add options
    option1 = data_fixture.create_select_option(
        field=single_select_field,
        value="To Do",
        color="blue",
        order=0,
    )
    option2 = data_fixture.create_select_option(
        field=single_select_field,
        value="Done",
        color="green",
        order=1,
    )
    
    # Create Kanban view
    view_handler = ViewHandler()
    kanban_view = view_handler.create_view(
        user=user,
        table=table,
        type_name="kanban",
        name="Kanban View",
        single_select_field=single_select_field,
    )
    
    # Create a row
    row = data_fixture.create_row_for_table(
        table=table,
        **{f"field_{single_select_field.id}": option1.id}
    )
    
    # Test moving the card
    kanban_handler = KanbanViewHandler()
    result = kanban_handler.move_card(
        user=user,
        kanban_view=kanban_view,
        row_id=row.id,
        to_column_value="Done",
    )
    
    assert result["moved_to_column"] == "Done"
    assert result["target_option_id"] == option2.id
    
    # Verify the row was updated
    updated_row = result["row"]
    field_name = f"field_{single_select_field.id}"
    assert getattr(updated_row, field_name) == option2.id