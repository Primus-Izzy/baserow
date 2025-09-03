<template>
  <div class="activity-log-entry">
    <div class="activity-log-entry__avatar">
      <Avatar
        v-if="entry.user"
        :initials="userInitials"
        :color="userColor"
        size="small"
      />
      <i
        v-else
        class="iconoir-system-restart activity-log-entry__system-icon"
      ></i>
    </div>

    <div class="activity-log-entry__content">
      <div class="activity-log-entry__header">
        <span class="activity-log-entry__user">
          {{
            entry.user
              ? entry.user_name || entry.user_email
              : $t('activityLog.system')
          }}
        </span>
        <span class="activity-log-entry__action">
          {{ getActionDescription(entry.action_type, entry.details) }}
        </span>
        <span class="activity-log-entry__time">
          {{ formatTime(entry.timestamp) }}
        </span>
      </div>

      <div v-if="hasDetails" class="activity-log-entry__details">
        <div
          v-if="entry.details.content_preview"
          class="activity-log-entry__preview"
        >
          "{{ entry.details.content_preview }}"
        </div>

        <div v-if="entry.details.field_name" class="activity-log-entry__field">
          <i class="iconoir-db"></i>
          {{ entry.details.field_name }}
        </div>

        <div v-if="entry.details.view_name" class="activity-log-entry__view">
          <i class="iconoir-eye-alt"></i>
          {{ entry.details.view_name }}
        </div>

        <div v-if="entry.details.row_id" class="activity-log-entry__row">
          <i class="iconoir-table-rows"></i>
          {{ $t('activityLog.row') }} #{{ entry.details.row_id }}
        </div>

        <div
          v-if="entry.details.mentions_count > 0"
          class="activity-log-entry__mentions"
        >
          <i class="iconoir-at-sign"></i>
          {{
            $tc('activityLog.mentions', entry.details.mentions_count, {
              count: entry.details.mentions_count,
            })
          }}
        </div>
      </div>
    </div>

    <div class="activity-log-entry__actions">
      <Button
        v-if="canNavigateToRow"
        type="ghost"
        size="tiny"
        @click="navigateToRow"
      >
        <i class="iconoir-nav-arrow-right"></i>
      </Button>
    </div>
  </div>
</template>

<script>
import { getHumanPeriodAgoCount } from '@baserow/modules/core/utils/date'

export default {
  name: 'ActivityLogEntry',
  props: {
    entry: {
      type: Object,
      required: true,
    },
    table: {
      type: Object,
      required: true,
    },
  },
  computed: {
    userInitials() {
      if (!this.entry.user) return 'SY'

      const name = this.entry.user_name || this.entry.user_email
      return name
        .split(' ')
        .map((word) => word.charAt(0).toUpperCase())
        .slice(0, 2)
        .join('')
    },

    userColor() {
      if (!this.entry.user) return 'gray'

      // Generate a consistent color based on user ID
      const colors = ['blue', 'green', 'purple', 'orange', 'red', 'teal']
      return colors[this.entry.user % colors.length]
    },

    hasDetails() {
      return this.entry.details && Object.keys(this.entry.details).length > 0
    },

    canNavigateToRow() {
      return (
        this.entry.details?.row_id && this.isRowAction(this.entry.action_type)
      )
    },
  },
  methods: {
    getActionDescription(actionType, details) {
      const actionMap = {
        row_created: this.$t('activityLog.actions.rowCreated'),
        row_updated: this.$t('activityLog.actions.rowUpdated'),
        row_deleted: this.$t('activityLog.actions.rowDeleted'),
        field_created: this.$t('activityLog.actions.fieldCreated'),
        field_updated: this.$t('activityLog.actions.fieldUpdated'),
        field_deleted: this.$t('activityLog.actions.fieldDeleted'),
        view_created: this.$t('activityLog.actions.viewCreated'),
        view_updated: this.$t('activityLog.actions.viewUpdated'),
        view_deleted: this.$t('activityLog.actions.viewDeleted'),
        comment_created: this.$t('activityLog.actions.commentCreated'),
        comment_updated: this.$t('activityLog.actions.commentUpdated'),
        comment_deleted: this.$t('activityLog.actions.commentDeleted'),
        comment_resolved: this.$t('activityLog.actions.commentResolved'),
        comment_unresolved: this.$t('activityLog.actions.commentUnresolved'),
        user_joined: this.$t('activityLog.actions.userJoined'),
        user_left: this.$t('activityLog.actions.userLeft'),
      }

      return actionMap[actionType] || actionType
    },

    formatTime(timestamp) {
      const date = new Date(timestamp)
      const now = new Date()
      const diffInHours = (now - date) / (1000 * 60 * 60)

      if (diffInHours < 24) {
        return getHumanPeriodAgoCount(date, now)
      } else {
        return date.toLocaleDateString(this.$i18n.locale, {
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        })
      }
    },

    isRowAction(actionType) {
      return [
        'row_created',
        'row_updated',
        'row_deleted',
        'comment_created',
        'comment_updated',
      ].includes(actionType)
    },

    navigateToRow() {
      if (!this.canNavigateToRow) return

      // Navigate to the row in the table view
      const rowId = this.entry.details.row_id
      this.$emit('navigate-to-row', rowId)

      // You could also emit an event to parent component or use router
      // this.$router.push({
      //   name: 'database-table',
      //   params: { tableId: this.table.id },
      //   query: { rowId }
      // })
    },
  },
}
</script>

<style lang="scss" scoped>
.activity-log-entry {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  background-color: var(--color-background);
  border: 1px solid var(--color-border);
  transition: all 0.2s ease;

  &:hover {
    border-color: var(--color-border-hover);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }

  &__avatar {
    flex-shrink: 0;
  }

  &__system-icon {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: var(--color-neutral-200);
    border-radius: 50%;
    color: var(--color-neutral-600);
    font-size: 16px;
  }

  &__content {
    flex: 1;
    min-width: 0;
  }

  &__header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
    flex-wrap: wrap;
  }

  &__user {
    font-weight: 600;
    color: var(--color-text);
    white-space: nowrap;
  }

  &__action {
    color: var(--color-text-muted);
    font-size: 14px;
  }

  &__time {
    color: var(--color-text-muted);
    font-size: 12px;
    margin-left: auto;
    white-space: nowrap;
  }

  &__details {
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin-top: 8px;
  }

  &__preview {
    font-style: italic;
    color: var(--color-text-muted);
    font-size: 13px;
    padding: 4px 8px;
    background-color: var(--color-neutral-50);
    border-radius: 4px;
    border-left: 3px solid var(--color-primary-200);
  }

  &__field,
  &__view,
  &__row,
  &__mentions {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: var(--color-text-muted);

    i {
      font-size: 14px;
      opacity: 0.7;
    }
  }

  &__actions {
    flex-shrink: 0;
    display: flex;
    align-items: flex-start;
    opacity: 0;
    transition: opacity 0.2s ease;
  }

  &:hover &__actions {
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .activity-log-entry {
    &__header {
      flex-direction: column;
      align-items: flex-start;
      gap: 4px;
    }

    &__time {
      margin-left: 0;
    }
  }
}
</style>
