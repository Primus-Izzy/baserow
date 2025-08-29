/**
 * Mobile accessibility service
 * Handles screen reader support, keyboard navigation, and accessibility features
 */

export class MobileAccessibilityService {
  constructor() {
    this.isScreenReaderActive = false
    this.announcements = []
    this.focusHistory = []
    this.gestureHandlers = new Map()
    
    this.initialize()
  }

  /**
   * Initialize accessibility service
   */
  initialize() {
    this.detectScreenReader()
    this.setupKeyboardNavigation()
    this.setupGestureHandlers()
    this.setupFocusManagement()
  }

  /**
   * Detect if screen reader is active
   */
  detectScreenReader() {
    // Check for common screen reader indicators
    this.isScreenReaderActive = !!(
      window.speechSynthesis ||
      navigator.userAgent.includes('NVDA') ||
      navigator.userAgent.includes('JAWS') ||
      navigator.userAgent.includes('VoiceOver') ||
      navigator.userAgent.includes('TalkBack')
    )

    // Listen for screen reader specific events
    document.addEventListener('keydown', (event) => {
      // Common screen reader shortcuts
      if (event.altKey && event.shiftKey) {
        this.isScreenReaderActive = true
      }
    })
  }

  /**
   * Announce text to screen readers
   */
  announce(text, priority = 'polite') {
    if (!text) return

    const announcement = {
      text,
      priority,
      timestamp: Date.now()
    }

    this.announcements.push(announcement)

    // Create live region for announcement
    const liveRegion = document.createElement('div')
    liveRegion.setAttribute('aria-live', priority)
    liveRegion.setAttribute('aria-atomic', 'true')
    liveRegion.className = 'sr-only'
    liveRegion.textContent = text

    document.body.appendChild(liveRegion)

    // Remove after announcement
    setTimeout(() => {
      document.body.removeChild(liveRegion)
    }, 1000)
  }

  /**
   * Setup keyboard navigation
   */
  setupKeyboardNavigation() {
    document.addEventListener('keydown', (event) => {
      this.handleKeyboardNavigation(event)
    })
  }

  /**
   * Handle keyboard navigation
   */
  handleKeyboardNavigation(event) {
    const { key, target, ctrlKey, altKey, shiftKey } = event

    // Skip navigation
    if (key === 'Tab' && shiftKey) {
      this.handleSkipNavigation(event, 'previous')
    } else if (key === 'Tab') {
      this.handleSkipNavigation(event, 'next')
    }

    // Landmark navigation
    if (altKey && key === 'ArrowDown') {
      this.navigateToNextLandmark()
      event.preventDefault()
    } else if (altKey && key === 'ArrowUp') {
      this.navigateToPreviousLandmark()
      event.preventDefault()
    }

    // Heading navigation
    if (ctrlKey && key === 'ArrowDown') {
      this.navigateToNextHeading()
      event.preventDefault()
    } else if (ctrlKey && key === 'ArrowUp') {
      this.navigateToPreviousHeading()
      event.preventDefault()
    }

    // Table navigation
    if (target.closest('table')) {
      this.handleTableNavigation(event)
    }
  }

  /**
   * Handle skip navigation
   */
  handleSkipNavigation(event, direction) {
    const focusableElements = this.getFocusableElements()
    const currentIndex = focusableElements.indexOf(event.target)
    
    if (currentIndex === -1) return

    let nextIndex
    if (direction === 'next') {
      nextIndex = (currentIndex + 1) % focusableElements.length
    } else {
      nextIndex = currentIndex === 0 ? focusableElements.length - 1 : currentIndex - 1
    }

    focusableElements[nextIndex]?.focus()
  }

  /**
   * Navigate to next landmark
   */
  navigateToNextLandmark() {
    const landmarks = document.querySelectorAll('[role="main"], [role="navigation"], [role="banner"], [role="contentinfo"], [role="complementary"], main, nav, header, footer, aside')
    const currentFocus = document.activeElement
    
    let nextLandmark = null
    let found = false
    
    for (const landmark of landmarks) {
      if (found) {
        nextLandmark = landmark
        break
      }
      if (landmark.contains(currentFocus)) {
        found = true
      }
    }
    
    if (!nextLandmark && landmarks.length > 0) {
      nextLandmark = landmarks[0]
    }
    
    if (nextLandmark) {
      nextLandmark.focus()
      this.announce(`Navigated to ${this.getLandmarkLabel(nextLandmark)}`)
    }
  }

