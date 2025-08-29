/**
 * Service for notification API calls
 */

export default (client) => {
  return {
    /**
     * Get notifications for the current user
     */
    getNotifications(params = {}) {
      return client.get('/database/notifications/', { params })
    },
    
    /**
     * Get a specific notification
     */
    getNotification(id) {
      return client.get(`/database/notifications/${id}/`)
    },
    
    /**
     * Mark notifications as read
     */
    markAsRead(notificationIds) {
      return client.post('/database/notifications/mark_read/', {
        notification_ids: notificationIds
      })
    },
    
    /**
     * Mark all notifications as read
     */
    markAllAsRead(workspaceId = null) {
      const data = {}
      if (workspaceId) {
        data.workspace_id = workspaceId
      }
      return client.post('/database/notifications/mark_all_read/', data)
    },
    
    /**
     * Get notification statistics
     */
    getStats(params = {}) {
      return client.get('/database/notifications/stats/', { params })
    },
    
    /**
     * Get notification types
     */
    getNotificationTypes() {
      return client.get('/database/notification-types/')
    },
    
    /**
     * Get notification preferences
     */
    getPreferences(params = {}) {
      return client.get('/database/preferences/', { params })
    },
    
    /**
     * Update notification preferences
     */
    updatePreferences(data) {
      return client.post('/database/preferences/bulk_update/', data)
    },
    
    /**
     * Reset preferences to defaults
     */
    resetPreferencesToDefaults(workspaceId = null) {
      const data = {}
      if (workspaceId) {
        data.workspace_id = workspaceId
      }
      return client.post('/database/preferences/reset_to_defaults/', data)
    },
    
    /**
     * Get notification templates
     */
    getTemplates(params = {}) {
      return client.get('/database/templates/', { params })
    },
    
    /**
     * Create notification template
     */
    createTemplate(data) {
      return client.post('/database/templates/', data)
    },
    
    /**
     * Update notification template
     */
    updateTemplate(id, data) {
      return client.patch(`/database/templates/${id}/`, data)
    },
    
    /**
     * Delete notification template
     */
    deleteTemplate(id) {
      return client.delete(`/database/templates/${id}/`)
    }
  }
}