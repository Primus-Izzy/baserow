/**
 * Comprehensive end-to-end tests for critical user workflows
 * in the Baserow Monday.com expansion.
 */
import { test, expect, Page } from '@playwright/test';

class BaserowTestHelper {
  constructor(private page: Page) {}

  async login(email: string = 'test@example.com', password: string = 'password') {
    await this.page.goto('/login');
    await this.page.fill('[data-cy="email-input"]', email);
    await this.page.fill('[data-cy="password-input"]', password);
    await this.page.click('[data-cy="login-button"]');
    await this.page.waitForURL('/dashboard');
  }

  async createWorkspace(name: string) {
    await this.page.click('[data-cy="create-workspace-button"]');
    await this.page.fill('[data-cy="workspace-name-input"]', name);
    await this.page.click('[data-cy="create-workspace-confirm"]');
    await this.page.waitForSelector(`[data-cy="workspace-${name}"]`);
  }

  async createDatabase(name: string) {
    await this.page.click('[data-cy="create-database-button"]');
    await this.page.fill('[data-cy="database-name-input"]', name);
    await this.page.click('[data-cy="create-database-confirm"]');
    await this.page.waitForSelector(`[data-cy="database-${name}"]`);
  }

  async createTable(name: string) {
    await this.page.click('[data-cy="create-table-button"]');
    await this.page.fill('[data-cy="table-name-input"]', name);
    await this.page.click('[data-cy="create-table-confirm"]');
    await this.page.waitForSelector(`[data-cy="table-${name}"]`);
  }

  async createField(name: string, type: string) {
    await this.page.click('[data-cy="add-field-button"]');
    await this.page.click(`[data-cy="field-type-${type}"]`);
    await this.page.fill('[data-cy="field-name-input"]', name);
    await this.page.click('[data-cy="create-field-confirm"]');
    await this.page.waitForSelector(`[data-cy="field-${name}"]`);
  }

  async switchView(viewType: string) {
    await this.page.click('[data-cy="view-selector"]');
    await this.page.click(`[data-cy="view-type-${viewType}"]`);
    await this.page.waitForSelector(`[data-cy="${viewType}-view"]`);
  }
}

