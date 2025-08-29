<template>
  <div class="notification-center">
    <!-- Notification Bell Icon -->
    <div class="notification-bell" @click="togglePanel">
      <i class="fas fa-bell" :class="{ 'has-notifications': hasUnreadNotifications }"></i>
      <span v-if="unreadCount > 0" class="notification-badge">
        {{ unreadCount > 99 ? '99+' : unreadCount }}
      </span>
    </div>

    <!-- Notification Panel -->
    <div v-if="showPanel" class="notification-panel" @click.stop>
      <div class="notification-header">
        <h3>Notifications</h3>
        <div class="notification-actions">
          <button
            v-if="hasUnreadNotifications"
            class="btn btn-sm btn-ghost"
            @click="markAllAsRead"
            :disabled="loading"
          >
            Mark all read
          </button>
          <button class="btn btn-sm btn-ghost" @click="openSettings">
            <i class="fas fa-cog"></i>
          </button>
        </div>
      </div>

      <div class="notification-filters">
        <button
          class="filter-btn"
          :class="{ active: currentFilter === 'all' }"
          @click="setFilter('all')"
        >
          All
        </button>
        <button
          class="filter-btn"
          :class="{ active: currentFilter === 'unread' }"
          @click="setFilter('unread')"
        >
          Unread ({{ unreadCount }})
        </button>
      </div>

      <div class="notification-list">
        <div v-if="loading" class="notification-loading">
          <div class="loading-spinner"></div>
          <span>Loading notifications...</span>
        </div>

        <div v-else-if="filteredNotifications.length === 0" class="notification-empty">
          <i class="fas fa-bell-slash"></i>
          <p>{{ currentFilter === 'unread' ? 'No unread notifications' : 'No notifications yet' }}</p>
        </div>

        <div v-else class="notification-items">
          <NotificationItem
            v-for="notification in filteredNotifications"
            :key="notification.id"
            :notification="notification"
            @click="handleNotificationClick"
            @mark-read="markAsRead"
          />
        </div>

        <div v-if="hasMoreNotifications" class="notification-load-more">
          <button
            class="btn btn-sm btn-outline"
            @click="loadMoreNotifications"
            :disabled="loadingMore"
          >
            {{ loadingMore ? 'Loading...' : 'Load more' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Settings Modal -->
    <NotificationSettings
      v-if="showSettings"
      @close="closeSettings"
      @updated="handleSettingsUpdated"
    />

    <!-- Overlay -->
    <div
      v-if="showPanel"
      class="notification-overlay"
      @click="closePanel"
    ></div>
  </div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex'
import NotificationItem from './NotificationItem'
import NotificationSettings from './NotificationSettings'

export default {
  name: 'NotificationCenter',
  components: {
    NotificationItem,
    NotificationSettings
  },
  data() {
    return {
      showPanel: false,
      showSettings: false,
      currentFilter: 'all',
      currentPage: 1,
      hasMoreNotifications: false,
      loadingMore: false
    }
  },
  computed: {
    ...mapState('database/notifications', [
      'notifications',
      'unreadCount',
      'loading',
      'error'
    ]),
    ...mapGetters('database/notifications', [
      'hasUnreadNotifications',
      'getUnreadNotifications'
    ]),
    filteredNotifications() {
      if (this.currentFilter === 'unread') {
        return this.getUnreadNotifications
      }
      return this.notifications
    }
  },
  async mounted() {
    // Load initial notifications
    await this.fetchNotifications()
    
    // Set up real-time updates
    this.setupRealtimeUpdates()
    
    // Close panel when clicking outside
    document.addEventListener('click', this.handleDocumentClick)
  },
  beforeDestroy() {
    document.removeEventListener('click', this.handleDocumentClick)
  },
  methods: {
    ...mapActions('database/notifications', [
      'fetchNotifications',
      'markAsRead',
      'markAllAsRead',
      'handleRealtimeNotification'
    ]),
    
    togglePanel() {
      this.showPanel = !this.showPanel
      if (this.showPanel) {
        this.refreshNotifications()
      }
    },
    
    closePanel() {
      this.showPanel = false
    },
    
    openSettings() {
      this.showSettings = true
    },
    
    closeSettings() {
      this.showSettings = false
    },
    
    setFilter(filter) {
      this.currentFilter = filter
    },
    
    async refreshNotifications() {
      try {
        const workspaceId = this.$store.getters['workspace/getCurrentWorkspaceId']
        await this.fetchNotifications({ 
          workspaceId,
          page: 1
        })
        this.currentPage = 1
      } catch (error) {
        this.$toast.error('Failed to load notifications')
      }
    },
    
    async loadMoreNotifications() {
      if (this.loadingMore) return
      
      this.loadingMore = true
      try {
        const workspaceId = this.$store.getters['workspace/getCurrentWorkspaceId']
        const response = await this.fetchNotifications({
          workspaceId,
          page: this.currentPage + 1
        })
        
        this.currentPage++
        this.hasMoreNotifications = response.next !== null
      } catch (error) {
        this.$toast.error('Failed to load more notifications')
      } finally {
        this.loadingMore = false
      }
    },
    
    async handleNotificationClick(notification) {
      // Mark as read if not already read
      if (!notification.is_read) {
        await this.markAsRead([notification.id])
      }
      
      // Navigate to the related content if applicable
      this.navigateToNotificationContent(notification)
      
      // Close panel
      this.closePanel()
    },
    
    navigateToNotificationContent(notification) {
      // Handle navigation based on notification type
      const { notification_type, data } = notification
      
      switch (notification_type.name) {
        case 'comment_mention':
        case 'comment_reply':
          if (data.table_id && data.row_id) {
            this.$router.push({
              name: 'database-table',
              params: {
                databaseId: data.database_id,
                tableId: data.table_id
              },
              query: {
                row: data.row_id,
                comments: 'true'
              }
            })
          }
          break
          
        case 'row_assigned':
          if (data.table_id && data.row_id) {
            this.$router.push({
              name: 'database-table',
              params: {
                databaseId: data.database_id,
                tableId: data.table_id
              },
              query: {
                row: data.row_id
              }
            })
          }
          break
          
        case 'form_submission':
          if (data.table_id) {
            this.$router.push({
              name: 'database-table',
              params: {
                databaseId: data.database_id,
                tableId: data.table_id
              }
            })
          }
          break
          
        case 'automation_failed':
          if (data.automation_id) {
            this.$router.push({
              name: 'database-automation',
              params: {
                databaseId: data.database_id,
                automationId: data.automation_id
              }
            })
          }
          break
      }
    },
    
    handleSettingsUpdated() {
      this.$toast.success('Notification settings updated')
      this.closeSettings()
    },
    
    handleDocumentClick(event) {
      // Close panel if clicking outside
      if (!this.$el.contains(event.target)) {
        this.closePanel()
      }
    },
    
    setupRealtimeUpdates() {
      // Listen for real-time notifications via WebSocket
      if (this.$realtime) {
        this.$realtime.subscribe('notifications', (data) => {
          if (data.type === 'notification_created') {
            this.handleRealtimeNotification(data.notification)
            
            // Show toast for important notifications
            if (data.notification.notification_type.category === 'security') {
              this.$toast.error(data.notification.title)
            } else {
              this.$toast.info(data.notification.title)
            }
          }
        })
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.notification-center {
  position: relative;
}

.notification-bell {
  position: relative;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: var(--color-neutral-100);
  }
  
  .fas {
    font-size: 18px;
    color: var(--color-neutral-600);
    
    &.has-notifications {
      color: var(--color-primary-600);
    }
  }
}

.notification-badge {
  position: absolute;
  top: 2px;
  right: 2px;
  background-color: var(--color-error-500);
  color: white;
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 16px;
  text-align: center;
}

.notification-panel {
  position: absolute;
  top: 100%;
  right: 0;
  width: 400px;
  max-height: 600px;
  background: white;
  border: 1px solid var(--color-neutral-200);
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  display: flex;
  flex-direction: column;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--color-neutral-200);
  
  h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
  }
}

.notification-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.notification-filters {
  display: flex;
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-neutral-200);
  gap: 8px;
}

.filter-btn {
  padding: 6px 12px;
  border: none;
  background: transparent;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  
  &:hover {
    background-color: var(--color-neutral-100);
  }
  
  &.active {
    background-color: var(--color-primary-100);
    color: var(--color-primary-700);
  }
}

.notification-list {
  flex: 1;
  overflow-y: auto;
  max-height: 400px;
}

.notification-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
  gap: 12px;
  color: var(--color-neutral-600);
}

.notification-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px;
  color: var(--color-neutral-500);
  
  .fas {
    font-size: 32px;
    margin-bottom: 12px;
  }
  
  p {
    margin: 0;
    font-size: 14px;
  }
}

.notification-items {
  padding: 8px 0;
}

.notification-load-more {
  padding: 16px;
  text-align: center;
  border-top: 1px solid var(--color-neutral-200);
}

.notification-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid var(--color-neutral-200);
  border-top: 2px solid var(--color-primary-500);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .notification-panel {
    width: 320px;
    max-height: 500px;
  }
}
</style>