# Field Type Development Guide

Learn how to create custom field types for the expanded Baserow platform, extending the database capabilities with new data types and behaviors.

## Overview

Field types in Baserow define how data is stored, validated, displayed, and interacted with. The expansion introduces several new field types and provides a framework for creating custom ones.

### New Field Types in Expansion
- **Progress Bar Field** - Visual progress indicators
- **People Field** - User assignment and collaboration
- **Formula Field** - Calculated values with Excel-like formulas
- **Rollup Field** - Aggregate data from linked records
- **Lookup Field** - Pull data from related tables

## Field Type Architecture

### Backend Components

#### Field Model
Every field type extends the base `Field` model:

```python
from baserow.contrib.database.fields.models import Field

class ProgressBarField(Field):
    # Field-specific configuration
    source_type = models.CharField(max_length=20, default='numeric_field')
    source_field = models.ForeignKey(Field, null=True, blank=True)
    min_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_value = models.DecimalField(max_digits=10, decimal_places=2, default=100)
    color_scheme = models.CharField(max_length=20, default='blue_to_green')
    show_percentage = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'database_progressbarfield'
```

#### Field Type Class
The field type class defines behavior and validation:

```python
from baserow.contrib.database.fields.registries import FieldType
from baserow.contrib.database.fields.models import Field

class ProgressBarFieldType(FieldType):
    type = 'progress_bar'
    model_class = ProgressBarField
    allowed_fields = ['source_type', 'source_field', 'min_value', 'max_value', 'color_scheme', 'show_percentage']
    serializer_field_names = ['source_type', 'source_field_id', 'min_value', 'max_value', 'color_scheme', 'show_percentage']
    
    def get_serializer_field(self, instance, **kwargs):
        """Return the serializer field for API responses."""
        return serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    
    def get_model_field(self, instance, **kwargs):
        """Return the Django model field for database storage."""
        return models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    def prepare_value_for_db(self, instance, value):
        """Prepare value before saving to database."""
        if value is None:
            return None
        return self.calculate_progress_value(instance, value)
    
    def get_serializer_help_text(self, instance):
        """Return help text for API documentation."""
        return "Progress value as percentage (0-100)"
    
    def calculate_progress_value(self, field_instance, context_row):
        """Calculate progress value based on field configuration."""
        if field_instance.source_type == 'numeric_field' and field_instance.source_field:
            source_value = getattr(context_row, f'field_{field_instance.source_field.id}', 0)
            if source_value is None:
                return 0
            
            # Calculate percentage based on min/max values
            progress = ((source_value - field_instance.min_value) / 
                       (field_instance.max_value - field_instance.min_value)) * 100
            return max(0, min(100, progress))
        
        return 0
```

#### Serializer
Define how the field is serialized for API responses:

```python
from rest_framework import serializers
from baserow.api.fields.serializers import FieldSerializer

class ProgressBarFieldSerializer(FieldSerializer):
    source_type = serializers.ChoiceField(
        choices=['numeric_field', 'formula', 'manual'],
        default='numeric_field'
    )
    source_field_id = serializers.IntegerField(required=False, allow_null=True)
    min_value = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_value = serializers.DecimalField(max_digits=10, decimal_places=2, default=100)
    color_scheme = serializers.ChoiceField(
        choices=['blue', 'green', 'red', 'blue_to_green', 'red_to_green'],
        default='blue_to_green'
    )
    show_percentage = serializers.BooleanField(default=True)
    
    class Meta(FieldSerializer.Meta):
        model = ProgressBarField
        fields = FieldSerializer.Meta.fields + (
            'source_type', 'source_field_id', 'min_value', 'max_value', 
            'color_scheme', 'show_percentage'
        )
```

### Frontend Components

#### Field Type Registration
Register the field type in the frontend:

```javascript
// modules/database/fieldTypes.js
import { FieldType } from '@baserow/modules/database/fieldTypes'

export class ProgressBarFieldType extends FieldType {
  static getType() {
    return 'progress_bar'
  }

  getName() {
    return 'Progress Bar'
  }

  getIconClass() {
    return 'fas fa-chart-bar'
  }

  getDescription() {
    return 'Visual progress indicator with customizable ranges and colors'
  }

  getFormComponent() {
    return () => import('@/components/field/ProgressBarFieldForm')
  }

  getGridViewFieldComponent() {
    return () => import('@/components/field/ProgressBarGridViewField')
  }

  getRowEditFieldComponent() {
    return () => import('@/components/field/ProgressBarRowEditField')
  }

  getCardComponent() {
    return () => import('@/components/field/ProgressBarCardField')
  }

  getSort(name, order) {
    return {
      field: name,
      order: order
    }
  }

  getDocsResponseExample(field) {
    return 75.5
  }

  getDocsDescription(field) {
    return 'Progress value as percentage (0-100)'
  }

  prepareValueForCopy(field, value) {
    return value
  }

  prepareValueForPaste(field, clipboardData) {
    const value = parseFloat(clipboardData)
    return isNaN(value) ? null : Math.max(0, Math.min(100, value))
  }
}
```