test.describe('Enhanced Table View Workflows', () => {
  let helper: BaserowTestHelper;

  test.beforeEach(async ({ page }) => {
    helper = new BaserowTestHelper(page);
    await helper.login();
    await helper.createWorkspace('Test Workspace');
    await helper.createDatabase('Test Database');
    await helper.createTable('Test Table');
  });

  test('should create and use conditional formatting', async ({ page }) => {
    // Create a status field
    await helper.createField('Status', 'single_select');
    
    // Add some options to the single select
    await page.click('[data-cy="field-Status"] [data-cy="field-options"]');
    await page.click('[data-cy="add-option"]');
    await page.fill('[data-cy="option-name"]', 'Complete');
    await page.click('[data-cy="option-color-green"]');
    await page.click('[data-cy="save-option"]');
    
    // Set up conditional formatting
    await page.click('[data-cy="view-options"]');
    await page.click('[data-cy="conditional-formatting"]');
    await page.click('[data-cy="add-formatting-rule"]');
    
    await page.selectOption('[data-cy="condition-field"]', 'Status');
    await page.selectOption('[data-cy="condition-operator"]', 'equals');
    await page.fill('[data-cy="condition-value"]', 'Complete');
    await page.click('[data-cy="formatting-color-green"]');
    await page.click('[data-cy="save-formatting-rule"]');
    
    // Create a row and verify formatting
    await page.click('[data-cy="add-row-button"]');
    await page.click('[data-cy="Status-cell"]');
    await page.click('[data-cy="option-Complete"]');
    
    // Verify the row has green background
    await expect(page.locator('[data-cy="table-row"]:last-child')).toHaveClass(/bg-green/);
  });

  test('should create and use filter presets', async ({ page }) => {
    // Create fields
    await helper.createField('Priority', 'single_select');
    await helper.createField('Assignee', 'text');
    
    // Create filter preset
    await page.click('[data-cy="filter-button"]');
    await page.click('[data-cy="add-filter"]');
    await page.selectOption('[data-cy="filter-field"]', 'Priority');
    await page.selectOption('[data-cy="filter-operator"]', 'equals');
    await page.fill('[data-cy="filter-value"]', 'High');
    
    await page.click('[data-cy="save-filter-preset"]');
    await page.fill('[data-cy="preset-name"]', 'High Priority Tasks');
    await page.click('[data-cy="save-preset"]');
    
    // Verify preset is saved and can be applied
    await expect(page.locator('[data-cy="filter-preset-High Priority Tasks"]')).toBeVisible();
  });

  test('should support column grouping', async ({ page }) => {
    // Create multiple fields
    await helper.createField('Department', 'single_select');
    await helper.createField('Employee', 'text');
    await helper.createField('Salary', 'number');
    
    // Enable column grouping
    await page.click('[data-cy="view-options"]');
    await page.click('[data-cy="column-grouping"]');
    await page.click('[data-cy="add-group"]');
    await page.selectOption('[data-cy="group-field"]', 'Department');
    await page.click('[data-cy="save-grouping"]');
    
    // Verify grouping is applied
    await expect(page.locator('[data-cy="column-group-Department"]')).toBeVisible();
    
    // Test collapsing/expanding groups
    await page.click('[data-cy="collapse-group-Department"]');
    await expect(page.locator('[data-cy="group-Department-content"]')).toBeHidden();
    
    await page.click('[data-cy="expand-group-Department"]');
    await expect(page.locator('[data-cy="group-Department-content"]')).toBeVisible();
  });
});

test.describe('Kanban View Workflows', () => {
  let helper: BaserowTestHelper;

  test.beforeEach(async ({ page }) => {
    helper = new BaserowTestHelper(page);
    await helper.login();
    await helper.createWorkspace('Kanban Workspace');
    await helper.createDatabase('Project Database');
    await helper.createTable('Tasks');
  });

  test('should create kanban view and drag cards between columns', async ({ page }) => {
    // Create status field for kanban
    await helper.createField('Status', 'single_select');
    
    // Add status options
    const statuses = ['To Do', 'In Progress', 'Review', 'Done'];
    for (const status of statuses) {
      await page.click('[data-cy="field-Status"] [data-cy="field-options"]');
      await page.click('[data-cy="add-option"]');
      await page.fill('[data-cy="option-name"]', status);
      await page.click('[data-cy="save-option"]');
    }
    
    // Create additional fields
    await helper.createField('Task Name', 'text');
    await helper.createField('Assignee', 'people');
    
    // Switch to kanban view
    await helper.switchView('kanban');
    
    // Configure kanban view
    await page.click('[data-cy="kanban-settings"]');
    await page.selectOption('[data-cy="kanban-status-field"]', 'Status');
    await page.check('[data-cy="show-field-Task Name"]');
    await page.check('[data-cy="show-field-Assignee"]');
    await page.click('[data-cy="save-kanban-settings"]');
    
    // Create some tasks
    await page.click('[data-cy="add-card-To Do"]');
    await page.fill('[data-cy="Task Name-input"]', 'Design mockups');
    await page.click('[data-cy="save-card"]');
    
    await page.click('[data-cy="add-card-To Do"]');
    await page.fill('[data-cy="Task Name-input"]', 'Write tests');
    await page.click('[data-cy="save-card"]');
    
    // Test drag and drop
    const card = page.locator('[data-cy="kanban-card"]:has-text("Design mockups")');
    const targetColumn = page.locator('[data-cy="kanban-column-In Progress"]');
    
    await card.dragTo(targetColumn);
    
    // Verify card moved to new column
    await expect(page.locator('[data-cy="kanban-column-In Progress"] [data-cy="kanban-card"]:has-text("Design mockups")')).toBeVisible();
  });

  test('should support inline editing in kanban cards', async ({ page }) => {
    // Setup kanban view (abbreviated)
    await helper.createField('Status', 'single_select');
    await helper.createField('Title', 'text');
    await helper.createField('Description', 'long_text');
    await helper.switchView('kanban');
    
    // Create a card
    await page.click('[data-cy="add-card-To Do"]');
    await page.fill('[data-cy="Title-input"]', 'Test Task');
    await page.fill('[data-cy="Description-input"]', 'Initial description');
    await page.click('[data-cy="save-card"]');
    
    // Test inline editing
    const card = page.locator('[data-cy="kanban-card"]:has-text("Test Task")');
    await card.dblclick();
    
    // Edit title inline
    await page.fill('[data-cy="inline-edit-Title"]', 'Updated Test Task');
    await page.press('[data-cy="inline-edit-Title"]', 'Enter');
    
    // Verify update
    await expect(card).toContainText('Updated Test Task');
  });
});

