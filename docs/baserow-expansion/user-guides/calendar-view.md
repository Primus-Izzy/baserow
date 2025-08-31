# Calendar View User Guide

The Calendar view in Baserow transforms your data into a visual calendar interface, perfect for managing events, deadlines, appointments, and any time-based information. This guide will help you make the most of the calendar functionality.

## Overview

The Calendar view provides:

- **Multiple Display Modes** - Month, week, and day views
- **Drag-and-Drop Event Management** - Move events between dates easily
- **Color-Coded Events** - Visual organization based on your data
- **External Calendar Integration** - Sync with Google Calendar, Outlook, and more
- **Recurring Events** - Support for repeating events and patterns
- **Mobile-Optimized Interface** - Touch-friendly calendar navigation

## Getting Started

### Creating a Calendar View

1. **Prerequisites**
   - Your table must have at least one date field
   - Consider having fields for event titles, descriptions, and categories
   - Optional: end date field for multi-day events

2. **Create the View**
   - Click "Create View" in your table
   - Select "Calendar" from the view type options
   - Give your calendar view a descriptive name

3. **Configure Basic Settings**
   - **Date Field**: Select the primary date field for events
   - **End Date Field**: Optional field for event duration
   - **Title Field**: Choose which field displays as event titles
   - **Color Field**: Select a field for color-coding events

### Setup Example

For an events table with these fields:
- Event Name (Text)
- Start Date (Date)
- End Date (Date)
- Event Type (Single Select: Meeting, Deadline, Holiday, Training)
- Organizer (People)
- Location (Text)
- Description (Long Text)

Configure your calendar view:
- **Date Field**: Start Date
- **End Date Field**: End Date
- **Title Field**: Event Name
- **Color Field**: Event Type

## Calendar Interface

### Display Modes

#### Month View
- **Overview**: Shows entire month with events displayed as colored blocks
- **Best For**: Getting a broad overview of upcoming events and deadlines
- **Features**:
  - Full month visibility
  - Event count indicators for busy days
  - Quick navigation between months
  - Compact event display

#### Week View
- **Overview**: Shows one week with detailed daily schedules
- **Best For**: Detailed weekly planning and scheduling
- **Features**:
  - Hourly time slots (if time data available)
  - Multi-day event spans
  - Detailed event information
  - Easy drag-and-drop scheduling

#### Day View
- **Overview**: Shows single day with hourly breakdown
- **Best For**: Detailed daily schedule management
- **Features**:
  - Hour-by-hour timeline
  - Detailed event descriptions
  - Precise time management
  - Conflict detection for overlapping events

### Navigation Controls

#### Date Navigation
- **Previous/Next Buttons** - Navigate between time periods
- **Today Button** - Jump to current date
- **Date Picker** - Jump to specific date
- **Mini Calendar** - Quick month overview with navigation

#### View Switching
- **View Tabs** - Switch between Month, Week, Day views
- **Keyboard Shortcuts** - Quick view switching
- **Default View** - Set preferred starting view

## Working with Events

### Creating Events

#### Quick Creation
1. **Click on Date/Time** - Click empty space in calendar
2. **Enter Event Details** - Title, time, description in popup
3. **Save** - Event appears immediately on calendar

#### Detailed Creation
1. **Double-Click Date** - Opens full event creation form
2. **Fill All Details**:
   - Event name and description
   - Start and end dates/times
   - Location and attendees
   - Category and priority
3. **Set Recurrence** - If event repeats
4. **Save Event**

#### Drag-and-Drop Creation
1. **Drag Across Time** - Click and drag to create time span
2. **Release** - Event creation popup appears
3. **Enter Details** - Fill in event information
4. **Confirm** - Event is created with selected time span

### Editing Events

#### Quick Edits
- **Click Event Title** - Edit title inline
- **Drag Event** - Move to different date/time
- **Resize Event** - Drag edges to change duration
- **Right-Click** - Access context menu with options

#### Detailed Editing
1. **Double-Click Event** - Opens full editing form
2. **Modify Any Field** - Change dates, details, recurrence
3. **Save Changes** - Updates appear immediately

#### Bulk Operations
- **Select Multiple Events** - Ctrl+click to select multiple
- **Bulk Actions** - Delete, move, or modify multiple events
- **Copy/Paste** - Duplicate events to other dates

### Event Properties

