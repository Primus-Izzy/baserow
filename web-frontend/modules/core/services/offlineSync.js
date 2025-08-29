/**
 * Offline synchronization service for mobile devices
 * Handles data caching, offline operations, and sync when online
 */

export class OfflineSyncService {
  constructor() {
    this.isOnline = navigator.onLine
    this.syncQueue = []
    this.offlineStorage = null
    this.syncInProgress = false
    this.lastSyncTime = null
    
    this.initializeOfflineStorage()
    this.setupNetworkListeners()
  }

  /**
   * Initialize offline storage using IndexedDB
   */
  async initializeOfflineStorage() {
    if (!('indexedDB' in window)) {
      console.warn('IndexedDB not supported, offline mode disabled')
      return
    }

    try {
      const { openDB } = await import('idb')
      this.offlineStorage = await openDB('baserow-offline', 1, {
        upgrade(db) {
          // Store for cached table data
          if (!db.objectStoreNames.contains('tables')) {
            const tableStore = db.createObjectStore('tables', { keyPath: 'id' })
            tableStore.createIndex('workspaceId', 'workspaceId')
          }

          // Store for pending operations
          if (!db.objectStoreNames.contains('pendingOps')) {
            const opsStore = db.createObjectStore('pendingOps', { 
              keyPath: 'id', 
              autoIncrement: true 
            })
            opsStore.createIndex('timestamp', 'timestamp')
            opsStore.createIndex('tableId', 'tableId')
          }

          // Store for cached views
          if (!db.objectStoreNames.contains('views')) {
            const viewStore = db.createObjectStore('views', { keyPath: 'id' })
            viewStore.createIndex('tableId', 'tableId')
          }
        }
      })
    } catch (error) {
      console.error('Failed to initialize offline storage:', error)
    }
  }

  /**
   * Setup network status listeners
   */
  setupNetworkListeners() {
    window.addEventListener('online', () => {
      this.isOnline = true
      this.syncPendingOperations()
    })

    window.addEventListener('offline', () => {
      this.isOnline = false
    })
  }

  /**
   * Cache table data for offline access
   */
  async cacheTableData(tableId, data, workspaceId) {
    if (!this.offlineStorage) return

    try {
      const tx = this.offlineStorage.transaction('tables', 'readwrite')
      await tx.store.put({
        id: tableId,
        workspaceId,
        data,
        cachedAt: Date.now()
      })
      await tx.done
    } catch (error) {
      console.error('Failed to cache table data:', error)
    }
  }

  /**
   * Get cached table data
   */
  async getCachedTableData(tableId) {
    if (!this.offlineStorage) return null

    try {
      const data = await this.offlineStorage.get('tables', tableId)
      return data?.data || null
    } catch (error) {
      console.error('Failed to get cached table data:', error)
      return null
    }
  }

  /**
   * Queue operation for later sync
   */
  async queueOperation(operation) {
    if (!this.offlineStorage) {
      this.syncQueue.push(operation)
      return
    }

    try {
      const tx = this.offlineStorage.transaction('pendingOps', 'readwrite')
      await tx.store.add({
        ...operation,
        timestamp: Date.now(),
        retryCount: 0
      })
      await tx.done
    } catch (error) {
      console.error('Failed to queue operation:', error)
      this.syncQueue.push(operation)
    }
  }

  /**
   * Sync pending operations when online
   */
  async syncPendingOperations() {
    if (!this.isOnline || this.syncInProgress) return

    this.syncInProgress = true

    try {
      // Get operations from IndexedDB
      let operations = []
      if (this.offlineStorage) {
        const tx = this.offlineStorage.transaction('pendingOps', 'readonly')
        operations = await tx.store.getAll()
      }

      // Add in-memory queue operations
      operations = [...operations, ...this.syncQueue]

      for (const operation of operations) {
        try {
          await this.executeOperation(operation)
          
          // Remove from IndexedDB if successful
          if (this.offlineStorage && operation.id) {
            const tx = this.offlineStorage.transaction('pendingOps', 'readwrite')
            await tx.store.delete(operation.id)
            await tx.done
          }
        } catch (error) {
          console.error('Failed to sync operation:', error)
          
          // Increment retry count
          if (this.offlineStorage && operation.id) {
            operation.retryCount = (operation.retryCount || 0) + 1
            if (operation.retryCount < 3) {
              const tx = this.offlineStorage.transaction('pendingOps', 'readwrite')
              await tx.store.put(operation)
              await tx.done
            }
          }
        }
      }

      // Clear in-memory queue
      this.syncQueue = []
      this.lastSyncTime = Date.now()

    } finally {
      this.syncInProgress = false
    }
  }

  /**
   * Execute a queued operation
   */
  async executeOperation(operation) {
    const { type, data, endpoint } = operation

    switch (type) {
      case 'CREATE_ROW':
        return await this.$axios.post(endpoint, data)
      case 'UPDATE_ROW':
        return await this.$axios.patch(endpoint, data)
      case 'DELETE_ROW':
        return await this.$axios.delete(endpoint)
      case 'UPDATE_FIELD':
        return await this.$axios.patch(endpoint, data)
      default:
        throw new Error(`Unknown operation type: ${type}`)
    }
  }

  /**
   * Check if offline mode is available
   */
  isOfflineModeAvailable() {
    return !!this.offlineStorage && 'serviceWorker' in navigator
  }

  /**
   * Get sync status
   */
  getSyncStatus() {
    return {
      isOnline: this.isOnline,
      syncInProgress: this.syncInProgress,
      pendingOperations: this.syncQueue.length,
      lastSyncTime: this.lastSyncTime
    }
  }
}

export default OfflineSyncService