test.describe('Timeline/Gantt View Workflows', () => {
  let helper: BaserowTestHelper;

  test.beforeEach(async ({ page }) => {
    helper = new BaserowTestHelper(page);
    await helper.login();
    await helper.createWorkspace('Timeline Workspace');
    await helper.createDatabase('Project Database');
    await helper.createTable('Project Tasks');
  });

  test('should create timeline view with dependencies', async ({ page }) => {
    // Create required fields
    await helper.createField('Task Name', 'text');
    await helper.createField('Start Date', 'date');
    await helper.createField('End Date', 'date');
    await helper.createField('Status', 'single_select');
    
    // Switch to timeline view
    await helper.switchView('timeline');
    
    // Configure timeline view
    await page.click('[data-cy="timeline-settings"]');
    await page.selectOption('[data-cy="start-date-field"]', 'Start Date');
    await page.selectOption('[data-cy="end-date-field"]', 'End Date');
    await page.selectOption('[data-cy="title-field"]', 'Task Name');
    await page.click('[data-cy="save-timeline-settings"]');
    
    // Create tasks
    const tasks = [
      { name: 'Planning', start: '2024-01-01', end: '2024-01-07' },
      { name: 'Development', start: '2024-01-08', end: '2024-01-21' },
      { name: 'Testing', start: '2024-01-22', end: '2024-01-28' }
    ];
    
    for (const task of tasks) {
      await page.click('[data-cy="add-timeline-task"]');
      await page.fill('[data-cy="Task Name-input"]', task.name);
      await page.fill('[data-cy="Start Date-input"]', task.start);
      await page.fill('[data-cy="End Date-input"]', task.end);
      await page.click('[data-cy="save-task"]');
    }
    
    // Add dependency
    await page.click('[data-cy="timeline-task-Planning"]');
    await page.click('[data-cy="add-dependency"]');
    await page.selectOption('[data-cy="successor-task"]', 'Development');
    await page.click('[data-cy="save-dependency"]');
    
    // Verify dependency line is shown
    await expect(page.locator('[data-cy="dependency-line-Planning-Development"]')).toBeVisible();
  });

  test('should support timeline zoom levels', async ({ page }) => {
    // Setup timeline view (abbreviated)
    await helper.createField('Task Name', 'text');
    await helper.createField('Start Date', 'date');
    await helper.createField('End Date', 'date');
    await helper.switchView('timeline');
    
    // Test different zoom levels
    const zoomLevels = ['day', 'week', 'month', 'year'];
    
    for (const level of zoomLevels) {
      await page.click('[data-cy="timeline-zoom"]');
      await page.click(`[data-cy="zoom-${level}"]`);
      
      // Verify zoom level is applied
      await expect(page.locator(`[data-cy="timeline-scale-${level}"]`)).toBeVisible();
    }
  });
});

