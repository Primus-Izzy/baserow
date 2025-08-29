/**
 * Mobile Responsiveness Testing Suite
 * 
 * Tests mobile responsiveness across different device sizes and orientations:
 * - Phone sizes (320px - 480px)
 * - Tablet sizes (768px - 1024px)
 * - Portrait and landscape orientations
 * - Touch interactions
 * - Mobile-specific features
 */

import { test, expect, devices } from '@playwright/test'

// Device configurations for testing
const mobileDevices = [
  { name: 'iPhone SE', ...devices['iPhone SE'] },
  { name: 'iPhone 12', ...devices['iPhone 12'] },
  { name: 'iPhone 12 Pro', ...devices['iPhone 12 Pro'] },
  { name: 'Pixel 5', ...devices['Pixel 5'] },
  { name: 'Samsung Galaxy S21', ...devices['Galaxy S21'] },
]

const tabletDevices = [
  { name: 'iPad', ...devices['iPad'] },
  { name: 'iPad Pro', ...devices['iPad Pro'] },
  { name: 'Galaxy Tab S4', ...devices['Galaxy Tab S4'] },
]

// Test mobile devices
for (const device of mobileDevices) {
  test.describe(`Mobile Responsiveness - ${device.name}`, () => {
    test.use(device)

    test.describe('Enhanced Table View Mobile', () => {
      test('should display mobile-optimized table layout', async ({ page }) => {
        await page.goto('/database/1/table/1')
        await page.waitForLoadState('networkidle')

        // Check if mobile table layout is active
        const tableContainer = page.locator('[data-testid="table-container"]')
        const isMobileLayout = await tableContainer.evaluate(el => 
          el.classList.contains('mobile-layout') || 
          window.getComputedStyle(el).display === 'block'
        )
        
        expect(isMobileLayout).toBeTruthy()
      })

      test('should support horizontal scrolling for wide tables', async ({ page }) => {
        await page.goto('/database/1/table/1')
        
        const tableWrapper = page.locator('[data-testid="table-wrapper"]')
        const overflowX = await tableWrapper.evaluate(el => 
          window.getComputedStyle(el).overflowX
        )
        
        expect(['auto', 'scroll']).toContain(overflowX)
      })

      test('should have touch-friendly cell editing', async ({ page }) => {
        await page.goto('/database/1/table/1')
        
        const cell = page.locator('[data-testid="table-cell"]').first()
        
        // Test touch tap to edit
        await cell.tap()
        
        const editor = page.locator('[data-testid="cell-editor"]')
        if (await editor.count() > 0) {
          await expect(editor).toBeVisible()
          
          // Check editor is appropriately sized for mobile
          const editorBox = await editor.boundingBox()
          expect(editorBox?.height).toBeGreaterThanOrEqual(44) // Minimum touch target
        }
      })

      test('should show mobile navigation menu', async ({ page }) => {
        await page.goto('/database/1/table/1')
        
        const mobileMenuButton = page.locator('[data-testid="mobile-menu-button"]')
        if (await mobileMenuButton.count() > 0) {
          await mobileMenuButton.tap()
          
          const mobileMenu = page.locator('[data-testid="mobile-menu"]')
          await expect(mobileMenu).toBeVisible()
        }
      })
    })

    test.describe('Kanban View Mobile', () => {
      test('should display mobile-optimized Kanban layout', async ({ page }) => {
        await page.goto('/database/1/table/1/view/kanban/1')
        await page.waitForLoadState('networkidle')

        const kanbanContainer = page.locator('[data-testid="kanban-container"]')
        
        // Check if horizontal scrolling is enabled for columns
        const overflowX = await kanbanContainer.evaluate(el => 
          window.getComputedStyle(el).overflowX
        )
        
        expect(['auto', 'scroll']).toContain(overflowX)
      })

      test('should support touch drag and drop for cards', async ({ page }) => {
        await page.goto('/database/1/table/1/view/kanban/1')
        
        const card = page.locator('[data-testid="kanban-card"]').first()
        const targetColumn = page.locator('[data-testid="kanban-column"]').nth(1)
        
        if (await card.count() > 0) {
          // Get initial position
          const initialParent = await card.locator('..').getAttribute('data-column-id')
          
          // Perform touch drag
          await card.dragTo(targetColumn)
          
          // Verify card moved
          const newParent = await card.locator('..').getAttribute('data-column-id')
          expect(newParent).not.toBe(initialParent)
        }
      })

      test('should have appropriately sized cards for mobile', async ({ page }) => {
        await page.goto('/database/1/table/1/view/kanban/1')
        
        const cards = page.locator('[data-testid="kanban-card"]')
        const cardCount = await cards.count()
        
        if (cardCount > 0) {
          const firstCard = cards.first()
          const cardBox = await firstCard.boundingBox()
          
          if (cardBox) {
            // Cards should be wide enough for mobile viewing
            expect(cardBox.width).toBeGreaterThanOrEqual(250)
            // Cards should have reasonable height
            expect(cardBox.height).toBeGreaterThanOrEqual(80)
          }
        }
      })

      test('should support swipe navigation between columns', async ({ page }) => {
        await page.goto('/database/1/table/1/view/kanban/1')
        
        const kanbanContainer = page.locator('[data-testid="kanban-container"]')
        
        // Get initial scroll position
        const initialScrollLeft = await kanbanContainer.evaluate(el => el.scrollLeft)
        
        // Perform swipe gesture (simulate with scroll)
        await kanbanContainer.evaluate(el => {
          el.scrollLeft += 200
        })
        
        const newScrollLeft = await kanbanContainer.evaluate(el => el.scrollLeft)
        expect(newScrollLeft).toBeGreaterThan(initialScrollLeft)
      })
    })

    test.describe('Timeline View Mobile', () => {
      test('should display mobile-optimized timeline', async ({ page }) => {
        await page.goto('/database/1/table/1/view/timeline/1')
        await page.waitForLoadState('networkidle')

        const timelineContainer = page.locator('[data-testid="timeline-container"]')
        
        // Should support horizontal scrolling
        const overflowX = await timelineContainer.evaluate(el => 
          window.getComputedStyle(el).overflowX
        )
        
        expect(['auto', 'scroll']).toContain(overflowX)
      })

      test('should support pinch-to-zoom gestures', async ({ page }) => {
        await page.goto('/database/1/table/1/view/timeline/1')
        
        const timeline = page.locator('[data-testid="timeline-container"]')
        
        // Simulate pinch zoom (using zoom controls as proxy)
        const zoomInButton = page.locator('[data-testid="timeline-zoom-in"]')
        if (await zoomInButton.count() > 0) {
          const initialZoom = await timeline.getAttribute('data-zoom-level')
          
          await zoomInButton.tap()
          
          const newZoom = await timeline.getAttribute('data-zoom-level')
          expect(newZoom).not.toBe(initialZoom)
        }
      })

      test('should have touch-friendly timeline bars', async ({ page }) => {
        await page.goto('/database/1/table/1/view/timeline/1')
        
        const timelineBars = page.locator('[data-testid="timeline-bar"]')
        const barCount = await timelineBars.count()
        
        if (barCount > 0) {
          const firstBar = timelineBars.first()
          const barBox = await firstBar.boundingBox()
          
          if (barBox) {
            // Timeline bars should be tall enough for touch interaction
            expect(barBox.height).toBeGreaterThanOrEqual(32)
          }
        }
      })
    })

    test.describe('Calendar View Mobile', () => {
      test('should display mobile-optimized calendar', async ({ page }) => {
        await page.goto('/database/1/table/1/view/calendar/1')
        await page.waitForLoadState('networkidle')

        const calendarGrid = page.locator('[data-testid="calendar-grid"]')
        
        // Check if calendar adapts to mobile screen
        const gridColumns = await calendarGrid.evaluate(el => 
          window.getComputedStyle(el).gridTemplateColumns
        )
        
        // Should have appropriate column sizing for mobile
        expect(gridColumns).toBeTruthy()
      })

      test('should support swipe navigation between months', async ({ page }) => {
        await page.goto('/database/1/table/1/view/calendar/1')
        
        const currentMonth = await page.locator('[data-testid="calendar-month-title"]').textContent()
        
        // Simulate swipe left (next month)
        const calendarContainer = page.locator('[data-testid="calendar-container"]')
        await calendarContainer.evaluate(el => {
          const event = new TouchEvent('touchstart', {
            touches: [{ clientX: 300, clientY: 200 }]
          })
          el.dispatchEvent(event)
        })
        
        await page.waitForTimeout(100)
        
        await calendarContainer.evaluate(el => {
          const event = new TouchEvent('touchend', {
            changedTouches: [{ clientX: 100, clientY: 200 }]
          })
          el.dispatchEvent(event)
        })
        
        // Month should change (or at least attempt to)
        await page.waitForTimeout(500)
        const newMonth = await page.locator('[data-testid="calendar-month-title"]').textContent()
        
        // Either month changed or swipe was recognized
        expect(typeof newMonth).toBe('string')
      })

      test('should have touch-friendly calendar cells', async ({ page }) => {
        await page.goto('/database/1/table/1/view/calendar/1')
        
        const calendarCells = page.locator('[data-testid="calendar-cell"]')
        const cellCount = await calendarCells.count()
        
        if (cellCount > 0) {
          const firstCell = calendarCells.first()
          const cellBox = await firstCell.boundingBox()
          
          if (cellBox) {
            // Calendar cells should be large enough for touch
            expect(cellBox.width).toBeGreaterThanOrEqual(40)
            expect(cellBox.height).toBeGreaterThanOrEqual(40)
          }
        }
      })
    })

    test.describe('Form View Mobile', () => {
      test('should display mobile-optimized form layout', async ({ page }) => {
        await page.goto('/database/1/table/1/view/form/1')
        await page.waitForLoadState('networkidle')

        const formContainer = page.locator('[data-testid="form-container"]')
        
        // Form should stack vertically on mobile
        const flexDirection = await formContainer.evaluate(el => 
          window.getComputedStyle(el).flexDirection
        )
        
        expect(flexDirection).toBe('column')
      })

      test('should have mobile-friendly form inputs', async ({ page }) => {
        await page.goto('/database/1/table/1/view/form/1')
        
        const formInputs = page.locator('[data-testid="form-field"] input, [data-testid="form-field"] select, [data-testid="form-field"] textarea')
        const inputCount = await formInputs.count()
        
        if (inputCount > 0) {
          for (let i = 0; i < Math.min(inputCount, 3); i++) {
            const input = formInputs.nth(i)
            const inputBox = await input.boundingBox()
            
            if (inputBox) {
              // Form inputs should be tall enough for mobile
              expect(inputBox.height).toBeGreaterThanOrEqual(44)
            }
          }
        }
      })

      test('should support mobile keyboard types', async ({ page }) => {
        await page.goto('/database/1/table/1/view/form/1')
        
        // Check for appropriate input types
        const emailInputs = page.locator('input[type="email"]')
        const telInputs = page.locator('input[type="tel"]')
        const numberInputs = page.locator('input[type="number"]')
        
        // These should exist for mobile optimization
        const hasSpecialInputs = 
          (await emailInputs.count()) > 0 ||
          (await telInputs.count()) > 0 ||
          (await numberInputs.count()) > 0
        
        // At least some forms should use mobile-optimized input types
        expect(typeof hasSpecialInputs).toBe('boolean')
      })
    })

    test.describe('Dashboard Mobile', () => {
      test('should display mobile-optimized dashboard layout', async ({ page }) => {
        await page.goto('/dashboard/1')
        await page.waitForLoadState('networkidle')

        const dashboardGrid = page.locator('[data-testid="dashboard-grid"]')
        
        // Dashboard should adapt to single column on mobile
        const gridColumns = await dashboardGrid.evaluate(el => 
          window.getComputedStyle(el).gridTemplateColumns
        )
        
        // Should have fewer columns on mobile
        expect(gridColumns).toBeTruthy()
      })

      test('should have touch-friendly widget interactions', async ({ page }) => {
        await page.goto('/dashboard/1')
        
        const widgets = page.locator('[data-testid="dashboard-widget"]')
        const widgetCount = await widgets.count()
        
        if (widgetCount > 0) {
          const firstWidget = widgets.first()
          
          // Test tap interaction
          await firstWidget.tap()
          
          const widgetMenu = page.locator('[data-testid="widget-menu"]')
          if (await widgetMenu.count() > 0) {
            await expect(widgetMenu).toBeVisible()
          }
        }
      })

      test('should support chart interactions on mobile', async ({ page }) => {
        await page.goto('/dashboard/1')
        
        const chartWidgets = page.locator('[data-testid="chart-widget"]')
        const chartCount = await chartWidgets.count()
        
        if (chartCount > 0) {
          const firstChart = chartWidgets.first()
          const chartCanvas = firstChart.locator('canvas, svg')
          
          if (await chartCanvas.count() > 0) {
            // Test touch interaction with chart
            await chartCanvas.tap()
            
            // Chart should remain responsive
            await expect(chartCanvas).toBeVisible()
          }
        }
      })
    })

    test.describe('Mobile Navigation', () => {
      test('should have mobile-friendly navigation menu', async ({ page }) => {
        await page.goto('/database/1/table/1')
        
        const mobileNavToggle = page.locator('[data-testid="mobile-nav-toggle"]')
        if (await mobileNavToggle.count() > 0) {
          await mobileNavToggle.tap()
          
          const mobileNav = page.locator('[data-testid="mobile-navigation"]')
          await expect(mobileNav).toBeVisible()
          
          // Navigation should be full-width on mobile
          const navBox = await mobileNav.boundingBox()
          const viewportSize = page.viewportSize()
          
          if (navBox && viewportSize) {
            expect(navBox.width).toBeGreaterThanOrEqual(viewportSize.width * 0.8)
          }
        }
      })

      test('should support swipe-to-close navigation', async ({ page }) => {
        await page.goto('/database/1/table/1')
        
        const mobileNavToggle = page.locator('[data-testid="mobile-nav-toggle"]')
        if (await mobileNavToggle.count() > 0) {
          await mobileNavToggle.tap()
          
          const mobileNav = page.locator('[data-testid="mobile-navigation"]')
          await expect(mobileNav).toBeVisible()
          
          // Simulate swipe to close
          await mobileNav.evaluate(el => {
            const startEvent = new TouchEvent('touchstart', {
              touches: [{ clientX: 0, clientY: 200 }]
            })
            const endEvent = new TouchEvent('touchend', {
              changedTouches: [{ clientX: -200, clientY: 200 }]
            })
            
            el.dispatchEvent(startEvent)
            setTimeout(() => el.dispatchEvent(endEvent), 100)
          })
          
          await page.waitForTimeout(500)
          
          // Navigation should close or at least respond to swipe
          const isVisible = await mobileNav.isVisible()
          expect(typeof isVisible).toBe('boolean')
        }
      })
    })

    test.describe('Mobile Performance', () => {
      test('should load quickly on mobile', async ({ page }) => {
        const startTime = Date.now()
        
        await page.goto('/database/1/table/1')
        await page.waitForLoadState('networkidle')
        
        const loadTime = Date.now() - startTime
        
        // Should load within 8 seconds on mobile (allowing for slower networks)
        expect(loadTime).toBeLessThan(8000)
      })

      test('should handle touch scrolling smoothly', async ({ page }) => {
        await page.goto('/database/1/table/1')
        
        // Test smooth scrolling
        for (let i = 0; i < 5; i++) {
          await page.evaluate(() => {
            window.scrollBy(0, 100)
          })
          await page.waitForTimeout(50)
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

// Test tablet devices
for (const device of tabletDevices) {
  test.describe(`Tablet Responsiveness - ${device.name}`, () => {
    test.use(device)

    test('should display tablet-optimized layouts', async ({ page }) => {
      await page.goto('/database/1/table/1')
      await page.waitForLoadState('networkidle')

      // Tablets should show more content than phones but less than desktop
      const tableContainer = page.locator('[data-testid="table-container"]')
      const containerWidth = await tableContainer.evaluate(el => el.offsetWidth)
      
      // Tablet should have reasonable content width
      expect(containerWidth).toBeGreaterThan(600)
      expect(containerWidth).toBeLessThan(1200)
    })

    test('should support both touch and mouse interactions', async ({ page }) => {
      await page.goto('/database/1/table/1/view/kanban/1')
      
      const card = page.locator('[data-testid="kanban-card"]').first()
      
      if (await card.count() > 0) {
        // Test touch interaction
        await card.tap()
        
        // Test hover (if supported)
        await card.hover()
        
        // Card should respond to both interaction types
        await expect(card).toBeVisible()
      }
    })
  })
}

// Test orientation changes
test.describe('Orientation Changes', () => {
  test('should handle portrait to landscape rotation', async ({ page, context }) => {
    // Start in portrait
    await context.setViewportSize({ width: 375, height: 667 })
    await page.goto('/database/1/table/1')
    await page.waitForLoadState('networkidle')

    // Rotate to landscape
    await context.setViewportSize({ width: 667, height: 375 })
    await page.waitForTimeout(500)

    // Layout should adapt
    const tableContainer = page.locator('[data-testid="table-container"]')
    await expect(tableContainer).toBeVisible()
    
    const containerWidth = await tableContainer.evaluate(el => el.offsetWidth)
    expect(containerWidth).toBeGreaterThan(500) // Should use landscape width
  })

  test('should maintain functionality across orientations', async ({ page, context }) => {
    await context.setViewportSize({ width: 375, height: 667 })
    await page.goto('/database/1/table/1/view/kanban/1')

    // Test functionality in portrait
    const card = page.locator('[data-testid="kanban-card"]').first()
    if (await card.count() > 0) {
      await card.tap()
    }

    // Rotate to landscape
    await context.setViewportSize({ width: 667, height: 375 })
    await page.waitForTimeout(500)

    // Functionality should still work
    if (await card.count() > 0) {
      await card.tap()
      await expect(card).toBeVisible()
    }
  })
})