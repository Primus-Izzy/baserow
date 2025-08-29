<template>
  <div class="activity-log">
    <div class="activity-log__header">
      <h3 class="activity-log__title">{{ $t('activityLog.title') }}</h3>
      <div class="activity-log__controls">
        <Button
          type="secondary"
          size="small"
          :class="{ 'activity-log__view-toggle--active': viewMode === 'simple' }"
          @click="setViewMode('simple')"
        >
          <i class="iconoir-list"></i>
          {{ $t('activityLog.views.simple') }}
        </Button>
        <Button
          type="secondary"
          size="small"
          :class="{ 'activity-log__view-toggle--active': viewMode === 'timeline' }"
          @click="setViewMode('timeline')"
        >
          <i class="iconoir-timeline"></i>
          {{ $t('activityLog.views.timeline') }}
        </Button>
        <Button
          type="secondary"
          size="small"
          @click="toggleFilters"
        >
          <i class="iconoir-filter"></i>
          {{ $t('activityLog.filters.toggle') }}
          <span
            v-if="activeFilterCount > 0"
            class="activity-log__filter-badge"
          >
            {{ activeFilterCount }}
          </span>
        </Button>
      </div>
    </div>

    <div
      v-if="showFilters"
      class="activity-log__filters-panel"
    >
      <ActivityLogFilters
        :available-users="availableUsers"
        :filters="currentFilters"
        :result-count="totalResults"
        @filters-changed="handleFiltersChanged"
      />
    </div>
    
    <div class="activity-log__content">
      <div
        v-if="loading"
        class="activity-log__loading"
      >
        <div class="loading"></div>
      </div>
      
      <div
        v-else-if="activityEntries.length === 0"
        class="activity-log__empty"
      >
        <i class="iconoir-clock-outline"></i>
        <p>{{ $t('activityLog.noActivity') }}</p>
      </div>
      
      <div
        v-else
        class="activity-log__entries"
      >
        <ActivityLogTimeline
          v-if="viewMode === 'timeline'"
          :table="table"
          @navigate-to-row="$emit('navigate-to-row', $event)"
        />
        
        <div
          v-else
          class="activity-log__simple-list"
        >
          <ActivityLogEntry
            v-for="entry in activityEntries"
            :key="entry.id"
            :entry="entry"
            :table="table"
            @navigate-to-row="$emit('navigate-to-row', $event)"
          />
          
          <div
            v-if="hasMore"
            class="activity-log__load-more"
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

    <!-- Real-time notification -->
    <div
      v-if="newEntriesCount > 0 && !isRealTimeEnabled"
      class="activity-log__new-entries-notification"
    >
      <Button
        type="primary"
        size="small"
        @click="loadNewEntries"
      >
        <i class="iconoir-refresh"></i>
        {{ $t('activityLog.newEntries', { count: newEntriesCount }) }}
      </Button>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import CommentsService from '@baserow/modules/database/services/comments'
import ActivityLogEntry from './ActivityLogEntry'
import ActivityLogTimeline from './ActivityLogTimeline'
import ActivityLogFilters from './ActivityLogFilters'

