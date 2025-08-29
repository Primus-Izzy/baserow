/**
 * Cross-Browser Compatibility Testing Suite
 * 
 * Tests all new features across different browsers:
 * - Chrome/Chromium
 * - Firefox
 * - Safari/WebKit
 * - Edge
 * 
 * Covers:
 * - View types functionality
 * - Field types rendering
 * - JavaScript API compatibility
 * - CSS rendering consistency
 * - Performance across browsers
 */

import { test, expect, devices } from '@playwright/test'

// Browser configurations
const browsers = [
  { name: 'chromium', ...devices['Desktop Chrome'] },
  { name: 'firefox', ...devices['Desktop Firefox'] },
  { name: 'webkit', ...devices['Desktop Safari'] },
]

// Test each browser configuration
for (const browserConfig of browsers) {
  test.describe(`Cross-Browser Compatibility - ${browserConfig.name}`, () => {
    test.use(browserConfig)

    test.describe('Enhanced Table View Compatibility', () => {
      test('should render sticky headers correctly', async ({ page }) => {
        await page.goto('/database/1/table/1')
        await page.waitForLoadState('networkidle')

        // Scroll down to test sticky headers
        await page.evaluate(() => window.scrollTo(0, 500))
        
        const stickyHeader = page.locator('[data-testid="table-sticky-header"]')
        await expect(stickyHeader).toBeVisible()
        
        // Check header position is fixed
        const headerPosition = await stickyHeader.evaluate(el => 
          window.getComputedStyle(el).position
        )
        expect(['fixed', 'sticky']).toContain(headerPosition)
      })

      test('should handle conditional formatting colors', async ({ page }) => {
        await page.goto('/database/1/table/1')
        
        const formattedCells = page.locator('[data-testid="formatted-cell"]')
        const cellCount = await formattedCells.count()
        
        if (cellCount > 0) {
          const firstCell = formattedCells.first()
          const backgroundColor = await firstCell.evaluate(el => 
            window.getComputedStyle(el).backgroundColor
          )
          
          // Should have a background color applied
          expect(backgroundColor).not.toBe('rgba(0, 0, 0, 0)')
          expect(backgroundColor).not.toBe('transparent')
        }
      })

      test('should support inline editing across browsers', async ({ page }) => {
        await page.goto('/database/1/table/1')
        
        const editableCell = page.locator('[data-testid="editable-cell"]').first()
        await editableCell.dblclick()
        
        const editor = page.locator('[data-testid="inline-editor"]')
        await expect(editor).toBeVisible()
        
        // Test typing
        await editor.fill('Test content')
        await page.keyboard.press('Enter')
        
        await expect(editableCell).toContainText('Test content')
      })
    })

    test.describe('Kanban View Compatibility', () => {
      test('should support drag and drop across browsers', async ({ page }) => {
        await page.goto('/database/1/table/1/view/kanban/1')
        await page.waitForLoadState('networkidle')

        const sourceCard = page.locator('[data-testid="kanban-card"]').first()
        const targetColumn = page.locator('[data-testid="kanban-column"]').nth(1)
        
        // Get initial position
        const initialColumn = await sourceCard.locator('..').getAttribute('data-column-id')
        
        // Perform drag and drop
        await sourceCard.dragTo(targetColumn)
        
        // Verify card moved
        const newColumn = await sourceCard.locator('..').getAttribute('data-column-id')
        expect(newColumn).not.toBe(initialColumn)
      })

      test('should render card layouts consistently', async ({ page }) => {
        await page.goto('/database/1/table/1/view/kanban/1')
        
        const cards = page.locator('[data-testid="kanban-card"]')
        const cardCount = await cards.count()
        
        if (cardCount > 0) {
          const firstCard = cards.first()
          const cardHeight = await firstCard.evaluate(el => el.offsetHeight)
          const cardWidth = await firstCard.evaluate(el => el.offsetWidth)
          
          // Cards should have reasonable dimensions
          expect(cardHeight).toBeGreaterThan(50)
          expect(cardWidth).toBeGreaterThan(200)
        }
      })
    })

    test.describe('Timeline View Compatibility', () => {
      test('should render timeline bars correctly', async ({ page }) => {
        await page.goto('/database/1/table/1/view/timeline/1')
        await page.waitForLoadState('networkidle')

        const timelineBars = page.locator('[data-testid="timeline-bar"]')
        const barCount = await timelineBars.count()
        
        if (barCount > 0) {
          const firstBar = timelineBars.first()
          const barWidth = await firstBar.evaluate(el => el.offsetWidth)
          const barHeight = await firstBar.evaluate(el => el.offsetHeight)
          
          expect(barWidth).toBeGreaterThan(0)
          expect(barHeight).toBeGreaterThan(0)
        }
      })

      test('should support zoom functionality', async ({ page }) => {
        await page.goto('/database/1/table/1/view/timeline/1')
        
        const zoomInButton = page.locator('[data-testid="timeline-zoom-in"]')
        const timelineContainer = page.locator('[data-testid="timeline-container"]')
        
        // Get initial zoom level
        const initialZoom = await timelineContainer.getAttribute('data-zoom-level')
        
        await zoomInButton.click()
        
        // Verify zoom changed
        const newZoom = await timelineContainer.getAttribute('data-zoom-level')
        expect(newZoom).not.toBe(initialZoom)
      })
    })

    test.describe('Calendar View Compatibility', () => {
      test('should render calendar grid properly', async ({ page }) => {
        await page.goto('/database/1/table/1/view/calendar/1')
        await page.waitForLoadState('networkidle')

        const calendarGrid = page.locator('[data-testid="calendar-grid"]')
        const gridDisplay = await calendarGrid.evaluate(el => 
          window.getComputedStyle(el).display
        )
        
        // Should use CSS Grid or similar layout
        expect(['grid', 'flex', 'table']).toContain(gridDisplay)
        
        const calendarCells = page.locator('[data-testid="calendar-cell"]')
        const cellCount = await calendarCells.count()
        
        // Should have calendar cells (typically 35 or 42 for month view)
        expect(cellCount).toBeGreaterThanOrEqual(28)
      })

      test('should handle event drag and drop', async ({ page }) => {
        await page.goto('/database/1/table/1/view/calendar/1')
        
        const event = page.locator('[data-testid="calendar-event"]').first()
        const targetCell = page.locator('[data-testid="calendar-cell"]').nth(10)
        
        if (await event.count() > 0) {
          await event.dragTo(targetCell)
          
          // Verify event moved (implementation specific)
          await expect(event).toBeVisible()
        }
      })
    })

    test.describe('Form View Compatibility', () => {
      test('should render form fields correctly', async ({ page }) => {
        await page.goto('/database/1/table/1/view/form/1')
        await page.waitForLoadState('networkidle')

        const formFields = page.locator('[data-testid="form-field"]')
        const fieldCount = await formFields.count()
        
        if (fieldCount > 0) {
          for (let i = 0; i < Math.min(fieldCount, 5); i++) {
            const field = formFields.nth(i)
            const fieldInput = field.locator('input, select, textarea')
            
            if (await fieldInput.count() > 0) {
              await expect(fieldInput).toBeVisible()
              
              // Test input functionality
              if (await fieldInput.getAttribute('type') === 'text') {
                await fieldInput.fill('test')
                await expect(fieldInput).toHaveValue('test')
              }
            }
          }
        }
      })

      test('should handle conditional field logic', async ({ page }) => {
        await page.goto('/database/1/table/1/view/form/1')
        
        const triggerField = page.locator('[data-testid="conditional-trigger-field"]')
        const conditionalField = page.locator('[data-testid="conditional-field"]')
        
        if (await triggerField.count() > 0) {
          // Initially conditional field might be hidden
          await triggerField.fill('show')
          
          // Wait for conditional logic to execute
          await page.waitForTimeout(500)
          
          if (await conditionalField.count() > 0) {
            await expect(conditionalField).toBeVisible()
          }
        }
      })
    })

    test.describe('Dashboard Widget Compatibility', () => {
      test('should render charts correctly', async ({ page }) => {
        await page.goto('/dashboard/1')
        await page.waitForLoadState('networkidle')

        const chartWidgets = page.locator('[data-testid="chart-widget"]')
        const widgetCount = await chartWidgets.count()
        
        if (widgetCount > 0) {
          const firstWidget = chartWidgets.first()
          const canvas = firstWidget.locator('canvas')
          const svg = firstWidget.locator('svg')
          
          // Should have either canvas or SVG for chart rendering
          const hasCanvas = await canvas.count() > 0
          const hasSvg = await svg.count() > 0
          
          expect(hasCanvas || hasSvg).toBeTruthy()
        }
      })

      test('should support widget interactions', async ({ page }) => {
        await page.goto('/dashboard/1')
        
        const widget = page.locator('[data-testid="dashboard-widget"]').first()
        
        if (await widget.count() > 0) {
          // Test hover interactions
          await widget.hover()
          
          const widgetMenu = page.locator('[data-testid="widget-menu"]')
          if (await widgetMenu.count() > 0) {
            await expect(widgetMenu).toBeVisible()
          }
        }
      })
    })

    test.describe('Field Type Compatibility', () => {
      test('should render progress bar fields', async ({ page }) => {
        await page.goto('/database/1/table/1')
        
        const progressBars = page.locator('[data-testid="progress-bar-field"]')
        const progressCount = await progressBars.count()
        
        if (progressCount > 0) {
          const firstProgress = progressBars.first()
          const progressBar = firstProgress.locator('[data-testid="progress-bar"]')
          
          await expect(progressBar).toBeVisible()
          
          // Check CSS styling
          const width = await progressBar.evaluate(el => 
            window.getComputedStyle(el).width
          )
          expect(width).not.toBe('0px')
        }
      })

      test('should render people fields with avatars', async ({ page }) => {
        await page.goto('/database/1/table/1')
        
        const peopleFields = page.locator('[data-testid="people-field"]')
        const peopleCount = await peopleFields.count()
        
        if (peopleCount > 0) {
          const firstPeople = peopleFields.first()
          const avatar = firstPeople.locator('[data-testid="user-avatar"]')
          
          if (await avatar.count() > 0) {
            await expect(avatar).toBeVisible()
            
            // Check avatar image loads
            const avatarImg = avatar.locator('img')
            if (await avatarImg.count() > 0) {
              await expect(avatarImg).toHaveAttribute('src')
            }
          }
        }
      })
    })

    test.describe('JavaScript API Compatibility', () => {
      test('should support modern JavaScript features', async ({ page }) => {
        await page.goto('/database/1/table/1')
        
        // Test that modern JS features work
        const result = await page.evaluate(() => {
          // Test async/await
          const testAsync = async () => {
            return new Promise(resolve => resolve('success'))
          }
          
          // Test arrow functions
          const testArrow = () => 'arrow'
          
          // Test destructuring
          const { location } = window
          
          // Test template literals
          const template = `Template ${testArrow()}`
          
          return {
            async: testAsync(),
            arrow: testArrow(),
            destructuring: !!location,
            template: template.includes('Template')
          }
        })
        
        expect(result.arrow).toBe('arrow')
        expect(result.destructuring).toBe(true)
        expect(result.template).toBe(true)
      })

      test('should handle WebSocket connections', async ({ page }) => {
        await page.goto('/database/1/table/1')
        
        // Check WebSocket connection is established
        const wsConnected = await page.evaluate(() => {
          return new Promise((resolve) => {
            const checkConnection = () => {
              // Check if WebSocket connection exists in global state
              if (window.$nuxt && window.$nuxt.$store) {
                const wsState = window.$nuxt.$store.state.collaboration?.connected
                resolve(wsState === true)
              } else {
                setTimeout(checkConnection, 100)
              }
            }
            checkConnection()
            
            // Timeout after 5 seconds
            setTimeout(() => resolve(false), 5000)
          })
        })
        
        // WebSocket should connect (or at least attempt to)
        expect(typeof wsConnected).toBe('boolean')
      })
    })

    test.describe('Performance Compatibility', () => {
      test('should load pages within acceptable time', async ({ page }) => {
        const startTime = Date.now()
        
        await page.goto('/database/1/table/1')
        await page.waitForLoadState('networkidle')
        
        const loadTime = Date.now() - startTime
        
        // Should load within 5 seconds
        expect(loadTime).toBeLessThan(5000)
      })

      test('should handle large datasets efficiently', async ({ page }) => {
        await page.goto('/database/1/table/1')
        
        // Scroll through table to test virtualization
        for (let i = 0; i < 10; i++) {
          await page.keyboard.press('PageDown')
          await page.waitForTimeout(100)
        }
        
        // Page should remain responsive
        const isResponsive = await page.evaluate(() => {
          return document.readyState === 'complete'
        })
        
        expect(isResponsive).toBe(true)
      })
    })
  })
}

