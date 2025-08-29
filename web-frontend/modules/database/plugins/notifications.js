/**
 * Notification system plugin for Baserow
 */

import NotificationService from '@baserow/modules/database/services/notifications'

export default (context) => {
  const { app, store, $realtime } = context
  
  // Register notification service
  app.$notificationService = NotificationService(app.$client)
  
  // Set up real-time notification handling
  if ($realtime) {
    $realtime.subscribe('notifications', (data) => {
      if (data.type === 'notification_created') {
        // Add notification to store
        store.commit('database/notifications/ADD_NOTIFICATION', data.notification)
        
        // Show toast notification for important types
        const { notification_type, title } = data.notification
        
        switch (notification_type.category) {
          case 'security':
            app.$toast.error(title, {
              duration: 10000,
              action: {
                text: 'View',
                onClick: () => {
                  // Navigate to notification center
                  store.commit('ui/setNotificationPanelOpen', true)
                }
              }
            })
            break
            
          case 'collaboration':
            app.$toast.info(title, {
              duration: 5000,
              action: {
                text: 'View',
                onClick: () => {
                  store.commit('ui/setNotificationPanelOpen', true)
                }
              }
            })
            break
            
          case 'automation':
            if (notification_type.name === 'automation_failed') {
              app.$toast.warning(title, {
                duration: 8000,
                action: {
                  text: 'View',
                  onClick: () => {
                    store.commit('ui/setNotificationPanelOpen', true)
                  }
                }
              })
            } else {
              app.$toast.success(title)
            }
            break
            
          default:
            app.$toast.info(title)
        }
      }
    })
  }
  
  // Initialize notification system on app start
  store.dispatch('database/notifications/fetchStats').catch(() => {
    // Silently fail if notifications are not available
  })
}