export default {
  name: 'ActivityLog',
  components: {
    ActivityLogEntry,
    ActivityLogTimeline,
    ActivityLogFilters,
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
      viewMode: 'simple', // 'simple' or 'timeline'
      showFilters: false,
      currentFilters: {
        selectedUsers: [],
        selectedActionTypes: [],
        timeRange: 'all',
        startDate: '',
        endDate: '',
        searchQuery: '',
      },
      loading: false,
      loadingMore: false,
      hasMore: false,
      currentPage: 1,
      pageSize: 20,
      totalResults: null,
      newEntriesCount: 0,
      isRealTimeEnabled: true,
      realTimeBuffer: [],
    }
  },
  computed: {
    ...mapGetters('collaboration', ['activityLog']),
    
    activeFilterCount() {
      let count = 0
      if (this.currentFilters.selectedUsers.length > 0) count++
      if (this.currentFilters.selectedActionTypes.length > 0) count++
      if (this.currentFilters.timeRange !== 'all') count++
      if (this.currentFilters.searchQuery.trim() !== '') count++
      return count
    },
  },
  async mounted() {
    await this.loadActivityLog()
    await this.loadAvailableUsers()
    
    // Listen for real-time activity updates
    this.unsubscribeStore = this.$store.subscribe((mutation) => {
      if (mutation.type === 'collaboration/ADD_ACTIVITY_LOG_ENTRY') {
        if (this.isRealTimeEnabled && this.viewMode === 'simple') {
          this.activityEntries.unshift(mutation.payload)
          // Keep only the latest entries to prevent memory issues
          if (this.activityEntries.length > 200) {
            this.activityEntries = this.activityEntries.slice(0, 200)
          }
        } else {
          // Buffer updates when real-time is paused or in timeline mode
          this.realTimeBuffer.unshift(mutation.payload)
          this.newEntriesCount = this.realTimeBuffer.length
        }
      }
    })

    // Initialize collaboration for real-time updates
    await this.$store.dispatch('collaboration/initializeCollaboration', {
      tableId: this.table.id,
    })
  },
  beforeDestroy() {
    if (this.unsubscribeStore) {
      this.unsubscribeStore()
    }
    
    // Disconnect collaboration
    this.$store.dispatch('collaboration/disconnectCollaboration')
  },
  methods: {
    async loadActivityLog(reset = true) {
      if (reset) {
        this.loading = true
        this.currentPage = 1
        this.activityEntries = []
        this.newEntriesCount = 0
        this.realTimeBuffer = []
      } else {
        this.loadingMore = true
      }
      
      try {
        const params = {
          page: this.currentPage,
          pageSize: this.pageSize,
        }
        
        // Apply current filters
        if (this.currentFilters.selectedUsers.length > 0) {
          params.userId = this.currentFilters.selectedUsers[0] // API supports single user for now
        }
        
        if (this.currentFilters.selectedActionTypes.length > 0) {
          params.actionTypes = this.currentFilters.selectedActionTypes
        }

        // Add time range filtering
        if (this.currentFilters.timeRange !== 'all') {
          const timeFilter = this.getTimeRangeFilter(this.currentFilters.timeRange)
          if (timeFilter) {
            params.startDate = timeFilter.startDate
            params.endDate = timeFilter.endDate
          }
        }

        // Custom date range
        if (this.currentFilters.startDate) {
          params.startDate = this.currentFilters.startDate
        }
        if (this.currentFilters.endDate) {
          params.endDate = this.currentFilters.endDate
        }

        // Search query
        if (this.currentFilters.searchQuery.trim()) {
          params.search = this.currentFilters.searchQuery.trim()
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
        this.totalResults = data.count || data.results.length
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

    setViewMode(mode) {
      this.viewMode = mode
      
      // Timeline mode handles its own data loading
      if (mode === 'simple') {
        this.loadActivityLog(true)
      }
    },

    toggleFilters() {
      this.showFilters = !this.showFilters
    },

    handleFiltersChanged(filters) {
      this.currentFilters = { ...filters }
      
      // Only reload for simple view, timeline handles its own filtering
      if (this.viewMode === 'simple') {
        this.loadActivityLog(true)
      }
    },

    loadNewEntries() {
      if (this.realTimeBuffer.length > 0) {
        this.activityEntries.unshift(...this.realTimeBuffer)
        this.realTimeBuffer = []
        this.newEntriesCount = 0
        
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
  },
}
</script>

<style lang="scss" scoped>
.activity-log {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
  
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
    align-items: center;
  }

  &__view-toggle--active {
    background-color: var(--color-primary-100);
    color: var(--color-primary-600);
  }

  &__filter-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 16px;
    height: 16px;
    background-color: var(--color-primary-500);
    color: white;
    border-radius: 8px;
    font-size: 10px;
    font-weight: 600;
    margin-left: 4px;
    padding: 0 4px;
  }

  &__filters-panel {
    border-bottom: 1px solid var(--color-border);
    background-color: var(--color-background-light);
  }
  
  &__content {
    flex: 1;
    overflow-y: auto;
    position: relative;
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

  &__simple-list {
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  
  &__load-more {
    display: flex;
    justify-content: center;
    margin-top: 16px;
  }

  &__new-entries-notification {
    position: absolute;
    top: 16px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 10;
    animation: slideDown 0.3s ease-out;
  }
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

@media (max-width: 768px) {
  .activity-log {
    &__header {
      flex-direction: column;
      align-items: stretch;
      gap: 12px;
    }

    &__controls {
      justify-content: center;
    }
  }
}
</style>