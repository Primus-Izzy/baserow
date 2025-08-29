import CommentsService from './comments'

/**
 * WebSocket service for real-time collaboration features
 */
export default class CollaborationService {
  constructor(app) {
    this.app = app
    this.ws = null
    this.isConnected = false
    this.messageHandlers = new Map()
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 1000
    this.heartbeatInterval = null
    this.subscribedPages = new Set()
  }

  /**
   * Connect to WebSocket
   */
  async connect() {
    if (this.isConnected) return

    const token = this.app.$auth.getToken('local')
    if (!token) {
      throw new Error('No authentication token available')
    }

    const wsUrl = `${this.app.$config.BASEROW_PUBLIC_URL.replace('http', 'ws')}/ws/core/?jwt_token=${token}`
    
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(wsUrl)
      
      this.ws.onopen = () => {
        this.isConnected = true
        this.reconnectAttempts = 0
        this.startHeartbeat()
        this.app.store.dispatch('database/collaboration/handleWebSocketConnect')
        resolve()
      }

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          this.handleMessage(message)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      this.ws.onclose = () => {
        this.isConnected = false
        this.stopHeartbeat()
        this.app.store.dispatch('database/collaboration/handleWebSocketDisconnect')
        this.attemptReconnect()
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        reject(error)
      }

      // Timeout after 10 seconds
      setTimeout(() => {
        if (!this.isConnected) {
          reject(new Error('WebSocket connection timeout'))
        }
      }, 10000)
    })
  }

  /**
   * Disconnect from WebSocket
   */
  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.isConnected = false
    this.stopHeartbeat()
    this.subscribedPages.clear()
  }

  /**
   * Send message to WebSocket
   */
  async send(message) {
    if (!this.isConnected || !this.ws) {
      throw new Error('WebSocket not connected')
    }

    return new Promise((resolve, reject) => {
      try {
        this.ws.send(JSON.stringify(message))
        resolve()
      } catch (error) {
        reject(error)
      }
    })
  }

  /**
   * Subscribe to a page for real-time updates
   */
  async subscribePage(pageType, parameters) {
    const pageKey = `${pageType}:${JSON.stringify(parameters)}`
    
    if (this.subscribedPages.has(pageKey)) {
      return // Already subscribed
    }

    await this.send({
      page: pageType,
      ...parameters,
    })

    this.subscribedPages.add(pageKey)
  }

  /**
   * Unsubscribe from a page
   */
  async unsubscribePage(pageType, parameters) {
    const pageKey = `${pageType}:${JSON.stringify(parameters)}`
    
    if (!this.subscribedPages.has(pageKey)) {
      return // Not subscribed
    }

    await this.send({
      remove_page: pageType,
      ...parameters,
    })

    this.subscribedPages.delete(pageKey)
  }

  /**
   * Handle incoming WebSocket messages
   */
  handleMessage(message) {
    // Dispatch to store for state management
    this.app.store.dispatch('database/collaboration/handleWebSocketMessage', message)

    // Call registered message handlers
    const handlers = this.messageHandlers.get(message.type) || []
    handlers.forEach(handler => {
      try {
        handler(message)
      } catch (error) {
        console.error('Error in message handler:', error)
      }
    })
  }

  /**
   * Register a message handler
   */
  on(messageType, handler) {
    if (!this.messageHandlers.has(messageType)) {
      this.messageHandlers.set(messageType, [])
    }
    this.messageHandlers.get(messageType).push(handler)
  }

  /**
   * Unregister a message handler
   */
  off(messageType, handler) {
    const handlers = this.messageHandlers.get(messageType)
    if (handlers) {
      const index = handlers.indexOf(handler)
      if (index > -1) {
        handlers.splice(index, 1)
      }
    }
  }

  /**
   * Start heartbeat to keep connection alive
   */
  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected) {
        this.send({ type: 'ping' }).catch(() => {
          // Ignore ping errors
        })
      }
    }, 30000) // Send ping every 30 seconds
  }

  /**
   * Stop heartbeat
   */
  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  /**
   * Attempt to reconnect with exponential backoff
   */
  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached')
      return
    }

    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts)
    this.reconnectAttempts++

    setTimeout(async () => {
      try {
        await this.connect()
        
        // Re-subscribe to all pages
        const pagesToResubscribe = Array.from(this.subscribedPages)
        this.subscribedPages.clear()
        
        for (const pageKey of pagesToResubscribe) {
          const [pageType, parametersJson] = pageKey.split(':')
          const parameters = JSON.parse(parametersJson)
          await this.subscribePage(pageType, parameters)
        }
      } catch (error) {
        console.error('Reconnection failed:', error)
        this.attemptReconnect()
      }
    }, delay)
  }

  /**
   * Get connection status
   */
  getConnectionStatus() {
    return {
      isConnected: this.isConnected,
      reconnectAttempts: this.reconnectAttempts,
      maxReconnectAttempts: this.maxReconnectAttempts,
    }
  }
}