/**
 * Push notification service for mobile devices
 * Handles service worker registration, push subscriptions, and notifications
 */

export class PushNotificationService {
  constructor() {
    this.registration = null
    this.subscription = null
    this.isSupported = this.checkSupport()
    this.vapidPublicKey = process.env.VAPID_PUBLIC_KEY || ''
  }

  /**
   * Check if push notifications are supported
   */
  checkSupport() {
    return !!(
      'serviceWorker' in navigator &&
      'PushManager' in window &&
      'Notification' in window
    )
  }

  /**
   * Initialize push notification service
   */
  async initialize() {
    if (!this.isSupported) {
      throw new Error('Push notifications not supported')
    }

    try {
      // Register service worker
      this.registration = await navigator.serviceWorker.register('/sw.js')
      
      // Wait for service worker to be ready
      await navigator.serviceWorker.ready
      
      return this.registration
    } catch (error) {
      throw new Error(`Service worker registration failed: ${error.message}`)
    }
  }

  /**
   * Request notification permission
   */
  async requestPermission() {
    if (!this.isSupported) {
      throw new Error('Notifications not supported')
    }

    const permission = await Notification.requestPermission()
    
    if (permission !== 'granted') {
      throw new Error('Notification permission denied')
    }
    
    return permission
  }

  /**
   * Subscribe to push notifications
   */
  async subscribe() {
    if (!this.registration) {
      await this.initialize()
    }

    try {
      const subscription = await this.registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: this.urlBase64ToUint8Array(this.vapidPublicKey)
      })

      this.subscription = subscription
      return subscription
    } catch (error) {
      throw new Error(`Push subscription failed: ${error.message}`)
    }
  }

  /**
   * Unsubscribe from push notifications
   */
  async unsubscribe() {
    if (!this.subscription) return

    try {
      await this.subscription.unsubscribe()
      this.subscription = null
    } catch (error) {
      throw new Error(`Push unsubscription failed: ${error.message}`)
    }
  }

  /**
   * Get current subscription
   */
  async getSubscription() {
    if (!this.registration) {
      await this.initialize()
    }

    try {
      this.subscription = await this.registration.pushManager.getSubscription()
      return this.subscription
    } catch (error) {
      console.error('Failed to get subscription:', error)
      return null
    }
  }

  /**
   * Show local notification
   */
  async showNotification(title, options = {}) {
    if (!this.isSupported) return

    const defaultOptions = {
      icon: '/icon-192x192.png',
      badge: '/badge-72x72.png',
      vibrate: [200, 100, 200],
      tag: 'baserow-notification',
      requireInteraction: false,
      ...options
    }

    if (this.registration) {
      return this.registration.showNotification(title, defaultOptions)
    } else {
      return new Notification(title, defaultOptions)
    }
  }

  /**
   * Handle notification click
   */
  setupNotificationHandlers() {
    if (!this.registration) return

    // Handle notification click
    navigator.serviceWorker.addEventListener('message', (event) => {
      if (event.data && event.data.type === 'NOTIFICATION_CLICK') {
        const { data } = event.data
        this.handleNotificationClick(data)
      }
    })
  }

  /**
   * Handle notification click action
   */
  handleNotificationClick(data) {
    // Navigate to relevant page based on notification data
    if (data.url) {
      window.open(data.url, '_blank')
    } else if (data.tableId) {
      this.$router.push(`/database/${data.databaseId}/table/${data.tableId}`)
    }
  }

  /**
   * Send subscription to server
   */
  async sendSubscriptionToServer(subscription, userId) {
    try {
      await this.$axios.post('/api/push-subscriptions/', {
        subscription: subscription.toJSON(),
        user_id: userId,
        user_agent: navigator.userAgent
      })
    } catch (error) {
      throw new Error(`Failed to save subscription: ${error.message}`)
    }
  }

  /**
   * Remove subscription from server
   */
  async removeSubscriptionFromServer(subscription) {
    try {
      await this.$axios.delete('/api/push-subscriptions/', {
        data: { subscription: subscription.toJSON() }
      })
    } catch (error) {
      console.error('Failed to remove subscription:', error)
    }
  }

  /**
   * Check notification permission status
   */
  getPermissionStatus() {
    if (!this.isSupported) return 'unsupported'
    return Notification.permission
  }

  /**
   * Convert VAPID key to Uint8Array
   */
  urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4)
    const base64 = (base64String + padding)
      .replace(/-/g, '+')
      .replace(/_/g, '/')

    const rawData = window.atob(base64)
    const outputArray = new Uint8Array(rawData.length)

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i)
    }
    return outputArray
  }

  /**
   * Test notification functionality
   */
  async testNotification() {
    try {
      await this.requestPermission()
      await this.showNotification('Test Notification', {
        body: 'Push notifications are working!',
        icon: '/icon-192x192.png'
      })
    } catch (error) {
      throw new Error(`Notification test failed: ${error.message}`)
    }
  }
}

export default PushNotificationService