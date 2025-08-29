# Kanban View User Guide

The Kanban view transforms your data into visual boards with cards that can be moved between columns, perfect for project management, task tracking, and workflow visualization.

## What is Kanban View?

Kanban view displays your records as cards organized in columns based on a single-select field. Each card represents a row in your table, and you can drag cards between columns to update their status.

### Key Features
- **Drag-and-drop functionality** - Move cards between columns effortlessly
- **Customizable cards** - Choose which fields to display on each card
- **Color coding** - Visual indicators based on field values
- **Real-time updates** - See changes from team members instantly
- **Mobile-friendly** - Touch-optimized for mobile devices

## Creating a Kanban View

### Prerequisites
Your table must have at least one **Single Select** field to use as columns. This field will determine the columns in your Kanban board.

### Steps to Create
1. Click the **+ Add View** button in your table
2. Select **Kanban** from the view type options
3. Give your view a descriptive name (e.g., "Project Board", "Task Status")
4. Configure the Kanban settings:
   - **Status Field**: Choose the single-select field for columns
   - **Card Fields**: Select which fields to show on cards
   - **Color Field**: Optional field for card color coding
   - **Cover Image**: Optional image field for card covers

### Example Configuration
```
View Name: Project Tasks
Status Field: Task Status (To Do, In Progress, Review, Done)
Card Fields: Task Name, Assignee, Due Date, Priority
Color Field: Priority (High=Red, Medium=Yellow, Low=Green)
```

## Using Kanban View

### Moving Cards
- **Drag and Drop**: Click and drag cards between columns
- **Touch Devices**: Long press and drag on mobile/tablet
- **Keyboard**: Use Tab and arrow keys for accessibility

### Card Information
Each card displays:
- **Primary field** (usually the record title)
- **Selected fields** from your configuration
- **Color indicators** based on your color field
- **Cover image** if configured

### Column Management
- **Column Headers**: Show the single-select field options
- **Card Count**: Display number of cards in each column
- **Column Colors**: Match the single-select field colors

## Customizing Your Kanban Board

### Card Field Selection
Choose which fields appear on cards:
1. Click the **Settings** icon in the view toolbar
2. Go to **Card Fields** section
3. Add or remove fields using the checkboxes
4. Drag to reorder field display

**Recommended Fields for Cards:**
- Title/Name field (always shown)
- Assignee (People field)
- Due date (Date field)
- Priority (Single select)
- Progress (Progress bar field)

### Color Coding Options
Set up visual indicators:
- **By Priority**: Use priority field for urgent task identification
- **By Assignee**: Color code by team member
- **By Category**: Use project or department fields
- **By Due Date**: Highlight overdue or upcoming tasks

### Cover Images
Add visual appeal with cover images:
- Use **File** or **URL** fields for images
- Images appear at the top of cards
- Helps with quick visual identification

## Advanced Kanban Features

### Filtering and Sorting
- **Filters**: Hide cards that don't meet criteria
- **Sorting**: Order cards within columns by date, priority, etc.
- **Search**: Find specific cards quickly

### Swimlanes (Coming Soon)
Group cards horizontally by another field:
- Group by assignee to see individual workloads
- Group by project to separate different initiatives
- Group by priority for better organization

### Card Templates
Create consistent card formats:
- Set default values for new cards
- Define required fields
- Standardize card appearance

## Collaboration in Kanban View

### Real-time Updates
- See cards move as team members drag them
- Live indicators show who's currently editing
- Automatic refresh when data changes

### Comments and Communication
- Click on any card to add comments
- Use @mentions to notify team members
- Track conversation history on each task

### Activity Tracking
- View who moved cards and when
- See field changes and updates
- Monitor team productivity

## Mobile Kanban Experience

### Touch Interactions
- **Long press** to start dragging cards
- **Swipe** to scroll between columns
- **Tap** to open card details
- **Pinch** to zoom in/out

### Mobile Optimizations
- Responsive column layout
- Touch-friendly card sizes
- Optimized for portrait and landscape modes
- Offline support with sync when reconnected

## Best Practices

### Board Organization
- **Keep columns simple**: 3-5 columns work best
- **Clear naming**: Use descriptive column names
- **Logical flow**: Arrange columns in workflow order
- **Regular cleanup**: Archive completed items

### Card Design
- **Essential information only**: Don't overcrowd cards
- **Consistent formatting**: Use similar field types
- **Visual hierarchy**: Most important info first
- **Color strategy**: Use colors meaningfully

### Team Workflow
- **Define column meanings**: Clear criteria for each status
- **Regular reviews**: Team check-ins on board status
- **Automation rules**: Set up automatic card movements
- **Permission settings**: Control who can move cards

## Common Use Cases

### Agile Development
```
Columns: Backlog → In Progress → Code Review → Testing → Done
Cards: User Story, Assignee, Story Points, Sprint
Colors: Priority (High/Medium/Low)
```

### Sales Pipeline
```
Columns: Lead → Qualified → Proposal → Negotiation → Closed
Cards: Company, Contact, Deal Value, Close Date
Colors: Deal Size or Probability
```

### Content Creation
```
Columns: Ideas → Writing → Review → Approved → Published
Cards: Title, Author, Due Date, Content Type
Colors: Content Category
```

### Bug Tracking
```
Columns: Reported → Assigned → In Progress → Testing → Resolved
Cards: Bug Title, Severity, Assignee, Reporter
Colors: Severity Level
```

## Troubleshooting

### Common Issues

**Cards not moving between columns**
- Check if you have edit permissions
- Ensure the status field is properly configured
- Verify the single-select field has the correct options

**Cards not displaying correctly**
- Review card field selections in settings
- Check field permissions and visibility
- Ensure fields contain data

**Performance issues with large boards**
- Use filters to reduce visible cards
- Consider breaking large projects into separate views
- Archive completed items regularly

### Performance Tips
- Limit cards per column (under 100 for best performance)
- Use filters to show relevant cards only
- Regular maintenance and archiving
- Optimize field selections for essential information

## Integration with Other Views

### Switching Between Views
- Use the same data across multiple view types
- Kanban changes reflect in Table, Calendar, and other views
- Maintain filters and sorts when switching

### Complementary Views
- **Table View**: Detailed data entry and bulk editing
- **Calendar View**: Date-based task scheduling
- **Timeline View**: Project planning and dependencies
- **Form View**: Task creation and data collection

## Advanced Automation

### Automatic Card Movement
Set up automations to move cards automatically:
- Move to "In Progress" when assignee is set
- Move to "Review" when task is marked complete
- Move to "Done" when approved

### Notifications
Configure alerts for:
- Cards moved to specific columns
- Overdue tasks in certain columns
- New cards added to the board
- Comments added to cards

This Kanban view provides a powerful way to visualize and manage your workflows while maintaining the flexibility and data integrity that Baserow is known for.