#### Basic Properties
- **Title** - Event name displayed on calendar
- **Start Date/Time** - When event begins
- **End Date/Time** - When event ends
- **All-Day** - Toggle for all-day events
- **Description** - Detailed event information

#### Advanced Properties
- **Location** - Where event takes place
- **Attendees** - People involved in event
- **Category/Type** - Event classification
- **Priority** - Importance level
- **Status** - Confirmed, tentative, cancelled
- **Visibility** - Public, private, confidential

## Color Coding and Organization

### Setting Up Color Coding

#### By Event Type
Configure colors based on event categories:
- **Meetings** - Blue
- **Deadlines** - Red
- **Training** - Green
- **Holidays** - Purple
- **Personal** - Orange

#### By Priority
Color-code by importance:
- **High Priority** - Red
- **Medium Priority** - Yellow
- **Low Priority** - Green

#### By Team/Department
Assign colors by responsible team:
- **Sales** - Blue
- **Marketing** - Orange
- **Development** - Green
- **HR** - Purple

### Custom Color Schemes

1. **Access View Settings**
2. **Go to Color Configuration**
3. **Choose Color Field** - Select field for color basis
4. **Assign Colors** - Set color for each option
5. **Apply Changes** - Colors update immediately

### Visual Organization Tips

- **Consistent Colors** - Use same colors across all calendar views
- **Meaningful Colors** - Choose colors that make intuitive sense
- **Accessibility** - Ensure colors are distinguishable for colorblind users
- **Legend** - Provide color legend for team members

## Recurring Events

### Understanding Recurrence

Recurring events repeat according to specified patterns, eliminating the need to create multiple individual events.

### Recurrence Patterns

#### Daily Recurrence
- **Every Day** - Event repeats daily
- **Every Weekday** - Monday through Friday only
- **Every N Days** - Custom interval (every 2 days, every 3 days, etc.)

#### Weekly Recurrence
- **Every Week** - Same day each week
- **Multiple Days** - Multiple days per week (e.g., Monday, Wednesday, Friday)
- **Every N Weeks** - Custom interval (every 2 weeks, monthly, etc.)

#### Monthly Recurrence
- **Same Date** - Same date each month (15th of every month)
- **Same Day** - Same day of week (first Monday of each month)
- **Last Day** - Last occurrence of day in month (last Friday)

#### Yearly Recurrence
- **Same Date** - Annual occurrence on same date
- **Relative Date** - Same relative day (third Thursday in November)

### Creating Recurring Events

1. **Create Base Event** - Set up the first occurrence
2. **Enable Recurrence** - Check "Repeat" option
3. **Choose Pattern** - Select recurrence type and frequency
4. **Set End Condition**:
   - **Never** - Continues indefinitely
   - **After N Occurrences** - Stops after specified number
   - **End Date** - Stops on specific date
5. **Save** - All occurrences are created

### Managing Recurring Events

#### Editing Recurrence
- **Edit Single Occurrence** - Changes only one instance
- **Edit All Occurrences** - Changes entire series
- **Edit Future Occurrences** - Changes from selected date forward

#### Breaking Recurrence
- **Delete Single** - Removes one occurrence
- **Delete Series** - Removes all occurrences
- **Stop Recurrence** - Ends series from specific date

## Filtering and Views

### Calendar Filters

#### Date Range Filters
- **This Week** - Show current week only
- **This Month** - Show current month only
- **Next 30 Days** - Show upcoming month
- **Custom Range** - Specify exact date range

#### Content Filters
- **Event Type** - Filter by category or type
- **Attendee** - Show events for specific people
- **Location** - Filter by event location
- **Status** - Show only confirmed, tentative, or cancelled events

#### Advanced Filters
- **Keyword Search** - Find events by title or description
- **Time of Day** - Morning, afternoon, evening events
- **Duration** - Short, medium, long events
- **Recurring vs. One-time** - Filter by recurrence status

### Saved Views

#### Creating Saved Views
1. **Apply Filters** - Set up desired filters and display options
2. **Save View** - Give it a descriptive name
3. **Share** - Make available to team members if needed

#### Common Saved Views
- **My Events** - Events assigned to current user
- **Team Meetings** - All team meeting events
- **Deadlines** - Important deadline events
- **This Week** - Current week focus view
- **Upcoming** - Next 30 days view

## External Calendar Integration

