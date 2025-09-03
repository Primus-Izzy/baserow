<template>
  <div class="activity-log-timeline-entry">
    <div class="activity-log-timeline-entry__time-marker">
      <div class="activity-log-timeline-entry__time">
        {{ formatTime(entry.timestamp) }}
      </div>
      <div class="activity-log-timeline-entry__dot">
        <i :class="getActionIcon(entry.action_type)"></i>
      </div>
    </div>

    <div class="activity-log-timeline-entry__content">
      <div class="activity-log-timeline-entry__card">
        <div class="activity-log-timeline-entry__header">
          <div class="activity-log-timeline-entry__avatar">
            <Avatar
              v-if="entry.user"
              :initials="userInitials"
              :color="userColor"
              size="small"
            />
            <i
              v-else
              class="iconoir-system-restart activity-log-timeline-entry__system-icon"
            ></i>
          </div>

          <div class="activity-log-timeline-entry__info">
            <div class="activity-log-timeline-entry__user-action">
              <span class="activity-log-timeline-entry__user">
                {{
                  entry.user
                    ? entry.user_name || entry.user_email
                    : $t('activityLog.system')
                }}
              </span>
              <span class="activity-log-timeline-entry__action">
                {{ getActionDescription(entry.action_type, entry.details) }}
              </span>
            </div>

            <div class="activity-log-timeline-entry__timestamp">
              {{ formatFullTime(entry.timestamp) }}
            </div>
          </div>

          <div class="activity-log-timeline-entry__actions">
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

        <div v-if="hasDetails" class="activity-log-timeline-entry__details">
          <div
            v-if="entry.details.content_preview"
            class="activity-log-timeline-entry__preview"
          >
            <i class="iconoir-quote"></i>
            <span>"{{ entry.details.content_preview }}"</span>
          </div>

          <div class="activity-log-timeline-entry__metadata">
            <div
              v-if="entry.details.field_name"
              class="activity-log-timeline-entry__field"
            >
              <i class="iconoir-db"></i>
              <span>{{ entry.details.field_name }}</span>
            </div>

            <div
              v-if="entry.details.view_name"
              class="activity-log-timeline-entry__view"
            >
              <i class="iconoir-eye-alt"></i>
              <span>{{ entry.details.view_name }}</span>
            </div>

            <div
              v-if="entry.details.row_id"
              class="activity-log-timeline-entry__row"
            >
              <i class="iconoir-table-rows"></i>
              <span
                >{{ $t('activityLog.row') }} #{{ entry.details.row_id }}</span
              >
            </div>

            <div
              v-if="entry.details.mentions_count > 0"
              class="activity-log-timeline-entry__mentions"
            >
              <i class="iconoir-at-sign"></i>
              <span>{{
                $tc('activityLog.mentions', entry.details.mentions_count, {
                  count: entry.details.mentions_count,
                })
              }}</span>
            </div>
          </div>

          <div
            v-if="entry.details.changes && entry.details.changes.length > 0"
            class="activity-log-timeline-entry__changes"
          >
            <div class="activity-log-timeline-entry__changes-header">
              <i class="iconoir-edit-pencil"></i>
              <span>{{ $t('activityLog.timeline.changes') }}</span>
            </div>
            <div class="activity-log-timeline-entry__changes-list">
              <div
                v-for="change in entry.details.changes.slice(0, 3)"
                :key="change.field"
                class="activity-log-timeline-entry__change"
              >
                <span class="activity-log-timeline-entry__change-field"
                  >{{ change.field }}:</span
                >
                <span class="activity-log-timeline-entry__change-from">{{
                  change.from || $t('activityLog.timeline.empty')
                }}</span>
                <i class="iconoir-arrow-right"></i>
                <span class="activity-log-timeline-entry__change-to">{{
                  change.to || $t('activityLog.timeline.empty')
                }}</span>
              </div>
              <div
                v-if="entry.details.changes.length > 3"
                class="activity-log-timeline-entry__change-more"
              >
                {{
                  $t('activityLog.timeline.moreChanges', {
                    count: entry.details.changes.length - 3,
                  })
                }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getHumanPeriodAgoCount } from '@baserow/modules/core/utils/date'

