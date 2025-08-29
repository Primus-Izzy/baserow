<template>
  <div class="activity-log-filters">
    <div class="activity-log-filters__section">
      <label class="activity-log-filters__label">
        {{ $t('activityLog.filters.users') }}
      </label>
      <Dropdown
        v-model="localFilters.selectedUsers"
        :placeholder="$t('activityLog.filterByUser')"
        :multiple="true"
        :show-search="true"
        class="activity-log-filters__dropdown"
        @input="emitFilters"
      >
        <DropdownItem
          v-for="user in availableUsers"
          :key="user.id"
          :name="user.first_name || user.email"
          :value="user.id"
        >
          <div class="activity-log-filters__user-item">
            <Avatar
              :initials="getUserInitials(user)"
              :color="getUserColor(user.id)"
              size="tiny"
            />
            <span>{{ user.first_name || user.email }}</span>
          </div>
        </DropdownItem>
      </Dropdown>
    </div>

    <div class="activity-log-filters__section">
      <label class="activity-log-filters__label">
        {{ $t('activityLog.filters.actions') }}
      </label>
      <Dropdown
        v-model="localFilters.selectedActionTypes"
        :placeholder="$t('activityLog.filterByAction')"
        :multiple="true"
        class="activity-log-filters__dropdown"
        @input="emitFilters"
      >
        <DropdownItem
          v-for="group in groupedActionTypes"
          :key="group.category"
          :name="group.category"
          :disabled="true"
          class="activity-log-filters__category-header"
        />
        <DropdownItem
          v-for="actionType in group.actions"
          :key="actionType.value"
          :name="actionType.label"
          :value="actionType.value"
          class="activity-log-filters__action-item"
        >
          <i :class="getActionIcon(actionType.value)"></i>
          <span>{{ actionType.label }}</span>
        </DropdownItem>
      </Dropdown>
    </div>

    <div class="activity-log-filters__section">
      <label class="activity-log-filters__label">
        {{ $t('activityLog.filters.timeRange') }}
      </label>
      <div class="activity-log-filters__time-controls">
        <Dropdown
          v-model="localFilters.timeRange"
          :placeholder="$t('activityLog.timeline.timeRange')"
          class="activity-log-filters__dropdown"
          @input="handleTimeRangeChange"
        >
          <DropdownItem
            v-for="range in timeRanges"
            :key="range.value"
            :name="range.label"
            :value="range.value"
          />
        </Dropdown>
        
        <div
          v-if="localFilters.timeRange === 'custom'"
          class="activity-log-filters__custom-date"
        >
          <input
            v-model="localFilters.startDate"
            type="datetime-local"
            class="activity-log-filters__date-input"
            :placeholder="$t('activityLog.filters.startDate')"
            @input="emitFilters"
          />
          <input
            v-model="localFilters.endDate"
            type="datetime-local"
            class="activity-log-filters__date-input"
            :placeholder="$t('activityLog.filters.endDate')"
            @input="emitFilters"
          />
        </div>
      </div>
    </div>

    <div class="activity-log-filters__section">
      <label class="activity-log-filters__label">
        {{ $t('activityLog.filters.search') }}
      </label>
      <div class="activity-log-filters__search">
        <input
          v-model="localFilters.searchQuery"
          type="text"
          class="activity-log-filters__search-input"
          :placeholder="$t('activityLog.filters.searchPlaceholder')"
          @input="debouncedEmitFilters"
        />
        <i class="iconoir-search activity-log-filters__search-icon"></i>
      </div>
    </div>

    <div class="activity-log-filters__actions">
      <Button
        type="secondary"
        size="small"
        @click="clearAllFilters"
      >
        <i class="iconoir-refresh-double"></i>
        {{ $t('activityLog.clearFilters') }}
      </Button>
      
      <Button
        v-if="hasActiveFilters"
        type="primary"
        size="small"
        @click="saveFilterPreset"
      >
        <i class="iconoir-bookmark"></i>
        {{ $t('activityLog.filters.savePreset') }}
      </Button>
    </div>

    <div
      v-if="filterPresets.length > 0"
      class="activity-log-filters__presets"
    >
      <label class="activity-log-filters__label">
        {{ $t('activityLog.filters.presets') }}
      </label>
      <div class="activity-log-filters__preset-list">
        <div
          v-for="preset in filterPresets"
          :key="preset.id"
          class="activity-log-filters__preset"
          @click="applyFilterPreset(preset)"
        >
          <span class="activity-log-filters__preset-name">{{ preset.name }}</span>
          <Button
            type="ghost"
            size="tiny"
            @click.stop="deleteFilterPreset(preset.id)"
          >
            <i class="iconoir-trash"></i>
          </Button>
        </div>
      </div>
    </div>

    <div class="activity-log-filters__summary">
      <div class="activity-log-filters__active-count">
        {{ $t('activityLog.filters.activeFilters', { count: activeFilterCount }) }}
      </div>
      <div
        v-if="resultCount !== null"
        class="activity-log-filters__result-count"
      >
        {{ $t('activityLog.filters.resultCount', { count: resultCount }) }}
      </div>
    </div>
  </div>