### Supported Platforms

#### Google Calendar
- **Two-way Sync** - Changes sync both directions
- **Multiple Calendars** - Sync with different Google calendars
- **Real-time Updates** - Changes appear quickly
- **Conflict Resolution** - Handle simultaneous edits

#### Microsoft Outlook
- **Exchange Integration** - Works with corporate Exchange servers
- **Outlook.com Support** - Personal Outlook calendars
- **Meeting Invitations** - Handle meeting requests
- **Availability Sync** - Share free/busy information

#### Apple Calendar (iCal)
- **iCloud Sync** - Sync with Apple iCloud calendars
- **CalDAV Support** - Standard calendar protocol
- **Cross-platform** - Works across Apple devices

### Setting Up Integration

#### Google Calendar Setup
1. **Access Integration Settings** - Go to calendar view settings
2. **Connect Google Account** - Authorize Baserow access
3. **Select Calendars** - Choose which Google calendars to sync
4. **Configure Sync Direction**:
   - **Import Only** - Bring Google events into Baserow
   - **Export Only** - Send Baserow events to Google
   - **Two-way** - Sync changes both directions
5. **Field Mapping** - Map Baserow fields to calendar properties
6. **Start Sync** - Initial synchronization begins

#### Sync Configuration
- **Sync Frequency** - How often to check for changes
- **Conflict Resolution** - How to handle simultaneous edits
- **Date Range** - Which date range to sync
- **Event Filtering** - Which events to include in sync

### Managing Synced Events

#### Identifying Synced Events
- **Sync Indicators** - Visual markers for synced events
- **Source Information** - Shows which calendar event came from
- **Sync Status** - Current synchronization state

#### Handling Conflicts
- **Automatic Resolution** - System resolves simple conflicts
- **Manual Resolution** - User chooses for complex conflicts
- **Conflict Notifications** - Alerts when conflicts occur
- **Sync History** - Track synchronization changes

## Mobile Experience

### Mobile Calendar Features

#### Touch Navigation
- **Swipe Between Months** - Navigate time periods with gestures
- **Pinch to Zoom** - Zoom in/out on calendar (week/day views)
- **Tap to Select** - Select events and dates
- **Long Press** - Access context menus and options

#### Mobile-Optimized Views
- **Responsive Layout** - Adapts to screen size and orientation
- **Touch-Friendly Controls** - Larger buttons and touch targets
- **Simplified Interface** - Streamlined options for mobile
- **Gesture Support** - Intuitive touch interactions

#### Mobile-Specific Features
- **Quick Add** - Fast event creation on mobile
- **Voice Input** - Speak event details (where supported)
- **Location Services** - Auto-fill location from GPS
- **Push Notifications** - Event reminders and updates

### Mobile Limitations

Some features work better on desktop:
- **Complex Recurrence Setup** - Easier with full interface
- **Detailed Event Forms** - More space for information
- **Multi-event Selection** - Better with mouse and keyboard
- **Advanced Filtering** - More options available on desktop

## Advanced Features

### Calendar Overlays

#### Multiple Calendar Display
- **Layer Calendars** - Show multiple data sources simultaneously
- **Toggle Visibility** - Show/hide different calendar layers
- **Color Coordination** - Distinct colors for each calendar
- **Conflict Detection** - Identify scheduling conflicts across calendars

#### Team Calendar Views
- **Individual Calendars** - Each team member's schedule
- **Combined View** - All team events in one calendar
- **Resource Calendars** - Room, equipment, or resource scheduling
- **Department Views** - Calendar by team or department

### Event Templates

#### Creating Templates
1. **Design Template Event** - Set up event with standard details
2. **Save as Template** - Store for reuse
3. **Template Categories** - Organize by event type
4. **Share Templates** - Make available to team

#### Using Templates
- **Quick Creation** - Create events from templates
- **Customization** - Modify template details as needed
- **Bulk Creation** - Create multiple events from template
- **Template Library** - Access saved and shared templates

### Calendar Analytics

#### Usage Statistics
- **Event Frequency** - How often different event types occur
- **Time Distribution** - When events typically happen
- **Duration Analysis** - Average event lengths
- **Attendance Patterns** - Who attends which events

#### Performance Metrics
- **Meeting Efficiency** - Track meeting outcomes
- **Schedule Utilization** - How full calendars are
- **Conflict Frequency** - How often scheduling conflicts occur
- **Response Times** - How quickly people respond to invitations

