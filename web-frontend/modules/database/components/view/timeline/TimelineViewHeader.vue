<template>
  <ViewHeader
    :view="view"
    :fields="fields"
    :table="table"
    :database="database"
    :read-only="readOnly"
    :store-prefix="storePrefix"
    @refresh="$emit('refresh', $event)"
  >
    <template #title>
      <i class="iconoir-timeline timeline-header__icon"></i>
      {{ view.name }}
    </template>

    <template #controls>
      <!-- Timeline-specific controls -->
      <div class="timeline-header__controls">
        <!-- Date range selector -->
        <div class="timeline-header__date-range">
          <button
            class="timeline-header__date-btn"
            @click="showDateRangePicker = !showDateRangePicker"
          >
            <i class="iconoir-calendar"></i>
            {{ formatDateRange() }}
          </button>

          <div v-if="showDateRangePicker" class="timeline-header__date-picker">
            <input
              v-model="startDate"
              type="date"
              class="timeline-header__date-input"
              @change="updateDateRange"
            />
            <span>to</span>
            <input
              v-model="endDate"
              type="date"
              class="timeline-header__date-input"
              @change="updateDateRange"
            />
          </div>
        </div>

        <!-- View options -->
        <Dropdown :show-search="false" class="timeline-header__options">
          <template #header>
            <button class="timeline-header__options-btn">
              <i class="iconoir-settings"></i>
              Options
            </button>
          </template>
          <template #items>
            <DropdownItem
              @click="toggleDependencies"
              :class="{ 'dropdown__item--selected': view.enable_dependencies }"
            >
              <i class="iconoir-link"></i>
              Show Dependencies
            </DropdownItem>
            <DropdownItem
              @click="toggleMilestones"
              :class="{ 'dropdown__item--selected': view.show_milestones }"
            >
              <i class="iconoir-flag"></i>
              Show Milestones
            </DropdownItem>
            <DropdownItem
              @click="toggleCriticalPath"
              :class="{ 'dropdown__item--selected': view.show_critical_path }"
            >
              <i class="iconoir-path"></i>
              Show Critical Path
            </DropdownItem>
          </template>
        </Dropdown>
      </div>
    </template>
  </ViewHeader>
</template>

<script>
import ViewHeader from '@baserow/modules/database/components/view/ViewHeader'
import Dropdown from '@baserow/modules/core/components/Dropdown'
import DropdownItem from '@baserow/modules/core/components/DropdownItem'

export default {
  name: 'TimelineViewHeader',
  components: {
    ViewHeader,
    Dropdown,
    DropdownItem,
  },
  props: {
    view: {
      type: Object,
      required: true,
    },
    fields: {
      type: Array,
      required: true,
    },
    table: {
      type: Object,
      required: true,
    },
    database: {
      type: Object,
      required: true,
    },
    readOnly: {
      type: Boolean,
      required: false,
      default: false,
    },
    storePrefix: {
      type: String,
      required: false,
      default: '',
    },
  },
  data() {
    return {
      showDateRangePicker: false,
      startDate: '',
      endDate: '',
    }
  },
  mounted() {
    this.initializeDateRange()
  },
  methods: {
    initializeDateRange() {
      const now = new Date()
      const start = new Date(now)
      start.setMonth(start.getMonth() - 1)
      const end = new Date(now)
      end.setMonth(end.getMonth() + 2)

      this.startDate = start.toISOString().split('T')[0]
      this.endDate = end.toISOString().split('T')[0]
    },
    formatDateRange() {
      if (!this.startDate || !this.endDate) return 'Select Range'

      const start = new Date(this.startDate)
      const end = new Date(this.endDate)

      return `${start.toLocaleDateString()} - ${end.toLocaleDateString()}`
    },
    updateDateRange() {
      this.$emit('date-range-changed', {
        start: new Date(this.startDate),
        end: new Date(this.endDate),
      })
    },
    async toggleDependencies() {
      await this.$store.dispatch('view/update', {
        view: this.view,
        values: { enable_dependencies: !this.view.enable_dependencies },
      })
      this.$emit('refresh')
    },
    async toggleMilestones() {
      await this.$store.dispatch('view/update', {
        view: this.view,
        values: { show_milestones: !this.view.show_milestones },
      })
      this.$emit('refresh')
    },
    async toggleCriticalPath() {
      await this.$store.dispatch('view/update', {
        view: this.view,
        values: { show_critical_path: !this.view.show_critical_path },
      })
      this.$emit('refresh')
    },
  },
}
</script>

<style lang="scss" scoped>
.timeline-header {
  &__icon {
    margin-right: 8px;
    color: var(--color-primary);
  }

  &__controls {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  &__date-range {
    position: relative;
  }

  &__date-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    border: 1px solid var(--color-border);
    background: white;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;

    &:hover {
      background: var(--color-neutral-50);
    }
  }

  &__date-picker {
    position: absolute;
    top: 100%;
    right: 0;
    background: white;
    border: 1px solid var(--color-border);
    border-radius: 4px;
    padding: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    gap: 8px;
    z-index: 10;
    white-space: nowrap;
  }

  &__date-input {
    padding: 4px 8px;
    border: 1px solid var(--color-border);
    border-radius: 4px;
    font-size: 12px;
  }

  &__options-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    border: 1px solid var(--color-border);
    background: white;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;

    &:hover {
      background: var(--color-neutral-50);
    }
  }
}
</style>
