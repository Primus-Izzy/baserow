<template>
  <div
    class="notification-item"
    :class="{
      unread: !notification.is_read,
      clickable: isClickable,
    }"
    @click="handleClick"
  >
    <div class="notification-icon">
      <i :class="getNotificationIcon(notification.notification_type)"></i>
    </div>

    <div class="notification-content">
      <div class="notification-title">
        {{ notification.title }}
      </div>

      <div class="notification-message">
        {{ notification.message }}
      </div>

      <div class="notification-meta">
        <span class="notification-time">
          {{ formatTime(notification.created_at) }}
        </span>
        <span class="notification-type">
          {{ getTypeLabel(notification.notification_type) }}
        </span>
      </div>
    </div>

    <div class="notification-actions">
      <button
        v-if="!notification.is_read"
        class="mark-read-btn"
        title="Mark as read"
        @click.stop="markAsRead"
      >
        <i class="fas fa-check"></i>
      </button>

      <div class="notification-status">
        <div v-if="!notification.is_read" class="unread-indicator"></div>
      </div>
    </div>
  </div>
</template>

<script>
import { getHumanPeriodAgoCount } from '@baserow/modules/core/utils/date'

export default {
  name: 'NotificationItem',
  props: {
    notification: {
      type: Object,
      required: true,
    },
  },
  computed: {
    isClickable() {
      // Determine if notification should be clickable based on type
      const clickableTypes = [
        'comment_mention',
        'comment_reply',
        'row_assigned',
        'form_submission',
        'automation_failed',
      ]
      return clickableTypes.includes(this.notification.notification_type.name)
    },
  },
  methods: {
    handleClick() {
      if (this.isClickable) {
        this.$emit('click', this.notification)
      }
    },

    markAsRead() {
      this.$emit('mark-read', [this.notification.id])
    },

    getNotificationIcon(notificationType) {
      const iconMap = {
        comment_mention: 'fas fa-at',
        comment_reply: 'fas fa-reply',
        row_assigned: 'fas fa-user-tag',
        automation_failed: 'fas fa-exclamation-triangle',
        form_submission: 'fas fa-file-alt',
        workspace_invitation: 'fas fa-user-plus',
        security_alert: 'fas fa-shield-alt',
        digest: 'fas fa-newspaper',
      }

      return iconMap[notificationType.name] || 'fas fa-bell'
    },

    getTypeLabel(notificationType) {
      const labelMap = {
        comment_mention: 'Mention',
        comment_reply: 'Reply',
        row_assigned: 'Assignment',
        automation_failed: 'Automation',
        form_submission: 'Form',
        workspace_invitation: 'Invitation',
        security_alert: 'Security',
        digest: 'Digest',
      }

      return labelMap[notificationType.name] || notificationType.category
    },

    formatTime(timestamp) {
      try {
        const { count, period } = getHumanPeriodAgoCount(timestamp)
        return `${count} ${period} ago`
      } catch (error) {
        return 'Recently'
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.notification-item {
  display: flex;
  align-items: flex-start;
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-neutral-100);
  transition: background-color 0.2s;

  &:hover {
    background-color: var(--color-neutral-50);
  }

  &.clickable {
    cursor: pointer;

    &:hover {
      background-color: var(--color-primary-50);
    }
  }

  &.unread {
    background-color: var(--color-primary-25);

    &:hover {
      background-color: var(--color-primary-75);
    }
  }

  &:last-child {
    border-bottom: none;
  }
}

.notification-icon {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-neutral-100);
  border-radius: 50%;
  margin-right: 12px;

  .fas {
    font-size: 14px;
    color: var(--color-neutral-600);
  }

  .unread & {
    background-color: var(--color-primary-100);

    .fas {
      color: var(--color-primary-600);
    }
  }
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-weight: 600;
  font-size: 14px;
  color: var(--color-neutral-900);
  margin-bottom: 4px;
  line-height: 1.3;
}

.notification-message {
  font-size: 13px;
  color: var(--color-neutral-700);
  line-height: 1.4;
  margin-bottom: 6px;

  // Truncate long messages
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.notification-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--color-neutral-500);
}

.notification-time {
  font-weight: 500;
}

.notification-type {
  padding: 2px 6px;
  background-color: var(--color-neutral-100);
  border-radius: 3px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.notification-actions {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 12px;
}

.mark-read-btn {
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;

  &:hover {
    background-color: var(--color-success-100);
    color: var(--color-success-600);
  }

  .fas {
    font-size: 12px;
  }
}

.notification-status {
  width: 8px;
  height: 8px;
}

.unread-indicator {
  width: 8px;
  height: 8px;
  background-color: var(--color-primary-500);
  border-radius: 50%;
}

// Category-specific icon colors
.notification-item {
  &[data-category='collaboration'] .notification-icon {
    background-color: var(--color-blue-100);

    .fas {
      color: var(--color-blue-600);
    }
  }

  &[data-category='automation'] .notification-icon {
    background-color: var(--color-purple-100);

    .fas {
      color: var(--color-purple-600);
    }
  }

  &[data-category='security'] .notification-icon {
    background-color: var(--color-error-100);

    .fas {
      color: var(--color-error-600);
    }
  }

  &[data-category='system'] .notification-icon {
    background-color: var(--color-neutral-100);

    .fas {
      color: var(--color-neutral-600);
    }
  }
}
</style>
