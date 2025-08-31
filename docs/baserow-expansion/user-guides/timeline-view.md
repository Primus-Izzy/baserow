# Timeline/Gantt View User Guide

The Timeline/Gantt view in Baserow provides powerful project management capabilities, allowing you to visualize project schedules, track dependencies, and manage timelines with an intuitive drag-and-drop interface.

## Overview

The Timeline view transforms your data into a visual project timeline, perfect for:

- **Project Planning** - Plan and schedule project phases and tasks
- **Dependency Management** - Track relationships between tasks
- **Resource Planning** - Visualize team workload and assignments
- **Progress Tracking** - Monitor project progress over time
- **Milestone Management** - Mark important project milestones

## Getting Started

### Creating a Timeline View

1. **Prerequisites**
   - Your table must have at least one date field for start dates
   - Optionally, have an end date field for task duration
   - Consider having fields for task names, assignees, and status

2. **Create the View**
   - Click "Create View" in your table
   - Select "Timeline" from the view type options
   - Give your timeline view a descriptive name

3. **Configure Basic Settings**
   - **Start Date Field**: Select the field containing task start dates
   - **End Date Field**: Select the field for task end dates (optional)
   - **Title Field**: Choose which field to display as task titles
   - **Color Field**: Select a field to color-code tasks (optional)

### Initial Setup Example

For a project management table with these fields:
- Task Name (Text)
- Start Date (Date)
- End Date (Date)
- Status (Single Select: Not Started, In Progress, Complete)
- Assigned To (People)
- Priority (Single Select: Low, Medium, High)

Configure your timeline view:
- **Start Date Field**: Start Date
- **End Date Field**: End Date
- **Title Field**: Task Name
- **Color Field**: Status or Priority

## Timeline Interface

### Main Components

#### Timeline Header
- **Zoom Controls** - Switch between day, week, month, and year views
- **Date Navigation** - Jump to specific dates or navigate by periods
- **View Options** - Toggle dependencies, milestones, and other features
- **Filter Controls** - Apply filters to show specific tasks

#### Task List (Left Panel)
- **Task Names** - Hierarchical list of all tasks
- **Task Details** - Key information like assignee, status, priority
- **Expand/Collapse** - Show/hide subtasks and task groups
- **Quick Actions** - Edit, duplicate, or delete tasks

#### Timeline Canvas (Right Panel)
- **Time Scale** - Visual representation of time periods
- **Task Bars** - Visual bars representing task duration
- **Dependencies** - Lines connecting related tasks
- **Milestones** - Diamond markers for important dates
- **Progress Indicators** - Visual progress within task bars

### Navigation and Zoom

#### Zoom Levels

**Day View**
- Shows individual days
- Best for detailed daily planning
- Useful for short-term projects (1-4 weeks)

**Week View**
- Shows weeks with day markers
- Good balance of detail and overview
- Ideal for monthly projects

**Month View**
- Shows months with week markers
- Great for quarterly planning
- Best for long-term projects

**Year View**
- Shows years with month markers
- Perfect for multi-year projects
- Strategic planning perspective

#### Navigation Controls

- **Scroll Horizontally** - Use mouse wheel or scrollbar to move through time
- **Zoom In/Out** - Use zoom controls or Ctrl + mouse wheel
- **Go to Date** - Click date picker to jump to specific dates
- **Today Button** - Quickly return to current date
- **Fit to Screen** - Auto-zoom to show all tasks

## Working with Tasks

### Creating Tasks

#### From Timeline View
1. **Double-click** on the timeline canvas at your desired start date
2. **Enter task details** in the popup form
3. **Set duration** by dragging the end handle or entering end date
4. **Save** to create the task

#### From Task List
1. **Click "Add Task"** in the task list panel
2. **Fill in task information** including dates
3. **Position** will be calculated automatically based on dates

### Editing Tasks

