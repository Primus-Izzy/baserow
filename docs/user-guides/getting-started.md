# Getting Started with Baserow

Welcome to Baserow! This guide will help you get up and running with the enhanced Monday.com-style features and understand how to make the most of your new project management platform.

## 🚀 What's New in Baserow 2.0

Baserow has evolved from a simple database tool into a comprehensive project management and collaboration platform. Here's what you can now do:

### 📊 Multiple View Types
- **Table View**: Traditional spreadsheet-like interface with advanced filtering
- **Kanban View**: Visual task management with drag-and-drop cards
- **Timeline View**: Gantt-style project timeline with dependencies
- **Calendar View**: Event management with recurring events
- **Form View**: Data collection with conditional logic

### 🤝 Team Collaboration
- **Real-time Editing**: See changes as they happen
- **Comments & Mentions**: Discuss work directly on records
- **Activity Tracking**: Complete audit trail of all changes
- **User Presence**: See who's working where

### 🔄 Automation & Workflows
- **Visual Workflow Builder**: Create automations without coding
- **Smart Triggers**: Automate based on data changes, dates, or external events
- **Multi-step Actions**: Complex workflows with conditional logic

### 📈 Dashboards & Reporting
- **Interactive Dashboards**: Drag-and-drop widget creation
- **Real-time Charts**: Live data visualization
- **KPI Tracking**: Monitor key metrics at a glance

## 🏁 Quick Start (5 Minutes)

