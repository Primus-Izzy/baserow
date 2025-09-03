/**
 * Vuex store for notification system
 */

import NotificationService from '@/modules/database/services/notifications'

export const state = () => ({
  notifications: [],
  unreadCount: 0,
  preferences: {},
  notificationTypes: [],
  loading: false,
  error: null,
  stats: {
    total_notifications: 0,
    unread_notifications: 0,
    notifications_by_type: {},
    recent_activity: []
  }
})

export const mutations = {
  SET_NOTIFICATIONS(state, notifications) {
    state.notifications = notifications
  },
  
  ADD_NOTIFICATION(state, notification) {
    state.notifications.unshift(notification)
    if (!notification.is_read) {
      state.unreadCount++
    }
  },
  
  UPDATE_NOTIFICATION(state, { id, updates }) {
    const index = state.notifications.findIndex(n => n.id === id)
    if (index !== -1) {
      Object.assign(state.notifications[index], updates)
    }
  },
  
  REMOVE_NOTIFICATION(state, id) {
    const index = state.notifications.findIndex(n => n.id === id)
    if (index !== -1) {
      const notification = state.notifications[index]
      if (!notification.is_read) {
        state.unreadCount--
      }
      state.notifications.splice(index, 1)
    }
  },
  
  SET_UNREAD_COUNT(state, count) {
    state.unreadCount = count
  },
  
  MARK_AS_READ(state, notificationIds) {
    notificationIds.forEach(id => {
      const notification = state.notifications.find(n => n.id === id)
      if (notification && !notification.is_read) {
        notification.is_read = true
        state.unreadCount--
      }
    })
  },
  
  SET_PREFERENCES(state, preferences) {
    state.preferences = preferences
  },
  
  UPDATE_PREFERENCE(state, { id, updates }) {
    if (state.preferences[id]) {
      Object.assign(state.preferences[id], updates)
    }
  },
  
  SET_NOTIFICATION_TYPES(state, types) {
    state.notificationTypes = types
  },
  
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  
  SET_ERROR(state, error) {
    state.error = error
  },
  
  SET_STATS(state, stats) {
    state.stats = stats
  },
  
  CLEAR_ERROR(state) {
    state.error = null
  }
}

export const actions = {
  /**
   * Fetch notifications for the current user
   */
  async fetchNotifications({ commit }, { workspaceId = null, unreadOnly = false, page = 1 } = {}) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const params = { page }
      if (workspaceId) params.workspace_id = workspaceId
      if (unreadOnly) params.unread_only = true
      
      const response = await NotificationService.getNotifications(params)
      
      commit('SET_NOTIFICATIONS', response.data.results)
      commit('SET_UNREAD_COUNT', response.data.results.filter(n => !n.is_read).length)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Failed to fetch notifications')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  /**
   * Mark notifications as read
   */
  async markAsRead({ commit }, notificationIds) {
    try {
      await NotificationService.markAsRead(notificationIds)
      commit('MARK_AS_READ', notificationIds)
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Failed to mark notifications as read')
      throw error
    }
  },
  
  /**
   * Mark all notifications as read
   */
  async markAllAsRead({ commit }, workspaceId = null) {
    try {
      const response = await NotificationService.markAllAsRead(workspaceId)
      
      // Update all notifications to read status
      const readIds = []
      this.state.database.notifications.notifications.forEach(notification => {
        if (!notification.is_read) {
          readIds.push(notification.id)
        }
      })
      
      commit('MARK_AS_READ', readIds)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Failed to mark all notifications as read')
      throw error
    }
  },
  
  /**
   * Fetch notification preferences
   */
  async fetchPreferences({ commit }, workspaceId = null) {
    try {
      const params = workspaceId ? { workspace_id: workspaceId } : {}
      const response = await NotificationService.getPreferences(params)
      
      // Convert array to object for easier access
      const preferences = {}
      response.data.results.forEach(pref => {
        preferences[pref.id] = pref
      })
      
      commit('SET_PREFERENCES', preferences)
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Failed to fetch preferences')
      throw error
    }
  },
  
  /**
   * Update notification preferences
   */
  async updatePreferences({ commit }, { preferences, workspaceId = null }) {
    try {
      const response = await NotificationService.updatePreferences({
        preferences,
        workspace_id: workspaceId
      })
      
      // Refresh preferences after update
      await this.dispatch('database/notifications/fetchPreferences', workspaceId)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Failed to update preferences')
      throw error
    }
  },
  
  /**
   * Fetch notification types
   */
  async fetchNotificationTypes({ commit }) {
    try {
      const response = await NotificationService.getNotificationTypes()
      commit('SET_NOTIFICATION_TYPES', response.data.results)
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Failed to fetch notification types')
      throw error
    }
  },
  
  /**
   * Fetch notification statistics
   */
  async fetchStats({ commit }, workspaceId = null) {
    try {
      const params = workspaceId ? { workspace_id: workspaceId } : {}
      const response = await NotificationService.getStats(params)
      
      commit('SET_STATS', response.data)
      commit('SET_UNREAD_COUNT', response.data.unread_notifications)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Failed to fetch stats')
      throw error
    }
  },
  
  /**
   * Handle real-time notification received via WebSocket
   */
  handleRealtimeNotification({ commit }, notification) {
    commit('ADD_NOTIFICATION', notification)
  },
  
  /**
   * Reset preferences to defaults
   */
  async resetPreferencesToDefaults({ commit }, workspaceId = null) {
    try {
      const response = await NotificationService.resetPreferencesToDefaults(workspaceId)
      
      // Refresh preferences after reset
      await this.dispatch('database/notifications/fetchPreferences', workspaceId)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Failed to reset preferences')
      throw error
    }
  }
}

export const getters = {
  getNotificationById: (state) => (id) => {
    return state.notifications.find(n => n.id === id)
  },
  
  getUnreadNotifications: (state) => {
    return state.notifications.filter(n => !n.is_read)
  },
  
  getNotificationsByType: (state) => (type) => {
    return state.notifications.filter(n => n.notification_type.name === type)
  },
  
  hasUnreadNotifications: (state) => {
    return state.unreadCount > 0
  },
  
  getPreferenceByType: (state) => (typeName) => {
    return Object.values(state.preferences).find(
      pref => pref.notification_type_name === typeName
    )
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions,
}