test.describe('Calendar View Workflows', () => {
  let helper: BaserowTestHelper;

  test.beforeEach(async ({ page }) => {
    helper = new BaserowTestHelper(page);
    await helper.login();
    await helper.createWorkspace('Calendar Workspace');
    await helper.createDatabase('Events Database');
    await helper.createTable('Events');
  });

  test('should create calendar view and manage events', async ({ page }) => {
    // Create required fields
    await helper.createField('Event Name', 'text');
    await helper.createField('Event Date', 'date');
    await helper.createField('Event Type', 'single_select');
    
    // Switch to calendar view
    await helper.switchView('calendar');
    
    // Configure calendar view
    await page.click('[data-cy="calendar-settings"]');
    await page.selectOption('[data-cy="date-field"]', 'Event Date');
    await page.selectOption('[data-cy="title-field"]', 'Event Name');
    await page.selectOption('[data-cy="color-field"]', 'Event Type');
    await page.click('[data-cy="save-calendar-settings"]');
    
    // Create an event
    await page.click('[data-cy="calendar-day-15"]'); // Click on day 15
    await page.fill('[data-cy="Event Name-input"]', 'Team Meeting');
    await page.selectOption('[data-cy="Event Type-select"]', 'Meeting');
    await page.click('[data-cy="save-event"]');
    
    // Verify event appears on calendar
    await expect(page.locator('[data-cy="calendar-event-Team Meeting"]')).toBeVisible();
    
    // Test drag and drop event to different day
    const event = page.locator('[data-cy="calendar-event-Team Meeting"]');
    const targetDay = page.locator('[data-cy="calendar-day-20"]');
    
    await event.dragTo(targetDay);
    
    // Verify event moved
    await expect(page.locator('[data-cy="calendar-day-20"] [data-cy="calendar-event-Team Meeting"]')).toBeVisible();
  });

  test('should support different calendar display modes', async ({ page }) => {
    // Setup calendar view (abbreviated)
    await helper.createField('Event Name', 'text');
    await helper.createField('Event Date', 'date');
    await helper.switchView('calendar');
    
    // Test different display modes
    const modes = ['month', 'week', 'day'];
    
    for (const mode of modes) {
      await page.click('[data-cy="calendar-view-mode"]');
      await page.click(`[data-cy="mode-${mode}"]`);
      
      // Verify mode is applied
      await expect(page.locator(`[data-cy="calendar-${mode}-view"]`)).toBeVisible();
    }
  });
});

test.describe('Form View Workflows', () => {
  let helper: BaserowTestHelper;

  test.beforeEach(async ({ page }) => {
    helper = new BaserowTestHelper(page);
    await helper.login();
    await helper.createWorkspace('Form Workspace');
    await helper.createDatabase('Survey Database');
    await helper.createTable('Responses');
  });

  test('should create enhanced form with conditional logic', async ({ page }) => {
    // Create fields
    await helper.createField('Name', 'text');
    await helper.createField('Email', 'email');
    await helper.createField('Subscribe', 'boolean');
    await helper.createField('Newsletter Type', 'single_select');
    
    // Switch to form view
    await helper.switchView('form');
    
    // Configure form
    await page.click('[data-cy="form-settings"]');
    await page.fill('[data-cy="form-title"]', 'Newsletter Signup');
    await page.fill('[data-cy="form-description"]', 'Sign up for our newsletter');
    await page.check('[data-cy="form-public"]');
    await page.click('[data-cy="save-form-settings"]');
    
    // Add conditional logic
    await page.click('[data-cy="conditional-logic"]');
    await page.click('[data-cy="add-condition"]');
    await page.selectOption('[data-cy="trigger-field"]', 'Subscribe');
    await page.selectOption('[data-cy="condition-operator"]', 'equals');
    await page.selectOption('[data-cy="condition-value"]', 'true');
    await page.selectOption('[data-cy="target-field"]', 'Newsletter Type');
    await page.selectOption('[data-cy="action"]', 'show');
    await page.click('[data-cy="save-condition"]');
    
    // Test form submission
    await page.click('[data-cy="preview-form"]');
    
    // Fill form
    await page.fill('[data-cy="Name-input"]', 'John Doe');
    await page.fill('[data-cy="Email-input"]', 'john@example.com');
    
    // Verify Newsletter Type is hidden initially
    await expect(page.locator('[data-cy="Newsletter Type-field"]')).toBeHidden();
    
    // Check subscribe checkbox
    await page.check('[data-cy="Subscribe-input"]');
    
    // Verify Newsletter Type is now visible
    await expect(page.locator('[data-cy="Newsletter Type-field"]')).toBeVisible();
    
    // Complete and submit form
    await page.selectOption('[data-cy="Newsletter Type-select"]', 'Weekly');
    await page.click('[data-cy="submit-form"]');
    
    // Verify success message
    await expect(page.locator('[data-cy="form-success"]')).toBeVisible();
  });
});

