<template>
  <div class="activity-log-timeline">
    <div class="activity-log-timeline__header">
      <h3 class="activity-log-timeline__title">{{ $t('activityLog.timeline.title') }}</h3>
      <div class="activity-log-timeline__controls">
        <Button
          type="secondary"
          size="small"
          :class="{ 'activity-log-timeline__view-toggle--active': viewMode === 'timeline' }"
          @click="setViewMode('timeline')"
        >
          <i class="iconoir-timeline"></i>
          {{ $t('activityLog.timeline.timelineView') }}
        </Button>
        <Button
          type="secondary"
          size="small"
          :class="{ 'activity-log-timeline__view-toggle--active': viewMode === 'list' }"
          @click="setViewMode('list')"
        >
          <i class="iconoir-list"></i>
          {{ $t('activityLog.timeline.listView') }}
        </Button>
      </div>
    </div>

    <div class="activity-log-timeline__filters">
      <Dropdown
        v-model="selectedTimeRange"
        :placeholder="$t('activityLog.timeline.timeRange')"
        class="activity-log-timeline__filter"
        @input="applyTimeFilter"
      >
        <DropdownItem
          v-for="range in timeRanges"
          :key="range.value"
          :name="range.label"
          :value="range.value"
        />
      </Dropdown>

      <Dropdown
        v-model="selectedUser"
        :placeholder="$t('activityLog.filterByUser')"
        :show-search="true"
        class="activity-log-timeline__filter"
        @input="applyFilters"
      >
        <DropdownItem
          :name="$t('activityLog.allUsers')"
          :value="null"
        />
        <DropdownItem
          v-for="user in availableUsers"
          :key="user.id"
          :name="user.first_name || user.email"
          :value="user.id"
        />
      </Dropdown>
      
      <Dropdown
        v-model="selectedActionTypes"
        :placeholder="$t('activityLog.filterByAction')"
        :multiple="true"
        class="activity-log-timeline__filter"
        @input="applyFilters"
      >
        <DropdownItem
          v-for="actionType in availableActionTypes"
          :key="actionType.value"
          :name="actionType.label"
          :value="actionType.value"
        />
      </Dropdown>
      
      <Button
        type="secondary"
        size="small"
        @click="clearFilters"
      >
        {{ $t('activityLog.clearFilters') }}
      </Button>

      <div class="activity-log-timeline__live-indicator">
        <div
          :class="[
            'activity-log-timeline__live-dot',
            { 'activity-log-timeline__live-dot--active': isRealTimeEnabled }
          ]"
        ></div>
        <span class="activity-log-timeline__live-text">
          {{ isRealTimeEnabled ? $t('activityLog.timeline.live') : $t('activityLog.timeline.paused') }}
        </span>
        <Button
          type="ghost"
          size="tiny"
          @click="toggleRealTime"
        >
          <i :class="isRealTimeEnabled ? 'iconoir-pause' : 'iconoir-play'"></i>
        </Button>
      </div>
    </div>
    
    <div class="activity-log-timeline__content">
      <div
        v-if="loading"
        class="activity-log-timeline__loading"
      >
        <div class="loading"></div>
      </div>
      
      <div
        v-else-if="groupedEntries.length === 0"
        class="activity-log-timeline__empty"
      >
        <i class="iconoir-clock-outline"></i>
        <p>{{ $t('activityLog.noActivity') }}</p>
      </div>
      
      <div
        v-else
        class="activity-log-timeline__entries"
      >
        <div
          v-if="viewMode === 'timeline'"
          class="activity-log-timeline__timeline"
        >
          <div
            v-for="group in groupedEntries"
            :key="group.date"
            class="activity-log-timeline__day-group"
          >
            <div class="activity-log-timeline__day-header">
              <div class="activity-log-timeline__day-line"></div>
              <div class="activity-log-timeline__day-label">
                {{ formatDateHeader(group.date) }}
              </div>
              <div class="activity-log-timeline__day-line"></div>
            </div>
            
            <div class="activity-log-timeline__day-entries">
              <ActivityLogTimelineEntry
                v-for="entry in group.entries"
                :key="entry.id"
                :entry="entry"
                :table="table"
                @navigate-to-row="$emit('navigate-to-row', $event)"
              />
            </div>
          </div>
        </div>

        <div
          v-else
          class="activity-log-timeline__list"
        >
          <ActivityLogEntry
            v-for="entry in flatEntries"
            :key="entry.id"
            :entry="entry"
            :table="table"
            @navigate-to-row="$emit('navigate-to-row', $event)"
          />
        </div>
        
        <div
          v-if="hasMore"
          class="activity-log-timeline__load-more"
        >
          <Button
            type="secondary"
            :loading="loadingMore"
            @click="loadMore"
          >
            {{ $t('activityLog.loadMore') }}
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import CommentsService from '@baserow/modules/database/services/comments'
import ActivityLogEntry from './ActivityLogEntry'
import ActivityLogTimelineEntry from './ActivityLogTimelineEntry'

