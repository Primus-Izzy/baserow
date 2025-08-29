/**
 * Mobile optimization utilities for bundle size and performance
 * Provides lazy loading, code splitting, and mobile-specific optimizations
 */

// Bundle size optimization utilities
export const bundleOptimization = {
  /**
   * Lazy load components for mobile to reduce initial bundle size
   */
  lazyLoadComponent(componentPath) {
    return () => import(componentPath)
  },

  /**
   * Preload critical components for better performance
   */
  preloadComponent(componentPath) {
    const link = document.createElement('link')
    link.rel = 'modulepreload'
    link.href = componentPath
    document.head.appendChild(link)
  },

  /**
   * Check if device has limited resources
   */
  isLowEndDevice() {
    // Check for various indicators of low-end devices
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection
    const memory = navigator.deviceMemory
    const hardwareConcurrency = navigator.hardwareConcurrency

    return (
      (connection && connection.effectiveType && connection.effectiveType.includes('2g')) ||
      (memory && memory < 4) ||
      (hardwareConcurrency && hardwareConcurrency < 4)
    )
  },

  /**
   * Optimize images for mobile devices
   */
  optimizeImage(src, options = {}) {
    const {
      width = 800,
      quality = 0.8,
      format = 'webp'
    } = options

    // Create optimized image URL (implementation would depend on your image service)
    return `${src}?w=${width}&q=${Math.round(quality * 100)}&f=${format}`
  },

  /**
   * Implement intersection observer for lazy loading
   */
  createIntersectionObserver(callback, options = {}) {
    const defaultOptions = {
      root: null,
      rootMargin: '50px',
      threshold: 0.1
    }

    return new IntersectionObserver(callback, { ...defaultOptions, ...options })
  }
}

// Network optimization utilities
export const networkOptimization = {
  /**
   * Check network connection quality
   */
  getConnectionQuality() {
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection
    
    if (!connection) return 'unknown'
    
    const effectiveType = connection.effectiveType
    const downlink = connection.downlink
    
    if (effectiveType === 'slow-2g' || effectiveType === '2g') return 'poor'
    if (effectiveType === '3g' || downlink < 1.5) return 'moderate'
    return 'good'
  },

  /**
   * Implement adaptive loading based on network conditions
   */
  shouldLoadHighQuality() {
    const quality = this.getConnectionQuality()
    const isLowEnd = bundleOptimization.isLowEndDevice()
    
    return quality === 'good' && !isLowEnd
  },

  /**
   * Debounce network requests to avoid overwhelming slow connections
   */
  debounceRequest(func, delay = 300) {
    let timeoutId
    return (...args) => {
      clearTimeout(timeoutId)
      timeoutId = setTimeout(() => func.apply(this, args), delay)
    }
  }
}

// Performance monitoring utilities
export const performanceOptimization = {
  /**
   * Measure and log performance metrics
   */
  measurePerformance(name, fn) {
    const start = performance.now()
    const result = fn()
    const end = performance.now()
    
    console.log(`${name} took ${end - start} milliseconds`)
    return result
  },

  /**
   * Implement virtual scrolling for large lists
   */
  createVirtualScroller(container, itemHeight, items, renderItem) {
    const containerHeight = container.clientHeight
    const visibleCount = Math.ceil(containerHeight / itemHeight) + 2
    let scrollTop = 0

    const render = () => {
      const startIndex = Math.floor(scrollTop / itemHeight)
      const endIndex = Math.min(startIndex + visibleCount, items.length)
      
      container.innerHTML = ''
      container.style.height = `${items.length * itemHeight}px`
      container.style.paddingTop = `${startIndex * itemHeight}px`
      
      for (let i = startIndex; i < endIndex; i++) {
        const item = renderItem(items[i], i)
        container.appendChild(item)
      }
    }

    container.addEventListener('scroll', () => {
      scrollTop = container.scrollTop
      requestAnimationFrame(render)
    })

    render()
  },

  /**
   * Optimize animations for mobile devices
   */
  optimizeAnimation(element, animation, options = {}) {
    const { duration = 300, easing = 'ease-out' } = options
    
    // Use transform and opacity for better performance
    element.style.willChange = 'transform, opacity'
    element.style.transition = `transform ${duration}ms ${easing}, opacity ${duration}ms ${easing}`
    
    // Apply animation
    Object.assign(element.style, animation)
    
    // Clean up after animation
    setTimeout(() => {
      element.style.willChange = 'auto'
    }, duration)
  }
}

