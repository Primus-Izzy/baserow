# Enhanced Table View User Guide

The enhanced table view in Baserow provides powerful features for managing and visualizing your data with improved editing capabilities, advanced formatting, and better organization tools.

## Overview

The enhanced table view builds upon Baserow's core table functionality with these key improvements:

- **Sticky Headers** - Column headers remain visible while scrolling
- **Conditional Formatting** - Color-code rows and cells based on data values
- **Column Grouping** - Organize related columns together
- **Enhanced Inline Editing** - Rich editing options for different field types
- **Filter Presets** - Save and reuse common filter configurations
- **Formula Syntax Highlighting** - Better formula editing experience

## Sticky Headers

### What are Sticky Headers?

Sticky headers keep your column labels visible at the top of the screen when scrolling through large datasets, making it easier to understand what data you're viewing.

### How to Use Sticky Headers

Sticky headers are automatically enabled in all table views. As you scroll down through your data:

1. Column headers will remain fixed at the top of the view
2. You can still interact with header controls (sorting, filtering, etc.)
3. The sticky behavior works with both vertical scrolling and column grouping

### Benefits

- **Better Navigation** - Always know which column you're viewing
- **Improved Productivity** - No need to scroll back to see column names
- **Enhanced User Experience** - Seamless data browsing

## Conditional Formatting

### Setting Up Conditional Formatting

Conditional formatting allows you to automatically color-code rows and cells based on field values and custom conditions.

#### Creating Formatting Rules

1. **Access Formatting Options**
   - Click the view settings menu (three dots) in the top right
   - Select "Conditional Formatting"

2. **Create a New Rule**
   - Click "Add Rule"
   - Choose the field to base the condition on
   - Set the condition (equals, greater than, contains, etc.)
   - Choose the formatting style (background color, text color, etc.)

3. **Rule Examples**
   ```
   Rule 1: Status = "Complete" → Green background
   Rule 2: Priority = "High" → Red text
   Rule 3: Due Date < Today → Yellow background
   Rule 4: Progress > 80% → Bold text
   ```

#### Advanced Conditions

- **Multiple Conditions** - Combine conditions with AND/OR logic
- **Date-based Rules** - Format based on relative dates (overdue, due soon)
- **Numeric Ranges** - Color-code based on value ranges
- **Text Patterns** - Format based on text content or patterns

### Managing Formatting Rules

- **Rule Priority** - Drag rules to reorder their priority
- **Enable/Disable** - Toggle rules on/off without deleting
- **Edit Rules** - Modify conditions and formatting at any time
- **Delete Rules** - Remove rules you no longer need

## Column Grouping

### Creating Column Groups

Column grouping helps organize related fields together for better data comprehension.

#### Setting Up Groups

1. **Select Columns**
   - Hold Ctrl/Cmd and click column headers to select multiple columns
   - Or drag to select a range of columns

2. **Create Group**
   - Right-click on selected columns
   - Choose "Group Columns"
   - Enter a group name (e.g., "Contact Information", "Project Details")

3. **Group Management**
   - **Expand/Collapse** - Click the group header to show/hide columns
   - **Rename Groups** - Double-click group name to edit
   - **Ungroup** - Right-click group header and select "Ungroup"

#### Group Features

- **Visual Indicators** - Groups are clearly marked with headers
- **Collapsible** - Hide groups you don't need to see
- **Nested Groups** - Create sub-groups within larger groups
- **Drag and Drop** - Reorder groups and columns within groups

## Enhanced Inline Editing

### Rich Text Editing

For text and long text fields:

- **Formatting Toolbar** - Bold, italic, underline, lists
- **Keyboard Shortcuts** - Standard text formatting shortcuts
- **Auto-save** - Changes save automatically as you type
- **Undo/Redo** - Full editing history support

### Dropdown and Multi-Select

- **Quick Selection** - Click to open dropdown options
- **Search Options** - Type to filter available choices
- **Multi-select Tags** - Visual tags for multiple selections
- **Add New Options** - Create new options on the fly

### Date and Time Pickers

- **Calendar Widget** - Visual date selection
- **Time Input** - Separate time controls
- **Date Formats** - Respect user locale settings
- **Keyboard Input** - Type dates in natural formats

### File Upload Interface

- **Drag and Drop** - Drop files directly into cells
- **Multiple Files** - Upload several files at once
- **Progress Indicators** - See upload progress
- **File Previews** - Thumbnail previews for images

## Filter Presets

### Creating Filter Presets

Filter presets allow you to save commonly used filter configurations for quick access.

#### Setting Up Presets

1. **Apply Filters**
   - Use the filter controls to set up your desired filters
   - Test the filters to ensure they show the right data

2. **Save as Preset**
   - Click the filter menu
   - Select "Save as Preset"
   - Enter a descriptive name (e.g., "High Priority Tasks", "Overdue Items")

3. **Using Presets**
   - Access saved presets from the filter dropdown
   - Click any preset to instantly apply those filters
   - Combine presets with additional filters if needed

#### Managing Presets

- **Edit Presets** - Modify existing preset configurations
- **Share Presets** - Make presets available to team members
- **Delete Presets** - Remove presets you no longer need
- **Default Presets** - Set a preset to apply automatically when opening the view

### Common Preset Examples

