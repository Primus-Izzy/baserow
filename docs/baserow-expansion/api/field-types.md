# Field Types API Documentation

This document covers the API endpoints for all new field types introduced in the Baserow expansion.

## Progress Bar Field

### Create Progress Bar Field

```http
POST /api/database/fields/
```

**Request Body:**
```json
{
  "type": "progress_bar",
  "name": "Task Progress",
  "table_id": 123,
  "progress_bar_source_type": "numeric_field",
  "progress_bar_source_field_id": 456,
  "progress_bar_min_value": 0,
  "progress_bar_max_value": 100,
  "progress_bar_color_scheme": "blue_to_green",
  "progress_bar_show_percentage": true
}
```

**Response:**
```json
{
  "id": 789,
  "type": "progress_bar",
  "name": "Task Progress",
  "table_id": 123,
  "progress_bar_source_type": "numeric_field",
  "progress_bar_source_field_id": 456,
  "progress_bar_min_value": 0,
  "progress_bar_max_value": 100,
  "progress_bar_color_scheme": "blue_to_green",
  "progress_bar_show_percentage": true,
  "created_on": "2024-01-15T10:30:00Z",
  "updated_on": "2024-01-15T10:30:00Z"
}
```

### Progress Bar Field Configuration Options

| Parameter | Type | Description |
|-----------|------|-------------|
| `progress_bar_source_type` | string | Source of progress value: `numeric_field`, `formula`, `manual` |
| `progress_bar_source_field_id` | integer | ID of source field (if source_type is `numeric_field`) |
| `progress_bar_formula` | string | Formula expression (if source_type is `formula`) |
| `progress_bar_min_value` | number | Minimum value for progress calculation |
| `progress_bar_max_value` | number | Maximum value for progress calculation |
| `progress_bar_color_scheme` | string | Color scheme: `blue`, `green`, `red`, `blue_to_green`, `red_to_green` |
| `progress_bar_show_percentage` | boolean | Whether to display percentage text |

## People Field

### Create People Field

```http
POST /api/database/fields/
```

**Request Body:**
```json
{
  "type": "people",
  "name": "Assigned To",
  "table_id": 123,
  "people_allow_multiple": true,
  "people_notify_on_change": true,
  "people_restrict_to_workspace": true
}
```

**Response:**
```json
{
  "id": 790,
  "type": "people",
  "name": "Assigned To",
  "table_id": 123,
  "people_allow_multiple": true,
  "people_notify_on_change": true,
  "people_restrict_to_workspace": true,
  "created_on": "2024-01-15T10:30:00Z",
  "updated_on": "2024-01-15T10:30:00Z"
}
```

### People Field Value Format

When setting values for people fields:

**Single User:**
```json
{
  "field_790": {
    "user_id": 123,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "avatar_url": "https://example.com/avatar.jpg"
  }
}
```

**Multiple Users:**
```json
{
  "field_790": [
    {
      "user_id": 123,
      "email": "user1@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "avatar_url": "https://example.com/avatar1.jpg"
    },
    {
      "user_id": 124,
      "email": "user2@example.com",
      "first_name": "Jane",
      "last_name": "Smith",
      "avatar_url": "https://example.com/avatar2.jpg"
    }
  ]
}
```

## Formula Field

### Create Formula Field

```http
POST /api/database/fields/
```

**Request Body:**
```json
{
  "type": "formula",
  "name": "Calculated Total",
  "table_id": 123,
  "formula_expression": "field('Quantity') * field('Price')",
  "formula_result_type": "number"
}
```

**Response:**
```json
{
  "id": 791,
  "type": "formula",
  "name": "Calculated Total",
  "table_id": 123,
  "formula_expression": "field('Quantity') * field('Price')",
  "formula_result_type": "number",
  "formula_dependencies": [456, 457],
  "formula_syntax_valid": true,
  "created_on": "2024-01-15T10:30:00Z",
  "updated_on": "2024-01-15T10:30:00Z"
}
```

### Formula Validation

```http
POST /api/database/fields/formula/validate/
```

**Request Body:**
```json
{
  "expression": "field('Quantity') * field('Price')",
  "table_id": 123
}
```