  /**
   * Navigate to previous landmark
   */
  navigateToPreviousLandmark() {
    const landmarks = Array.from(document.querySelectorAll('[role="main"], [role="navigation"], [role="banner"], [role="contentinfo"], [role="complementary"], main, nav, header, footer, aside')).reverse()
    const currentFocus = document.activeElement
    
    let prevLandmark = null
    let found = false
    
    for (const landmark of landmarks) {
      if (found) {
        prevLandmark = landmark
        break
      }
      if (landmark.contains(currentFocus)) {
        found = true
      }
    }
    
    if (!prevLandmark && landmarks.length > 0) {
      prevLandmark = landmarks[landmarks.length - 1]
    }
    
    if (prevLandmark) {
      prevLandmark.focus()
      this.announce(`Navigated to ${this.getLandmarkLabel(prevLandmark)}`)
    }
  }

  /**
   * Navigate to next heading
   */
  navigateToNextHeading() {
    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6, [role="heading"]')
    const currentFocus = document.activeElement
    
    let nextHeading = null
    let found = false
    
    for (const heading of headings) {
      if (found) {
        nextHeading = heading
        break
      }
      if (heading === currentFocus || heading.contains(currentFocus)) {
        found = true
      }
    }
    
    if (!nextHeading && headings.length > 0) {
      nextHeading = headings[0]
    }
    
    if (nextHeading) {
      nextHeading.focus()
      this.announce(`Heading level ${this.getHeadingLevel(nextHeading)}: ${nextHeading.textContent}`)
    }
  }

  /**
   * Navigate to previous heading
   */
  navigateToPreviousHeading() {
    const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6, [role="heading"]')).reverse()
    const currentFocus = document.activeElement
    
    let prevHeading = null
    let found = false
    
    for (const heading of headings) {
      if (found) {
        prevHeading = heading
        break
      }
      if (heading === currentFocus || heading.contains(currentFocus)) {
        found = true
      }
    }
    
    if (!prevHeading && headings.length > 0) {
      prevHeading = headings[headings.length - 1]
    }
    
    if (prevHeading) {
      prevHeading.focus()
      this.announce(`Heading level ${this.getHeadingLevel(prevHeading)}: ${prevHeading.textContent}`)
    }
  }

  /**
   * Handle table navigation
   */
  handleTableNavigation(event) {
    const { key, ctrlKey, altKey } = event
    const cell = event.target.closest('td, th')
    if (!cell) return

    const table = cell.closest('table')
    const row = cell.closest('tr')
    const cellIndex = Array.from(row.children).indexOf(cell)
    const rowIndex = Array.from(table.querySelectorAll('tr')).indexOf(row)

    let targetCell = null

    if (ctrlKey && altKey) {
      switch (key) {
        case 'ArrowRight':
          targetCell = row.children[cellIndex + 1]
          break
        case 'ArrowLeft':
          targetCell = row.children[cellIndex - 1]
          break
        case 'ArrowDown':
          const nextRow = table.querySelectorAll('tr')[rowIndex + 1]
          targetCell = nextRow?.children[cellIndex]
          break
        case 'ArrowUp':
          const prevRow = table.querySelectorAll('tr')[rowIndex - 1]
          targetCell = prevRow?.children[cellIndex]
          break
      }

      if (targetCell) {
        targetCell.focus()
        this.announceTablePosition(targetCell, table)
        event.preventDefault()
      }
    }
  }

  /**
   * Setup gesture handlers for mobile
   */
  setupGestureHandlers() {
    let touchStartX = 0
    let touchStartY = 0
    let touchEndX = 0
    let touchEndY = 0

    document.addEventListener('touchstart', (event) => {
      touchStartX = event.changedTouches[0].screenX
      touchStartY = event.changedTouches[0].screenY
    })

    document.addEventListener('touchend', (event) => {
      touchEndX = event.changedTouches[0].screenX
      touchEndY = event.changedTouches[0].screenY
      this.handleGesture(touchStartX, touchStartY, touchEndX, touchEndY, event)
    })
  }

