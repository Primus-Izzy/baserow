# Dashboard & Reporting User Guide

Create powerful, interactive dashboards with charts, KPIs, and real-time data visualization to gain insights from your Baserow data.

## What are Dashboards?

Dashboards provide a centralized view of your most important data through customizable widgets including charts, counters, calendars, and KPI indicators. They update in real-time and can pull data from multiple tables and views.

### Key Features
- **Multiple Widget Types** - Charts, counters, tables, calendars, and KPIs
- **Drag-and-Drop Layout** - Arrange widgets exactly how you want
- **Real-Time Updates** - Data refreshes automatically as your tables change
- **Multi-Data Sources** - Combine data from different tables and views
- **Sharing and Export** - Share dashboards publicly or export as PDF/PNG
- **Mobile Responsive** - Works perfectly on all devices

## Creating Your First Dashboard

### Step 1: Create a Dashboard
1. Navigate to the **Dashboards** section in your workspace
2. Click **+ New Dashboard**
3. Give your dashboard a descriptive name (e.g., "Sales Overview", "Project Status")
4. Choose a layout template or start with a blank dashboard

### Step 2: Add Widgets
1. Click **+ Add Widget** in your dashboard
2. Select the widget type:
   - **Chart Widget** - Bar, line, pie, donut, area charts
   - **Counter Widget** - Display single metrics with comparisons
   - **Table Widget** - Show filtered table data
   - **Calendar Widget** - Display date-based information
   - **KPI Widget** - Key performance indicators with targets

### Step 3: Configure Widget Data
1. **Select Data Source**: Choose table and view
2. **Apply Filters**: Narrow down the data shown
3. **Choose Fields**: Select which fields to display or analyze
4. **Set Aggregation**: Sum, count, average, min, max for numeric data

### Example: Sales Dashboard
```
Dashboard: Monthly Sales Overview
Widgets:
- Revenue Chart (Line chart showing monthly revenue trend)
- Deal Counter (Total deals closed this month vs last month)
- Pipeline Table (Active deals with status and value)
- Activity Calendar (Meetings and follow-ups scheduled)
```

## Widget Types and Configuration

### Chart Widgets

#### Bar Charts
Perfect for comparing categories or showing data over time.

**Configuration:**
- **X-Axis**: Category field (text, single-select, date)
- **Y-Axis**: Numeric field to measure
- **Group By**: Optional field to create grouped bars
- **Aggregation**: Sum, count, average, min, max

**Example Use Cases:**
- Sales by region
- Tasks by status
- Revenue by month

#### Line Charts
Ideal for showing trends over time.

**Configuration:**
- **X-Axis**: Date field
- **Y-Axis**: Numeric field to track
- **Multiple Lines**: Group by another field
- **Time Period**: Day, week, month, year grouping

**Example Use Cases:**
- Revenue trends
- User growth over time
- Project progress tracking

#### Pie/Donut Charts
Great for showing proportions and percentages.

**Configuration:**
- **Category Field**: Field to create slices
- **Value Field**: Numeric field for slice sizes
- **Color Scheme**: Choose colors for different categories

**Example Use Cases:**
- Market share breakdown
- Task distribution by team
- Budget allocation

### Counter Widgets

Display single metrics with optional comparisons and targets.

**Configuration:**
- **Primary Metric**: Main number to display
- **Comparison Period**: Compare to previous period
- **Target Value**: Set goals and track progress
- **Format**: Currency, percentage, number formatting
- **Color Coding**: Green/red based on performance

**Examples:**
- Total Revenue: $125,000 (↑15% vs last month)
- Active Users: 1,247 (Target: 1,500)
- Completion Rate: 87% (↑3% vs last week)

### Table Widgets

Show filtered and formatted table data within your dashboard.

**Configuration:**
- **Data Source**: Select table and view
- **Visible Fields**: Choose which columns to show
- **Filters**: Apply specific filters
- **Sorting**: Default sort order
- **Row Limit**: Maximum rows to display

