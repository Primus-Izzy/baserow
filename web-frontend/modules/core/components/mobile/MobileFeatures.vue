<template>
  <div class="mobile-features">
    <!-- Offline Status Indicator -->
    <div v-if="!isOnline" class="offline-indicator">
      <i class="fas fa-wifi-slash"></i>
      <span>{{ $t('mobileFeatures.offlineMode') }}</span>
      <button
        v-if="hasPendingSync"
        @click="syncNow"
        class="sync-button"
        :disabled="syncInProgress"
      >
        <i class="fas fa-sync" :class="{ 'fa-spin': syncInProgress }"></i>
        {{ $t('mobileFeatures.syncNow') }}
      </button>
    </div>

    <!-- Camera Access Modal -->
    <modal
      v-if="showCameraModal"
      @hide="closeCameraModal"
      :title="$t('mobileFeatures.cameraAccess')"
    >
      <div class="camera-modal">
        <video
          ref="videoElement"
          autoplay
          playsinline
          class="camera-preview"
        ></video>

        <div class="camera-controls">
          <button @click="switchCamera" class="camera-switch">
            <i class="fas fa-camera-rotate"></i>
          </button>

          <button @click="capturePhoto" class="capture-button">
            <i class="fas fa-camera"></i>
          </button>

          <button @click="accessPhotoLibrary" class="gallery-button">
            <i class="fas fa-images"></i>
          </button>
        </div>
      </div>
    </modal>

    <!-- Push Notification Settings -->
    <div v-if="showNotificationSettings" class="notification-settings">
      <h3>{{ $t('mobileFeatures.notificationSettings') }}</h3>

      <div class="setting-item">
        <label>
          <input
            type="checkbox"
            v-model="notificationPreferences.enabled"
            @change="updateNotificationSettings"
          />
          {{ $t('mobileFeatures.enableNotifications') }}
        </label>
      </div>

      <div class="setting-item" v-if="notificationPreferences.enabled">
        <label>
          <input
            type="checkbox"
            v-model="notificationPreferences.comments"
            @change="updateNotificationSettings"
          />
          {{ $t('mobileFeatures.commentNotifications') }}
        </label>
      </div>

      <div class="setting-item" v-if="notificationPreferences.enabled">
        <label>
          <input
            type="checkbox"
            v-model="notificationPreferences.mentions"
            @change="updateNotificationSettings"
          />
          {{ $t('mobileFeatures.mentionNotifications') }}
        </label>
      </div>

      <button @click="testNotification" class="test-button">
        {{ $t('mobileFeatures.testNotification') }}
      </button>
    </div>

    <!-- Accessibility Settings -->
    <div v-if="showAccessibilitySettings" class="accessibility-settings">
      <h3>{{ $t('mobileFeatures.accessibilitySettings') }}</h3>

      <div class="setting-item">
        <label>
          <input
            type="checkbox"
            v-model="accessibilitySettings.highContrast"
            @change="updateAccessibilitySettings"
          />
          {{ $t('mobileFeatures.highContrast') }}
        </label>
      </div>

      <div class="setting-item">
        <label>
          <input
            type="checkbox"
            v-model="accessibilitySettings.largeText"
            @change="updateAccessibilitySettings"
          />
          {{ $t('mobileFeatures.largeText') }}
        </label>
      </div>

      <div class="setting-item">
        <label>
          <input
            type="checkbox"
            v-model="accessibilitySettings.reducedMotion"
            @change="updateAccessibilitySettings"
          />
          {{ $t('mobileFeatures.reducedMotion') }}
        </label>
      </div>

      <div class="setting-item">
        <label>
          <input
            type="checkbox"
            v-model="accessibilitySettings.screenReaderAnnouncements"
            @change="updateAccessibilitySettings"
          />
          {{ $t('mobileFeatures.screenReaderAnnouncements') }}
        </label>
      </div>
    </div>

    <!-- Sync Status -->
    <div v-if="showSyncStatus" class="sync-status">
      <div class="sync-info">
        <span class="sync-label">{{ $t('mobileFeatures.lastSync') }}:</span>
        <span class="sync-time">{{ formattedLastSyncTime }}</span>
      </div>

      <div v-if="pendingOperations > 0" class="pending-operations">
        <i class="fas fa-clock"></i>
        {{
          $t('mobileFeatures.pendingOperations', { count: pendingOperations })
        }}
      </div>
    </div>
  </div>