- **Active Projects** - Status = "Active" AND Due Date > Today
- **My Tasks** - Assigned To = Current User
- **Urgent Items** - Priority = "High" OR Due Date < Tomorrow
- **Recent Updates** - Modified Date > Last Week

## Formula Syntax Highlighting

### Enhanced Formula Editor

The formula editor now provides a rich editing experience similar to code editors.

#### Features

- **Syntax Highlighting** - Different colors for functions, fields, operators
- **Auto-completion** - Suggestions for functions and field names
- **Error Detection** - Real-time syntax error highlighting
- **Bracket Matching** - Visual matching of parentheses and brackets

#### Using the Formula Editor

1. **Opening the Editor**
   - Click on a formula field
   - The enhanced editor opens with syntax highlighting

2. **Writing Formulas**
   - Type your formula with automatic color coding
   - Use Ctrl+Space for auto-completion suggestions
   - Errors are highlighted in red with helpful messages

3. **Formula Validation**
   - Real-time validation as you type
   - Clear error messages with suggestions
   - Preview of formula results

#### Formula Examples with Highlighting

```javascript
// Basic calculation
field('Quantity') * field('Price')

// Conditional logic
if(field('Status') = 'Complete', 100, 
   field('Progress') * 100)

// Text manipulation
concat(field('First Name'), ' ', field('Last Name'))

// Date calculations
datediff(field('Due Date'), today(), 'days')
```

## Performance Optimization

### Working with Large Datasets

The enhanced table view is optimized for performance with large amounts of data.

#### Virtualization

- **Row Virtualization** - Only visible rows are rendered
- **Column Virtualization** - Only visible columns are loaded
- **Smooth Scrolling** - Optimized scrolling performance

#### Best Practices

1. **Use Filters** - Reduce visible data with appropriate filters
2. **Limit Columns** - Hide columns you don't need to see
3. **Group Related Data** - Use column grouping to organize information
4. **Optimize Formulas** - Avoid complex calculations in frequently updated fields

### Loading States

- **Skeleton Loading** - Placeholder content while data loads
- **Progressive Loading** - Data appears as it becomes available
- **Error Handling** - Clear messages when data fails to load

## Keyboard Shortcuts

### Navigation Shortcuts

| Shortcut | Action |
|----------|--------|
| `Arrow Keys` | Navigate between cells |
| `Tab` | Move to next cell |
| `Shift + Tab` | Move to previous cell |
| `Enter` | Edit current cell |
| `Escape` | Cancel editing |
| `Ctrl + Home` | Go to first cell |
| `Ctrl + End` | Go to last cell |

### Editing Shortcuts

| Shortcut | Action |
|----------|--------|
| `F2` | Edit current cell |
| `Delete` | Clear cell content |
| `Ctrl + C` | Copy cell |
| `Ctrl + V` | Paste content |
| `Ctrl + Z` | Undo last action |
| `Ctrl + Y` | Redo last action |

### Selection Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + A` | Select all visible cells |
| `Shift + Click` | Select range |
| `Ctrl + Click` | Add to selection |
| `Shift + Arrow` | Extend selection |

## Mobile Experience

### Touch-Friendly Interface

The enhanced table view is optimized for mobile devices:

- **Larger Touch Targets** - Easier to tap on mobile screens
- **Swipe Gestures** - Swipe to scroll horizontally
- **Pinch to Zoom** - Zoom in/out for better visibility
- **Long Press** - Access context menus

### Mobile-Specific Features

- **Horizontal Scrolling** - Smooth column navigation
- **Sticky First Column** - Keep key information visible
- **Responsive Headers** - Headers adapt to screen size
- **Touch Editing** - Optimized editing experience

## Troubleshooting

### Common Issues

#### Slow Performance
- **Solution**: Apply filters to reduce visible data
- **Solution**: Hide unused columns
- **Solution**: Check for complex formulas that might be slowing down calculations

#### Formatting Not Applying
- **Solution**: Check rule conditions and field types
- **Solution**: Verify rule priority order
- **Solution**: Ensure the field has data that matches the condition

#### Sticky Headers Not Working
- **Solution**: Refresh the page
- **Solution**: Check browser compatibility
- **Solution**: Disable browser extensions that might interfere

### Getting Help

If you encounter issues not covered here:

1. **Check the FAQ** - Common questions and solutions
2. **Community Forum** - Ask questions and get help from other users
3. **Support Documentation** - Detailed technical information
4. **Contact Support** - Direct help for complex issues

## Tips and Best Practices

### Organizing Your Data

1. **Use Meaningful Column Names** - Clear, descriptive field names
2. **Group Related Fields** - Keep similar information together
3. **Apply Consistent Formatting** - Use conditional formatting for visual consistency
4. **Create Useful Presets** - Save time with commonly used filters

### Collaboration

1. **Share Filter Presets** - Help team members find relevant data quickly
2. **Use Conditional Formatting** - Make important information stand out
3. **Document Your Rules** - Add descriptions to complex formatting rules
4. **Regular Cleanup** - Remove unused presets and formatting rules

### Performance

1. **Monitor Data Size** - Be aware of how much data you're displaying
2. **Optimize Formulas** - Keep calculations simple when possible
3. **Use Appropriate Field Types** - Choose the right field type for your data
4. **Regular Maintenance** - Clean up old data and unused configurations