**Example Use Cases:**
- Top 10 customers by revenue
- Overdue tasks
- Recent activity log

### Calendar Widgets

Display date-based information in calendar format.

**Configuration:**
- **Date Field**: Field containing dates
- **Title Field**: Field for event titles
- **Color Field**: Field for color coding
- **View Type**: Month, week, or agenda view

**Example Use Cases:**
- Project deadlines
- Team schedules
- Event planning

### KPI Widgets

Key Performance Indicators with targets and progress tracking.

**Configuration:**
- **Metric**: Value to track
- **Target**: Goal value
- **Time Period**: Measurement period
- **Threshold**: Warning and danger levels
- **Visualization**: Gauge, progress bar, or simple number

**Examples:**
- Customer Satisfaction: 4.2/5.0 (Target: 4.5)
- Project Completion: 75% (On track)
- Response Time: 2.3 hours (Target: < 4 hours)

## Dashboard Layout and Design

### Drag-and-Drop Interface
- **Resize Widgets**: Drag corners to resize
- **Move Widgets**: Drag to reposition
- **Grid System**: Widgets snap to grid for alignment
- **Responsive Layout**: Automatically adjusts for different screen sizes

### Layout Best Practices
- **Most Important First**: Place key metrics at the top
- **Logical Grouping**: Group related widgets together
- **Consistent Sizing**: Use similar sizes for related widgets
- **White Space**: Don't overcrowd the dashboard
- **Color Harmony**: Use consistent color schemes

### Dashboard Themes
- **Light Theme**: Clean, professional appearance
- **Dark Theme**: Reduced eye strain, modern look
- **Custom Branding**: Add your logo and brand colors
- **High Contrast**: Accessibility-friendly options

## Real-Time Data and Refresh

### Automatic Updates
- **Live Data**: Widgets update automatically when underlying data changes
- **Refresh Intervals**: Configure how often data refreshes (1 min to 1 hour)
- **Manual Refresh**: Force immediate data refresh
- **Last Updated**: See when data was last refreshed

### Performance Optimization
- **Efficient Queries**: Dashboards use optimized database queries
- **Caching**: Frequently accessed data is cached for speed
- **Lazy Loading**: Widgets load as they become visible
- **Background Updates**: Data refreshes without interrupting use

## Sharing and Collaboration

### Public Dashboard Sharing
1. Click **Share** in your dashboard
2. Enable **Public Access**
3. Configure sharing options:
   - **Password Protection**: Require password for access
   - **Expiration Date**: Set when link expires
   - **Download Permissions**: Allow PDF/PNG downloads
4. Copy the public link to share

### Team Collaboration
- **View Permissions**: Control who can view dashboards
- **Edit Permissions**: Control who can modify dashboards
- **Comments**: Add comments to discuss insights
- **Notifications**: Get notified when dashboards are updated

### Embedding Dashboards
Embed dashboard widgets in external applications:

```html
<iframe 
  src="https://your-baserow.com/dashboard/embed/widget/123"
  width="600" 
  height="400"
  frameborder="0">
</iframe>
```

## Export and Reporting

### Export Options
- **PDF Export**: Full dashboard as PDF document
- **PNG Export**: Dashboard as high-resolution image
- **CSV Export**: Raw data from dashboard widgets
- **Scheduled Reports**: Automatic email delivery

### Scheduled Reports
1. Click **Schedule Report** in dashboard
2. Configure schedule:
   - **Frequency**: Daily, weekly, monthly
   - **Time**: When to send
   - **Recipients**: Email addresses
   - **Format**: PDF or PNG
3. Reports are automatically generated and emailed

### Print-Friendly Layouts
- **Print Mode**: Optimized layout for printing
- **Page Breaks**: Automatic page breaks for large dashboards
- **Header/Footer**: Add titles and page numbers
- **Black & White**: Printer-friendly color schemes

## Advanced Dashboard Features