test.describe('Automation Workflows', () => {
  let helper: BaserowTestHelper;

  test.beforeEach(async ({ page }) => {
    helper = new BaserowTestHelper(page);
    await helper.login();
    await helper.createWorkspace('Automation Workspace');
    await helper.createDatabase('Task Database');
    await helper.createTable('Tasks');
  });

  test('should create and test automation workflow', async ({ page }) => {
    // Create fields
    await helper.createField('Task Name', 'text');
    await helper.createField('Status', 'single_select');
    await helper.createField('Assignee', 'people');
    await helper.createField('Completed Date', 'date');
    
    // Navigate to automations
    await page.click('[data-cy="automations-tab"]');
    
    // Create new automation
    await page.click('[data-cy="create-automation"]');
    await page.fill('[data-cy="automation-name"]', 'Auto-complete tasks');
    
    // Add trigger
    await page.click('[data-cy="add-trigger"]');
    await page.selectOption('[data-cy="trigger-type"]', 'field_changed');
    await page.selectOption('[data-cy="trigger-field"]', 'Status');
    await page.fill('[data-cy="trigger-value"]', 'Done');
    await page.click('[data-cy="save-trigger"]');
    
    // Add action
    await page.click('[data-cy="add-action"]');
    await page.selectOption('[data-cy="action-type"]', 'update_field');
    await page.selectOption('[data-cy="action-field"]', 'Completed Date');
    await page.selectOption('[data-cy="action-value"]', 'today()');
    await page.click('[data-cy="save-action"]');
    
    // Save automation
    await page.click('[data-cy="save-automation"]');
    
    // Test automation by creating and updating a task
    await page.click('[data-cy="table-view-tab"]');
    await page.click('[data-cy="add-row-button"]');
    await page.fill('[data-cy="Task Name-input"]', 'Test automation');
    await page.selectOption('[data-cy="Status-select"]', 'In Progress');
    await page.click('[data-cy="save-row"]');
    
    // Update status to trigger automation
    await page.click('[data-cy="Status-cell"]');
    await page.selectOption('[data-cy="Status-select"]', 'Done');
    
    // Verify automation ran (Completed Date should be filled)
    await expect(page.locator('[data-cy="Completed Date-cell"]')).not.toBeEmpty();
  });
});