#### Vue Components

##### Grid View Component
```vue
<template>
  <div class="progress-bar-field">
    <div class="progress-bar-container">
      <div 
        class="progress-bar-fill"
        :style="progressStyle"
        :class="colorClass"
      ></div>
      <span v-if="field.show_percentage" class="progress-text">
        {{ displayValue }}%
      </span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProgressBarGridViewField',
  props: {
    field: {
      type: Object,
      required: true
    },
    value: {
      type: Number,
      default: 0
    }
  },
  computed: {
    displayValue() {
      return this.value ? Math.round(this.value * 10) / 10 : 0
    },
    progressStyle() {
      return {
        width: `${Math.max(0, Math.min(100, this.displayValue))}%`
      }
    },
    colorClass() {
      return `progress-bar-${this.field.color_scheme}`
    }
  }
}
</script>

<style lang="scss" scoped>
.progress-bar-field {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 4px 8px;
}

.progress-bar-container {
  position: relative;
  width: 100%;
  height: 20px;
  background-color: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  transition: width 0.3s ease;
  border-radius: 10px;
  
  &.progress-bar-blue {
    background-color: #3498db;
  }
  
  &.progress-bar-green {
    background-color: #2ecc71;
  }
  
  &.progress-bar-red {
    background-color: #e74c3c;
  }
  
  &.progress-bar-blue_to_green {
    background: linear-gradient(to right, #3498db, #2ecc71);
  }
  
  &.progress-bar-red_to_green {
    background: linear-gradient(to right, #e74c3c, #2ecc71);
  }
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 12px;
  font-weight: bold;
  color: white;
  text-shadow: 1px 1px 1px rgba(0, 0, 0, 0.5);
}
</style>
```

##### Field Configuration Form
```vue
<template>
  <div class="progress-bar-field-form">
    <div class="form-group">
      <label class="control-label">Progress Source</label>
      <Dropdown
        v-model="values.source_type"
        :options="sourceTypeOptions"
        @input="$emit('input', values)"
      />
    </div>

    <div v-if="values.source_type === 'numeric_field'" class="form-group">
      <label class="control-label">Source Field</label>
      <Dropdown
        v-model="values.source_field_id"
        :options="numericFieldOptions"
        @input="$emit('input', values)"
      />
    </div>

    <div class="form-group">
      <label class="control-label">Minimum Value</label>
      <input
        v-model.number="values.min_value"
        type="number"
        class="form-control"
        @input="$emit('input', values)"
      />
    </div>

    <div class="form-group">
      <label class="control-label">Maximum Value</label>
      <input
        v-model.number="values.max_value"
        type="number"
        class="form-control"
        @input="$emit('input', values)"
      />
    </div>

    <div class="form-group">
      <label class="control-label">Color Scheme</label>
      <Dropdown
        v-model="values.color_scheme"
        :options="colorSchemeOptions"
        @input="$emit('input', values)"
      />
    </div>

    <div class="form-group">
      <Checkbox
        v-model="values.show_percentage"
        @input="$emit('input', values)"
      >
        Show percentage text
      </Checkbox>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProgressBarFieldForm',
  props: {
    field: {
      type: Object,
      required: true
    },
    table: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      values: {
        source_type: this.field.source_type || 'numeric_field',
        source_field_id: this.field.source_field_id || null,
        min_value: this.field.min_value || 0,
        max_value: this.field.max_value || 100,
        color_scheme: this.field.color_scheme || 'blue_to_green',
        show_percentage: this.field.show_percentage !== false
      }
    }
  },
  computed: {
    sourceTypeOptions() {
      return [
        { value: 'numeric_field', name: 'Numeric Field' },
        { value: 'formula', name: 'Formula' },
        { value: 'manual', name: 'Manual Entry' }
      ]
    },
    numericFieldOptions() {
      return this.table.fields
        .filter(field => ['number', 'rating'].includes(field.type))
        .map(field => ({ value: field.id, name: field.name }))
    },
    colorSchemeOptions() {
      return [
        { value: 'blue', name: 'Blue' },
        { value: 'green', name: 'Green' },
        { value: 'red', name: 'Red' },
        { value: 'blue_to_green', name: 'Blue to Green' },
        { value: 'red_to_green', name: 'Red to Green' }
      ]
    }
  }
}
</script>
```

