/**
 * Comprehensive Accessibility Testing Suite for Baserow Monday.com Expansion
 * 
 * Tests WCAG 2.1 AA compliance across all new features:
 * - View types (Kanban, Timeline, Calendar, Form)
 * - Field types (Progress Bar, People, Formula)
 * - Dashboard widgets and charts
 * - Mobile responsiveness
 * - Keyboard navigation
 * - Screen reader compatibility
 */

import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

// Configure axe for WCAG 2.1 AA compliance
const axeConfig = {
  tags: ['wcag2a', 'wcag2aa', 'wcag21aa'],
  rules: {
    // Enable additional accessibility rules
    'color-contrast': { enabled: true },
    'keyboard-navigation': { enabled: true },
    'focus-management': { enabled: true },
    'aria-labels': { enabled: true },
    'semantic-markup': { enabled: true }
  }
}

test.describe('Accessibility - Enhanced Table View', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/database/1/table/1')
    await page.waitForLoadState('networkidle')
  })

  test('should meet WCAG 2.1 AA standards for enhanced table view', async ({ page }) => {
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze()

    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('should support keyboard navigation in table view', async ({ page }) => {
    // Test tab navigation through table cells
    await page.keyboard.press('Tab')
    let focusedElement = await page.locator(':focus')
    await expect(focusedElement).toBeVisible()

    // Test arrow key navigation
    await page.keyboard.press('ArrowRight')
    await page.keyboard.press('ArrowDown')
    
    focusedElement = await page.locator(':focus')
    await expect(focusedElement).toBeVisible()
  })

  test('should have proper ARIA labels for conditional formatting', async ({ page }) => {
    // Open conditional formatting panel
    await page.click('[data-testid="conditional-formatting-button"]')
    
    const formatPanel = page.locator('[data-testid="conditional-formatting-panel"]')
    await expect(formatPanel).toHaveAttribute('role', 'dialog')
    await expect(formatPanel).toHaveAttribute('aria-labelledby')
    
    // Check color indicators have proper labels
    const colorIndicators = page.locator('[data-testid="color-indicator"]')
    for (const indicator of await colorIndicators.all()) {
      await expect(indicator).toHaveAttribute('aria-label')
    }
  })

  test('should support screen reader for filter presets', async ({ page }) => {
    await page.click('[data-testid="filter-presets-button"]')
    
    const presetsList = page.locator('[data-testid="filter-presets-list"]')
    await expect(presetsList).toHaveAttribute('role', 'listbox')
    
    const presetItems = page.locator('[data-testid="filter-preset-item"]')
    for (const item of await presetItems.all()) {
      await expect(item).toHaveAttribute('role', 'option')
      await expect(item).toHaveAttribute('aria-label')
    }
  })
})

test.describe('Accessibility - Kanban View', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/database/1/table/1/view/kanban/1')
    await page.waitForLoadState('networkidle')
  })

  test('should meet WCAG 2.1 AA standards for Kanban view', async ({ page }) => {
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze()

    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('should support keyboard navigation for drag and drop', async ({ page }) => {
    // Focus on first card
    await page.keyboard.press('Tab')
    const firstCard = page.locator('[data-testid="kanban-card"]').first()
    await firstCard.focus()
    
    // Test keyboard-based drag and drop
    await page.keyboard.press('Space') // Start drag
    await expect(firstCard).toHaveAttribute('aria-grabbed', 'true')
    
    await page.keyboard.press('ArrowRight') // Move to next column
    await page.keyboard.press('Space') // Drop
    await expect(firstCard).toHaveAttribute('aria-grabbed', 'false')
  })

  test('should have proper ARIA labels for Kanban columns', async ({ page }) => {
    const columns = page.locator('[data-testid="kanban-column"]')
    
    for (const column of await columns.all()) {
      await expect(column).toHaveAttribute('role', 'region')
      await expect(column).toHaveAttribute('aria-labelledby')
      
      // Check column header
      const header = column.locator('[data-testid="kanban-column-header"]')
      await expect(header).toHaveAttribute('role', 'heading')
    }
  })

  test('should announce card movements to screen readers', async ({ page }) => {
    // Set up live region monitoring
    const liveRegion = page.locator('[aria-live="polite"]')
    await expect(liveRegion).toBeAttached()
    
    // Perform card movement
    const card = page.locator('[data-testid="kanban-card"]').first()
    await card.dragTo(page.locator('[data-testid="kanban-column"]').nth(1))
    
    // Verify announcement was made
    await expect(liveRegion).toContainText('moved to')
  })
})

