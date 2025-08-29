export default class RealTimeUpdatesService {
  constructor() {
    this.connections = new Map()
    this.subscriptions = new Map()
    this.reconnectAttempts = new Map()
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 1000
  }

  /**
   * Subscribe to real-time updates for a widget
   * @param {string} widgetId - The widget ID
   * @param {Function} callback - Callback function to handle updates
   * @param {Object} options - Configuration options
   */
  subscribe(widgetId, callback, options = {}) {
    const config = {
      interval: options.interval || 30000, // 30 seconds default
      enabled: options.enabled !== false,
      ...options,
    }

    if (!config.enabled) {
      return { unsubscribe: () => {} }
    }

    // Store subscription
    this.subscriptions.set(widgetId, {
      callback,
      config,
      lastUpdate: Date.now(),
    })

    // Start polling or WebSocket connection
    if (config.useWebSocket) {
      this.setupWebSocketConnection(widgetId, callback, config)
    } else {
      this.setupPolling(widgetId, callback, config)
    }

    return {
      unsubscribe: () => this.unsubscribe(widgetId),
    }
  }

  /**
   * Unsubscribe from real-time updates
   * @param {string} widgetId - The widget ID
   */
  unsubscribe(widgetId) {
    // Clear polling interval
    if (this.connections.has(widgetId)) {
      const connection = this.connections.get(widgetId)
      if (connection.type === 'polling' && connection.intervalId) {
        clearInterval(connection.intervalId)
      } else if (connection.type === 'websocket' && connection.socket) {
        connection.socket.close()
      }
      this.connections.delete(widgetId)
    }

    // Remove subscription
    this.subscriptions.delete(widgetId)
    this.reconnectAttempts.delete(widgetId)
  }

  /**
   * Setup polling-based updates
   * @param {string} widgetId - The widget ID
   * @param {Function} callback - Callback function
   * @param {Object} config - Configuration
   */
  setupPolling(widgetId, callback, config) {
    const intervalId = setInterval(async () => {
      try {
        await this.fetchWidgetData(widgetId, callback)
      } catch (error) {
        console.error(`Error fetching data for widget ${widgetId}:`, error)
        callback({ error: error.message })
      }
    }, config.interval)

    this.connections.set(widgetId, {
      type: 'polling',
      intervalId,
      config,
    })

    // Initial fetch
    this.fetchWidgetData(widgetId, callback)
  }

  /**
   * Setup WebSocket connection for real-time updates
   * @param {string} widgetId - The widget ID
   * @param {Function} callback - Callback function
   * @param {Object} config - Configuration
   */
  setupWebSocketConnection(widgetId, callback, config) {
    const wsUrl = this.getWebSocketUrl(widgetId)
    const socket = new WebSocket(wsUrl)

    socket.onopen = () => {
      console.log(`WebSocket connected for widget ${widgetId}`)
      this.reconnectAttempts.set(widgetId, 0)
      
      // Send subscription message
      socket.send(JSON.stringify({
        type: 'subscribe',
        widget_id: widgetId,
        config,
      }))
    }

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'widget_update' && data.widget_id === widgetId) {
          callback(data.payload)
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
      }
    }

    socket.onclose = () => {
      console.log(`WebSocket closed for widget ${widgetId}`)
      this.handleWebSocketReconnect(widgetId, callback, config)
    }

    socket.onerror = (error) => {
      console.error(`WebSocket error for widget ${widgetId}:`, error)
    }

    this.connections.set(widgetId, {
      type: 'websocket',
      socket,
      config,
    })
  }

  /**
   * Handle WebSocket reconnection
   * @param {string} widgetId - The widget ID
   * @param {Function} callback - Callback function
   * @param {Object} config - Configuration
   */
  handleWebSocketReconnect(widgetId, callback, config) {
    const attempts = this.reconnectAttempts.get(widgetId) || 0
    
    if (attempts < this.maxReconnectAttempts) {
      const delay = this.reconnectDelay * Math.pow(2, attempts) // Exponential backoff
      
      setTimeout(() => {
        console.log(`Attempting to reconnect WebSocket for widget ${widgetId} (attempt ${attempts + 1})`)
        this.reconnectAttempts.set(widgetId, attempts + 1)
        this.setupWebSocketConnection(widgetId, callback, config)
      }, delay)
    } else {
      console.error(`Max reconnection attempts reached for widget ${widgetId}`)
      // Fall back to polling
      this.setupPolling(widgetId, callback, config)
    }
  }

  /**
   * Fetch widget data via HTTP
   * @param {string} widgetId - The widget ID
   * @param {Function} callback - Callback function
   */
  async fetchWidgetData(widgetId, callback) {
    const subscription = this.subscriptions.get(widgetId)
    if (!subscription) return

    const { config } = subscription
    let endpoint

    // Determine the correct endpoint based on widget type
    if (config.widgetType === 'kpi') {
      endpoint = `/api/dashboard/enhanced/kpi-widgets/${widgetId}/data/`
    } else if (config.widgetType === 'enhanced_chart') {
      endpoint = `/api/dashboard/enhanced/enhanced-chart-widgets/${widgetId}/data/`
    } else {
      endpoint = `/api/dashboard/widgets/${widgetId}/data/`
    }

    try {
      const response = await fetch(endpoint, {
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`,
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      
      // Update last update timestamp
      subscription.lastUpdate = Date.now()
      
      callback(data)
    } catch (error) {
      throw error
    }
  }

  /**
   * Get WebSocket URL for widget updates
   * @param {string} widgetId - The widget ID
   * @returns {string} WebSocket URL
   */
  getWebSocketUrl(widgetId) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    return `${protocol}//${host}/ws/dashboard/widgets/${widgetId}/`
  }

  /**
   * Get authentication token
   * @returns {string} Auth token
   */
  getAuthToken() {
    // This should be implemented based on your authentication system
    return localStorage.getItem('authToken') || ''
  }

  /**
   * Pause all subscriptions
   */
  pauseAll() {
    this.subscriptions.forEach((subscription, widgetId) => {
      const connection = this.connections.get(widgetId)
      if (connection && connection.type === 'polling' && connection.intervalId) {
        clearInterval(connection.intervalId)
        connection.paused = true
      }
    })
  }

  /**
   * Resume all subscriptions
   */
  resumeAll() {
    this.subscriptions.forEach((subscription, widgetId) => {
      const connection = this.connections.get(widgetId)
      if (connection && connection.paused) {
        this.setupPolling(widgetId, subscription.callback, subscription.config)
      }
    })
  }

  /**
   * Get subscription status
   * @param {string} widgetId - The widget ID
   * @returns {Object} Status information
   */
  getStatus(widgetId) {
    const subscription = this.subscriptions.get(widgetId)
    const connection = this.connections.get(widgetId)
    
    if (!subscription || !connection) {
      return { active: false }
    }

    return {
      active: true,
      type: connection.type,
      lastUpdate: subscription.lastUpdate,
      config: subscription.config,
      reconnectAttempts: this.reconnectAttempts.get(widgetId) || 0,
    }
  }

  /**
   * Update subscription configuration
   * @param {string} widgetId - The widget ID
   * @param {Object} newConfig - New configuration
   */
  updateConfig(widgetId, newConfig) {
    const subscription = this.subscriptions.get(widgetId)
    if (!subscription) return

    // Update config
    subscription.config = { ...subscription.config, ...newConfig }

    // Restart connection with new config
    this.unsubscribe(widgetId)
    this.subscribe(widgetId, subscription.callback, subscription.config)
  }

  /**
   * Cleanup all connections
   */
  destroy() {
    this.subscriptions.forEach((_, widgetId) => {
      this.unsubscribe(widgetId)
    })
    
    this.connections.clear()
    this.subscriptions.clear()
    this.reconnectAttempts.clear()
  }
}

// Create singleton instance
export const realTimeUpdatesService = new RealTimeUpdatesService()

// Handle page visibility changes to pause/resume updates
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    realTimeUpdatesService.pauseAll()
  } else {
    realTimeUpdatesService.resumeAll()
  }
})

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  realTimeUpdatesService.destroy()
})