## Advanced Field Type Features

### Formula Field Implementation

#### Backend Formula Engine
```python
import ast
import operator
from decimal import Decimal
from datetime import datetime, date

class FormulaEvaluator:
    """Evaluates formula expressions safely."""
    
    ALLOWED_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }
    
    ALLOWED_FUNCTIONS = {
        'sum': sum,
        'min': min,
        'max': max,
        'abs': abs,
        'round': round,
        'len': len,
        'upper': str.upper,
        'lower': str.lower,
        'concat': lambda *args: ''.join(str(arg) for arg in args),
        'if': lambda condition, true_val, false_val: true_val if condition else false_val,
    }
    
    def __init__(self, table, row_data):
        self.table = table
        self.row_data = row_data
        self.field_cache = {}
    
    def evaluate(self, expression):
        """Evaluate a formula expression."""
        try:
            tree = ast.parse(expression, mode='eval')
            return self._eval_node(tree.body)
        except Exception as e:
            raise FormulaError(f"Formula evaluation error: {str(e)}")
    
    def _eval_node(self, node):
        """Recursively evaluate AST nodes."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            return self._get_variable(node.id)
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op = self.ALLOWED_OPERATORS.get(type(node.op))
            if op:
                return op(left, right)
            else:
                raise FormulaError(f"Unsupported operator: {type(node.op)}")
        elif isinstance(node, ast.Call):
            return self._eval_function_call(node)
        else:
            raise FormulaError(f"Unsupported node type: {type(node)}")
    
    def _eval_function_call(self, node):
        """Evaluate function calls."""
        func_name = node.func.id
        if func_name == 'field':
            # Special handling for field() function
            field_name = self._eval_node(node.args[0])
            return self._get_field_value(field_name)
        elif func_name in self.ALLOWED_FUNCTIONS:
            func = self.ALLOWED_FUNCTIONS[func_name]
            args = [self._eval_node(arg) for arg in node.args]
            return func(*args)
        else:
            raise FormulaError(f"Unknown function: {func_name}")
    
    def _get_field_value(self, field_name):
        """Get value from a field by name."""
        if field_name not in self.field_cache:
            field = self.table.fields.filter(name=field_name).first()
            if not field:
                raise FormulaError(f"Field not found: {field_name}")
            self.field_cache[field_name] = field
        
        field = self.field_cache[field_name]
        return getattr(self.row_data, f'field_{field.id}', None)
```

### Linked Record Field Enhancements

#### Bidirectional Linking
```python
class LinkRowFieldType(FieldType):
    def after_create(self, field, model, user, connection, before):
        """Create reverse relationship after field creation."""
        super().after_create(field, model, user, connection, before)
        
        if field.link_row_table and not field.reverse_field:
            # Create reverse field in linked table
            reverse_field = self.create_reverse_field(field, user)
            field.reverse_field = reverse_field
            field.save()
    
    def create_reverse_field(self, field, user):
        """Create the reverse relationship field."""
        reverse_field_name = f"{field.table.name} ({field.name})"
        
        reverse_field = LinkRowField.objects.create(
            table=field.link_row_table,
            name=reverse_field_name,
            link_row_table=field.table,
            reverse_field=field,
            created_by=user
        )
        
        return reverse_field
    
    def update_linked_records(self, field, row, new_values, old_values):
        """Update bidirectional relationships."""
        if not field.reverse_field:
            return
        
        # Handle removed relationships
        removed_ids = set(old_values or []) - set(new_values or [])
        for removed_id in removed_ids:
            self.remove_reverse_link(field, row.id, removed_id)
        
        # Handle added relationships
        added_ids = set(new_values or []) - set(old_values or [])
        for added_id in added_ids:
            self.add_reverse_link(field, row.id, added_id)
    
    def add_reverse_link(self, field, from_row_id, to_row_id):
        """Add reverse relationship link."""
        reverse_field = field.reverse_field
        reverse_row = reverse_field.table.get_model().objects.get(id=to_row_id)
        
        current_links = getattr(reverse_row, f'field_{reverse_field.id}') or []
        if from_row_id not in current_links:
            current_links.append(from_row_id)
            setattr(reverse_row, f'field_{reverse_field.id}', current_links)
            reverse_row.save()
```