export default {
  name: 'ActivityLogTimeline',
  components: {
    ActivityLogEntry,
    ActivityLogTimelineEntry,
  },
  props: {
    table: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      activityEntries: [],
      availableUsers: [],
      selectedUser: null,
      selectedActionTypes: [],
      selectedTimeRange: 'all',
      viewMode: 'timeline', // 'timeline' or 'list'
      isRealTimeEnabled: true,
      loading: false,
      loadingMore: false,
      hasMore: false,
      currentPage: 1,
      pageSize: 50,
      realTimeBuffer: [], // Buffer for real-time updates when paused
    }
  },
  computed: {
    ...mapGetters('collaboration', ['activityLog']),
    
    timeRanges() {
      return [
        { value: 'all', label: this.$t('activityLog.timeline.timeRanges.all') },
        { value: 'today', label: this.$t('activityLog.timeline.timeRanges.today') },
        { value: 'yesterday', label: this.$t('activityLog.timeline.timeRanges.yesterday') },
        { value: 'week', label: this.$t('activityLog.timeline.timeRanges.thisWeek') },
        { value: 'month', label: this.$t('activityLog.timeline.timeRanges.thisMonth') },
        { value: 'custom', label: this.$t('activityLog.timeline.timeRanges.custom') },
      ]
    },
    
    availableActionTypes() {
      return [
        { value: 'row_created', label: this.$t('activityLog.actions.rowCreated') },
        { value: 'row_updated', label: this.$t('activityLog.actions.rowUpdated') },
        { value: 'row_deleted', label: this.$t('activityLog.actions.rowDeleted') },
        { value: 'field_created', label: this.$t('activityLog.actions.fieldCreated') },
        { value: 'field_updated', label: this.$t('activityLog.actions.fieldUpdated') },
        { value: 'field_deleted', label: this.$t('activityLog.actions.fieldDeleted') },
        { value: 'view_created', label: this.$t('activityLog.actions.viewCreated') },
        { value: 'view_updated', label: this.$t('activityLog.actions.viewUpdated') },
        { value: 'view_deleted', label: this.$t('activityLog.actions.viewDeleted') },
        { value: 'comment_created', label: this.$t('activityLog.actions.commentCreated') },
        { value: 'comment_updated', label: this.$t('activityLog.actions.commentUpdated') },
        { value: 'comment_deleted', label: this.$t('activityLog.actions.commentDeleted') },
        { value: 'comment_resolved', label: this.$t('activityLog.actions.commentResolved') },
        { value: 'comment_unresolved', label: this.$t('activityLog.actions.commentUnresolved') },
        { value: 'user_joined', label: this.$t('activityLog.actions.userJoined') },
        { value: 'user_left', label: this.$t('activityLog.actions.userLeft') },
      ]
    },

    groupedEntries() {
      if (this.viewMode !== 'timeline') return []
      
      const groups = {}
      this.activityEntries.forEach(entry => {
        const date = new Date(entry.timestamp).toDateString()
        if (!groups[date]) {
          groups[date] = {
            date,
            entries: []
          }
        }
        groups[date].entries.push(entry)
      })
      
      return Object.values(groups).sort((a, b) => new Date(b.date) - new Date(a.date))
    },

    flatEntries() {
      return this.activityEntries
    },
  },
  async mounted() {
    await this.loadActivityLog()
    await this.loadAvailableUsers()
    
    // Listen for real-time activity updates
    this.$store.subscribe((mutation) => {
      if (mutation.type === 'collaboration/ADD_ACTIVITY_LOG_ENTRY') {
        if (this.isRealTimeEnabled) {
          this.activityEntries.unshift(mutation.payload)
          // Keep only the latest entries to prevent memory issues
          if (this.activityEntries.length > 200) {
            this.activityEntries = this.activityEntries.slice(0, 200)
          }
        } else {
          // Buffer updates when real-time is paused
          this.realTimeBuffer.unshift(mutation.payload)
        }
      }
    })
  },
  methods: {
    async loadActivityLog(reset = true) {
      if (reset) {
        this.loading = true
        this.currentPage = 1
        this.activityEntries = []
      } else {
        this.loadingMore = true
      }
      
      try {
        const params = {
          page: this.currentPage,
          pageSize: this.pageSize,
        }
        
        if (this.selectedUser) {
          params.userId = this.selectedUser
        }
        
        if (this.selectedActionTypes.length > 0) {
          params.actionTypes = this.selectedActionTypes
        }

        // Add time range filtering
        if (this.selectedTimeRange !== 'all') {
          const timeFilter = this.getTimeRangeFilter(this.selectedTimeRange)
          if (timeFilter) {
            params.startDate = timeFilter.startDate
            params.endDate = timeFilter.endDate
          }
        }
        
        const { data } = await CommentsService(this.$client).getActivityLog(
          this.table.id,
          params
        )
        
        if (reset) {
          this.activityEntries = data.results
        } else {
          this.activityEntries.push(...data.results)
        }
        
        this.hasMore = !!data.next
      } catch (error) {
        this.$store.dispatch('toast/error', {
          title: this.$t('activityLog.loadError'),
          message: error.response?.data?.error || error.message,
        })
      } finally {
        this.loading = false
        this.loadingMore = false
      }
    },
    
    async loadAvailableUsers() {
      try {
        // Get workspace users for filtering
        const workspace = this.table.database.workspace
        this.availableUsers = workspace.users || []
      } catch (error) {
        console.error('Failed to load available users:', error)
      }
    },
    
    async loadMore() {
      this.currentPage += 1
      await this.loadActivityLog(false)
    },
    
    async applyFilters() {
      await this.loadActivityLog(true)
    },

    async applyTimeFilter() {
      await this.loadActivityLog(true)
    },
    
    async clearFilters() {
      this.selectedUser = null
      this.selectedActionTypes = []
      this.selectedTimeRange = 'all'
      await this.loadActivityLog(true)
    },

    setViewMode(mode) {
      this.viewMode = mode
    },

    toggleRealTime() {
      this.isRealTimeEnabled = !this.isRealTimeEnabled
      
      if (this.isRealTimeEnabled && this.realTimeBuffer.length > 0) {
        // Apply buffered updates
        this.activityEntries.unshift(...this.realTimeBuffer)
        this.realTimeBuffer = []
        
        // Keep only the latest entries
        if (this.activityEntries.length > 200) {
          this.activityEntries = this.activityEntries.slice(0, 200)
        }
      }
    },

    getTimeRangeFilter(range) {
      const now = new Date()
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
      
      switch (range) {
        case 'today':
          return {
            startDate: today.toISOString(),
            endDate: new Date(today.getTime() + 24 * 60 * 60 * 1000).toISOString()
          }
        case 'yesterday':
          const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000)
          return {
            startDate: yesterday.toISOString(),
            endDate: today.toISOString()
          }
        case 'week':
          const weekStart = new Date(today.getTime() - (today.getDay() * 24 * 60 * 60 * 1000))
          return {
            startDate: weekStart.toISOString(),
            endDate: now.toISOString()
          }
        case 'month':
          const monthStart = new Date(today.getFullYear(), today.getMonth(), 1)
          return {
            startDate: monthStart.toISOString(),
            endDate: now.toISOString()
          }
        default:
          return null
      }
    },

    formatDateHeader(dateString) {
      const date = new Date(dateString)
      const now = new Date()
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
      const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000)
      
      if (date.toDateString() === today.toDateString()) {
        return this.$t('activityLog.timeline.today')
      } else if (date.toDateString() === yesterday.toDateString()) {
        return this.$t('activityLog.timeline.yesterday')
      } else {
        return date.toLocaleDateString(this.$i18n.locale, {
          weekday: 'long',
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        })
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.activity-log-timeline {
  display: flex;
  flex-direction: column;
  height: 100%;
  
  &__header {
    padding: 16px;
    border-bottom: 1px solid var(--color-border);
    background-color: var(--color-background);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  &__title {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: var(--color-text);
  }

  &__controls {
    display: flex;
    gap: 4px;
  }

  &__view-toggle--active {
    background-color: var(--color-primary-100);
    color: var(--color-primary-600);
  }
  
  &__filters {
    padding: 12px 16px;
    border-bottom: 1px solid var(--color-border);
    background-color: var(--color-background-light);
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    align-items: center;
  }
  
  &__filter {
    min-width: 150px;
  }

  &__live-indicator {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-left: auto;
    padding: 4px 8px;
    border-radius: 12px;
    background-color: var(--color-background);
    border: 1px solid var(--color-border);
  }

  &__live-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: var(--color-neutral-400);
    transition: background-color 0.2s ease;

    &--active {
      background-color: var(--color-success-500);
      animation: pulse 2s infinite;
    }
  }

  &__live-text {
    font-size: 12px;
    color: var(--color-text-muted);
    font-weight: 500;
  }
  
  &__content {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
  }
  
  &__loading {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 200px;
  }
  
  &__empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 200px;
    color: var(--color-text-muted);
    
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
  
  &__entries {
    display: flex;
    flex-direction: column;
  }

  &__timeline {
    position: relative;
  }

  &__day-group {
    margin-bottom: 32px;

    &:last-child {
      margin-bottom: 0;
    }
  }

  &__day-header {
    display: flex;
    align-items: center;
    margin-bottom: 16px;
    gap: 12px;
  }

  &__day-line {
    flex: 1;
    height: 1px;
    background-color: var(--color-border);
  }

  &__day-label {
    font-size: 14px;
    font-weight: 600;
    color: var(--color-text-muted);
    padding: 4px 12px;
    background-color: var(--color-background);
    border-radius: 12px;
    border: 1px solid var(--color-border);
    white-space: nowrap;
  }

  &__day-entries {
    position: relative;
    padding-left: 24px;

    &::before {
      content: '';
      position: absolute;
      left: 12px;
      top: 0;
      bottom: 0;
      width: 2px;
      background-color: var(--color-border);
    }
  }

  &__list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  
  &__load-more {
    display: flex;
    justify-content: center;
    margin-top: 24px;
  }
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
  }
  70% {
    box-shadow: 0 0 0 6px rgba(34, 197, 94, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(34, 197, 94, 0);
  }
}

@media (max-width: 768px) {
  .activity-log-timeline {
    &__header {
      flex-direction: column;
      align-items: stretch;
      gap: 12px;
    }

    &__filters {
      flex-direction: column;
      align-items: stretch;

      .activity-log-timeline__live-indicator {
        margin-left: 0;
        align-self: flex-start;
      }
    }
    
    &__filter {
      min-width: auto;
    }

    &__day-entries {
      padding-left: 16px;

      &::before {
        left: 8px;
      }
    }
  }
}
</style>