#### Visual Editing
- **Drag Task Bars** - Move tasks to different dates
- **Resize Task Bars** - Extend start handle to change start date, end handle to change end date
- **Double-click Task** - Open detailed editing form

#### Quick Edits
- **Inline Editing** - Click task name to edit directly
- **Status Updates** - Click status indicators to change quickly
- **Progress Updates** - Drag progress indicator within task bar

### Task Properties

#### Essential Properties
- **Task Name** - Clear, descriptive title
- **Start Date** - When the task begins
- **End Date** - When the task should complete
- **Duration** - Automatically calculated from dates
- **Assigned To** - Team member responsible
- **Status** - Current progress state

#### Advanced Properties
- **Priority** - Task importance level
- **Progress Percentage** - Completion status (0-100%)
- **Description** - Detailed task information
- **Tags/Labels** - Categorization and filtering
- **Estimated Hours** - Time estimation
- **Actual Hours** - Time tracking

## Dependencies and Relationships

### Understanding Dependencies

Dependencies define relationships between tasks, showing which tasks must complete before others can begin.

#### Dependency Types

**Finish-to-Start (FS)**
- Most common type
- Task B cannot start until Task A finishes
- Example: "Design must finish before Development starts"

**Start-to-Start (SS)**
- Tasks start at the same time
- Example: "Testing starts when Development starts"

**Finish-to-Finish (FF)**
- Tasks finish at the same time
- Example: "Documentation finishes when Development finishes"

**Start-to-Finish (SF)**
- Rarely used
- Task B cannot finish until Task A starts

### Creating Dependencies

#### Visual Method
1. **Hover over task** to see connection points
2. **Click and drag** from predecessor to successor task
3. **Choose dependency type** from the popup menu
4. **Confirm** to create the dependency

#### Form Method
1. **Open task details** by double-clicking
2. **Go to Dependencies tab**
3. **Add predecessor/successor** tasks
4. **Select dependency type**
5. **Save changes**

### Managing Dependencies

#### Visual Indicators
- **Dependency Lines** - Arrows showing task relationships
- **Critical Path** - Highlighted path showing project bottlenecks
- **Slack Time** - Visual indication of task flexibility

#### Automatic Scheduling
When dependencies are enabled:
- **Auto-adjustment** - Moving a task automatically adjusts dependent tasks
- **Conflict Detection** - Warnings when dependencies create scheduling conflicts
- **Critical Path Calculation** - Automatic identification of critical tasks

## Milestones

### What are Milestones?

Milestones are significant events or achievements in your project timeline. They represent important deadlines, deliverables, or decision points.

### Creating Milestones

#### Method 1: Dedicated Milestone Tasks
1. **Create a task** with the same start and end date
2. **Mark as milestone** in task properties
3. **Milestone appears** as a diamond shape on timeline

#### Method 2: Milestone Field
1. **Add a checkbox field** called "Is Milestone"
2. **Configure timeline view** to recognize milestone field
3. **Check the box** for tasks that should be milestones

### Milestone Features

- **Visual Distinction** - Diamond shapes instead of bars
- **Date Labels** - Clear date markers
- **Color Coding** - Different colors for milestone types
- **Filtering** - Show/hide milestones as needed

## Color Coding and Visual Organization

### Setting Up Color Coding

#### By Status
Configure colors based on task status:
- **Not Started** - Gray
- **In Progress** - Blue
- **Complete** - Green
- **Overdue** - Red
- **On Hold** - Yellow

#### By Priority
Color-code by task priority:
- **High Priority** - Red
- **Medium Priority** - Orange
- **Low Priority** - Green

#### By Team/Department
Assign colors by responsible team:
- **Development** - Blue
- **Design** - Purple
- **Marketing** - Orange
- **Sales** - Green

### Custom Color Schemes

1. **Access View Settings**
2. **Go to Color Configuration**
3. **Choose color field** (status, priority, assignee, etc.)
4. **Assign colors** to each option
5. **Apply changes**