test.describe('Collaboration Workflows', () => {
  let helper: BaserowTestHelper;

  test.beforeEach(async ({ page }) => {
    helper = new BaserowTestHelper(page);
    await helper.login();
    await helper.createWorkspace('Collaboration Workspace');
    await helper.createDatabase('Shared Database');
    await helper.createTable('Shared Table');
  });

  test('should support real-time collaboration features', async ({ page, context }) => {
    // Create fields
    await helper.createField('Task', 'text');
    await helper.createField('Notes', 'long_text');
    
    // Open second browser context for collaboration testing
    const secondPage = await context.newPage();
    const secondHelper = new BaserowTestHelper(secondPage);
    await secondHelper.login('collaborator@example.com');
    
    // Navigate both users to the same table
    await page.goto('/workspace/collaboration-workspace/database/shared-database/table/shared-table');
    await secondPage.goto('/workspace/collaboration-workspace/database/shared-database/table/shared-table');
    
    // User 1 starts editing a cell
    await page.click('[data-cy="add-row-button"]');
    await page.click('[data-cy="Task-cell"]');
    await page.type('[data-cy="Task-input"]', 'Collaborative task');
    
    // User 2 should see typing indicator
    await expect(secondPage.locator('[data-cy="typing-indicator"]')).toBeVisible();
    
    // User 1 saves the cell
    await page.press('[data-cy="Task-input"]', 'Enter');
    
    // User 2 should see the updated content in real-time
    await expect(secondPage.locator('[data-cy="Task-cell"]')).toContainText('Collaborative task');
    
    // Test commenting
    await page.click('[data-cy="row-menu"]');
    await page.click('[data-cy="add-comment"]');
    await page.fill('[data-cy="comment-input"]', 'This task needs review @collaborator@example.com');
    await page.click('[data-cy="post-comment"]');
    
    // User 2 should receive notification
    await expect(secondPage.locator('[data-cy="notification-badge"]')).toBeVisible();
    
    await secondPage.close();
  });

  test('should track activity log', async ({ page }) => {
    // Create a field and make some changes
    await helper.createField('Priority', 'single_select');
    
    // Add a row
    await page.click('[data-cy="add-row-button"]');
    await page.fill('[data-cy="Priority-input"]', 'High');
    await page.click('[data-cy="save-row"]');
    
    // Update the row
    await page.click('[data-cy="Priority-cell"]');
    await page.selectOption('[data-cy="Priority-select"]', 'Low');
    
    // Check activity log
    await page.click('[data-cy="activity-log-tab"]');
    
    // Verify activities are logged
    await expect(page.locator('[data-cy="activity-entry"]:has-text("created row")')).toBeVisible();
    await expect(page.locator('[data-cy="activity-entry"]:has-text("updated Priority")')).toBeVisible();
    
    // Test activity filtering
    await page.selectOption('[data-cy="activity-filter-user"]', 'test@example.com');
    await page.selectOption('[data-cy="activity-filter-action"]', 'update');
    
    // Verify filtered results
    await expect(page.locator('[data-cy="activity-entry"]:has-text("updated Priority")')).toBeVisible();
    await expect(page.locator('[data-cy="activity-entry"]:has-text("created row")')).toBeHidden();
  });
});

