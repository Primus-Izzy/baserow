<template>
  <div class="comment-notifications">
    <div class="comment-notifications__header">
      <h4 class="comment-notifications__title">
        <i class="iconoir-bell"></i>
        Comment Notifications
        <span v-if="unreadCount > 0" class="comment-notifications__badge">
          {{ unreadCount }}
        </span>
      </h4>
      <div class="comment-notifications__actions">
        <button
          v-if="notifications.length > 0"
          class="comment-notifications__action-btn"
          @click="markAllAsRead"
          :disabled="unreadCount === 0"
        >
          Mark all read
        </button>
        <button
          class="comment-notifications__action-btn"
          @click="refreshNotifications"
          :disabled="loading"
        >
          <i class="iconoir-refresh" :class="{ spinning: loading }"></i>
        </button>
      </div>
    </div>

    <div class="comment-notifications__content">
      <div v-if="loading && notifications.length === 0" class="comment-notifications__loading">
        <div class="notification-skeleton" v-for="i in 3" :key="i">
          <div class="notification-skeleton__avatar"></div>
          <div class="notification-skeleton__content">
            <div class="notification-skeleton__header"></div>
            <div class="notification-skeleton__text"></div>
          </div>
        </div>
      </div>

      <div v-else-if="notifications.length === 0" class="comment-notifications__empty">
        <i class="iconoir-bell-off"></i>
        <p>No comment notifications</p>
      </div>

      <div v-else class="comment-notifications__list">
        <div
          v-for="notification in notifications"
          :key="notification.id"
          class="comment-notification"
          :class="{ 'comment-notification--unread': !notification.read }"
          @click="handleNotificationClick(notification)"
        >
          <div class="comment-notification__avatar">
            <div
              class="comment-notification__avatar-circle"
              :style="{ backgroundColor: getUserColor(notification.sender_id) }"
            >
              {{ getUserInitials(notification.sender_name) }}
            </div>
          </div>

          <div class="comment-notification__content">
            <div class="comment-notification__header">
              <span class="comment-notification__sender">{{ notification.sender_name }}</span>
              <span class="comment-notification__action">{{ getNotificationAction(notification.type) }}</span>
              <span class="comment-notification__timestamp">
                {{ formatRelativeTime(notification.created_at) }}
              </span>
            </div>
            
            <div class="comment-notification__message">
              {{ notification.message }}
            </div>
            
            <div class="comment-notification__context">
              <i class="iconoir-table"></i>
              {{ notification.table_name }} - Row {{ notification.row_id }}
            </div>
          </div>

          <div class="comment-notification__actions">
            <button
              v-if="!notification.read"
              class="comment-notification__mark-read"
              @click.stop="markAsRead(notification.id)"
              title="Mark as read"
            >
              <i class="iconoir-check"></i>
            </button>
            <button
              class="comment-notification__dismiss"
              @click.stop="dismissNotification(notification.id)"
              title="Dismiss"
            >
              <i class="iconoir-xmark"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CommentNotifications',
  data() {
    return {
      notifications: [],
      loading: false,
    }
  },
  computed: {
    unreadCount() {
      return this.notifications.filter(n => !n.read).length
    },
  },
  async mounted() {
    await this.loadNotifications()
    this.setupWebSocketListener()
  },
  beforeDestroy() {
    this.cleanupWebSocketListener()
  },
  methods: {
    async loadNotifications() {
      this.loading = true
      try {
        const response = await this.$axios.get('/api/notifications/comments/')
        this.notifications = response.data.results || response.data
      } catch (error) {
        console.error('Failed to load comment notifications:', error)
        this.$toast.error('Failed to load notifications')
      } finally {
        this.loading = false
      }
    },
    async refreshNotifications() {
      await this.loadNotifications()
    },
    async markAsRead(notificationId) {
      try {
        await this.$axios.patch(`/api/notifications/${notificationId}/`, {
          read: true,
        })
        
        const notification = this.notifications.find(n => n.id === notificationId)
        if (notification) {
          notification.read = true
        }
      } catch (error) {
        console.error('Failed to mark notification as read:', error)
        this.$toast.error('Failed to update notification')
      }
    },
    async markAllAsRead() {
      const unreadIds = this.notifications
        .filter(n => !n.read)
        .map(n => n.id)
      
      if (unreadIds.length === 0) return
      
      try {
        await this.$axios.post('/api/notifications/mark-all-read/', {
          notification_ids: unreadIds,
        })
        
        this.notifications.forEach(notification => {
          if (unreadIds.includes(notification.id)) {
            notification.read = true
          }
        })
        
        this.$toast.success('All notifications marked as read')
      } catch (error) {
        console.error('Failed to mark all notifications as read:', error)
        this.$toast.error('Failed to update notifications')
      }
    },
    async dismissNotification(notificationId) {
      try {
        await this.$axios.delete(`/api/notifications/${notificationId}/`)
        
        this.notifications = this.notifications.filter(n => n.id !== notificationId)
      } catch (error) {
        console.error('Failed to dismiss notification:', error)
        this.$toast.error('Failed to dismiss notification')
      }
    },
    handleNotificationClick(notification) {
      // Navigate to the comment location
      this.$router.push({
        name: 'database-table',
        params: {
          databaseId: notification.database_id,
          tableId: notification.table_id,
        },
        query: {
          rowId: notification.row_id,
          commentId: notification.comment_id,
        },
      })
      
      // Mark as read if not already
      if (!notification.read) {
        this.markAsRead(notification.id)
      }
    },
    setupWebSocketListener() {
      // Listen for real-time notification updates
      if (this.$ws) {
        this.$ws.on('comment_notification', this.handleNewNotification)
      }
    },
    cleanupWebSocketListener() {
      if (this.$ws) {
        this.$ws.off('comment_notification', this.handleNewNotification)
      }
    },
    handleNewNotification(notification) {
      // Add new notification to the top of the list
      this.notifications.unshift(notification)
      
      // Show toast notification
      this.$toast.info(`New comment from ${notification.sender_name}`)
    },
    getUserInitials(name) {
      if (!name) return '?'
      return name
        .split(' ')
        .map(part => part.charAt(0).toUpperCase())
        .join('')
        .substring(0, 2)
    },
    getUserColor(userId) {
      const colors = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
        '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
      ]
      return colors[userId % colors.length]
    },
    formatRelativeTime(dateString) {
      const date = new Date(dateString)
      const now = new Date()
      const diffInSeconds = Math.floor((now - date) / 1000)
      
      if (diffInSeconds < 60) {
        return 'just now'
      } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60)
        return `${minutes}m ago`
      } else if (diffInSeconds < 86400) {
        const hours = Math.floor(diffInSeconds / 3600)
        return `${hours}h ago`
      } else if (diffInSeconds < 604800) {
        const days = Math.floor(diffInSeconds / 86400)
        return `${days}d ago`
      } else {
        return date.toLocaleDateString()
      }
    },
    getNotificationAction(type) {
      switch (type) {
        case 'comment_mention':
          return 'mentioned you in a comment'
        case 'comment_reply':
          return 'replied to your comment'
        case 'comment_created':
          return 'commented on'
        default:
          return 'interacted with'
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.comment-notifications {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.comment-notifications__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #e9ecef;
}

.comment-notifications__title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  
  i {
    font-size: 18px;
  }
}

.comment-notifications__badge {
  background: #dc3545;
  color: white;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
}

.comment-notifications__actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.comment-notifications__action-btn {
  padding: 6px 12px;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  background: white;
  color: #6c757d;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover:not(:disabled) {
    background: #f8f9fa;
    border-color: #adb5bd;
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  i {
    font-size: 14px;
  }
}

.comment-notifications__content {
  flex: 1;
  overflow: hidden;
}

.comment-notifications__loading {
  padding: 20px;
}

.notification-skeleton {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  
  &__avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #e9ecef;
    animation: pulse 1.5s ease-in-out infinite;
  }
  
  &__content {
    flex: 1;
  }
  
  &__header {
    width: 200px;
    height: 12px;
    background: #e9ecef;
    border-radius: 4px;
    margin-bottom: 8px;
    animation: pulse 1.5s ease-in-out infinite;
  }
  
  &__text {
    width: 100%;
    height: 32px;
    background: #e9ecef;
    border-radius: 4px;
    animation: pulse 1.5s ease-in-out infinite;
  }
}