## Collaboration Features

### Shared Calendars

#### Calendar Sharing
- **View Permissions** - Who can see calendar events
- **Edit Permissions** - Who can modify events
- **Admin Permissions** - Who can manage calendar settings
- **Public Calendars** - Share with external users

#### Team Collaboration
- **Event Comments** - Discuss events with team members
- **@Mentions** - Notify specific people about events
- **Status Updates** - Communicate event changes
- **Attendee Management** - Track who's attending events

### Meeting Management

#### Meeting Invitations
- **Send Invitations** - Invite attendees to events
- **RSVP Tracking** - Track responses to invitations
- **Reminder Notifications** - Automatic event reminders
- **Meeting Updates** - Notify attendees of changes

#### Meeting Resources
- **Room Booking** - Reserve meeting rooms
- **Equipment Scheduling** - Book projectors, equipment
- **Catering Requests** - Arrange meeting refreshments
- **Document Sharing** - Attach meeting materials

## Troubleshooting

### Common Issues

#### Sync Problems
**Problem**: External calendar not syncing properly
**Solutions**:
- Check internet connection
- Verify account permissions
- Refresh sync manually
- Check sync settings and field mappings

#### Performance Issues
**Problem**: Calendar loads slowly with many events
**Solutions**:
- Apply date range filters
- Reduce number of visible calendars
- Use appropriate view (month vs. day)
- Clear browser cache

#### Display Problems
**Problem**: Events not showing correctly
**Solutions**:
- Verify date field formats
- Check timezone settings
- Ensure required fields have data
- Refresh the view

### Best Practices

#### Calendar Setup
1. **Plan field structure** - Design fields before creating calendar
2. **Consistent data entry** - Use standardized formats
3. **Regular maintenance** - Clean up old events periodically
4. **Backup important data** - Export calendar data regularly

#### Team Usage
1. **Establish conventions** - Agree on color coding and naming
2. **Regular updates** - Keep event information current
3. **Clear communication** - Use descriptions and comments effectively
4. **Respect permissions** - Follow access control guidelines

#### Performance Optimization
1. **Use filters** - Don't display more events than necessary
2. **Archive old events** - Move historical data to separate tables
3. **Optimize recurrence** - Use recurring events instead of many individual events
4. **Monitor sync frequency** - Balance freshness with performance

## Tips for Success

### Getting Started
1. **Start simple** - Begin with basic events, add complexity gradually
2. **Focus on key dates** - Identify most important events first
3. **Involve the team** - Get input on calendar structure and usage
4. **Test integration** - Verify external calendar sync works properly

### Ongoing Management
1. **Regular review** - Check calendar accuracy and completeness
2. **Update as needed** - Modify structure as requirements change
3. **Train team members** - Ensure everyone knows how to use features
4. **Monitor usage** - Track how calendar is being used and improve

### Advanced Usage
1. **Experiment with views** - Try different display options and filters
2. **Use templates** - Create reusable event structures
3. **Integrate workflows** - Connect calendar with other business processes
4. **Analyze patterns** - Use calendar data to improve scheduling and planning

## Integration with Other Views

### Cross-View Functionality

#### Timeline Integration
- **Project Deadlines** - Show project milestones in calendar
- **Task Scheduling** - View task due dates in calendar format
- **Resource Planning** - See team availability across projects

#### Kanban Integration
- **Sprint Planning** - Calendar view of sprint dates and milestones
- **Release Scheduling** - Track release dates and deadlines
- **Workflow Deadlines** - See when tasks need to move between stages

#### Dashboard Integration
- **Calendar Widgets** - Embed calendar in dashboards
- **Event Analytics** - Calendar data in dashboard charts
- **Upcoming Events** - Dashboard widgets showing next events

### Workflow Integration

#### Automation Triggers
- **Date-based Triggers** - Automate actions based on calendar events
- **Event Reminders** - Automatic notifications before events
- **Follow-up Actions** - Automated tasks after events complete
- **Status Updates** - Automatic status changes based on dates

#### Form Integration
- **Event Registration** - Forms that create calendar events
- **Meeting Requests** - Forms for scheduling meetings
- **Resource Booking** - Forms for reserving rooms or equipment
- **Event Feedback** - Forms linked to completed events