## Filtering and Grouping

### Timeline Filters

#### Common Filters
- **Date Range** - Show tasks within specific time periods
- **Assignee** - Filter by team member
- **Status** - Show only active, completed, or pending tasks
- **Priority** - Focus on high-priority items
- **Department** - Filter by team or department

#### Advanced Filters
- **Overdue Tasks** - Tasks past their due date
- **Critical Path** - Tasks that affect project completion
- **Milestones Only** - Show just milestone events
- **Custom Conditions** - Complex filter combinations

### Grouping Options

#### By Team Member
- Group tasks by assigned person
- See individual workloads
- Identify resource conflicts

#### By Project Phase
- Group related tasks together
- Show project structure
- Track phase completion

#### By Priority Level
- Separate high, medium, low priority tasks
- Focus on critical items first
- Balance workload priorities

## Progress Tracking

### Progress Indicators

#### Task Progress Bars
- **Visual Progress** - Colored portion shows completion percentage
- **Manual Updates** - Click to update progress directly
- **Automatic Calculation** - Based on subtask completion

#### Project Progress
- **Overall Completion** - Calculated from all tasks
- **Phase Completion** - Progress by project phase
- **Milestone Achievement** - Track milestone completion

### Progress Updates

#### Individual Tasks
1. **Click progress indicator** on task bar
2. **Drag slider** to set completion percentage
3. **Or enter exact percentage** in task details

#### Bulk Updates
1. **Select multiple tasks** using Ctrl+click
2. **Right-click** for context menu
3. **Choose "Update Progress"**
4. **Set percentage** for all selected tasks

## Resource Management

### Workload Visualization

#### Team Member View
- **Switch to resource view** to see individual workloads
- **Identify overallocation** - team members with too many concurrent tasks
- **Balance workload** - redistribute tasks as needed

#### Capacity Planning
- **Set working hours** for team members
- **Track allocation percentage** - how much of their time is allocated
- **Identify conflicts** - overlapping task assignments

### Resource Optimization

#### Load Balancing
1. **Identify overloaded** team members
2. **Find available capacity** in other team members
3. **Reassign tasks** to balance workload
4. **Adjust timelines** if necessary

#### Skill Matching
- **Match tasks to skills** - assign tasks to team members with appropriate skills
- **Cross-training opportunities** - identify where team members can learn new skills
- **Backup assignments** - ensure critical tasks have backup assignees

## Mobile Experience

### Mobile Timeline Features

#### Touch Navigation
- **Pinch to Zoom** - Zoom in/out on timeline
- **Swipe to Pan** - Move through time periods
- **Tap to Select** - Select tasks and milestones
- **Long Press** - Access context menus

#### Mobile-Optimized Interface
- **Responsive Layout** - Adapts to screen size
- **Touch-Friendly Controls** - Larger buttons and touch targets
- **Simplified Menus** - Streamlined options for mobile
- **Gesture Support** - Intuitive touch gestures

### Mobile Limitations

Some features are optimized for desktop use:
- **Complex dependency editing** - Better on desktop
- **Detailed task forms** - More space on desktop
- **Multi-task selection** - Easier with mouse and keyboard

## Advanced Features

### Critical Path Analysis

#### Understanding Critical Path
The critical path is the sequence of tasks that determines the minimum project duration. Any delay in critical path tasks will delay the entire project.

#### Critical Path Features
- **Automatic Calculation** - System identifies critical path
- **Visual Highlighting** - Critical tasks shown in distinct color
- **Impact Analysis** - See how changes affect project timeline
- **Optimization Suggestions** - Recommendations for timeline improvement

### Baseline Comparison

#### Setting Baselines
1. **Create baseline** when project plan is approved
2. **Track changes** against original plan
3. **Compare actual vs. planned** progress
4. **Identify variances** and their causes