// Touch and gesture utilities
export const touchOptimization = {
  /**
   * Implement smooth scrolling for mobile
   */
  enableSmoothScrolling(element) {
    element.style.webkitOverflowScrolling = 'touch'
    element.style.overflowScrolling = 'touch'
  },

  /**
   * Prevent zoom on double tap for specific elements
   */
  preventZoom(element) {
    element.style.touchAction = 'manipulation'
  },

  /**
   * Add haptic feedback for touch interactions
   */
  addHapticFeedback(type = 'light') {
    if (navigator.vibrate) {
      const patterns = {
        light: 50,
        medium: 100,
        heavy: 200
      }
      navigator.vibrate(patterns[type] || patterns.light)
    }
  },

  /**
   * Implement pull-to-refresh functionality
   */
  addPullToRefresh(container, onRefresh) {
    let startY = 0
    let currentY = 0
    let pulling = false
    const threshold = 100

    container.addEventListener('touchstart', (e) => {
      if (container.scrollTop === 0) {
        startY = e.touches[0].clientY
        pulling = true
      }
    })

    container.addEventListener('touchmove', (e) => {
      if (!pulling) return
      
      currentY = e.touches[0].clientY
      const pullDistance = currentY - startY
      
      if (pullDistance > 0) {
        e.preventDefault()
        const pullRatio = Math.min(pullDistance / threshold, 1)
        container.style.transform = `translateY(${pullDistance * 0.5}px)`
        container.style.opacity = 1 - pullRatio * 0.2
      }
    })

    container.addEventListener('touchend', () => {
      if (!pulling) return
      
      const pullDistance = currentY - startY
      
      if (pullDistance > threshold) {
        onRefresh()
      }
      
      container.style.transform = ''
      container.style.opacity = ''
      pulling = false
    })
  }
}

// Accessibility optimization for mobile
export const accessibilityOptimization = {
  /**
   * Ensure touch targets meet minimum size requirements
   */
  ensureTouchTargetSize(element, minSize = 44) {
    const rect = element.getBoundingClientRect()
    
    if (rect.width < minSize || rect.height < minSize) {
      element.style.minWidth = `${minSize}px`
      element.style.minHeight = `${minSize}px`
      element.style.display = 'inline-flex'
      element.style.alignItems = 'center'
      element.style.justifyContent = 'center'
    }
  },

  /**
   * Add screen reader support for dynamic content
   */
  announceToScreenReader(message) {
    const announcement = document.createElement('div')
    announcement.setAttribute('aria-live', 'polite')
    announcement.setAttribute('aria-atomic', 'true')
    announcement.style.position = 'absolute'
    announcement.style.left = '-10000px'
    announcement.style.width = '1px'
    announcement.style.height = '1px'
    announcement.style.overflow = 'hidden'
    
    document.body.appendChild(announcement)
    announcement.textContent = message
    
    setTimeout(() => {
      document.body.removeChild(announcement)
    }, 1000)
  },

  /**
   * Implement focus management for mobile navigation
   */
  manageFocus(element) {
    element.setAttribute('tabindex', '-1')
    element.focus()
    
    // Remove tabindex after focus to maintain natural tab order
    element.addEventListener('blur', () => {
      element.removeAttribute('tabindex')
    }, { once: true })
  },

  /**
   * Add ARIA labels for better accessibility
   */
  addAriaLabels(element, label, description = null) {
    element.setAttribute('aria-label', label)
    if (description) {
      element.setAttribute('aria-describedby', description)
    }
  },

  /**
   * Implement keyboard navigation support
   */
  addKeyboardSupport(element, handlers = {}) {
    element.addEventListener('keydown', (event) => {
      switch (event.key) {
        case 'Enter':
        case ' ':
          if (handlers.activate) {
            event.preventDefault()
            handlers.activate(event)
          }
          break
        case 'Escape':
          if (handlers.escape) {
            event.preventDefault()
            handlers.escape(event)
          }
          break
        case 'ArrowUp':
        case 'ArrowDown':
        case 'ArrowLeft':
        case 'ArrowRight':
          if (handlers.navigate) {
            event.preventDefault()
            handlers.navigate(event.key, event)
          }
          break
      }
    })
  }
}

// Export all utilities as default
export default {
  bundleOptimization,
  networkOptimization,
  performanceOptimization,
  touchOptimization,
  accessibilityOptimization
}