## Testing Field Types

### Backend Tests
```python
from django.test import TestCase
from baserow.contrib.database.fields.models import ProgressBarField
from baserow.contrib.database.fields.handler import FieldHandler

class TestProgressBarField(TestCase):
    def setUp(self):
        self.user = self.create_user()
        self.table = self.create_table_for_user(self.user)
        self.numeric_field = self.create_number_field(self.table)
        
    def test_create_progress_bar_field(self):
        """Test creating a progress bar field."""
        field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='progress_bar',
            name='Task Progress',
            source_type='numeric_field',
            source_field_id=self.numeric_field.id,
            min_value=0,
            max_value=100
        )
        
        self.assertIsInstance(field, ProgressBarField)
        self.assertEqual(field.source_type, 'numeric_field')
        self.assertEqual(field.source_field_id, self.numeric_field.id)
    
    def test_progress_calculation(self):
        """Test progress value calculation."""
        field = self.create_progress_bar_field(
            table=self.table,
            source_field=self.numeric_field,
            min_value=0,
            max_value=100
        )
        
        row = self.create_row_for_table(self.table, {
            f'field_{self.numeric_field.id}': 75
        })
        
        field_type = field.get_field_type()
        progress = field_type.calculate_progress_value(field, row)
        self.assertEqual(progress, 75.0)
    
    def test_field_validation(self):
        """Test field configuration validation."""
        with self.assertRaises(ValidationError):
            self.create_progress_bar_field(
                table=self.table,
                min_value=100,
                max_value=0  # Invalid: max < min
            )
```

### Frontend Tests
```javascript
import { mount } from '@vue/test-utils'
import ProgressBarGridViewField from '@/components/field/ProgressBarGridViewField'

describe('ProgressBarGridViewField', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(ProgressBarGridViewField, {
      propsData: {
        field: {
          id: 1,
          name: 'Progress',
          type: 'progress_bar',
          color_scheme: 'blue_to_green',
          show_percentage: true
        },
        value: 75.5
      }
    })
  })

  test('renders progress bar correctly', () => {
    expect(wrapper.find('.progress-bar-field').exists()).toBe(true)
    expect(wrapper.find('.progress-bar-fill').exists()).toBe(true)
  })

  test('displays correct percentage', () => {
    expect(wrapper.find('.progress-text').text()).toBe('75.5%')
  })

  test('applies correct color scheme', () => {
    expect(wrapper.find('.progress-bar-fill').classes()).toContain('progress-bar-blue_to_green')
  })

  test('handles null values', async () => {
    await wrapper.setProps({ value: null })
    expect(wrapper.find('.progress-text').text()).toBe('0%')
  })
})
```

## Field Type Registration

### Backend Registration
```python
# In your app's ready() method
from baserow.contrib.database.fields.registries import field_type_registry

def ready(self):
    from .field_types import ProgressBarFieldType, PeopleFieldType, FormulaFieldType
    
    field_type_registry.register(ProgressBarFieldType())
    field_type_registry.register(PeopleFieldType())
    field_type_registry.register(FormulaFieldType())
```

### Frontend Registration
```javascript
// In your module's index.js
import { FieldTypeRegistry } from '@baserow/modules/database/fieldTypes'
import { ProgressBarFieldType, PeopleFieldType, FormulaFieldType } from './fieldTypes'

export default (context) => {
  const { app } = context
  
  app.$registry.register('field', new ProgressBarFieldType(context))
  app.$registry.register('field', new PeopleFieldType(context))
  app.$registry.register('field', new FormulaFieldType(context))
}
```

## Best Practices

### Performance Optimization
- **Lazy Loading**: Load field components only when needed
- **Efficient Queries**: Optimize database queries for field calculations
- **Caching**: Cache calculated values when appropriate
- **Batch Operations**: Process multiple field updates together

### User Experience
- **Clear Validation**: Provide clear error messages for invalid configurations
- **Progressive Enhancement**: Ensure basic functionality works without JavaScript
- **Accessibility**: Support screen readers and keyboard navigation
- **Mobile Optimization**: Ensure fields work well on mobile devices

### Code Quality
- **Type Safety**: Use TypeScript for frontend components
- **Error Handling**: Handle edge cases gracefully
- **Documentation**: Document field type behavior and configuration
- **Testing**: Comprehensive test coverage for all field functionality

This guide provides the foundation for creating powerful, custom field types that integrate seamlessly with the expanded Baserow platform.