# Automation User Guide

Automate repetitive tasks and create powerful workflows that respond to data changes, dates, and external events to streamline your processes.

## What is Automation?

Automation in Baserow allows you to create "If this, then that" rules that automatically perform actions when specific conditions are met. This eliminates manual work and ensures consistent processes across your organization.

### Key Features
- **Visual Workflow Builder** - Drag-and-drop interface for creating automations
- **Multiple Trigger Types** - Record changes, dates, external events, and more
- **Powerful Actions** - Update records, send notifications, call webhooks
- **Conditional Logic** - Complex branching and decision-making
- **Error Handling** - Robust error handling with retry mechanisms
- **Monitoring** - Track automation execution and performance

## Getting Started with Automation

### Creating Your First Automation

1. **Navigate to Automations**
   - Go to your table or workspace
   - Click on the **Automations** tab
   - Click **+ New Automation**

2. **Choose a Trigger**
   - Select what event will start your automation
   - Configure the trigger conditions
   - Test the trigger to ensure it works

3. **Add Actions**
   - Choose what happens when the trigger fires
   - Configure action parameters
   - Add multiple actions if needed

4. **Test and Activate**
   - Test your automation with sample data
   - Review the execution log
   - Activate the automation

### Example: Task Assignment Notification
```
Trigger: When "Assignee" field is updated
Condition: Assignee is not empty
Action: Send email notification to assigned user
```

## Trigger Types

### Record-Based Triggers

#### Record Created
Fires when a new record is added to a table.

**Configuration:**
- **Table**: Which table to monitor
- **Conditions**: Optional filters for specific records
- **Fields**: Monitor specific field values

**Use Cases:**
- Welcome new customers
- Assign default values
- Create related records
- Send notifications

#### Record Updated
Fires when an existing record is modified.

**Configuration:**
- **Table**: Which table to monitor
- **Fields**: Specific fields to watch for changes
- **Conditions**: Only trigger for certain values
- **Change Type**: Any change, specific values, or value ranges

**Use Cases:**
- Status change notifications
- Approval workflows
- Data validation
- Progress tracking

#### Record Deleted
Fires when a record is removed from a table.

**Configuration:**
- **Table**: Which table to monitor
- **Conditions**: Filter which deletions trigger automation
- **Backup Actions**: Archive or backup deleted data

**Use Cases:**
- Cleanup related records
- Send deletion notifications
- Archive important data
- Update counters

### Date-Based Triggers

#### Date Reached
Fires when a date field reaches a specific date.

**Configuration:**
- **Date Field**: Field containing the target date
- **Timing**: Exact date, before, or after
- **Offset**: Days/hours before or after the date
- **Recurring**: One-time or recurring trigger

**Use Cases:**
- Project deadline reminders
- Contract renewal alerts
- Birthday notifications
- Subscription renewals

#### Scheduled Trigger
Fires at regular intervals regardless of data changes.

**Configuration:**
- **Schedule**: Daily, weekly, monthly, or custom cron
- **Time**: Specific time of day
- **Timezone**: Account for different timezones
- **Conditions**: Optional data conditions

**Use Cases:**
- Daily reports
- Data cleanup
- Backup processes
- Periodic notifications

### External Triggers

#### Webhook Trigger
Fires when an external system sends a webhook.

**Configuration:**
- **Webhook URL**: Unique URL for your automation
- **Authentication**: Optional security tokens
- **Payload Mapping**: Map webhook data to table fields
- **Validation**: Verify webhook authenticity

**Use Cases:**
- Form submissions
- Payment notifications
- External system updates
- API integrations

#### API Trigger
Fires when specific API calls are made.

**Configuration:**
- **Endpoint**: Which API endpoint to monitor
- **Method**: GET, POST, PUT, DELETE
- **Parameters**: Required parameters
- **Authentication**: API key or token validation

**Use Cases:**
- Custom integrations
- Mobile app actions
- Third-party services
- Automated imports

## Action Types

### Data Actions

#### Update Record
Modify fields in existing records.

**Configuration:**
- **Target Record**: Same record, related record, or specific record
- **Field Updates**: Which fields to update and their new values
- **Conditions**: Only update if certain conditions are met
- **Bulk Updates**: Update multiple records at once

**Examples:**
- Set status to "Complete" when all subtasks are done
- Update priority based on due date
- Calculate totals from related records

#### Create Record
Add new records to tables.

**Configuration:**
- **Target Table**: Where to create the record
- **Field Values**: Values for the new record
- **Data Source**: Use trigger data or static values
- **Duplicate Prevention**: Avoid creating duplicate records