.comment-notifications__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #6c757d;
  text-align: center;
  
  i {
    font-size: 48px;
    margin-bottom: 16px;
    opacity: 0.5;
  }
  
  p {
    margin: 0;
    font-size: 14px;
  }
}

.comment-notifications__list {
  overflow-y: auto;
  padding: 8px;
}

.comment-notification {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 4px;
  
  &:hover {
    background: #f8f9fa;
  }
  
  &--unread {
    background: #e3f2fd;
    border-left: 3px solid #2196f3;
    
    &:hover {
      background: #bbdefb;
    }
  }
}

.comment-notification__avatar {
  flex-shrink: 0;
}

.comment-notification__avatar-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  font-weight: 600;
}

.comment-notification__content {
  flex: 1;
  min-width: 0;
}

.comment-notification__header {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 4px;
  font-size: 12px;
}

.comment-notification__sender {
  font-weight: 600;
  color: #333;
}

.comment-notification__action {
  color: #6c757d;
}

.comment-notification__timestamp {
  color: #6c757d;
  margin-left: auto;
}

.comment-notification__message {
  color: #333;
  font-size: 14px;
  line-height: 1.4;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.comment-notification__context {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #6c757d;
  
  i {
    font-size: 12px;
  }
}

.comment-notification__actions {
  display: flex;
  align-items: flex-start;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s ease;
  
  .comment-notification:hover & {
    opacity: 1;
  }
}

.comment-notification__mark-read,
.comment-notification__dismiss {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: #6c757d;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(0, 0, 0, 0.1);
    color: #333;
  }
  
  i {
    font-size: 12px;
  }
}

.comment-notification__dismiss:hover {
  background: #dc3545;
  color: white;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>