import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError

from baserow.contrib.database.fields.models import ProgressBarField
from baserow.contrib.database.fields.field_types import ProgressBarFieldType
from baserow.contrib.database.fields.registries import field_type_registry


@pytest.mark.django_db
def test_progress_bar_field_type_registered():
    """Test that the ProgressBarFieldType is properly registered."""
    field_type = field_type_registry.get("progress_bar")
    assert isinstance(field_type, ProgressBarFieldType)
    assert field_type.model_class == ProgressBarField


@pytest.mark.django_db
def test_progress_bar_field_model_validation():
    """Test ProgressBarField model validation."""
    # Test valid field creation
    field = ProgressBarField(
        source_type='manual',
        min_value=Decimal('0'),
        max_value=Decimal('100'),
        show_percentage=True,
        color_scheme='default'
    )
    # Should not raise an exception
    field.save = lambda *args, **kwargs: None  # Mock save to avoid DB operations
    
    # Test invalid min/max values
    field.min_value = Decimal('100')
    field.max_value = Decimal('50')
    with pytest.raises(ValueError, match="Minimum value must be less than maximum value"):
        field.save()


def test_progress_bar_field_type_prepare_value_for_db():
    """Test value preparation for database storage."""
    field_type = ProgressBarFieldType()
    
    # Create a mock field instance
    class MockField:
        id = 1
        source_type = 'manual'
        min_value = Decimal('0')
        max_value = Decimal('100')
    
    field_instance = MockField()
    
    # Test valid numeric value
    result = field_type.prepare_value_for_db(field_instance, "50.5")
    assert result == Decimal("50.5")
    
    # Test None value
    result = field_type.prepare_value_for_db(field_instance, None)
    assert result is None
    
    # Test invalid value
    with pytest.raises(ValidationError):
        field_type.prepare_value_for_db(field_instance, "invalid")


def test_progress_bar_field_type_calculate_percentage():
    """Test percentage calculation."""
    field_type = ProgressBarFieldType()
    
    # Create a mock field instance
    class MockField:
        min_value = Decimal('0')
        max_value = Decimal('100')
    
    field_instance = MockField()
    
    # Test normal calculation
    result = field_type._calculate_percentage(field_instance, Decimal('50'))
    assert result == Decimal('50.00')
    
    # Test value at minimum
    result = field_type._calculate_percentage(field_instance, Decimal('0'))
    assert result == Decimal('0.00')
    
    # Test value at maximum
    result = field_type._calculate_percentage(field_instance, Decimal('100'))
    assert result == Decimal('100.00')
    
    # Test value below minimum (should be clamped)
    result = field_type._calculate_percentage(field_instance, Decimal('-10'))
    assert result == Decimal('0.00')
    
    # Test value above maximum (should be clamped)
    result = field_type._calculate_percentage(field_instance, Decimal('150'))
    assert result == Decimal('100.00')


def test_progress_bar_field_type_get_human_readable_value():
    """Test human readable value formatting."""
    field_type = ProgressBarFieldType()
    
    # Test with percentage display
    field_object = {"show_percentage": True}
    result = field_type.get_human_readable_value(Decimal('75.5'), field_object)
    assert result == "75.5%"
    
    # Test without percentage display
    field_object = {"show_percentage": False}
    result = field_type.get_human_readable_value(Decimal('75.5'), field_object)
    assert result == "75.5"
    
    # Test with None value
    result = field_type.get_human_readable_value(None, field_object)
    assert result == ""


def test_progress_bar_field_type_get_export_value():
    """Test export value formatting."""
    field_type = ProgressBarFieldType()
    
    # Test simple export
    result = field_type.get_export_value(Decimal('75.5'), {}, rich_value=False)
    assert result == "75.5"
    
    # Test rich export
    field_object = {
        "color_scheme": "success",
        "show_percentage": True
    }
    result = field_type.get_export_value(Decimal('75.5'), field_object, rich_value=True)
    expected = {
        "value": 75.5,
        "percentage": 75.5,
        "color_scheme": "success",
        "show_percentage": True
    }
    assert result == expected
    
    # Test None value
    result = field_type.get_export_value(None, {}, rich_value=False)
    assert result == ""
    
    result = field_type.get_export_value(None, {}, rich_value=True)
    assert result is None