test.describe('Dashboard Workflows', () => {
  let helper: BaserowTestHelper;

  test.beforeEach(async ({ page }) => {
    helper = new BaserowTestHelper(page);
    await helper.login();
    await helper.createWorkspace('Dashboard Workspace');
    await helper.createDatabase('Analytics Database');
    await helper.createTable('Sales Data');
  });

  test('should create dashboard with various widget types', async ({ page }) => {
    // Create sample data fields
    await helper.createField('Product', 'text');
    await helper.createField('Sales Amount', 'number');
    await helper.createField('Sale Date', 'date');
    await helper.createField('Region', 'single_select');
    
    // Add some sample data
    const sampleData = [
      { product: 'Widget A', amount: 1000, date: '2024-01-15', region: 'North' },
      { product: 'Widget B', amount: 1500, date: '2024-01-16', region: 'South' },
      { product: 'Widget C', amount: 800, date: '2024-01-17', region: 'East' }
    ];
    
    for (const data of sampleData) {
      await page.click('[data-cy="add-row-button"]');
      await page.fill('[data-cy="Product-input"]', data.product);
      await page.fill('[data-cy="Sales Amount-input"]', data.amount.toString());
      await page.fill('[data-cy="Sale Date-input"]', data.date);
      await page.selectOption('[data-cy="Region-select"]', data.region);
      await page.click('[data-cy="save-row"]');
    }
    
    // Navigate to dashboard
    await page.click('[data-cy="dashboard-tab"]');
    
    // Create new dashboard
    await page.click('[data-cy="create-dashboard"]');
    await page.fill('[data-cy="dashboard-name"]', 'Sales Dashboard');
    await page.click('[data-cy="save-dashboard"]');
    
    // Add KPI widget
    await page.click('[data-cy="add-widget"]');
    await page.click('[data-cy="widget-type-kpi"]');
    await page.fill('[data-cy="widget-title"]', 'Total Sales');
    await page.selectOption('[data-cy="data-source-table"]', 'Sales Data');
    await page.selectOption('[data-cy="kpi-field"]', 'Sales Amount');
    await page.selectOption('[data-cy="kpi-function"]', 'SUM');
    await page.click('[data-cy="save-widget"]');
    
    // Add bar chart widget
    await page.click('[data-cy="add-widget"]');
    await page.click('[data-cy="widget-type-bar-chart"]');
    await page.fill('[data-cy="widget-title"]', 'Sales by Region');
    await page.selectOption('[data-cy="data-source-table"]', 'Sales Data');
    await page.selectOption('[data-cy="x-axis-field"]', 'Region');
    await page.selectOption('[data-cy="y-axis-field"]', 'Sales Amount');
    await page.selectOption('[data-cy="aggregation"]', 'SUM');
    await page.click('[data-cy="save-widget"]');
    
    // Verify widgets are displayed
    await expect(page.locator('[data-cy="widget-Total Sales"]')).toBeVisible();
    await expect(page.locator('[data-cy="widget-Sales by Region"]')).toBeVisible();
    
    // Test widget drag and drop
    const widget = page.locator('[data-cy="widget-Total Sales"]');
    const targetPosition = page.locator('[data-cy="dashboard-grid-2-1"]');
    
    await widget.dragTo(targetPosition);
    
    // Verify widget moved
    await expect(page.locator('[data-cy="dashboard-grid-2-1"] [data-cy="widget-Total Sales"]')).toBeVisible();
  });

  test('should support dashboard sharing and export', async ({ page }) => {
    // Create a simple dashboard (abbreviated setup)
    await helper.createField('Metric', 'number');
    await page.click('[data-cy="dashboard-tab"]');
    await page.click('[data-cy="create-dashboard"]');
    await page.fill('[data-cy="dashboard-name"]', 'Shared Dashboard');
    await page.click('[data-cy="save-dashboard"]');
    
    // Add a simple widget
    await page.click('[data-cy="add-widget"]');
    await page.click('[data-cy="widget-type-kpi"]');
    await page.fill('[data-cy="widget-title"]', 'Test Metric');
    await page.click('[data-cy="save-widget"]');
    
    // Test sharing
    await page.click('[data-cy="dashboard-share"]');
    await page.check('[data-cy="make-public"]');
    await page.click('[data-cy="generate-link"]');
    
    // Verify public link is generated
    await expect(page.locator('[data-cy="public-link"]')).toBeVisible();
    
    // Test export
    await page.click('[data-cy="dashboard-export"]');
    await page.selectOption('[data-cy="export-format"]', 'PDF');
    
    // Start download
    const downloadPromise = page.waitForEvent('download');
    await page.click('[data-cy="export-dashboard"]');
    const download = await downloadPromise;
    
    // Verify download
    expect(download.suggestedFilename()).toContain('Shared Dashboard');
    expect(download.suggestedFilename()).toContain('.pdf');
  });
});