**Examples:**
- Create follow-up tasks
- Generate invoices from orders
- Add entries to activity logs

#### Delete Record
Remove records from tables.

**Configuration:**
- **Target Record**: Which record to delete
- **Conditions**: Safety conditions before deletion
- **Backup**: Archive before deletion
- **Related Records**: Handle linked records

**Examples:**
- Remove expired records
- Clean up test data
- Archive completed projects

### Communication Actions

#### Send Email
Send email notifications to users or external addresses.

**Configuration:**
- **Recipients**: Users, email addresses, or field values
- **Subject**: Dynamic subject lines with field data
- **Body**: Rich text with field placeholders
- **Attachments**: Include files from file fields
- **Templates**: Reusable email templates

**Examples:**
- Task assignment notifications
- Status update alerts
- Weekly progress reports
- Customer communications

#### Send Slack Message
Post messages to Slack channels or direct messages.

**Configuration:**
- **Channel**: Slack channel or user
- **Message**: Text with field data
- **Formatting**: Rich formatting and mentions
- **Attachments**: Include files or links

**Examples:**
- Team notifications
- Alert messages
- Progress updates
- Integration announcements

#### Send Teams Message
Post messages to Microsoft Teams channels.

**Configuration:**
- **Team/Channel**: Target Teams channel
- **Message**: Formatted message content
- **Mentions**: Tag specific users
- **Cards**: Rich card formatting

**Examples:**
- Project updates
- Meeting reminders
- Status alerts
- Collaboration notifications

### External Actions

#### Call Webhook
Send HTTP requests to external services.

**Configuration:**
- **URL**: Target webhook URL
- **Method**: GET, POST, PUT, DELETE
- **Headers**: Custom HTTP headers
- **Body**: JSON payload with field data
- **Authentication**: API keys or tokens

**Examples:**
- Update external systems
- Trigger third-party workflows
- Send data to analytics tools
- Integrate with custom applications

#### API Call
Make structured API calls to external services.

**Configuration:**
- **Service**: Predefined service or custom endpoint
- **Operation**: Specific API operation
- **Parameters**: Required and optional parameters
- **Response Handling**: Process API responses

**Examples:**
- Update CRM records
- Send SMS messages
- Create calendar events
- Sync with external databases

## Visual Workflow Builder

### Drag-and-Drop Interface

The visual workflow builder makes it easy to create complex automations:

1. **Trigger Block**: Starting point for your automation
2. **Condition Blocks**: Add decision points and branching
3. **Action Blocks**: Define what actions to take
4. **Connection Lines**: Show the flow between blocks

### Building Complex Workflows

#### Conditional Branching
```
Trigger: Record Updated
├─ If Priority = "High"
│  ├─ Send urgent notification
│  └─ Assign to senior team member
└─ If Priority = "Low"
   └─ Add to backlog
```

#### Sequential Actions
```
Trigger: Order Created
├─ Action 1: Send confirmation email
├─ Action 2: Update inventory
├─ Action 3: Create shipping record
└─ Action 4: Notify fulfillment team
```

#### Parallel Actions
```
Trigger: Project Completed
├─ Send client notification (parallel)
├─ Update project status (parallel)
├─ Generate invoice (parallel)
└─ Archive project files (parallel)
```

### Testing and Debugging

#### Test Mode
- **Dry Run**: Execute automation without making changes
- **Sample Data**: Use test data to verify logic
- **Step-by-Step**: See each action's result
- **Error Simulation**: Test error handling

#### Execution Logs
- **Trigger Events**: When and why automations fired
- **Action Results**: Success/failure of each action
- **Error Details**: Detailed error messages
- **Performance Metrics**: Execution time and resource usage

## Automation Templates

### Project Management Templates

#### Task Assignment Workflow
```
Trigger: Task created with assignee
Actions:
1. Send email to assignee
2. Add to assignee's calendar
3. Set status to "Assigned"
4. Create subtasks if template exists
```

#### Project Completion Workflow
```
Trigger: All project tasks marked complete
Actions:
1. Update project status to "Complete"
2. Send completion notification to stakeholders
3. Generate project report
4. Archive project files
5. Create follow-up tasks
```

### Sales and CRM Templates

#### Lead Qualification Workflow
```
Trigger: New lead created
Actions:
1. Score lead based on criteria
2. Assign to appropriate sales rep
3. Send welcome email sequence
4. Create follow-up tasks
5. Add to nurture campaign
```