export default {
  name: 'ActivityLogTimelineEntry',
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

    getActionIcon(actionType) {
      const iconMap = {
        row_created: 'iconoir-plus-circle',
        row_updated: 'iconoir-edit-pencil',
        row_deleted: 'iconoir-trash',
        field_created: 'iconoir-db-add',
        field_updated: 'iconoir-db-edit',
        field_deleted: 'iconoir-db-remove',
        view_created: 'iconoir-eye-alt',
        view_updated: 'iconoir-eye-alt',
        view_deleted: 'iconoir-eye-close',
        comment_created: 'iconoir-chat-bubble',
        comment_updated: 'iconoir-edit-pencil',
        comment_deleted: 'iconoir-trash',
        comment_resolved: 'iconoir-check-circle',
        comment_unresolved: 'iconoir-cancel-circle',
        user_joined: 'iconoir-user-plus',
        user_left: 'iconoir-user-minus',
      }

      return iconMap[actionType] || 'iconoir-info-circle'
    },

    formatTime(timestamp) {
      const date = new Date(timestamp)
      return date.toLocaleTimeString(this.$i18n.locale, {
        hour: '2-digit',
        minute: '2-digit',
      })
    },

    formatFullTime(timestamp) {
      const date = new Date(timestamp)
      const now = new Date()
      const diffInHours = (now - date) / (1000 * 60 * 60)

      if (diffInHours < 1) {
        return getHumanPeriodAgoCount(date, now)
      } else if (diffInHours < 24) {
        return date.toLocaleTimeString(this.$i18n.locale, {
          hour: '2-digit',
          minute: '2-digit',
        })
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
    },
  },
}
</script>

<style lang="scss" scoped>
.activity-log-timeline-entry {
  display: flex;
  margin-bottom: 24px;
  position: relative;

  &:last-child {
    margin-bottom: 0;
  }

  &__time-marker {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-right: 16px;
    position: relative;
    z-index: 1;
  }

  &__time {
    font-size: 12px;
    color: var(--color-text-muted);
    font-weight: 500;
    margin-bottom: 8px;
    white-space: nowrap;
    background-color: var(--color-background);
    padding: 2px 6px;
    border-radius: 4px;
  }

  &__dot {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background-color: var(--color-primary-100);
    border: 2px solid var(--color-primary-500);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--color-primary-600);
    font-size: 14px;
    position: relative;

    &::before {
      content: '';
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background-color: var(--color-primary-500);
      z-index: -1;
    }
  }

  &__content {
    flex: 1;
    min-width: 0;
  }

  &__card {
    background-color: var(--color-background);
    border: 1px solid var(--color-border);
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    transition: all 0.2s ease;

    &:hover {
      border-color: var(--color-border-hover);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
  }

  &__header {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 12px;
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

  &__info {
    flex: 1;
    min-width: 0;
  }

  &__user-action {
    display: flex;
    align-items: center;
    gap: 6px;
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

  &__timestamp {
    color: var(--color-text-muted);
    font-size: 12px;
  }

  &__actions {
    flex-shrink: 0;
    opacity: 0;
    transition: opacity 0.2s ease;
  }

  &__card:hover &__actions {
    opacity: 1;
  }

  &__details {
    border-top: 1px solid var(--color-border);
    padding-top: 12px;
    margin-top: 12px;
  }

  &__preview {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    font-style: italic;
    color: var(--color-text-muted);
    font-size: 13px;
    padding: 8px 12px;
    background-color: var(--color-neutral-50);
    border-radius: 6px;
    border-left: 3px solid var(--color-primary-200);
    margin-bottom: 12px;

    i {
      margin-top: 2px;
      opacity: 0.7;
    }
  }

  &__metadata {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 12px;
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
    padding: 4px 8px;
    background-color: var(--color-neutral-50);
    border-radius: 4px;

    i {
      font-size: 14px;
      opacity: 0.7;
    }
  }

  &__changes {
    margin-top: 12px;
  }

  &__changes-header {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    font-weight: 600;
    color: var(--color-text-muted);
    margin-bottom: 8px;

    i {
      font-size: 14px;
    }
  }

  &__changes-list {
    background-color: var(--color-neutral-50);
    border-radius: 6px;
    padding: 8px;
  }

  &__change {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    margin-bottom: 4px;

    &:last-child {
      margin-bottom: 0;
    }
  }

  &__change-field {
    font-weight: 600;
    color: var(--color-text);
    min-width: 80px;
  }

  &__change-from {
    color: var(--color-error-600);
    background-color: var(--color-error-50);
    padding: 2px 6px;
    border-radius: 3px;
    max-width: 100px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__change-to {
    color: var(--color-success-600);
    background-color: var(--color-success-50);
    padding: 2px 6px;
    border-radius: 3px;
    max-width: 100px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__change-more {
    font-size: 11px;
    color: var(--color-text-muted);
    font-style: italic;
    margin-top: 4px;
  }
}

@media (max-width: 768px) {
  .activity-log-timeline-entry {
    &__time-marker {
      margin-right: 12px;
    }

    &__time {
      font-size: 11px;
    }

    &__dot {
      width: 24px;
      height: 24px;
      font-size: 12px;
    }

    &__card {
      padding: 12px;
    }

    &__user-action {
      flex-direction: column;
      align-items: flex-start;
      gap: 2px;
    }

    &__metadata {
      flex-direction: column;
      gap: 6px;
    }

    &__change {
      flex-direction: column;
      align-items: flex-start;
      gap: 4px;
    }

    &__change-field {
      min-width: auto;
    }
  }
}
</style>