**Response:**
```json
{
  "valid": true,
  "result_type": "number",
  "dependencies": [456, 457],
  "errors": []
}
```

### Available Formula Functions

| Function | Description | Example |
|----------|-------------|---------|
| `field('name')` | Reference another field | `field('Price')` |
| `sum(field1, field2, ...)` | Sum multiple values | `sum(field('A'), field('B'))` |
| `avg(field1, field2, ...)` | Average of values | `avg(field('Score1'), field('Score2'))` |
| `min(field1, field2, ...)` | Minimum value | `min(field('Start'), field('End'))` |
| `max(field1, field2, ...)` | Maximum value | `max(field('High'), field('Low'))` |
| `if(condition, true_value, false_value)` | Conditional logic | `if(field('Status') = 'Done', 100, 0)` |
| `concat(text1, text2, ...)` | Concatenate text | `concat(field('First'), ' ', field('Last'))` |
| `len(text)` | Text length | `len(field('Description'))` |
| `upper(text)` | Uppercase text | `upper(field('Name'))` |
| `lower(text)` | Lowercase text | `lower(field('Email'))` |
| `round(number, decimals)` | Round number | `round(field('Price'), 2)` |
| `now()` | Current date/time | `now()` |
| `today()` | Current date | `today()` |

## Rollup Field

### Create Rollup Field

```http
POST /api/database/fields/
```

**Request Body:**
```json
{
  "type": "rollup",
  "name": "Total Orders",
  "table_id": 123,
  "rollup_linked_field_id": 456,
  "rollup_target_field_id": 789,
  "rollup_function": "sum"
}
```

**Response:**
```json
{
  "id": 792,
  "type": "rollup",
  "name": "Total Orders",
  "table_id": 123,
  "rollup_linked_field_id": 456,
  "rollup_target_field_id": 789,
  "rollup_function": "sum",
  "rollup_result_type": "number",
  "created_on": "2024-01-15T10:30:00Z",
  "updated_on": "2024-01-15T10:30:00Z"
}
```

### Rollup Functions

| Function | Description | Compatible Field Types |
|----------|-------------|------------------------|
| `sum` | Sum of all values | Number, Currency, Rating |
| `avg` | Average of all values | Number, Currency, Rating |
| `count` | Count of non-empty values | All types |
| `count_unique` | Count of unique values | All types |
| `min` | Minimum value | Number, Currency, Date, Rating |
| `max` | Maximum value | Number, Currency, Date, Rating |
| `concat` | Concatenate all values | Text, Long Text, Email, URL |
| `first` | First value | All types |
| `last` | Last value | All types |

## Lookup Field

### Create Lookup Field

```http
POST /api/database/fields/
```

**Request Body:**
```json
{
  "type": "lookup",
  "name": "Customer Name",
  "table_id": 123,
  "lookup_linked_field_id": 456,
  "lookup_target_field_id": 789
}
```

**Response:**
```json
{
  "id": 793,
  "type": "lookup",
  "name": "Customer Name",
  "table_id": 123,
  "lookup_linked_field_id": 456,
  "lookup_target_field_id": 789,
  "lookup_result_type": "text",
  "created_on": "2024-01-15T10:30:00Z",
  "updated_on": "2024-01-15T10:30:00Z"
}
```

## Field Type Validation

All field types support validation during creation and updates:

### Validation Response Format

```json
{
  "valid": true,
  "errors": {
    "field_name": ["Field name is required"],
    "formula_expression": ["Invalid formula syntax"]
  },
  "warnings": {
    "performance": ["This formula may be slow with large datasets"]
  }
}
```

## Common Field Operations

### Update Field Configuration

```http
PATCH /api/database/fields/{field_id}/
```

### Delete Field

```http
DELETE /api/database/fields/{field_id}/
```

### Get Field Dependencies

```http
GET /api/database/fields/{field_id}/dependencies/
```

**Response:**
```json
{
  "dependencies": [
    {
      "field_id": 456,
      "field_name": "Source Field",
      "dependency_type": "direct"
    }
  ],
  "dependents": [
    {
      "field_id": 789,
      "field_name": "Dependent Field",
      "dependency_type": "formula"
    }
  ]
}
```