#### Deal Closure Workflow
```
Trigger: Deal status changed to "Won"
Actions:
1. Generate contract
2. Send to legal for review
3. Create onboarding tasks
4. Update sales forecasts
5. Notify customer success team
```

### Customer Support Templates

#### Ticket Escalation Workflow
```
Trigger: Ticket unresolved for 24 hours
Actions:
1. Increase priority level
2. Assign to senior support agent
3. Notify customer of escalation
4. Add to management dashboard
5. Schedule follow-up check
```

#### Customer Satisfaction Workflow
```
Trigger: Ticket marked as resolved
Actions:
1. Wait 2 hours
2. Send satisfaction survey
3. If rating < 3, create follow-up ticket
4. Update agent performance metrics
5. Add to customer history
```

## Advanced Automation Features

### Conditional Logic

#### If-Then-Else Statements
```
If customer_type = "Premium"
  Then assign to premium support queue
  Else assign to standard support queue
```

#### Multiple Conditions
```
If priority = "High" AND customer_type = "Enterprise"
  Then notify account manager immediately
  Else follow standard escalation process
```

#### Field Comparisons
```
If due_date < today + 3 days
  Then send urgent reminder
  Else send standard reminder
```

### Data Transformations

#### Field Calculations
- **Mathematical Operations**: Add, subtract, multiply, divide
- **Text Operations**: Concatenate, format, extract
- **Date Operations**: Add days, format dates, calculate differences
- **Lookup Operations**: Get data from related records

#### Data Validation
- **Format Checking**: Email, phone, URL validation
- **Range Validation**: Numeric ranges, date ranges
- **Required Fields**: Ensure critical fields are filled
- **Duplicate Detection**: Prevent duplicate entries

### Error Handling

#### Retry Logic
- **Automatic Retries**: Retry failed actions automatically
- **Retry Intervals**: Exponential backoff for retries
- **Maximum Attempts**: Limit retry attempts
- **Failure Actions**: What to do after all retries fail

#### Error Notifications
- **Admin Alerts**: Notify administrators of failures
- **Error Logging**: Detailed error logs for debugging
- **Fallback Actions**: Alternative actions when primary fails
- **Recovery Procedures**: Automatic recovery from errors

## Monitoring and Analytics

### Automation Dashboard
- **Active Automations**: List of all active automations
- **Execution Statistics**: Success rates, failure rates
- **Performance Metrics**: Average execution time
- **Resource Usage**: System resource consumption

### Execution History
- **Detailed Logs**: Complete execution history
- **Filtering**: Filter by automation, date, status
- **Search**: Search logs for specific events
- **Export**: Export logs for analysis

### Performance Optimization
- **Bottleneck Identification**: Find slow automations
- **Resource Monitoring**: Track CPU and memory usage
- **Optimization Suggestions**: Recommendations for improvement
- **Scaling Guidance**: When to scale automation infrastructure

## Best Practices

### Design Principles
- **Single Responsibility**: Each automation should have one clear purpose
- **Fail-Safe Design**: Handle errors gracefully
- **Idempotent Actions**: Actions should be safe to repeat
- **Clear Naming**: Use descriptive names for automations

### Performance Guidelines
- **Batch Operations**: Process multiple records together when possible
- **Avoid Loops**: Prevent infinite automation loops
- **Rate Limiting**: Respect external API rate limits
- **Resource Management**: Monitor system resource usage

### Security Considerations
- **Permission Checks**: Ensure automations respect user permissions
- **Data Validation**: Validate all input data
- **Secure Communications**: Use HTTPS for external calls
- **Audit Trails**: Maintain logs for security auditing

### Testing Strategy
- **Unit Testing**: Test individual automation components
- **Integration Testing**: Test complete automation workflows
- **Load Testing**: Test with high volumes of data
- **User Acceptance Testing**: Verify automations meet business needs

## Troubleshooting

### Common Issues

**Automation not triggering**
- Check trigger conditions
- Verify table permissions
- Review filter criteria
- Check automation status (active/inactive)

**Actions failing**
- Review error logs
- Check external service availability
- Verify API credentials
- Test with simpler actions

**Performance problems**
- Reduce automation complexity
- Optimize database queries
- Implement batching
- Review resource usage

### Debugging Tools
- **Execution Logs**: Detailed step-by-step execution
- **Test Mode**: Safe testing environment
- **Error Alerts**: Real-time error notifications
- **Performance Metrics**: Execution time analysis

Automation transforms how you work with data, eliminating repetitive tasks and ensuring consistent processes. Start with simple automations and gradually build more complex workflows as your confidence grows.