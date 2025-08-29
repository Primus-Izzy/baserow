# Field Types Architecture

## Field Type System
Baserow's field type system should be extended to support advanced field types while maintaining backward compatibility.

## New Field Types Implementation
Each new field type must implement:
- **Backend Serializer**: Data validation and serialization
- **Database Column**: Appropriate database column type
- **Frontend Component**: Display and editing components
- **API Endpoints**: CRUD operations specific to the field type
- **Export/Import**: CSV and JSON support

## Formula Field Requirements
- **Parser**: Implement robust formula parsing with error handling
- **Evaluator**: Efficient formula evaluation engine
- **Dependencies**: Track field dependencies for recalculation
- **Syntax Highlighting**: Rich text editor with formula syntax support
- **Functions Library**: Comprehensive set of built-in functions

## Linked Records Enhancement
- **Bidirectional Linking**: Automatic reverse relationship creation
- **Display Fields**: Configure which fields show in linked record cells
- **Lookup Performance**: Optimize queries for lookup fields
- **Rollup Calculations**: Efficient aggregation of linked data

## People/Owner Field
- **User Integration**: Link to Baserow user accounts
- **Permissions**: Respect user permissions in field display
- **Notifications**: Integration with notification system
- **Avatar Display**: Show user avatars in cells

## Progress Bar Field
- **Value Sources**: Support numeric fields, formulas, or manual input
- **Customization**: Configurable colors, ranges, and display formats
- **Calculations**: Automatic percentage calculations from related data