  /**
   * Handle gesture recognition
   */
  handleGesture(startX, startY, endX, endY, event) {
    const deltaX = endX - startX
    const deltaY = endY - startY
    const minSwipeDistance = 50

    // Swipe right - next element
    if (deltaX > minSwipeDistance && Math.abs(deltaY) < minSwipeDistance) {
      this.navigateToNextElement()
    }
    // Swipe left - previous element
    else if (deltaX < -minSwipeDistance && Math.abs(deltaY) < minSwipeDistance) {
      this.navigateToPreviousElement()
    }
    // Swipe down - next heading/landmark
    else if (deltaY > minSwipeDistance && Math.abs(deltaX) < minSwipeDistance) {
      this.navigateToNextHeading()
    }
    // Swipe up - previous heading/landmark
    else if (deltaY < -minSwipeDistance && Math.abs(deltaX) < minSwipeDistance) {
      this.navigateToPreviousHeading()
    }
  }

  /**
   * Setup focus management
   */
  setupFocusManagement() {
    document.addEventListener('focusin', (event) => {
      this.focusHistory.push(event.target)
      if (this.focusHistory.length > 10) {
        this.focusHistory.shift()
      }
    })
  }

  /**
   * Get focusable elements
   */
  getFocusableElements() {
    return Array.from(document.querySelectorAll(
      'a[href], button, input, textarea, select, details, [tabindex]:not([tabindex="-1"])'
    )).filter(el => !el.disabled && !el.hidden)
  }

  /**
   * Navigate to next focusable element
   */
  navigateToNextElement() {
    const focusableElements = this.getFocusableElements()
    const currentIndex = focusableElements.indexOf(document.activeElement)
    const nextIndex = (currentIndex + 1) % focusableElements.length
    
    focusableElements[nextIndex]?.focus()
  }

  /**
   * Navigate to previous focusable element
   */
  navigateToPreviousElement() {
    const focusableElements = this.getFocusableElements()
    const currentIndex = focusableElements.indexOf(document.activeElement)
    const prevIndex = currentIndex === 0 ? focusableElements.length - 1 : currentIndex - 1
    
    focusableElements[prevIndex]?.focus()
  }

  /**
   * Get landmark label
   */
  getLandmarkLabel(element) {
    const role = element.getAttribute('role') || element.tagName.toLowerCase()
    const label = element.getAttribute('aria-label') || element.getAttribute('aria-labelledby')
    
    if (label) return `${role} ${label}`
    
    switch (role) {
      case 'main': return 'main content'
      case 'navigation': return 'navigation'
      case 'banner': return 'banner'
      case 'contentinfo': return 'content info'
      case 'complementary': return 'complementary'
      default: return role
    }
  }

  /**
   * Get heading level
   */
  getHeadingLevel(element) {
    if (element.tagName.match(/^H[1-6]$/)) {
      return element.tagName.charAt(1)
    }
    return element.getAttribute('aria-level') || '1'
  }

  /**
   * Announce table position
   */
  announceTablePosition(cell, table) {
    const row = cell.closest('tr')
    const cellIndex = Array.from(row.children).indexOf(cell) + 1
    const rowIndex = Array.from(table.querySelectorAll('tr')).indexOf(row) + 1
    const totalRows = table.querySelectorAll('tr').length
    const totalCols = row.children.length
    
    this.announce(`Row ${rowIndex} of ${totalRows}, Column ${cellIndex} of ${totalCols}`)
  }

  /**
   * Set high contrast mode
   */
  setHighContrastMode(enabled) {
    if (enabled) {
      document.body.classList.add('high-contrast')
    } else {
      document.body.classList.remove('high-contrast')
    }
  }

  /**
   * Set large text mode
   */
  setLargeTextMode(enabled) {
    if (enabled) {
      document.body.classList.add('large-text')
    } else {
      document.body.classList.remove('large-text')
    }
  }

  /**
   * Set reduced motion mode
   */
  setReducedMotionMode(enabled) {
    if (enabled) {
      document.body.classList.add('reduced-motion')
    } else {
      document.body.classList.remove('reduced-motion')
    }
  }

  /**
   * Get accessibility status
   */
  getAccessibilityStatus() {
    return {
      isScreenReaderActive: this.isScreenReaderActive,
      announcements: this.announcements.length,
      focusHistory: this.focusHistory.length,
      highContrast: document.body.classList.contains('high-contrast'),
      largeText: document.body.classList.contains('large-text'),
      reducedMotion: document.body.classList.contains('reduced-motion')
    }
  }
}

export default MobileAccessibilityService