</template>

<script>
import OfflineSyncService from '~/modules/core/services/offlineSync'
import CameraAccessService from '~/modules/core/services/cameraAccess'
import PushNotificationService from '~/modules/core/services/pushNotifications'
import MobileAccessibilityService from '~/modules/core/services/mobileAccessibility'

export default {
  name: 'MobileFeatures',

  data() {
    return {
      isOnline: navigator.onLine,
      syncInProgress: false,
      hasPendingSync: false,
      pendingOperations: 0,
      lastSyncTime: null,

      showCameraModal: false,
      showNotificationSettings: false,
      showAccessibilitySettings: false,
      showSyncStatus: false,

      cameraStream: null,
      facingMode: 'environment',

      notificationPreferences: {
        enabled: false,
        comments: true,
        mentions: true,
        updates: false,
      },

      accessibilitySettings: {
        highContrast: false,
        largeText: false,
        reducedMotion: false,
        screenReaderAnnouncements: true,
      },
    }
  },

  computed: {
    formattedLastSyncTime() {
      if (!this.lastSyncTime) return this.$t('mobileFeatures.never')
      return new Date(this.lastSyncTime).toLocaleString()
    },
  },

  async mounted() {
    await this.initializeMobileServices()
    this.setupEventListeners()
    this.loadSettings()
  },

  beforeDestroy() {
    this.cleanup()
  },

  methods: {
    /**
     * Initialize mobile services
     */
    async initializeMobileServices() {
      try {
        // Initialize offline sync
        this.offlineSync = new OfflineSyncService()

        // Initialize camera access
        this.cameraAccess = new CameraAccessService()

        // Initialize push notifications
        this.pushNotifications = new PushNotificationService()
        await this.pushNotifications.initialize()

        // Initialize accessibility
        this.accessibility = new MobileAccessibilityService()

        // Update sync status
        this.updateSyncStatus()
      } catch (error) {
        console.error('Failed to initialize mobile services:', error)
        this.$toast.error(this.$t('mobileFeatures.initializationError'))
      }
    },

    /**
     * Setup event listeners
     */
    setupEventListeners() {
      // Network status
      window.addEventListener('online', this.handleOnline)
      window.addEventListener('offline', this.handleOffline)

      // Visibility change for sync
      document.addEventListener('visibilitychange', this.handleVisibilityChange)
    },

    /**
     * Handle online event
     */
    handleOnline() {
      this.isOnline = true
      this.syncNow()
      this.accessibility?.announce(this.$t('mobileFeatures.backOnline'))
    },

    /**
     * Handle offline event
     */
    handleOffline() {
      this.isOnline = false
      this.accessibility?.announce(this.$t('mobileFeatures.nowOffline'))
    },

    /**
     * Handle visibility change
     */
    handleVisibilityChange() {
      if (!document.hidden && this.isOnline) {
        this.syncNow()
      }
    },

    /**
     * Sync pending operations
     */
    async syncNow() {
      if (this.syncInProgress || !this.isOnline) return

      this.syncInProgress = true

      try {
        await this.offlineSync.syncPendingOperations()
        this.updateSyncStatus()
        this.$toast.success(this.$t('mobileFeatures.syncComplete'))
      } catch (error) {
        console.error('Sync failed:', error)
        this.$toast.error(this.$t('mobileFeatures.syncError'))
      } finally {
        this.syncInProgress = false
      }
    },

    /**
     * Update sync status
     */
    updateSyncStatus() {
      const status = this.offlineSync?.getSyncStatus()
      if (status) {
        this.hasPendingSync = status.pendingOperations > 0
        this.pendingOperations = status.pendingOperations
        this.lastSyncTime = status.lastSyncTime
      }
    },

    /**
     * Open camera modal
     */
    async openCamera() {
      try {
        this.showCameraModal = true
        this.cameraStream = await this.cameraAccess.requestCameraPermission()

        this.$nextTick(() => {
          if (this.$refs.videoElement) {
            this.$refs.videoElement.srcObject = this.cameraStream
          }
        })
      } catch (error) {
        console.error('Camera access failed:', error)
        this.$toast.error(error.message)
        this.closeCameraModal()
      }
    },

    /**
     * Close camera modal
     */
    closeCameraModal() {
      this.showCameraModal = false
      this.cameraAccess?.stopCamera()
      this.cameraStream = null
    },

    /**
     * Switch camera (front/back)
     */
    async switchCamera() {
      try {
        this.facingMode = this.facingMode === 'user' ? 'environment' : 'user'
        this.cameraStream = await this.cameraAccess.switchCamera(
          this.facingMode
        )

        if (this.$refs.videoElement) {
          this.$refs.videoElement.srcObject = this.cameraStream
        }
      } catch (error) {
        console.error('Camera switch failed:', error)
        this.$toast.error(this.$t('mobileFeatures.cameraSwitchError'))
      }
    },

    /**
     * Capture photo from camera
     */
    async capturePhoto() {
      try {
        const blob = await this.cameraAccess.capturePhoto(
          this.$refs.videoElement
        )
        const file = new File([blob], `photo-${Date.now()}.jpg`, {
          type: 'image/jpeg',
        })

        this.$emit('file-captured', file)
        this.closeCameraModal()

        this.accessibility?.announce(this.$t('mobileFeatures.photoCaptured'))
      } catch (error) {
        console.error('Photo capture failed:', error)
        this.$toast.error(this.$t('mobileFeatures.captureError'))
      }
    },

    /**
     * Access photo library
     */
    async accessPhotoLibrary() {
      try {
        const files = await this.cameraAccess.accessPhotoLibrary({
          multiple: true,
        })
        this.$emit('files-selected', files)
        this.closeCameraModal()
      } catch (error) {
        console.error('Photo library access failed:', error)
        this.$toast.error(this.$t('mobileFeatures.libraryError'))
      }
    },

    /**
     * Update notification settings
     */
    async updateNotificationSettings() {
      try {
        if (this.notificationPreferences.enabled) {
          await this.pushNotifications.requestPermission()
          const subscription = await this.pushNotifications.subscribe()
          await this.pushNotifications.sendSubscriptionToServer(
            subscription,
            this.$store.getters['auth/getUserId']
          )
        } else {
          await this.pushNotifications.unsubscribe()
        }

        this.saveSettings()
        this.$toast.success(this.$t('mobileFeatures.settingsUpdated'))
      } catch (error) {
        console.error('Notification settings update failed:', error)
        this.$toast.error(error.message)
      }
    },

    /**
     * Test notification
     */
    async testNotification() {
      try {
        await this.pushNotifications.testNotification()
      } catch (error) {
        console.error('Test notification failed:', error)
        this.$toast.error(error.message)
      }
    },

    /**
     * Update accessibility settings
     */
    updateAccessibilitySettings() {
      this.accessibility?.setHighContrastMode(
        this.accessibilitySettings.highContrast
      )
      this.accessibility?.setLargeTextMode(this.accessibilitySettings.largeText)
      this.accessibility?.setReducedMotionMode(
        this.accessibilitySettings.reducedMotion
      )

      this.saveSettings()
      this.$toast.success(this.$t('mobileFeatures.accessibilityUpdated'))
    },

    /**
     * Load settings from localStorage
     */
    loadSettings() {
      try {
        const saved = localStorage.getItem('baserow-mobile-settings')
        if (saved) {
          const settings = JSON.parse(saved)
          this.notificationPreferences = {
            ...this.notificationPreferences,
            ...settings.notifications,
          }
          this.accessibilitySettings = {
            ...this.accessibilitySettings,
            ...settings.accessibility,
          }

          // Apply accessibility settings
          this.updateAccessibilitySettings()
        }
      } catch (error) {
        console.error('Failed to load settings:', error)
      }
    },

    /**
     * Save settings to localStorage
     */
    saveSettings() {
      try {
        const settings = {
          notifications: this.notificationPreferences,
          accessibility: this.accessibilitySettings,
        }
        localStorage.setItem(
          'baserow-mobile-settings',
          JSON.stringify(settings)
        )
      } catch (error) {
        console.error('Failed to save settings:', error)
      }
    },

    /**
     * Cleanup resources
     */
    cleanup() {
      window.removeEventListener('online', this.handleOnline)
      window.removeEventListener('offline', this.handleOffline)
      document.removeEventListener(
        'visibilitychange',
        this.handleVisibilityChange
      )

      this.cameraAccess?.stopCamera()
    },
  },
}
</script>