### Filters and Interactivity
- **Global Filters**: Apply filters to all widgets
- **Widget Filters**: Individual widget filtering
- **Date Range Picker**: Filter by date ranges
- **Interactive Charts**: Click charts to drill down

### Multi-Dashboard Navigation
- **Dashboard Tabs**: Switch between related dashboards
- **Dashboard Links**: Link dashboards together
- **Breadcrumbs**: Navigate dashboard hierarchies
- **Favorites**: Mark frequently used dashboards

### Custom Calculations
- **Calculated Fields**: Create custom metrics
- **Formula Widgets**: Use formulas for complex calculations
- **Aggregation Functions**: Sum, average, count, etc.
- **Conditional Logic**: Show different data based on conditions

## Mobile Dashboard Experience

### Responsive Design
- **Automatic Layout**: Widgets rearrange for mobile screens
- **Touch Interactions**: Tap, swipe, and pinch gestures
- **Optimized Charts**: Charts adapt to small screens
- **Offline Viewing**: View cached dashboard data offline

### Mobile-Specific Features
- **Swipe Navigation**: Swipe between dashboard pages
- **Touch Zoom**: Pinch to zoom on charts
- **Mobile Sharing**: Share via messaging apps
- **Push Notifications**: Get alerts for important changes

## Common Dashboard Use Cases

### Sales Dashboard
```
Widgets:
- Monthly Revenue (Line chart)
- Deals Closed (Counter with target)
- Sales Pipeline (Funnel chart)
- Top Customers (Table widget)
- Activity Calendar (Upcoming meetings)
```

### Project Management Dashboard
```
Widgets:
- Project Progress (Progress bars)
- Task Status (Kanban-style chart)
- Team Workload (Bar chart)
- Upcoming Deadlines (Calendar widget)
- Budget vs Actual (Comparison chart)
```

### Customer Support Dashboard
```
Widgets:
- Ticket Volume (Line chart)
- Response Time (KPI with target)
- Satisfaction Score (Gauge widget)
- Open Tickets (Table widget)
- Agent Performance (Bar chart)
```

### Marketing Dashboard
```
Widgets:
- Website Traffic (Line chart)
- Conversion Rate (KPI widget)
- Campaign Performance (Bar chart)
- Lead Sources (Pie chart)
- Social Media Metrics (Counter widgets)
```

## Troubleshooting

### Common Issues

**Dashboard loading slowly**
- Reduce the number of widgets
- Optimize filters to reduce data volume
- Increase refresh intervals
- Use summary tables for complex calculations

**Widgets showing no data**
- Check data source permissions
- Verify filters aren't too restrictive
- Ensure fields contain data
- Check date ranges

**Charts not displaying correctly**
- Verify field types match chart requirements
- Check for null or empty values
- Ensure proper aggregation settings
- Try different chart types

### Performance Tips
- **Limit Data**: Use filters to show only relevant data
- **Optimize Queries**: Use indexed fields for filtering
- **Cache Settings**: Adjust refresh intervals appropriately
- **Widget Limits**: Don't exceed 20 widgets per dashboard

## Best Practices

### Dashboard Design
- **Clear Purpose**: Each dashboard should have a specific goal
- **Relevant Metrics**: Only show metrics that drive decisions
- **Consistent Layout**: Use similar widget sizes and spacing
- **Color Coding**: Use colors meaningfully and consistently

### Data Accuracy
- **Regular Reviews**: Periodically review dashboard accuracy
- **Data Validation**: Ensure source data is clean and accurate
- **Update Schedules**: Keep refresh rates appropriate for data changes
- **Documentation**: Document what each metric means

### User Experience
- **Loading Performance**: Optimize for fast loading
- **Mobile Friendly**: Test on mobile devices
- **Accessibility**: Use high contrast and clear labels
- **User Training**: Provide guidance on interpreting dashboards

Dashboards transform your raw data into actionable insights, helping you make informed decisions quickly and effectively. Start with simple dashboards and gradually add complexity as your needs grow.