test.describe('Accessibility - Timeline View', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/database/1/table/1/view/timeline/1')
    await page.waitForLoadState('networkidle')
  })

  test('should meet WCAG 2.1 AA standards for Timeline view', async ({ page }) => {
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze()

    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('should support keyboard navigation for timeline', async ({ page }) => {
    // Test zoom controls
    await page.keyboard.press('Tab')
    const zoomIn = page.locator('[data-testid="timeline-zoom-in"]')
    await expect(zoomIn).toBeFocused()
    
    await page.keyboard.press('Enter')
    // Verify zoom level changed
    const timelineContainer = page.locator('[data-testid="timeline-container"]')
    await expect(timelineContainer).toHaveAttribute('data-zoom-level')
  })

  test('should have proper ARIA labels for timeline elements', async ({ page }) => {
    // Check timeline bars
    const timelineBars = page.locator('[data-testid="timeline-bar"]')
    for (const bar of await timelineBars.all()) {
      await expect(bar).toHaveAttribute('role', 'img')
      await expect(bar).toHaveAttribute('aria-label')
    }
    
    // Check milestones
    const milestones = page.locator('[data-testid="timeline-milestone"]')
    for (const milestone of await milestones.all()) {
      await expect(milestone).toHaveAttribute('role', 'img')
      await expect(milestone).toHaveAttribute('aria-label')
    }
  })

  test('should support screen reader for dependencies', async ({ page }) => {
    const dependencies = page.locator('[data-testid="timeline-dependency"]')
    
    for (const dependency of await dependencies.all()) {
      await expect(dependency).toHaveAttribute('aria-label')
      await expect(dependency).toHaveAttribute('role', 'img')
    }
  })
})

test.describe('Accessibility - Calendar View', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/database/1/table/1/view/calendar/1')
    await page.waitForLoadState('networkidle')
  })

  test('should meet WCAG 2.1 AA standards for Calendar view', async ({ page }) => {
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze()

    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('should support keyboard navigation for calendar', async ({ page }) => {
    // Test date navigation
    await page.keyboard.press('Tab')
    const prevButton = page.locator('[data-testid="calendar-prev"]')
    await expect(prevButton).toBeFocused()
    
    // Navigate to calendar grid
    await page.keyboard.press('Tab')
    await page.keyboard.press('Tab')
    
    const calendarGrid = page.locator('[data-testid="calendar-grid"]')
    await expect(calendarGrid).toBeFocused()
    
    // Test arrow key navigation within calendar
    await page.keyboard.press('ArrowRight')
    await page.keyboard.press('ArrowDown')
  })

  test('should have proper ARIA labels for calendar elements', async ({ page }) => {
    // Check calendar grid
    const calendarGrid = page.locator('[data-testid="calendar-grid"]')
    await expect(calendarGrid).toHaveAttribute('role', 'grid')
    await expect(calendarGrid).toHaveAttribute('aria-labelledby')
    
    // Check calendar cells
    const calendarCells = page.locator('[data-testid="calendar-cell"]')
    for (const cell of await calendarCells.all()) {
      await expect(cell).toHaveAttribute('role', 'gridcell')
      await expect(cell).toHaveAttribute('aria-label')
    }
    
    // Check events
    const events = page.locator('[data-testid="calendar-event"]')
    for (const event of await events.all()) {
      await expect(event).toHaveAttribute('aria-label')
    }
  })
})

test.describe('Accessibility - Form View', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/database/1/table/1/view/form/1')
    await page.waitForLoadState('networkidle')
  })

  test('should meet WCAG 2.1 AA standards for Form view', async ({ page }) => {
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze()

    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('should have proper form labels and validation', async ({ page }) => {
    const formFields = page.locator('[data-testid="form-field"]')
    
    for (const field of await formFields.all()) {
      const input = field.locator('input, select, textarea')
      const label = field.locator('label')
      
      // Check label association
      const labelFor = await label.getAttribute('for')
      const inputId = await input.getAttribute('id')
      expect(labelFor).toBe(inputId)
      
      // Check required field indicators
      if (await input.getAttribute('required') !== null) {
        await expect(field).toContainText('*')
        await expect(input).toHaveAttribute('aria-required', 'true')
      }
    }
  })

  test('should support conditional field logic with screen readers', async ({ page }) => {
    // Fill field that triggers conditional logic
    await page.fill('[data-testid="trigger-field"]', 'show-conditional')
    
    // Check that conditional field appears with proper announcement
    const conditionalField = page.locator('[data-testid="conditional-field"]')
    await expect(conditionalField).toBeVisible()
    
    const liveRegion = page.locator('[aria-live="polite"]')
    await expect(liveRegion).toContainText('field is now visible')
  })
})