<style lang="scss" scoped>
.mobile-features {
  .offline-indicator {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: #ff6b6b;
    color: white;
    padding: 8px 16px;
    display: flex;
    align-items: center;
    gap: 8px;
    z-index: 1000;

    .sync-button {
      margin-left: auto;
      background: rgba(255, 255, 255, 0.2);
      border: 1px solid rgba(255, 255, 255, 0.3);
      color: white;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 12px;

      &:disabled {
        opacity: 0.6;
      }
    }
  }

  .camera-modal {
    .camera-preview {
      width: 100%;
      max-height: 400px;
      object-fit: cover;
      border-radius: 8px;
    }

    .camera-controls {
      display: flex;
      justify-content: center;
      gap: 16px;
      margin-top: 16px;

      button {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        border: none;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;

        &.capture-button {
          background: #007bff;
          color: white;
          width: 80px;
          height: 80px;
          font-size: 24px;
        }

        &.camera-switch,
        &.gallery-button {
          background: #6c757d;
          color: white;
        }
      }
    }
  }

  .notification-settings,
  .accessibility-settings {
    padding: 16px;

    h3 {
      margin-bottom: 16px;
      color: #333;
    }

    .setting-item {
      margin-bottom: 12px;

      label {
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;

        input[type='checkbox'] {
          width: 18px;
          height: 18px;
        }
      }
    }

    .test-button {
      background: #28a745;
      color: white;
      border: none;
      padding: 8px 16px;
      border-radius: 4px;
      margin-top: 16px;
    }
  }

  .sync-status {
    padding: 12px 16px;
    background: #f8f9fa;
    border-radius: 8px;
    margin: 16px 0;

    .sync-info {
      display: flex;
      justify-content: space-between;
      margin-bottom: 8px;

      .sync-label {
        font-weight: 500;
      }

      .sync-time {
        color: #6c757d;
        font-size: 14px;
      }
    }

    .pending-operations {
      color: #ffc107;
      font-size: 14px;
      display: flex;
      align-items: center;
      gap: 4px;
    }
  }
}

// High contrast mode
:global(.high-contrast) {
  .mobile-features {
    .offline-indicator {
      background: #000;
      border: 2px solid #fff;
    }

    .notification-settings,
    .accessibility-settings {
      background: #000;
      color: #fff;
      border: 2px solid #fff;

      h3 {
        color: #fff;
      }
    }
  }
}

// Large text mode
:global(.large-text) {
  .mobile-features {
    font-size: 18px;

    .setting-item label {
      font-size: 16px;
    }

    button {
      font-size: 16px;
      padding: 12px 20px;
    }
  }
}

// Reduced motion mode
:global(.reduced-motion) {
  .mobile-features {
    * {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
    }
  }
}

// Screen reader only content
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
