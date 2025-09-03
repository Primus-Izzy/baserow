<template>
  <div class="mobile-navigation">
    <!-- Bottom Navigation Bar -->
    <nav class="bottom-nav" :class="{ 'nav-hidden': hideNavigation }">
      <div class="nav-container">
        <router-link
          v-for="item in navigationItems"
          :key="item.name"
          :to="item.to"
          class="nav-item touch-feedback"
          :class="{
            'nav-item-active': isActiveRoute(item.to),
            'nav-item-disabled': item.disabled,
          }"
          @click="handleNavClick(item)"
        >
          <div class="nav-icon">
            <i :class="item.icon"></i>
            <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span>
          </div>
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </div>
    </nav>

    <!-- Floating Action Button -->
    <button
      v-if="showFab && fabAction"
      class="fab touch-feedback"
      :class="{ 'fab-hidden': hideNavigation }"
      @click="handleFabClick"
    >
      <i :class="fabAction.icon"></i>
    </button>

    <!-- Mobile Menu Overlay -->
    <div
      v-if="showMobileMenu"
      class="mobile-menu-overlay"
      @click="closeMobileMenu"
    >
      <div class="mobile-menu" @click.stop>
        <div class="menu-header">
          <h3>Menu</h3>
          <button class="close-btn" @click="closeMobileMenu">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="menu-content">
          <div class="menu-section">
            <h4>Views</h4>
            <div class="menu-items">
              <button
                v-for="view in availableViews"
                :key="view.id"
                class="menu-item touch-feedback"
                @click="switchView(view)"
              >
                <i :class="view.icon"></i>
                <span>{{ view.name }}</span>
              </button>
            </div>
          </div>

          <div class="menu-section">
            <h4>Actions</h4>
            <div class="menu-items">
              <button
                v-for="action in menuActions"
                :key="action.name"
                class="menu-item touch-feedback"
                @click="handleMenuAction(action)"
              >
                <i :class="action.icon"></i>
                <span>{{ action.label }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Swipe Gesture Indicator -->
    <div
      v-if="showSwipeIndicator"
      class="swipe-indicator"
      :class="swipeDirection"
    >
      <i class="fas fa-hand-paper"></i>
      <span>{{ swipeIndicatorText }}</span>
    </div>
  </div>
</template>

<script>
import mobileResponsive from '@baserow/modules/core/mixins/mobileResponsive'

export default {
  name: 'MobileNavigation',
  mixins: [mobileResponsive],
  props: {
    navigationItems: {
      type: Array,
      default: () => [
        {
          name: 'tables',
          label: 'Tables',
          icon: 'fas fa-table',
          to: '/tables',
          badge: null,
        },
        {
          name: 'views',
          label: 'Views',
          icon: 'fas fa-eye',
          to: '/views',
          badge: null,
        },
        {
          name: 'dashboard',
          label: 'Dashboard',
          icon: 'fas fa-chart-bar',
          to: '/dashboard',
          badge: null,
        },
        {
          name: 'settings',
          label: 'Settings',
          icon: 'fas fa-cog',
          to: '/settings',
          badge: null,
        },
      ],
    },
    fabAction: {
      type: Object,
      default: null,
    },
    showFab: {
      type: Boolean,
      default: true,
    },
    availableViews: {
      type: Array,
      default: () => [],
    },
    menuActions: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      hideNavigation: false,
      showMobileMenu: false,
      lastScrollY: 0,
      scrollThreshold: 10,
      showSwipeIndicator: false,
      swipeDirection: '',
      swipeIndicatorText: '',
      swipeIndicatorTimer: null,
      touchStartX: 0,
      touchStartY: 0,
      touchEndX: 0,
      touchEndY: 0,
    }
  },
  mounted() {
    this.setupScrollListener()
    this.setupSwipeGestures()
  },
  beforeDestroy() {
    this.removeScrollListener()
    this.removeSwipeGestures()
  },
  methods: {
    setupScrollListener() {
      if (this.isMobileDevice) {
        window.addEventListener('scroll', this.handleScroll, { passive: true })
      }
    },

    removeScrollListener() {
      window.removeEventListener('scroll', this.handleScroll)
    },

    handleScroll() {
      const currentScrollY = window.scrollY

      if (Math.abs(currentScrollY - this.lastScrollY) < this.scrollThreshold) {
        return
      }

      // Hide navigation when scrolling down, show when scrolling up
      if (currentScrollY > this.lastScrollY && currentScrollY > 100) {
        this.hideNavigation = true
      } else {
        this.hideNavigation = false
      }

      this.lastScrollY = currentScrollY
    },

    setupSwipeGestures() {
      if (this.isMobileDevice) {
        document.addEventListener('touchstart', this.handleTouchStart, {
          passive: true,
        })
        document.addEventListener('touchend', this.handleTouchEnd, {
          passive: true,
        })
      }
    },

    removeSwipeGestures() {
      document.removeEventListener('touchstart', this.handleTouchStart)
      document.removeEventListener('touchend', this.handleTouchEnd)
    },

    handleTouchStart(event) {
      this.touchStartX = event.touches[0].clientX
      this.touchStartY = event.touches[0].clientY
    },

    handleTouchEnd(event) {
      this.touchEndX = event.changedTouches[0].clientX
      this.touchEndY = event.changedTouches[0].clientY
      this.handleSwipeGesture()
    },

    handleSwipeGesture() {
      const deltaX = this.touchEndX - this.touchStartX
      const deltaY = this.touchEndY - this.touchStartY
      const minSwipeDistance = 50

      // Horizontal swipe
      if (
        Math.abs(deltaX) > Math.abs(deltaY) &&
        Math.abs(deltaX) > minSwipeDistance
      ) {
        if (deltaX > 0) {
          this.onSwipeRight()
        } else {
          this.onSwipeLeft()
        }
      }
      // Vertical swipe
      else if (Math.abs(deltaY) > minSwipeDistance) {
        if (deltaY > 0) {
          this.onSwipeDown()
        } else {
          this.onSwipeUp()
        }
      }
    },

    addHapticFeedback(type = 'light') {
      if (navigator.vibrate) {
        const patterns = {
          light: 50,
          medium: 100,
          heavy: 200,
        }
        navigator.vibrate(patterns[type] || patterns.light)
      }
    },

    isActiveRoute(route) {
      return this.$route.path.startsWith(route)
    },

    handleNavClick(item) {
      if (item.disabled) return

      if (item.action) {
        this.$emit('nav-action', item.action)
      } else {
        this.$router.push(item.to)
      }

      // Haptic feedback
      if (navigator.vibrate) {
        navigator.vibrate(50)
      }
    },

    handleFabClick() {
      if (this.fabAction && this.fabAction.action) {
        this.$emit('fab-action', this.fabAction.action)
      }

      // Haptic feedback
      if (navigator.vibrate) {
        navigator.vibrate(100)
      }
    },

    showMobileMenuOverlay() {
      this.showMobileMenu = true
      document.body.style.overflow = 'hidden'
    },

    closeMobileMenu() {
      this.showMobileMenu = false
      document.body.style.overflow = ''
    },

    switchView(view) {
      this.$emit('switch-view', view)
      this.closeMobileMenu()
    },

    handleMenuAction(action) {
      this.$emit('menu-action', action)
      this.closeMobileMenu()
    },

    showSwipeHint(direction, text) {
      this.swipeDirection = direction
      this.swipeIndicatorText = text
      this.showSwipeIndicator = true

      if (this.swipeIndicatorTimer) {
        clearTimeout(this.swipeIndicatorTimer)
      }

      this.swipeIndicatorTimer = setTimeout(() => {
        this.showSwipeIndicator = false
      }, 2000)
    },

    // Handle swipe gestures from parent components
    onSwipeLeft() {
      this.$emit('swipe-left')
      this.showSwipeHint('left', 'Swipe left for next')
    },

    onSwipeRight() {
      this.$emit('swipe-right')
      this.showSwipeHint('right', 'Swipe right for previous')
    },

    onSwipeUp() {
      this.$emit('swipe-up')
      this.showSwipeHint('up', 'Swipe up for more')
    },

    onSwipeDown() {
      this.$emit('swipe-down')
      this.showSwipeHint('down', 'Swipe down to refresh')
    },

    // Update navigation badges
    updateBadge(itemName, count) {
      const item = this.navigationItems.find((item) => item.name === itemName)
      if (item) {
        item.badge = count > 0 ? count : null
      }
    },

    // Show/hide navigation programmatically
    showNavigation() {
      this.hideNavigation = false
    },

    hideNavigationBar() {
      this.hideNavigation = true
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@baserow/modules/core/assets/scss/components/mobile/responsive.scss';

.mobile-navigation {
  @include mobile-only {
    .bottom-nav {
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      background: var(--color-neutral-50);
      border-top: 1px solid var(--color-neutral-200);
      z-index: 1000;
      transform: translateY(0);
      transition: transform 0.3s ease;

      &.nav-hidden {
        transform: translateY(100%);
      }

      .nav-container {
        display: flex;
        padding: $mobile-spacing-sm 0;

        .nav-item {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: $mobile-spacing-sm;
          text-decoration: none;
          color: var(--color-neutral-600);
          transition: all 0.2s ease;

          &.nav-item-active {
            color: var(--color-primary);

            .nav-icon i {
              transform: scale(1.1);
            }
          }

          &.nav-item-disabled {
            opacity: 0.5;
            pointer-events: none;
          }

          .nav-icon {
            position: relative;
            margin-bottom: 4px;

            i {
              font-size: 20px;
              transition: transform 0.2s ease;
            }

            .nav-badge {
              position: absolute;
              top: -8px;
              right: -8px;
              background: var(--color-error);
              color: white;
              border-radius: 10px;
              padding: 2px 6px;
              font-size: 10px;
              font-weight: 600;
              min-width: 16px;
              text-align: center;
            }
          }

          .nav-label {
            font-size: $mobile-font-size-xs;
            font-weight: 500;
            text-align: center;
            line-height: 1.2;
          }
        }
      }
    }

    .fab {
      position: fixed;
      bottom: 80px;
      right: $mobile-spacing-md;
      width: 56px;
      height: 56px;
      border-radius: 50%;
      background: var(--color-primary);
      color: white;
      border: none;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      z-index: 999;
      transform: scale(1);
      transition: all 0.3s ease;

      &.fab-hidden {
        transform: scale(0) translateY(100px);
      }

      &:active {
        transform: scale(0.9);
      }

      &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        border-radius: 50%;
        background: var(--color-primary);
        z-index: -1;
        transform: scale(0);
        transition: transform 0.3s ease;
      }

      &:active::before {
        transform: scale(1.2);
        opacity: 0.3;
      }
    }

    .mobile-menu-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.5);
      z-index: 1001;
      display: flex;
      align-items: flex-end;

      .mobile-menu {
        width: 100%;
        background: var(--color-neutral-50);
        border-radius: 16px 16px 0 0;
        max-height: 80vh;
        overflow-y: auto;
        -webkit-overflow-scrolling: touch;

        .menu-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: $mobile-spacing-lg $mobile-spacing-md;
          border-bottom: 1px solid var(--color-neutral-200);

          h3 {
            margin: 0;
            font-size: $mobile-font-size-lg;
            font-weight: 600;
          }

          .close-btn {
            @include touch-friendly;
            background: none;
            border: none;
            font-size: $mobile-font-size-lg;
            color: var(--color-neutral-600);
          }
        }

        .menu-content {
          padding: $mobile-spacing-md;

          .menu-section {
            margin-bottom: $mobile-spacing-lg;

            h4 {
              margin: 0 0 $mobile-spacing-md 0;
              font-size: $mobile-font-size-md;
              font-weight: 600;
              color: var(--color-neutral-700);
            }

            .menu-items {
              display: grid;
              gap: $mobile-spacing-sm;

              .menu-item {
                @include touch-friendly;
                display: flex;
                align-items: center;
                gap: $mobile-spacing-md;
                background: var(--color-neutral-100);
                border: none;
                border-radius: 8px;
                padding: $mobile-spacing-md;
                text-align: left;
                color: var(--color-neutral-700);

                i {
                  font-size: 18px;
                  width: 20px;
                  text-align: center;
                }

                span {
                  font-size: $mobile-font-size-md;
                  font-weight: 500;
                }
              }
            }
          }
        }
      }
    }

    .swipe-indicator {
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: rgba(0, 0, 0, 0.8);
      color: white;
      padding: $mobile-spacing-md $mobile-spacing-lg;
      border-radius: 24px;
      display: flex;
      align-items: center;
      gap: $mobile-spacing-sm;
      z-index: 1002;
      animation: swipeIndicatorFade 2s ease-in-out;

      i {
        font-size: 20px;
      }

      span {
        font-size: $mobile-font-size-sm;
        font-weight: 500;
      }

      &.left {
        animation: swipeIndicatorSlideLeft 2s ease-in-out;
      }

      &.right {
        animation: swipeIndicatorSlideRight 2s ease-in-out;
      }

      &.up {
        animation: swipeIndicatorSlideUp 2s ease-in-out;
      }

      &.down {
        animation: swipeIndicatorSlideDown 2s ease-in-out;
      }
    }
  }

  // Hide on desktop
  @include desktop-up {
    display: none;
  }
}