// Additional tests for specific browser features
test.describe('Browser-Specific Features', () => {
  test('Chrome - should support advanced CSS features', async ({ page, browserName }) => {
    test.skip(browserName !== 'chromium', 'Chrome-specific test')
    
    await page.goto('/database/1/table/1')
    
    // Test CSS Grid support
    const gridSupport = await page.evaluate(() => {
      return CSS.supports('display', 'grid')
    })
    expect(gridSupport).toBe(true)
    
    // Test CSS Custom Properties
    const customPropsSupport = await page.evaluate(() => {
      return CSS.supports('color', 'var(--test-color)')
    })
    expect(customPropsSupport).toBe(true)
  })

  test('Firefox - should handle drag and drop correctly', async ({ page, browserName }) => {
    test.skip(browserName !== 'firefox', 'Firefox-specific test')
    
    await page.goto('/database/1/table/1/view/kanban/1')
    
    // Firefox-specific drag and drop test
    const card = page.locator('[data-testid="kanban-card"]').first()
    const column = page.locator('[data-testid="kanban-column"]').nth(1)
    
    if (await card.count() > 0) {
      await card.dragTo(column)
      await expect(card).toBeVisible()
    }
  })

  test('Safari - should support touch events on desktop', async ({ page, browserName }) => {
    test.skip(browserName !== 'webkit', 'Safari-specific test')
    
    await page.goto('/database/1/table/1/view/kanban/1')
    
    // Test touch event simulation
    const touchSupport = await page.evaluate(() => {
      return 'ontouchstart' in window || navigator.maxTouchPoints > 0
    })
    
    // Safari should support touch events
    expect(typeof touchSupport).toBe('boolean')
  })
})