/**
 * Mobile responsive mixin for Vue components
 * Provides common mobile functionality and utilities
 */
export default {
  data() {
    return {
      isMobile: false,
      isTablet: false,
      screenWidth: 0,
      touchStartX: 0,
      touchStartY: 0,
      touchEndX: 0,
      touchEndY: 0,
    }
  },

  computed: {
    /**
     * Determine if current device is mobile
     */
    isMobileDevice() {
      return this.screenWidth < 768
    },

    /**
     * Determine if current device is tablet
     */
    isTabletDevice() {
      return this.screenWidth >= 768 && this.screenWidth < 1024
    },

    /**
     * Determine if current device is desktop
     */
    isDesktopDevice() {
      return this.screenWidth >= 1024
    },

    /**
     * Get appropriate touch target size based on device
     */
    touchTargetSize() {
      if (this.isMobileDevice) return 44
      if (this.isTabletDevice) return 48
      return 32
    },

    /**
     * Get appropriate spacing for current device
     */
    deviceSpacing() {
      if (this.isMobileDevice) return {
        xs: 4, sm: 8, md: 16, lg: 24, xl: 32
      }
      if (this.isTabletDevice) return {
        xs: 6, sm: 12, md: 20, lg: 28, xl: 36
      }
      return {
        xs: 8, sm: 16, md: 24, lg: 32, xl: 40
      }
    }
  },

  mounted() {
    this.updateScreenSize()
    window.addEventListener('resize', this.updateScreenSize)
    window.addEventListener('orientationchange', this.handleOrientationChange)
  },

  beforeDestroy() {
    window.removeEventListener('resize', this.updateScreenSize)
    window.removeEventListener('orientationchange', this.handleOrientationChange)
  },

  methods: {
    /**
     * Update screen size and device type
     */
    updateScreenSize() {
      this.screenWidth = window.innerWidth
      this.isMobile = this.isMobileDevice
      this.isTablet = this.isTabletDevice
    },

    /**
     * Handle device orientation change
     */
    handleOrientationChange() {
      // Delay to allow for orientation change to complete
      setTimeout(() => {
        this.updateScreenSize()
        this.$emit('orientation-change', {
          width: this.screenWidth,
          height: window.innerHeight,
          orientation: window.orientation
        })
      }, 100)
    },

    /**
     * Handle touch start event
     */
    handleTouchStart(event) {
      this.touchStartX = event.touches[0].clientX
      this.touchStartY = event.touches[0].clientY
    },

    /**
     * Handle touch end event
     */
    handleTouchEnd(event) {
      this.touchEndX = event.changedTouches[0].clientX
      this.touchEndY = event.changedTouches[0].clientY
      this.handleSwipeGesture()
    },

    /**
     * Detect and handle swipe gestures
     */
    handleSwipeGesture() {
      const deltaX = this.touchEndX - this.touchStartX
      const deltaY = this.touchEndY - this.touchStartY
      const minSwipeDistance = 50

      // Horizontal swipe
      if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > minSwipeDistance) {
        if (deltaX > 0) {
          this.$emit('swipe-right', { deltaX, deltaY })
        } else {
          this.$emit('swipe-left', { deltaX, deltaY })
        }
      }
      // Vertical swipe
      else if (Math.abs(deltaY) > minSwipeDistance) {
        if (deltaY > 0) {
          this.$emit('swipe-down', { deltaX, deltaY })
        } else {
          this.$emit('swipe-up', { deltaX, deltaY })
        }
      }
    },

    /**
     * Handle long press gesture
     */
    handleLongPress(event, callback, duration = 500) {
      let pressTimer = null

      const startPress = () => {
        pressTimer = setTimeout(() => {
          callback(event)
        }, duration)
      }

      const cancelPress = () => {
        if (pressTimer) {
          clearTimeout(pressTimer)
          pressTimer = null
        }
      }

      event.target.addEventListener('touchstart', startPress)
      event.target.addEventListener('touchend', cancelPress)
      event.target.addEventListener('touchmove', cancelPress)

      return {
        cancel: cancelPress
      }
    },

    /**
     * Optimize scroll performance for mobile
     */
    optimizeScrolling(element) {
      if (this.isMobileDevice) {
        element.style.webkitOverflowScrolling = 'touch'
        element.style.overflowScrolling = 'touch'
      }
    },

    /**
     * Prevent zoom on double tap for specific elements
     */
    preventZoom(element) {
      if (this.isMobileDevice) {
        element.style.touchAction = 'manipulation'
      }
    },

    /**
     * Get optimal column count for current screen size
     */
    getOptimalColumnCount(minColumnWidth = 200) {
      const availableWidth = this.screenWidth - (this.deviceSpacing.md * 2)
      return Math.max(1, Math.floor(availableWidth / minColumnWidth))
    },

    /**
     * Calculate responsive font size
     */
    getResponsiveFontSize(baseSize = 16) {
      if (this.isMobileDevice) {
        return Math.max(14, baseSize - 2)
      }
      if (this.isTabletDevice) {
        return Math.max(15, baseSize - 1)
      }
      return baseSize
    },

    /**
     * Show mobile-friendly loading indicator
     */
    showMobileLoader() {
      // Implementation would depend on your loading system
      this.$emit('show-mobile-loader')
    },

    /**
     * Hide mobile loading indicator
     */
    hideMobileLoader() {
      this.$emit('hide-mobile-loader')
    },

    /**
     * Debounce function for performance optimization
     */
    debounce(func, wait = 300) {
      let timeout
      return function executedFunction(...args) {
        const later = () => {
          clearTimeout(timeout)
          func(...args)
        }
        clearTimeout(timeout)
        timeout = setTimeout(later, wait)
      }
    },

    /**
     * Throttle function for scroll/resize events
     */
    throttle(func, limit = 100) {
      let inThrottle
      return function executedFunction(...args) {
        if (!inThrottle) {
          func.apply(this, args)
          inThrottle = true
          setTimeout(() => inThrottle = false, limit)
        }
      }
    }
  }
}