@keyframes swipeIndicatorFade {
  0%,
  100% {
    opacity: 0;
  }
  20%,
  80% {
    opacity: 1;
  }
}

@keyframes swipeIndicatorSlideLeft {
  0% {
    opacity: 0;
    transform: translate(-30%, -50%);
  }
  20%,
  80% {
    opacity: 1;
    transform: translate(-50%, -50%);
  }
  100% {
    opacity: 0;
    transform: translate(-70%, -50%);
  }
}

@keyframes swipeIndicatorSlideRight {
  0% {
    opacity: 0;
    transform: translate(-70%, -50%);
  }
  20%,
  80% {
    opacity: 1;
    transform: translate(-50%, -50%);
  }
  100% {
    opacity: 0;
    transform: translate(-30%, -50%);
  }
}

@keyframes swipeIndicatorSlideUp {
  0% {
    opacity: 0;
    transform: translate(-50%, -30%);
  }
  20%,
  80% {
    opacity: 1;
    transform: translate(-50%, -50%);
  }
  100% {
    opacity: 0;
    transform: translate(-50%, -70%);
  }
}

@keyframes swipeIndicatorSlideDown {
  0% {
    opacity: 0;
    transform: translate(-50%, -70%);
  }
  20%,
  80% {
    opacity: 1;
    transform: translate(-50%, -50%);
  }
  100% {
    opacity: 0;
    transform: translate(-50%, -30%);
  }
}
</style>