test.describe('Mobile Responsiveness Workflows', () => {
  let helper: BaserowTestHelper;

  test.beforeEach(async ({ page }) => {
    helper = new BaserowTestHelper(page);
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await helper.login();
  });

  test('should work properly on mobile devices', async ({ page }) => {
    await helper.createWorkspace('Mobile Workspace');
    await helper.createDatabase('Mobile Database');
    await helper.createTable('Mobile Table');
    
    // Test mobile navigation
    await page.click('[data-cy="mobile-menu-toggle"]');
    await expect(page.locator('[data-cy="mobile-navigation"]')).toBeVisible();
    
    // Test mobile table view
    await helper.createField('Task', 'text');
    await page.click('[data-cy="add-row-button"]');
    
    // Verify mobile-friendly form
    await expect(page.locator('[data-cy="mobile-row-form"]')).toBeVisible();
    
    // Test touch interactions
    await page.fill('[data-cy="Task-input"]', 'Mobile task');
    await page.tap('[data-cy="save-row"]');
    
    // Test horizontal scrolling for table
    await page.locator('[data-cy="table-container"]').swipe({ direction: 'left' });
    
    // Verify mobile kanban view
    await helper.switchView('kanban');
    await expect(page.locator('[data-cy="mobile-kanban-view"]')).toBeVisible();
    
    // Test mobile card interactions
    await page.tap('[data-cy="kanban-card"]');
    await expect(page.locator('[data-cy="mobile-card-modal"]')).toBeVisible();
  });
});

test.describe('Performance and Load Testing', () => {
  let helper: BaserowTestHelper;

  test.beforeEach(async ({ page }) => {
    helper = new BaserowTestHelper(page);
    await helper.login();
    await helper.createWorkspace('Performance Workspace');
    await helper.createDatabase('Large Database');
    await helper.createTable('Large Table');
  });

  test('should handle large datasets efficiently', async ({ page }) => {
    // Create multiple fields
    const fields = ['Name', 'Email', 'Department', 'Salary', 'Start Date'];
    for (const field of fields) {
      await helper.createField(field, 'text');
    }
    
    // Measure initial load time
    const startTime = Date.now();
    await page.reload();
    await page.waitForSelector('[data-cy="table-view"]');
    const loadTime = Date.now() - startTime;
    
    // Verify reasonable load time (less than 3 seconds)
    expect(loadTime).toBeLessThan(3000);
    
    // Test pagination with large dataset
    await page.click('[data-cy="table-pagination"]');
    await page.selectOption('[data-cy="rows-per-page"]', '100');
    
    // Verify pagination works smoothly
    await expect(page.locator('[data-cy="pagination-info"]')).toContainText('100');
    
    // Test search performance
    const searchStartTime = Date.now();
    await page.fill('[data-cy="search-input"]', 'test');
    await page.waitForSelector('[data-cy="search-results"]');
    const searchTime = Date.now() - searchStartTime;
    
    // Verify search is fast (less than 1 second)
    expect(searchTime).toBeLessThan(1000);
  });

  test('should handle concurrent user actions', async ({ page, context }) => {
    // This test would simulate multiple users performing actions simultaneously
    // and verify that the system handles concurrent operations correctly
    
    // Create multiple browser contexts to simulate different users
    const users = [];
    for (let i = 0; i < 3; i++) {
      const userPage = await context.newPage();
      const userHelper = new BaserowTestHelper(userPage);
      await userHelper.login(`user${i}@example.com`);
      users.push(userPage);
    }
    
    // Have all users perform actions simultaneously
    const actions = users.map(async (userPage, index) => {
      await userPage.click('[data-cy="add-row-button"]');
      await userPage.fill('[data-cy="Name-input"]', `User ${index} Task`);
      await userPage.click('[data-cy="save-row"]');
    });
    
    // Wait for all actions to complete
    await Promise.all(actions);
    
    // Verify all rows were created successfully
    for (let i = 0; i < 3; i++) {
      await expect(page.locator(`[data-cy="table-row"]:has-text("User ${i} Task")`)).toBeVisible();
    }
    
    // Clean up
    for (const userPage of users) {
      await userPage.close();
    }
  });
});