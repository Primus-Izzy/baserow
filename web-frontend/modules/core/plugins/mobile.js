/**
 * Mobile features plugin for Baserow
 * Integrates offline sync, camera access, push notifications, and accessibility
 */

import OfflineSyncService from '~/modules/core/services/offlineSync'
import CameraAccessService from '~/modules/core/services/cameraAccess'
import PushNotificationService from '~/modules/core/services/pushNotifications'
import MobileAccessibilityService from '~/modules/core/services/mobileAccessibility'

export default function ({ app, store, $axios, isDev }, inject) {
  // Initialize mobile services
  const mobileServices = {
    offlineSync: null,
    cameraAccess: null,
    pushNotifications: null,
    accessibility: null
  }

  // Mobile detection
  const isMobile = () => {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
           (window.innerWidth <= 768)
  }

  // Initialize services
  const initializeMobileServices = async () => {
    try {
      // Initialize offline sync
      mobileServices.offlineSync = new OfflineSyncService()
      mobileServices.offlineSync.$axios = $axios

      // Initialize camera access
      mobileServices.cameraAccess = new CameraAccessService()

      // Initialize push notifications
      mobileServices.pushNotifications = new PushNotificationService()
      mobileServices.pushNotifications.$axios = $axios
      mobileServices.pushNotifications.$router = app.router

      // Initialize accessibility
      mobileServices.accessibility = new MobileAccessibilityService()

      // Setup service worker if supported
      if ('serviceWorker' in navigator && !isDev) {
        await setupServiceWorker()
      }

      if (isDev) console.log('Mobile services initialized successfully')
    } catch (error) {
      if (isDev) console.error('Failed to initialize mobile services:', error)
    }
  }

  // Setup service worker
  const setupServiceWorker = async () => {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js')
      
      // Handle service worker updates
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing
        
        newWorker.addEventListener('statechange', () => {
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
            // New service worker available
            store.dispatch('mobile/setServiceWorkerUpdate', true)
          }
        })
      })

      // Listen for messages from service worker
      navigator.serviceWorker.addEventListener('message', (event) => {
        const { type, data } = event.data

        switch (type) {
          case 'SYNC_COMPLETE':
            store.dispatch('mobile/setSyncStatus', data)
            break
          case 'NOTIFICATION_CLICK':
            handleNotificationClick(data)
            break
        }
      })

      if (isDev) console.log('Service worker registered successfully')
    } catch (error) {
      if (isDev) console.error('Service worker registration failed:', error)
    }
  }

  // Handle notification clicks
  const handleNotificationClick = (data) => {
    if (data.url) {
      app.router.push(data.url)
    } else if (data.tableId) {
      app.router.push(`/database/${data.databaseId}/table/${data.tableId}`)
    }
  }

  // Mobile-specific API methods
  const mobileAPI = {
    // Offline sync methods
    async queueOperation(operation) {
      if (mobileServices.offlineSync) {
        return await mobileServices.offlineSync.queueOperation(operation)
      }
    },

    async syncPendingOperations() {
      if (mobileServices.offlineSync) {
        return await mobileServices.offlineSync.syncPendingOperations()
      }
    },

    getSyncStatus() {
      if (mobileServices.offlineSync) {
        return mobileServices.offlineSync.getSyncStatus()
      }
      return null
    },

    // Camera methods
    async openCamera() {
      if (mobileServices.cameraAccess) {
        return await mobileServices.cameraAccess.requestCameraPermission()
      }
    },

    async capturePhoto(videoElement, options) {
      if (mobileServices.cameraAccess) {
        return await mobileServices.cameraAccess.capturePhoto(videoElement, options)
      }
    },

    async accessPhotoLibrary(options) {
      if (mobileServices.cameraAccess) {
        return await mobileServices.cameraAccess.accessPhotoLibrary(options)
      }
    },

    // Push notification methods
    async requestNotificationPermission() {
      if (mobileServices.pushNotifications) {
        return await mobileServices.pushNotifications.requestPermission()
      }
    },

    async subscribeToNotifications() {
      if (mobileServices.pushNotifications) {
        const subscription = await mobileServices.pushNotifications.subscribe()
        
        // Send subscription to server
        if (subscription && store.getters['auth/isAuthenticated']) {
          await mobileServices.pushNotifications.sendSubscriptionToServer(
            subscription,
            store.getters['auth/getUserId']
          )
        }
        
        return subscription
      }
    },

    async unsubscribeFromNotifications() {
      if (mobileServices.pushNotifications) {
        const subscription = await mobileServices.pushNotifications.getSubscription()
        
        if (subscription) {
          await mobileServices.pushNotifications.removeSubscriptionFromServer(subscription)
          await mobileServices.pushNotifications.unsubscribe()
        }
      }
    },

    // Accessibility methods
    announce(text, priority = 'polite') {
      if (mobileServices.accessibility) {
        mobileServices.accessibility.announce(text, priority)
      }
    },

    setHighContrastMode(enabled) {
      if (mobileServices.accessibility) {
        mobileServices.accessibility.setHighContrastMode(enabled)
      }
    },

    setLargeTextMode(enabled) {
      if (mobileServices.accessibility) {
        mobileServices.accessibility.setLargeTextMode(enabled)
      }
    },

    setReducedMotionMode(enabled) {
      if (mobileServices.accessibility) {
        mobileServices.accessibility.setReducedMotionMode(enabled)
      }
    },

    // Utility methods
    isMobile,
    
    isOfflineModeAvailable() {
      return mobileServices.offlineSync?.isOfflineModeAvailable() || false
    },

    isCameraSupported() {
      return mobileServices.cameraAccess?.isSupported || false
    },

    areNotificationsSupported() {
      return mobileServices.pushNotifications?.isSupported || false
    }
  }

  // Inject mobile API
  inject('mobile', mobileAPI)

  // Initialize services when plugin loads
  if (process.client) {
    initializeMobileServices()

    // Setup network status listeners
    window.addEventListener('online', () => {
      store.dispatch('mobile/setOnlineStatus', true)
      mobileAPI.syncPendingOperations()
    })

    window.addEventListener('offline', () => {
      store.dispatch('mobile/setOnlineStatus', false)
    })

    // Setup visibility change listener for sync
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden && navigator.onLine) {
        mobileAPI.syncPendingOperations()
      }
    })
  }
}

