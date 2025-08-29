"""
Tests for the People field type implementation.
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from baserow.contrib.database.fields.field_types import PeopleFieldType
from baserow.contrib.database.fields.models import PeopleField
from baserow.core.models import WorkspaceUser

User = get_user_model()


@pytest.mark.django_db
def test_people_field_creation():
    """Test that PeopleField can be created with correct attributes."""
    field = PeopleField(
        name="Test People Field",
        multiple_people=False,
        notify_when_added=True,
        notify_when_removed=False,
        show_avatar=True,
        show_email=False
    )
    
    assert field.name == "Test People Field"
    assert field.multiple_people is False
    assert field.notify_when_added is True
    assert field.notify_when_removed is False
    assert field.show_avatar is True
    assert field.show_email is False


@pytest.mark.django_db
def test_people_field_type_properties():
    """Test that PeopleFieldType has correct properties."""
    field_type = PeopleFieldType()
    
    assert field_type.type == "people"
    assert field_type.model_class == PeopleField
    assert field_type.can_get_unique_values is False
    assert "multiple_people" in field_type.allowed_fields
    assert "notify_when_added" in field_type.allowed_fields
    assert "show_avatar" in field_type.allowed_fields


@pytest.mark.django_db
def test_people_field_type_can_represent_collaborators():
    """Test that PeopleFieldType can represent collaborators."""
    field_type = PeopleFieldType()
    field = PeopleField()
    
    assert field_type.can_represent_collaborators(field) is True


@pytest.mark.django_db
def test_people_field_serializer_help_text():
    """Test that PeopleFieldType provides correct help text."""
    field_type = PeopleFieldType()
    
    # Test single people field
    single_field = PeopleField(multiple_people=False)
    help_text = field_type.get_serializer_help_text(single_field)
    assert "single" in help_text.lower()
    assert "object" in help_text.lower()
    
    # Test multiple people field
    multiple_field = PeopleField(multiple_people=True)
    help_text = field_type.get_serializer_help_text(multiple_field)
    assert "list" in help_text.lower()
    assert "objects" in help_text.lower()


@pytest.mark.django_db
def test_people_field_export_value():
    """Test that PeopleFieldType exports values correctly."""
    field_type = PeopleFieldType()
    
    # Mock user object
    class MockUser:
        def __init__(self, first_name, email):
            self.first_name = first_name
            self.email = email
    
    user = MockUser("John Doe", "john@example.com")
    
    # Test single people field
    single_field = PeopleField(multiple_people=False)
    export_value = field_type.get_export_value(user, single_field, rich_value=False)
    assert export_value == "John Doe <john@example.com>"
    
    export_value_rich = field_type.get_export_value(user, single_field, rich_value=True)
    assert export_value_rich == ["John Doe <john@example.com>"]
    
    # Test multiple people field
    multiple_field = PeopleField(multiple_people=True)
    users = [user, MockUser("Jane Smith", "jane@example.com")]
    
    # Mock the .all() method
    class MockQuerySet:
        def __init__(self, items):
            self.items = items
        def all(self):
            return self.items
    
    users_qs = MockQuerySet(users)
    export_value = field_type.get_export_value(users_qs, multiple_field, rich_value=False)
    assert "John Doe <john@example.com>" in export_value
    assert "Jane Smith <jane@example.com>" in export_value


@pytest.mark.django_db
def test_people_field_human_readable_value():
    """Test that PeopleFieldType provides human readable values."""
    field_type = PeopleFieldType()
    
    # Mock user object
    class MockUser:
        def __init__(self, first_name, email):
            self.first_name = first_name
            self.email = email
    
    user = MockUser("John Doe", "john@example.com")
    
    # Test single people field
    single_field = PeopleField(multiple_people=False)
    readable_value = field_type.get_human_readable_value(user, single_field)
    assert readable_value == "John Doe <john@example.com>"
    
    # Test empty value
    readable_value = field_type.get_human_readable_value(None, single_field)
    assert readable_value == ""


@pytest.mark.django_db
def test_people_field_random_value():
    """Test that PeopleFieldType generates random values for testing."""
    field_type = PeopleFieldType()
    
    # Mock field with workspace
    class MockWorkspace:
        id = 1
    
    class MockDatabase:
        workspace_id = 1
        workspace = MockWorkspace()
    
    class MockTable:
        database = MockDatabase()
    
    # Mock field
    single_field = PeopleField(multiple_people=False)
    single_field.table = MockTable()
    
    multiple_field = PeopleField(multiple_people=True)
    multiple_field.table = MockTable()
    
    # Mock fake object
    class MockFake:
        def random_element(self, elements):
            return elements[0] if elements else None
        
        def random_sample(self, elements, count):
            return elements[:count]
        
        def random_int(self, min_val, max_val):
            return min_val
    
    fake = MockFake()
    
    # Test with no workspace users (should return None/empty list)
    with pytest.mock.patch('baserow.core.models.WorkspaceUser.objects.filter') as mock_filter:
        mock_filter.return_value.values_list.return_value = []
        
        single_value = field_type.random_value(single_field, fake, {})
        assert single_value is None
        
        multiple_value = field_type.random_value(multiple_field, fake, {})
        assert multiple_value == []


if __name__ == "__main__":
    pytest.main([__file__])