</template>

<script>
import { debounce } from 'lodash'

export default {
  name: 'ActivityLogFilters',
  props: {
    availableUsers: {
      type: Array,
      default: () => [],
    },
    filters: {
      type: Object,
      default: () => ({}),
    },
    resultCount: {
      type: Number,
      default: null,
    },
  },
  data() {
    return {
      localFilters: {
        selectedUsers: [],
        selectedActionTypes: [],
        timeRange: 'all',
        startDate: '',
        endDate: '',
        searchQuery: '',
      },
      filterPresets: [],
    }
  },
  computed: {
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

    groupedActionTypes() {
      return [
        {
          category: this.$t('activityLog.filters.categories.rows'),
          actions: [
            { value: 'row_created', label: this.$t('activityLog.actions.rowCreated') },
            { value: 'row_updated', label: this.$t('activityLog.actions.rowUpdated') },
            { value: 'row_deleted', label: this.$t('activityLog.actions.rowDeleted') },
          ]
        },
        {
          category: this.$t('activityLog.filters.categories.fields'),
          actions: [
            { value: 'field_created', label: this.$t('activityLog.actions.fieldCreated') },
            { value: 'field_updated', label: this.$t('activityLog.actions.fieldUpdated') },
            { value: 'field_deleted', label: this.$t('activityLog.actions.fieldDeleted') },
          ]
        },
        {
          category: this.$t('activityLog.filters.categories.views'),
          actions: [
            { value: 'view_created', label: this.$t('activityLog.actions.viewCreated') },
            { value: 'view_updated', label: this.$t('activityLog.actions.viewUpdated') },
            { value: 'view_deleted', label: this.$t('activityLog.actions.viewDeleted') },
          ]
        },
        {
          category: this.$t('activityLog.filters.categories.comments'),
          actions: [
            { value: 'comment_created', label: this.$t('activityLog.actions.commentCreated') },
            { value: 'comment_updated', label: this.$t('activityLog.actions.commentUpdated') },
            { value: 'comment_deleted', label: this.$t('activityLog.actions.commentDeleted') },
            { value: 'comment_resolved', label: this.$t('activityLog.actions.commentResolved') },
            { value: 'comment_unresolved', label: this.$t('activityLog.actions.commentUnresolved') },
          ]
        },
        {
          category: this.$t('activityLog.filters.categories.users'),
          actions: [
            { value: 'user_joined', label: this.$t('activityLog.actions.userJoined') },
            { value: 'user_left', label: this.$t('activityLog.actions.userLeft') },
          ]
        },
      ]
    },

    hasActiveFilters() {
      return (
        this.localFilters.selectedUsers.length > 0 ||
        this.localFilters.selectedActionTypes.length > 0 ||
        this.localFilters.timeRange !== 'all' ||
        this.localFilters.searchQuery.trim() !== ''
      )
    },

    activeFilterCount() {
      let count = 0
      if (this.localFilters.selectedUsers.length > 0) count++
      if (this.localFilters.selectedActionTypes.length > 0) count++
      if (this.localFilters.timeRange !== 'all') count++
      if (this.localFilters.searchQuery.trim() !== '') count++
      return count
    },
  },
  watch: {
    filters: {
      handler(newFilters) {
        this.localFilters = { ...this.localFilters, ...newFilters }
      },
      immediate: true,
      deep: true,
    },
  },
  created() {
    this.debouncedEmitFilters = debounce(this.emitFilters, 300)
    this.loadFilterPresets()
  },
  methods: {
    emitFilters() {
      this.$emit('filters-changed', { ...this.localFilters })
    },

    handleTimeRangeChange() {
      if (this.localFilters.timeRange !== 'custom') {
        this.localFilters.startDate = ''
        this.localFilters.endDate = ''
      }
      this.emitFilters()
    },

    clearAllFilters() {
      this.localFilters = {
        selectedUsers: [],
        selectedActionTypes: [],
        timeRange: 'all',
        startDate: '',
        endDate: '',
        searchQuery: '',
      }
      this.emitFilters()
    },

    getUserInitials(user) {
      const name = user.first_name || user.email
      return name
        .split(' ')
        .map(word => word.charAt(0).toUpperCase())
        .slice(0, 2)
        .join('')
    },

    getUserColor(userId) {
      const colors = ['blue', 'green', 'purple', 'orange', 'red', 'teal']
      return colors[userId % colors.length]
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

    async saveFilterPreset() {
      const name = prompt(this.$t('activityLog.filters.presetNamePrompt'))
      if (!name) return

      const preset = {
        id: Date.now(),
        name,
        filters: { ...this.localFilters },
        createdAt: new Date().toISOString(),
      }

      this.filterPresets.push(preset)
      this.saveFilterPresets()

      this.$store.dispatch('toast/success', {
        title: this.$t('activityLog.filters.presetSaved'),
        message: this.$t('activityLog.filters.presetSavedMessage', { name }),
      })
    },

    applyFilterPreset(preset) {
      this.localFilters = { ...preset.filters }
      this.emitFilters()

      this.$store.dispatch('toast/info', {
        title: this.$t('activityLog.filters.presetApplied'),
        message: this.$t('activityLog.filters.presetAppliedMessage', { name: preset.name }),
      })
    },

    deleteFilterPreset(presetId) {
      this.filterPresets = this.filterPresets.filter(p => p.id !== presetId)
      this.saveFilterPresets()
    },

    loadFilterPresets() {
      try {
        const saved = localStorage.getItem('baserow_activity_log_filter_presets')
        if (saved) {
          this.filterPresets = JSON.parse(saved)
        }
      } catch (error) {
        console.error('Failed to load filter presets:', error)
      }
    },

    saveFilterPresets() {
      try {
        localStorage.setItem('baserow_activity_log_filter_presets', JSON.stringify(this.filterPresets))
      } catch (error) {
        console.error('Failed to save filter presets:', error)
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.activity-log-filters {
  padding: 16px;
  background-color: var(--color-background-light);
  border-radius: 8px;
  border: 1px solid var(--color-border);
  
  &__section {
    margin-bottom: 16px;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  &__label {
    display: block;
    font-size: 12px;
    font-weight: 600;
    color: var(--color-text-muted);
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  
  &__dropdown {
    width: 100%;
  }

  &__user-item {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  &__category-header {
    font-weight: 600;
    color: var(--color-text-muted);
    background-color: var(--color-neutral-50);
    pointer-events: none;
  }

  &__action-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding-left: 16px;
  }
  
  &__time-controls {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  &__custom-date {
    display: flex;
    gap: 8px;
  }
  
  &__date-input {
    flex: 1;
    padding: 8px 12px;
    border: 1px solid var(--color-border);
    border-radius: 4px;
    font-size: 14px;
    background-color: var(--color-background);
    
    &:focus {
      outline: none;
      border-color: var(--color-primary-500);
      box-shadow: 0 0 0 2px var(--color-primary-100);
    }
  }
  
  &__search {
    position: relative;
  }
  
  &__search-input {
    width: 100%;
    padding: 8px 12px 8px 36px;
    border: 1px solid var(--color-border);
    border-radius: 4px;
    font-size: 14px;
    background-color: var(--color-background);
    
    &:focus {
      outline: none;
      border-color: var(--color-primary-500);
      box-shadow: 0 0 0 2px var(--color-primary-100);
    }
  }
  
  &__search-icon {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--color-text-muted);
    font-size: 16px;
  }
  
  &__actions {
    display: flex;
    gap: 8px;
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid var(--color-border);
  }
  
  &__presets {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid var(--color-border);
  }
  
  &__preset-list {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  
  &__preset {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 8px;
    background-color: var(--color-background);
    border: 1px solid var(--color-border);
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s ease;
    
    &:hover {
      border-color: var(--color-primary-300);
      background-color: var(--color-primary-50);
    }
  }
  
  &__preset-name {
    font-size: 13px;
    color: var(--color-text);
  }
  
  &__summary {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid var(--color-border);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  &__active-count,
  &__result-count {
    font-size: 12px;
    color: var(--color-text-muted);
  }
  
  &__active-count {
    font-weight: 600;
  }
}

@media (max-width: 768px) {
  .activity-log-filters {
    &__custom-date {
      flex-direction: column;
    }
    
    &__actions {
      flex-direction: column;
    }
    
    &__summary {
      flex-direction: column;
      align-items: flex-start;
      gap: 4px;
    }
  }
}
</style>