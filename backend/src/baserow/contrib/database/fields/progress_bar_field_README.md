# Progress Bar Field Implementation

## Overview

The Progress Bar field type provides visual progress indicators based on numeric values. It supports three different source types for calculating progress values:

1. **Manual Input**: Users can directly enter numeric values
2. **Field Reference**: Progress is calculated from another numeric field in the same table
3. **Formula Calculation**: Progress is calculated using a formula expression (future enhancement)

## Features

### Source Configuration
- **Manual**: Direct numeric input by users
- **Field**: Links to another numeric field for automatic calculation
- **Formula**: Uses formula expressions for complex calculations

### Range Configuration
- Configurable minimum and maximum values for progress calculation
- Automatic percentage calculation based on the range
- Value clamping to ensure values stay within the defined range

### Display Configuration
- Toggle percentage text display on/off
- Multiple color schemes: Default (blue), Success (green), Warning (yellow), Danger (red), Custom
- Custom gradient colors with start and end color configuration

### Color Schemes
- **Default**: Blue gradient (#3b82f6 to #1d4ed8)
- **Success**: Green gradient for completed tasks
- **Warning**: Yellow gradient for in-progress items
- **Danger**: Red gradient for overdue or critical items
- **Custom**: User-defined gradient with custom start and end colors

## Database Schema

The `ProgressBarField` model extends the base `Field` model with the following additional fields:

```python
source_type = CharField(choices=['manual', 'field', 'formula'], default='manual')
source_field = ForeignKey(Field, null=True, blank=True)
source_formula = TextField(blank=True, default='')
min_value = DecimalField(max_digits=10, decimal_places=2, default=0)
max_value = DecimalField(max_digits=10, decimal_places=2, default=100)
show_percentage = BooleanField(default=True)
color_scheme = CharField(choices=[...], default='default')
custom_color_start = CharField(max_length=7, default='#3b82f6')
custom_color_end = CharField(max_length=7, default='#1d4ed8')
```

## API Integration

The field type integrates with Baserow's existing API system through:

- **Field Type Registry**: Registered as 'progress_bar' type
- **Serialization**: Automatic serialization through the polymorphic field system
- **Validation**: Built-in validation for numeric values and configuration
- **Export/Import**: Support for CSV and JSON export/import

## Usage Examples

### Manual Input Field
```json
{
  "type": "progress_bar",
  "name": "Task Progress",
  "source_type": "manual",
  "min_value": 0,
  "max_value": 100,
  "show_percentage": true,
  "color_scheme": "success"
}
```

### Field Reference
```json
{
  "type": "progress_bar",
  "name": "Completion Rate",
  "source_type": "field",
  "source_field": 123,
  "min_value": 0,
  "max_value": 10,
  "show_percentage": true,
  "color_scheme": "default"
}
```

### Custom Colors
```json
{
  "type": "progress_bar",
  "name": "Custom Progress",
  "source_type": "manual",
  "color_scheme": "custom",
  "custom_color_start": "#ff6b6b",
  "custom_color_end": "#ee5a24"
}
```

## Implementation Details

### Value Calculation
- Manual values are validated and stored directly
- Field references calculate percentage based on the source field value
- Formula calculations are prepared for future implementation
- All values are clamped to the min/max range

### Percentage Calculation
```python
def _calculate_percentage(self, instance, value):
    if instance.min_value >= instance.max_value:
        return Decimal('0')
    
    # Clamp value to range
    value = max(instance.min_value, min(instance.max_value, value))
    
    # Calculate percentage
    range_size = instance.max_value - instance.min_value
    progress = (value - instance.min_value) / range_size * 100
    
    return round(progress, 2)
```

### Export Formats
- **Simple**: String representation of the percentage value
- **Rich**: JSON object with value, percentage, color scheme, and display settings

## Future Enhancements

1. **Formula Integration**: Full integration with Baserow's formula engine
2. **Advanced Color Rules**: Conditional coloring based on value ranges
3. **Animation Support**: Smooth progress bar animations
4. **Custom Formatting**: Additional display formats beyond percentage
5. **Milestone Markers**: Visual indicators for specific progress milestones

## Testing

The implementation includes comprehensive tests covering:
- Field type registration
- Model validation
- Value preparation and calculation
- Percentage calculation with edge cases
- Export value formatting
- Human-readable value display

Run tests with:
```bash
pytest backend/tests/baserow/contrib/database/fields/test_progress_bar_field.py
```