// Vuex store module for mobile state
export const mobileStore = {
  namespaced: true,
  
  state: () => ({
    isOnline: true,
    syncInProgress: false,
    pendingOperations: 0,
    lastSyncTime: null,
    serviceWorkerUpdate: false,
    notificationPermission: 'default',
    cameraPermission: 'default',
    settings: {
      offlineMode: true,
      notifications: true,
      highContrast: false,
      largeText: false,
      reducedMotion: false
    }
  }),
  
  mutations: {
    SET_ONLINE_STATUS(state, isOnline) {
      state.isOnline = isOnline
    },
    
    SET_SYNC_STATUS(state, { syncInProgress, pendingOperations, lastSyncTime }) {
      state.syncInProgress = syncInProgress
      state.pendingOperations = pendingOperations
      state.lastSyncTime = lastSyncTime
    },
    
    SET_SERVICE_WORKER_UPDATE(state, hasUpdate) {
      state.serviceWorkerUpdate = hasUpdate
    },
    
    SET_NOTIFICATION_PERMISSION(state, permission) {
      state.notificationPermission = permission
    },
    
    SET_CAMERA_PERMISSION(state, permission) {
      state.cameraPermission = permission
    },
    
    UPDATE_SETTINGS(state, settings) {
      state.settings = { ...state.settings, ...settings }
    }
  },
  
  actions: {
    setOnlineStatus({ commit }, isOnline) {
      commit('SET_ONLINE_STATUS', isOnline)
    },
    
    setSyncStatus({ commit }, status) {
      commit('SET_SYNC_STATUS', status)
    },
    
    setServiceWorkerUpdate({ commit }, hasUpdate) {
      commit('SET_SERVICE_WORKER_UPDATE', hasUpdate)
    },
    
    setNotificationPermission({ commit }, permission) {
      commit('SET_NOTIFICATION_PERMISSION', permission)
    },
    
    setCameraPermission({ commit }, permission) {
      commit('SET_CAMERA_PERMISSION', permission)
    },
    
    updateSettings({ commit }, settings) {
      commit('UPDATE_SETTINGS', settings)
      
      // Save to localStorage
      if (process.client) {
        localStorage.setItem('baserow-mobile-settings', JSON.stringify(settings))
      }
    },
    
    loadSettings({ commit }) {
      if (process.client) {
        try {
          const saved = localStorage.getItem('baserow-mobile-settings')
          if (saved) {
            const settings = JSON.parse(saved)
            commit('UPDATE_SETTINGS', settings)
          }
        } catch (error) {
          if (isDev) console.error('Failed to load mobile settings:', error)
        }
      }
    }
  },
  
  getters: {
    isOnline: (state) => state.isOnline,
    syncInProgress: (state) => state.syncInProgress,
    hasPendingOperations: (state) => state.pendingOperations > 0,
    lastSyncTime: (state) => state.lastSyncTime,
    hasServiceWorkerUpdate: (state) => state.serviceWorkerUpdate,
    notificationPermission: (state) => state.notificationPermission,
    cameraPermission: (state) => state.cameraPermission,
    settings: (state) => state.settings
  }
}