#### Baseline Features
- **Visual Comparison** - Show planned vs. actual timelines
- **Variance Reports** - Quantify differences from plan
- **Change Tracking** - History of timeline modifications
- **Performance Metrics** - Schedule performance indicators

### Custom Views and Templates

#### Saved Views
- **Save configurations** - Timeline settings, filters, grouping
- **Quick switching** - Rapidly change between different views
- **Team sharing** - Share useful views with team members
- **Default views** - Set preferred view for different users

#### Timeline Templates
- **Project Templates** - Pre-configured timelines for common project types
- **Task Templates** - Standard task structures
- **Milestone Templates** - Common milestone patterns
- **Industry Templates** - Specialized templates for different industries

## Integration and Collaboration

### Real-Time Collaboration

#### Multi-User Editing
- **Live Updates** - See changes from other users in real-time
- **User Cursors** - See where other users are working
- **Conflict Resolution** - Handle simultaneous edits gracefully
- **Change Notifications** - Alerts when others modify tasks

#### Comments and Communication
- **Task Comments** - Discuss specific tasks
- **@Mentions** - Notify team members
- **Status Updates** - Communicate progress changes
- **Decision Tracking** - Record important decisions

### External Integration

#### Calendar Sync
- **Export to Calendar** - Sync timeline with external calendars
- **Import Events** - Bring in external deadlines and meetings
- **Two-way Sync** - Keep timeline and calendar in sync
- **Multiple Calendars** - Sync with different calendar systems

#### Project Management Tools
- **Import Projects** - Bring in data from other PM tools
- **Export Timelines** - Share with external stakeholders
- **API Integration** - Connect with other business systems
- **Reporting Tools** - Export data for analysis

## Troubleshooting

### Common Issues

#### Performance with Large Projects
**Problem**: Timeline becomes slow with many tasks
**Solutions**:
- Apply filters to reduce visible tasks
- Use appropriate zoom level
- Group related tasks
- Consider breaking large projects into phases

#### Dependency Conflicts
**Problem**: Dependencies create impossible schedules
**Solutions**:
- Review dependency types
- Check for circular dependencies
- Adjust task durations
- Consider parallel task execution

#### Date Calculation Issues
**Problem**: Dates don't calculate correctly
**Solutions**:
- Verify date field formats
- Check timezone settings
- Ensure working days are configured correctly
- Review holiday calendars

### Best Practices

#### Project Setup
1. **Plan structure first** - Define phases and major milestones
2. **Start with high-level tasks** - Break down into details later
3. **Set realistic durations** - Account for dependencies and resources
4. **Define clear milestones** - Mark important achievements

#### Timeline Management
1. **Regular updates** - Keep progress current
2. **Review dependencies** - Ensure relationships are still valid
3. **Monitor critical path** - Focus on tasks that affect project completion
4. **Communicate changes** - Keep team informed of timeline updates

#### Team Collaboration
1. **Clear ownership** - Assign tasks to specific team members
2. **Regular check-ins** - Review progress and obstacles
3. **Document decisions** - Use comments to record important choices
4. **Share views** - Create views that help different team members

## Tips for Success

### Getting Started
1. **Start simple** - Begin with basic timeline, add complexity gradually
2. **Focus on key dates** - Identify critical milestones first
3. **Involve the team** - Get input from people doing the work
4. **Iterate and improve** - Refine timeline based on experience

### Ongoing Management
1. **Update regularly** - Keep timeline current with actual progress
2. **Review and adjust** - Adapt timeline as project evolves
3. **Learn from experience** - Use completed projects to improve future planning
4. **Share knowledge** - Help team members learn timeline management skills

### Advanced Usage
1. **Experiment with views** - Try different groupings and filters
2. **Use templates** - Create reusable timeline structures
3. **Integrate with other tools** - Connect timeline with other business systems
4. **Analyze performance** - Use timeline data to improve project management