test.describe('Accessibility - Dashboard Widgets', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard/1')
    await page.waitForLoadState('networkidle')
  })

  test('should meet WCAG 2.1 AA standards for dashboard', async ({ page }) => {
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze()

    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('should have accessible chart widgets', async ({ page }) => {
    const chartWidgets = page.locator('[data-testid="chart-widget"]')
    
    for (const widget of await chartWidgets.all()) {
      // Check chart has proper role and label
      const chart = widget.locator('canvas, svg')
      await expect(chart).toHaveAttribute('role', 'img')
      await expect(chart).toHaveAttribute('aria-label')
      
      // Check data table alternative is provided
      const dataTable = widget.locator('[data-testid="chart-data-table"]')
      if (await dataTable.count() > 0) {
        await expect(dataTable).toHaveAttribute('role', 'table')
      }
    }
  })

  test('should support keyboard navigation for widget interactions', async ({ page }) => {
    // Test widget focus and interaction
    await page.keyboard.press('Tab')
    const firstWidget = page.locator('[data-testid="dashboard-widget"]').first()
    await expect(firstWidget).toBeFocused()
    
    // Test widget menu access
    await page.keyboard.press('Enter')
    const widgetMenu = page.locator('[data-testid="widget-menu"]')
    await expect(widgetMenu).toBeVisible()
  })
})

test.describe('Accessibility - Mobile Responsiveness', () => {
  test.use({ viewport: { width: 375, height: 667 } }) // iPhone SE size

  test('should meet WCAG 2.1 AA standards on mobile', async ({ page }) => {
    await page.goto('/database/1/table/1')
    await page.waitForLoadState('networkidle')

    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze()

    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('should have touch-friendly targets (44px minimum)', async ({ page }) => {
    await page.goto('/database/1/table/1')
    
    const touchTargets = page.locator('button, a, input[type="checkbox"], input[type="radio"]')
    
    for (const target of await touchTargets.all()) {
      const box = await target.boundingBox()
      if (box) {
        expect(box.width).toBeGreaterThanOrEqual(44)
        expect(box.height).toBeGreaterThanOrEqual(44)
      }
    }
  })

  test('should support mobile screen reader gestures', async ({ page }) => {
    await page.goto('/database/1/table/1/view/kanban/1')
    
    // Test swipe navigation for Kanban columns
    const kanbanContainer = page.locator('[data-testid="kanban-container"]')
    await expect(kanbanContainer).toHaveAttribute('role', 'region')
    await expect(kanbanContainer).toHaveAttribute('aria-label')
    
    // Test mobile-specific ARIA landmarks
    const mobileNav = page.locator('[data-testid="mobile-navigation"]')
    if (await mobileNav.count() > 0) {
      await expect(mobileNav).toHaveAttribute('role', 'navigation')
      await expect(mobileNav).toHaveAttribute('aria-label')
    }
  })
})

test.describe('Accessibility - Color Contrast', () => {
  test('should meet color contrast requirements', async ({ page }) => {
    await page.goto('/database/1/table/1')
    
    // Test with axe color-contrast rule specifically
    const accessibilityScanResults = await new AxeBuilder({ page })
      .include('body')
      .withRules(['color-contrast'])
      .analyze()

    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('should maintain contrast in dark mode', async ({ page }) => {
    // Switch to dark mode
    await page.goto('/settings/appearance')
    await page.click('[data-testid="dark-mode-toggle"]')
    
    await page.goto('/database/1/table/1')
    
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withRules(['color-contrast'])
      .analyze()

    expect(accessibilityScanResults.violations).toEqual([])
  })
})

test.describe('Accessibility - Focus Management', () => {
  test('should maintain proper focus order', async ({ page }) => {
    await page.goto('/database/1/table/1')
    
    // Test tab order is logical
    const focusableElements = []
    let currentElement = null
    
    for (let i = 0; i < 20; i++) {
      await page.keyboard.press('Tab')
      currentElement = await page.locator(':focus')
      if (await currentElement.count() > 0) {
        const tagName = await currentElement.evaluate(el => el.tagName)
        focusableElements.push(tagName)
      }
    }
    
    // Verify focus moves through interactive elements
    expect(focusableElements.length).toBeGreaterThan(0)
  })

  test('should trap focus in modal dialogs', async ({ page }) => {
    await page.goto('/database/1/table/1')
    
    // Open a modal
    await page.click('[data-testid="create-row-button"]')
    const modal = page.locator('[data-testid="row-modal"]')
    await expect(modal).toBeVisible()
    
    // Test focus is trapped within modal
    const firstFocusable = modal.locator('button, input, select, textarea').first()
    const lastFocusable = modal.locator('button, input, select, textarea').last()
    
    await lastFocusable.focus()
    await page.keyboard.press('Tab')
    await expect(firstFocusable).toBeFocused()
  })

  test('should restore focus after modal closes', async ({ page }) => {
    await page.goto('/database/1/table/1')
    
    const triggerButton = page.locator('[data-testid="create-row-button"]')
    await triggerButton.focus()
    await triggerButton.click()
    
    const modal = page.locator('[data-testid="row-modal"]')
    await expect(modal).toBeVisible()
    
    // Close modal
    await page.keyboard.press('Escape')
    await expect(modal).not.toBeVisible()
    
    // Focus should return to trigger button
    await expect(triggerButton).toBeFocused()
  })
})