### Step 1: Create Your First Workspace
1. **Sign up** at [baserow.io](https://baserow.io) or log into your existing account
2. **Create a workspace** - this is where your team will collaborate
3. **Invite team members** using their email addresses

### Step 2: Set Up Your First Project
1. **Create a database** called "Project Management"
2. **Add a table** called "Tasks"
3. **Set up these essential fields**:
   - **Task Name** (Text)
   - **Assignee** (People field)
   - **Status** (Single Select: To Do, In Progress, Done)
   - **Priority** (Single Select: Low, Medium, High)
   - **Due Date** (Date)
   - **Progress** (Progress Bar)

### Step 3: Add Your First Tasks
1. **Switch to Table view** if not already there
2. **Add some sample tasks**:
   ```
   Task Name: "Set up project workspace"
   Assignee: [Your name]
   Status: "Done"
   Priority: "High"
   Due Date: [Today]
   Progress: 100%
   ```

### Step 4: Try Different Views
1. **Create a Kanban view**:
   - Click "Create view" → "Kanban"
   - Group by "Status" field
   - Drag tasks between columns

2. **Create a Timeline view**:
   - Click "Create view" → "Timeline"
   - Set start date and end date fields
   - View your project timeline

3. **Create a Calendar view**:
   - Click "Create view" → "Calendar"
   - Map to your "Due Date" field
   - See tasks on a calendar

### Step 5: Set Up Basic Automation
1. **Go to Automations** in the sidebar
2. **Create a new automation**:
   - **Trigger**: "When field changes" → Status → "Done"
   - **Action**: "Update field" → Progress → 100%
3. **Test it**: Change a task status to "Done" and watch progress update automatically

## 📋 Essential Concepts

### Workspaces
Your **workspace** is the top-level container for all your projects. Think of it as your company or team space where all collaboration happens.

**Best Practices**:
- Create separate workspaces for different teams or clients
- Use clear, descriptive names
- Set up proper permissions from the start

### Databases and Tables
- **Database**: A collection of related tables (like "Project Management")
- **Table**: Contains your actual data (like "Tasks", "Projects", "Clients")

**Organization Tips**:
```
📁 Project Management Database
  ├── 📊 Tasks
  ├── 📊 Projects  
  ├── 📊 Team Members
  └── 📊 Clients
```

### Views
**Views** are different ways to look at the same data. Each view can have:
- Different visible fields
- Custom filters and sorting
- Unique layouts (table, kanban, timeline, etc.)

**View Strategy**:
- **"All Tasks"** (Table) - Complete overview for managers
- **"My Tasks"** (Table) - Filtered to current user
- **"Sprint Board"** (Kanban) - Current sprint workflow
- **"Project Timeline"** (Timeline) - High-level project view
- **"Deadlines"** (Calendar) - Upcoming due dates

### Fields and Field Types
Choose the right field type for your data:

| Field Type | Best For | Example |
|------------|----------|---------|
| **Text** | Names, descriptions | Task titles, notes |
| **Number** | Quantities, scores | Hours, budget |
| **Single Select** | Status, categories | Priority, Department |
| **Multiple Select** | Tags, skills | Technologies, Labels |
| **Date** | Deadlines, events | Due dates, meetings |
| **People** | Assignments | Task owner, reviewer |
| **Progress Bar** | Completion tracking | Task progress, goals |
| **Formula** | Calculations | Days remaining, totals |
| **Linked Records** | Relationships | Project → Tasks |

## 🎯 Common Use Cases

### Project Management
**Setup**:
1. **Projects table**: Name, Description, Start Date, End Date, Status
2. **Tasks table**: Name, Project (linked), Assignee, Status, Priority, Due Date
3. **Team Members table**: Name, Role, Email, Skills

**Views to Create**:
- **Project Dashboard** (Table): All projects with status overview
- **Active Sprint** (Kanban): Current tasks grouped by status
- **Project Timeline** (Timeline): Gantt view of all projects
- **Team Calendar** (Calendar): All deadlines and meetings

### Customer Relationship Management (CRM)
**Setup**:
1. **Companies table**: Name, Industry, Size, Status
2. **Contacts table**: Name, Company (linked), Email, Phone, Role
3. **Deals table**: Name, Company (linked), Value, Stage, Close Date

**Views to Create**:
- **Sales Pipeline** (Kanban): Deals grouped by stage
- **Contact Directory** (Table): Searchable contact list
- **Deal Timeline** (Timeline): Sales forecast view
- **Follow-up Calendar** (Calendar): Scheduled activities

### Content Planning
**Setup**:
1. **Content Ideas table**: Title, Type, Status, Assigned Writer
2. **Editorial Calendar table**: Title, Publish Date, Platform, Status
3. **Writers table**: Name, Specialties, Availability

**Views to Create**:
- **Content Pipeline** (Kanban): Ideas → Draft → Review → Published
- **Publishing Calendar** (Calendar): Scheduled content by date
- **Writer Workload** (Table): Tasks by assignee

## 🔧 Customization Tips

### Workspace Setup
1. **Create a clear structure**:
   ```
   📁 Marketing Workspace
     ├── 🗂️ Campaigns Database
     ├── 🗂️ Content Database
     └── 🗂️ Analytics Database
   ```

2. **Set up team permissions**:
   - **Admins**: Full access to everything
   - **Editors**: Can edit data, create views
   - **Viewers**: Read-only access to specific tables

3. **Establish naming conventions**:
   - Tables: Plural nouns ("Tasks", "Projects")
   - Fields: Clear, consistent names ("Due Date", not "Due")
   - Views: Purpose-based ("My Active Tasks", "Q4 Projects")

### Field Configuration
1. **Use field descriptions** to explain what data should go in each field
2. **Set up validation rules** for important fields
3. **Create field dependencies** where one field affects another
4. **Use consistent formatting** (date formats, number formats)

### View Optimization
1. **Start with Table view** to set up your data structure
2. **Create specialized views** for different use cases
3. **Use filters effectively** to show only relevant data
4. **Set up default sorting** to show most important items first

## 🚀 Advanced Features

### Automation Examples
**Automatic Status Updates**:
- **Trigger**: Progress reaches 100%
- **Action**: Set Status to "Complete"

**Deadline Reminders**:
- **Trigger**: 2 days before due date
- **Action**: Send notification to assignee

**Project Completion**:
- **Trigger**: All linked tasks are complete
- **Action**: Update project status and notify team

### Dashboard Creation
1. **Plan your metrics**: What KPIs matter most?
2. **Create supporting views**: Dashboards pull from views
3. **Choose appropriate charts**: Bar, pie, line, or KPI widgets
4. **Set up real-time updates**: Keep data fresh
5. **Share with stakeholders**: Create public dashboard links

### Integration Setup
**Popular Integrations**:
- **Slack**: Get notifications in your team channels
- **Google Calendar**: Sync deadlines and meetings
- **Email**: Automated status updates and reminders
- **Zapier**: Connect to 1000+ other tools

## 📱 Mobile Usage

### Mobile App Features
- **Full editing capabilities**: Add, edit, delete records
- **Offline support**: Work without internet, sync later
- **Push notifications**: Stay updated on important changes
- **Camera integration**: Add photos directly to records

### Mobile Best Practices
1. **Design mobile-friendly views**: Fewer columns, larger text
2. **Use touch-friendly field types**: Single select vs. text input
3. **Set up mobile notifications**: Critical updates only
4. **Test on actual devices**: Different screen sizes behave differently

## 🎓 Learning Path

### Week 1: Basics
- [ ] Set up workspace and first database
- [ ] Create tables with appropriate field types
- [ ] Add sample data and explore table view
- [ ] Invite team members and set permissions

### Week 2: Views and Visualization
- [ ] Create Kanban view for workflow management
- [ ] Set up Timeline view for project planning
- [ ] Build Calendar view for deadline tracking
- [ ] Customize views with filters and sorting

### Week 3: Collaboration
- [ ] Start using comments and mentions
- [ ] Set up activity notifications
- [ ] Practice real-time collaboration
- [ ] Create shared views for team use

### Week 4: Automation and Dashboards
- [ ] Build first automation workflow
- [ ] Create dashboard with key metrics
- [ ] Set up integrations with other tools
- [ ] Optimize performance and organization

## 🆘 Getting Help

### Self-Service Resources
- **Help Center**: Searchable knowledge base
- **Video Tutorials**: Step-by-step visual guides
- **Community Forum**: Ask questions, share tips
- **Template Gallery**: Pre-built solutions for common use cases

### Direct Support
- **In-app Chat**: Quick questions and technical issues
- **Email Support**: Detailed questions and bug reports
- **Enterprise Support**: Priority support for business customers

### Community
- **Discord**: Real-time chat with other users
- **GitHub**: Feature requests and bug reports
- **Social Media**: Updates and tips on Twitter/LinkedIn

## 🔗 What's Next?

Now that you've got the basics down, explore these advanced topics:

1. **[View Types Guide](view-types.md)** - Master all view types
2. **[Automation Guide](automation.md)** - Build powerful workflows
3. **[Dashboard Guide](dashboards.md)** - Create stunning visualizations
4. **[API Documentation](../api/overview.md)** - Integrate with other tools
5. **[Mobile Guide](mobile.md)** - Optimize for mobile usage

---

**Ready to dive deeper?** Check out our [View Types Guide](view-types.md) to master Kanban, Timeline, and Calendar views, or jump into [Automation](automation.md) to start building powerful workflows!