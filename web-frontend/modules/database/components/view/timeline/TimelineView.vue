<template>
  <div class="timeline-view">
    <div class="timeline-view__loading" v-if="loading">
      <div class="loading"></div>
    </div>
    <div v-else class="timeline-view__container">
      <!-- Timeline header with zoom controls -->
      <div class="timeline-view__header">
        <div class="timeline-view__zoom-controls">
          <button
            v-for="zoomLevel in zoomLevels"
            :key="zoomLevel.value"
            :class="[
              'timeline-view__zoom-btn',
              {
                'timeline-view__zoom-btn--active':
                  currentZoom === zoomLevel.value,
              },
            ]"
            @click="setZoomLevel(zoomLevel.value)"
          >
            {{ zoomLevel.label }}
          </button>
        </div>
        <div class="timeline-view__date-range">
          {{ formatDateRange(visibleDateRange.start, visibleDateRange.end) }}
        </div>
      </div>

      <!-- Timeline content -->
      <div class="timeline-view__content" ref="timelineContent">
        <!-- Timeline scale -->
        <div class="timeline-view__scale" ref="timelineScale">
          <div
            v-for="(period, index) in timelinePeriods"
            :key="index"
            :class="[
              'timeline-view__scale-period',
              `timeline-view__scale-period--${currentZoom}`,
            ]"
            :style="{ width: period.width + 'px' }"
          >
            {{ period.label }}
          </div>
        </div>

        <!-- Timeline rows -->
        <div class="timeline-view__rows" ref="timelineRows">
          <TimelineRow
            v-for="row in visibleRows"
            :key="row.id"
            :row="row"
            :fields="fields"
            :start-date-field="view.start_date_field"
            :end-date-field="view.end_date_field"
            :visible-date-range="visibleDateRange"
            :zoom-level="currentZoom"
            :dependencies="getDependenciesForRow(row.id)"
            :milestones="getMilestonesForRow(row.id)"
            :read-only="readOnly"
            :database="database"
            :table="table"
            :view="view"
            :store-prefix="storePrefix"
            @row-updated="updateValue"
            @row-clicked="rowClick"
            @date-changed="handleDateChange"
            @dependency-created="handleDependencyCreated"
            @dependency-deleted="handleDependencyDeleted"
          />
        </div>

        <!-- Dependency lines -->
        <svg
          class="timeline-view__dependencies"
          :width="timelineWidth"
          :height="timelineHeight"
        >
          <TimelineDependencyLine
            v-for="dependency in visibleDependencies"
            :key="dependency.id"
            :dependency="dependency"
            :rows="visibleRows"
            :visible-date-range="visibleDateRange"
            :zoom-level="currentZoom"
            @dependency-clicked="handleDependencyClicked"
          />
        </svg>

        <!-- Milestones -->
        <div class="timeline-view__milestones">
          <TimelineMilestone
            v-for="milestone in visibleMilestones"
            :key="milestone.id"
            :milestone="milestone"
            :visible-date-range="visibleDateRange"
            :zoom-level="currentZoom"
            @milestone-clicked="handleMilestoneClicked"
          />
        </div>
      </div>
    </div>

    <!-- Row create modal -->
    <RowCreateModal
      v-if="
        !readOnly &&
        $hasPermission(
          'database.table.create_row',
          table,
          database.workspace.id
        )
      "
      ref="rowCreateModal"
      :database="database"
      :table="table"
      :view="view"
      :primary-is-sortable="true"
      :visible-fields="visibleFields"
      :hidden-fields="hiddenFields"
      :show-hidden-fields="showHiddenFieldsInRowModal"
      :all-fields-in-table="fields"
      @toggle-hidden-fields-visibility="
        showHiddenFieldsInRowModal = !showHiddenFieldsInRowModal
      "
      @created="createRow"
      @order-fields="orderFields"
      @toggle-field-visibility="toggleFieldVisibility"
      @field-updated="$emit('refresh', $event)"
      @field-deleted="$emit('refresh')"
    />

    <!-- Row edit modal -->
    <RowEditModal
      ref="rowEditModal"
      enable-navigation
      :database="database"
      :table="table"
      :view="view"
      :all-fields-in-table="fields"
      :primary-is-sortable="true"
      :visible-fields="visibleFields"
      :hidden-fields="hiddenFields"
      :rows="allRows"
      :read-only="
        readOnly ||
        !$hasPermission(
          'database.table.update_row',
          table,
          database.workspace.id
        )
      "
      :show-hidden-fields="showHiddenFieldsInRowModal"
      @hidden="$emit('selected-row', undefined)"
      @toggle-hidden-fields-visibility="
        showHiddenFieldsInRowModal = !showHiddenFieldsInRowModal
      "
      @update="updateValue"
      @order-fields="orderFields"
      @toggle-field-visibility="toggleFieldVisibility"
      @field-updated="$emit('refresh', $event)"
      @field-deleted="$emit('refresh')"
      @field-created="showFieldCreated"
      @field-created-callback-done="afterFieldCreatedUpdateFieldOptions"
      @navigate-previous="$emit('navigate-previous', $event, activeSearchTerm)"
      @navigate-next="$emit('navigate-next', $event, activeSearchTerm)"
      @refresh-row="refreshRow"
    />

    <!-- Floating add button -->
    <ButtonFloating
      v-if="
        !readOnly &&
        !table.data_sync &&
        $hasPermission(
          'database.table.create_row',
          table,
          database.workspace.id
        )
      "
      icon="iconoir-plus"
      position="fixed"
      @click="$refs.rowCreateModal.show()"
    />
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { notifyIf } from '@baserow/modules/core/utils/error'
import RowCreateModal from '@baserow/modules/database/components/row/RowCreateModal'
import RowEditModal from '@baserow/modules/database/components/row/RowEditModal'
import ButtonFloating from '@baserow/modules/core/components/ButtonFloating'
import TimelineRow from './TimelineRow'
import TimelineDependencyLine from './TimelineDependencyLine'
import TimelineMilestone from './TimelineMilestone'

export default {
  name: 'TimelineView',
  components: {
    RowCreateModal,
    RowEditModal,
    ButtonFloating,
    TimelineRow,
    TimelineDependencyLine,
    TimelineMilestone,
  },
  props: {
    database: {
      type: Object,
      required: true,
    },
    table: {
      type: Object,
      required: true,
    },
    view: {
      type: Object,
      required: true,
    },
    fields: {
      type: Array,
      required: true,
    },
    readOnly: {
      type: Boolean,
      required: true,
    },
    storePrefix: {
      type: String,
      required: false,
      default: '',
    },
    decorationsByPlace: {
      type: Object,
      required: false,
      default: () => ({}),
    },
  },
  data() {
    return {
      showHiddenFieldsInRowModal: false,
      currentZoom: 'week',
      visibleDateRange: {
        start: new Date(),
        end: new Date(),
      },
      timelineWidth: 0,
      timelineHeight: 0,
      zoomLevels: [
        { value: 'day', label: this.$t('timelineView.zoomDay') },
        { value: 'week', label: this.$t('timelineView.zoomWeek') },
        { value: 'month', label: this.$t('timelineView.zoomMonth') },
        { value: 'year', label: this.$t('timelineView.zoomYear') },
      ],
    }
  },
  computed: {
    ...mapGetters({
      loading: 'view/timeline/getLoading',
      allRows: 'view/timeline/getAllRows',
      dependencies: 'view/timeline/getDependencies',
      milestones: 'view/timeline/getMilestones',
      fieldOptions: 'view/timeline/getAllFieldOptions',
    }),
    visibleFields() {
      return this.fields.filter((field) => !this.fieldOptions[field.id]?.hidden)
    },
    hiddenFields() {
      return this.fields.filter((field) => this.fieldOptions[field.id]?.hidden)
    },
    visibleRows() {
      return this.allRows.filter((row) => {
        const startDate = this.getRowDate(row, this.view.start_date_field)
        const endDate = this.getRowDate(row, this.view.end_date_field)

        if (!startDate && !endDate) return false

        // Check if row overlaps with visible date range
        const rowStart = startDate || endDate
        const rowEnd = endDate || startDate

        return (
          rowStart <= this.visibleDateRange.end &&
          rowEnd >= this.visibleDateRange.start
        )
      })
    },
    visibleDependencies() {
      return this.dependencies.filter((dep) => {
        const predecessorRow = this.allRows.find(
          (r) => r.id === dep.predecessor_row_id
        )
        const successorRow = this.allRows.find(
          (r) => r.id === dep.successor_row_id
        )
        return predecessorRow && successorRow
      })
    },
    visibleMilestones() {
      return this.milestones.filter((milestone) => {
        const milestoneDate = this.getMilestoneDate(milestone)
        return (
          milestoneDate &&
          milestoneDate >= this.visibleDateRange.start &&
          milestoneDate <= this.visibleDateRange.end
        )
      })
    },
    timelinePeriods() {
      return this.generateTimelinePeriods()
    },
    activeSearchTerm() {
      return this.$store.getters[
        this.storePrefix + 'view/timeline/getActiveSearchTerm'
      ]
    },
  },
  mounted() {
    this.initializeTimeline()
    this.setupResizeObserver()
    this.setupTouchGestures()
  },
  beforeDestroy() {
    if (this.resizeObserver) {
      this.resizeObserver.disconnect()
    }
  },
  methods: {
    initializeTimeline() {
      // Set initial date range based on data
      this.calculateVisibleDateRange()
      this.updateTimelineDimensions()
    },
    setupResizeObserver() {
      if (window.ResizeObserver) {
        this.resizeObserver = new ResizeObserver(() => {
          this.updateTimelineDimensions()
        })
        this.resizeObserver.observe(this.$refs.timelineContent)
      }
    },
    setupTouchGestures() {
      if (!this.$refs.timelineContent) return

      let startX = 0
      let startY = 0
      let initialDistance = 0

      const handleTouchStart = (e) => {
        if (e.touches.length === 1) {
          startX = e.touches[0].clientX
          startY = e.touches[0].clientY
        } else if (e.touches.length === 2) {
          initialDistance = this.getTouchDistance(e.touches[0], e.touches[1])
        }
      }

      const handleTouchMove = (e) => {
        e.preventDefault()

        if (e.touches.length === 1) {
          const deltaX = e.touches[0].clientX - startX
          const deltaY = e.touches[0].clientY - startY

          // Pan timeline
          if (Math.abs(deltaX) > Math.abs(deltaY)) {
            this.panTimeline(deltaX)
          }
        } else if (e.touches.length === 2) {
          const currentDistance = this.getTouchDistance(
            e.touches[0],
            e.touches[1]
          )
          const scale = currentDistance / initialDistance

          // Zoom timeline
          if (scale > 1.1) {
            this.zoomIn()
            initialDistance = currentDistance
          } else if (scale < 0.9) {
            this.zoomOut()
            initialDistance = currentDistance
          }
        }
      }

      this.$refs.timelineContent.addEventListener(
        'touchstart',
        handleTouchStart,
        { passive: false }
      )
      this.$refs.timelineContent.addEventListener(
        'touchmove',
        handleTouchMove,
        { passive: false }
      )
    },
    getTouchDistance(touch1, touch2) {
      const dx = touch1.clientX - touch2.clientX
      const dy = touch1.clientY - touch2.clientY
      return Math.sqrt(dx * dx + dy * dy)
    },
    setZoomLevel(zoomLevel) {
      this.currentZoom = zoomLevel
      this.calculateVisibleDateRange()
      this.updateTimelineDimensions()
    },
    zoomIn() {
      const currentIndex = this.zoomLevels.findIndex(
        (z) => z.value === this.currentZoom
      )
      if (currentIndex > 0) {
        this.setZoomLevel(this.zoomLevels[currentIndex - 1].value)
      }
    },
    zoomOut() {
      const currentIndex = this.zoomLevels.findIndex(
        (z) => z.value === this.currentZoom
      )
      if (currentIndex < this.zoomLevels.length - 1) {
        this.setZoomLevel(this.zoomLevels[currentIndex + 1].value)
      }
    },
    panTimeline(deltaX) {
      const pixelsPerDay = this.getPixelsPerDay()
      const daysDelta = deltaX / pixelsPerDay

      const newStart = new Date(this.visibleDateRange.start)
      const newEnd = new Date(this.visibleDateRange.end)

      newStart.setDate(newStart.getDate() - daysDelta)
      newEnd.setDate(newEnd.getDate() - daysDelta)

      this.visibleDateRange = { start: newStart, end: newEnd }
    },
    calculateVisibleDateRange() {
      const now = new Date()
      let start, end

      switch (this.currentZoom) {
        case 'day':
          start = new Date(now)
          start.setDate(start.getDate() - 7)
          end = new Date(now)
          end.setDate(end.getDate() + 7)
          break
        case 'week':
          start = new Date(now)
          start.setDate(start.getDate() - 30)
          end = new Date(now)
          end.setDate(end.getDate() + 30)
          break
        case 'month':
          start = new Date(now)
          start.setMonth(start.getMonth() - 6)
          end = new Date(now)
          end.setMonth(end.getMonth() + 6)
          break
        case 'year':
          start = new Date(now)
          start.setFullYear(start.getFullYear() - 2)
          end = new Date(now)
          end.setFullYear(end.getFullYear() + 2)
          break
      }

      this.visibleDateRange = { start, end }
    },
    generateTimelinePeriods() {
      const periods = []
      const pixelsPerDay = this.getPixelsPerDay()

      let current = new Date(this.visibleDateRange.start)
      const end = new Date(this.visibleDateRange.end)

      while (current <= end) {
        let periodEnd
        let label
        let width

        switch (this.currentZoom) {
          case 'day':
            periodEnd = new Date(current)
            periodEnd.setDate(periodEnd.getDate() + 1)
            label = current.toLocaleDateString(undefined, {
              weekday: 'short',
              day: 'numeric',
            })
            width = pixelsPerDay
            break
          case 'week':
            periodEnd = new Date(current)
            periodEnd.setDate(periodEnd.getDate() + 7)
            label = `Week ${this.getWeekNumber(current)}`
            width = pixelsPerDay * 7
            break
          case 'month':
            periodEnd = new Date(current)
            periodEnd.setMonth(periodEnd.getMonth() + 1)
            label = current.toLocaleDateString(undefined, {
              month: 'short',
              year: 'numeric',
            })
            width = this.getDaysInMonth(current) * pixelsPerDay
            break
          case 'year':
            periodEnd = new Date(current)
            periodEnd.setFullYear(periodEnd.getFullYear() + 1)
            label = current.getFullYear().toString()
            width = this.getDaysInYear(current) * pixelsPerDay
            break
        }

        periods.push({ label, width })
        current = periodEnd
      }

      return periods
    },
    getPixelsPerDay() {
      switch (this.currentZoom) {
        case 'day':
          return 100
        case 'week':
          return 20
        case 'month':
          return 5
        case 'year':
          return 1
        default:
          return 20
      }
    },
    getWeekNumber(date) {
      const d = new Date(
        Date.UTC(date.getFullYear(), date.getMonth(), date.getDate())
      )
      const dayNum = d.getUTCDay() || 7
      d.setUTCDate(d.getUTCDate() + 4 - dayNum)
      const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1))
      return Math.ceil(((d - yearStart) / 86400000 + 1) / 7)
    },
    getDaysInMonth(date) {
      return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate()
    },
    getDaysInYear(date) {
      return (date.getFullYear() % 4 === 0 && date.getFullYear() % 100 !== 0) ||
        date.getFullYear() % 400 === 0
        ? 366
        : 365
    },
    updateTimelineDimensions() {
      if (this.$refs.timelineContent) {
        this.timelineWidth = this.$refs.timelineContent.scrollWidth
        this.timelineHeight = this.$refs.timelineContent.scrollHeight
      }
    },
    formatDateRange(start, end) {
      const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      }
      return `${start.toLocaleDateString(
        undefined,
        options
      )} - ${end.toLocaleDateString(undefined, options)}`
    },
    getRowDate(row, fieldId) {
      if (!fieldId) return null
      const fieldName = `field_${fieldId}`
      return row[fieldName] ? new Date(row[fieldName]) : null
    },
    getMilestoneDate(milestone) {
      if (milestone.row_id) {
        const row = this.allRows.find((r) => r.id === milestone.row_id)
        if (row) {
          return this.getRowDate(row, milestone.date_field.id)
        }
      }
      return null
    },
    getDependenciesForRow(rowId) {
      return this.dependencies.filter(
        (dep) =>
          dep.predecessor_row_id === rowId || dep.successor_row_id === rowId
      )
    },
    getMilestonesForRow(rowId) {
      return this.milestones.filter((milestone) => milestone.row_id === rowId)
    },
    async updateValue(row, field, value, oldValue) {
      try {
        await this.$store.dispatch(
          this.storePrefix + 'view/timeline/updateRowValue',
          {
            table: this.table,
            view: this.view,
            row,
            field,
            value,
            oldValue,
          }
        )
      } catch (error) {
        notifyIf(error, 'row')
      }
    },
    async createRow(values) {
      try {
        await this.$store.dispatch(
          this.storePrefix + 'view/timeline/createNewRow',
          {
            view: this.view,
            table: this.table,
            values,
          }
        )
      } catch (error) {
        notifyIf(error, 'row')
      }
    },
    rowClick(row, field) {
      this.$emit('selected-row', row)
      this.$refs.rowEditModal.show(row.id, field)
    },
    async handleDateChange(row, field, newDate) {
      await this.updateValue(
        row,
        field,
        newDate,
        this.getRowDate(row, field.id)
      )

      // Trigger schedule recalculation if dependencies are enabled
      if (this.view.enable_dependencies && this.view.auto_reschedule) {
        try {
          await this.$store.dispatch(
            this.storePrefix + 'view/timeline/recalculateSchedule',
            {
              viewId: this.view.id,
              rowId: row.id,
              newStartDate:
                field.id === this.view.start_date_field ? newDate : null,
              newEndDate:
                field.id === this.view.end_date_field ? newDate : null,
            }
          )
        } catch (error) {
          notifyIf(error, 'timeline')
        }
      }
    },
    async handleDependencyCreated(
      predecessorRowId,
      successorRowId,
      dependencyType = 'finish_to_start'
    ) {
      try {
        await this.$store.dispatch(
          this.storePrefix + 'view/timeline/createDependency',
          {
            viewId: this.view.id,
            predecessorRowId,
            successorRowId,
            dependencyType,
          }
        )
      } catch (error) {
        notifyIf(error, 'timeline')
      }
    },
    async handleDependencyDeleted(dependencyId) {
      try {
        await this.$store.dispatch(
          this.storePrefix + 'view/timeline/deleteDependency',
          {
            viewId: this.view.id,
            dependencyId,
          }
        )
      } catch (error) {
        notifyIf(error, 'timeline')
      }
    },
    handleDependencyClicked(dependency) {
      // Show dependency details or context menu
      this.$emit('dependency-clicked', dependency)
    },
    handleMilestoneClicked(milestone) {
      // Show milestone details or context menu
      this.$emit('milestone-clicked', milestone)
    },
    async refreshRow(row) {
      try {
        await this.$store.dispatch(
          this.storePrefix + 'view/timeline/refreshRow',
          {
            table: this.table,
            row,
          }
        )
      } catch (error) {
        notifyIf(error, 'row')
      }
    },
    showFieldCreated(field) {
      this.$emit('field-created', field)
    },
    afterFieldCreatedUpdateFieldOptions(field) {
      this.$emit('field-created-callback-done', field)
    },
    orderFields(order) {
      this.$emit('order-fields', order)
    },
    toggleFieldVisibility(field) {
      this.$emit('toggle-field-visibility', field)
    },
  },
}
</script>

<style lang="scss" scoped>
.timeline-view {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  &__loading {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
  }

  &__container {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  &__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid var(--color-border);
    background: var(--color-neutral-50);
  }

  &__zoom-controls {
    display: flex;
    gap: 4px;
  }

  &__zoom-btn {
    padding: 6px 12px;
    border: 1px solid var(--color-border);
    background: var(--color-neutral-0);
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    transition: all 0.2s;

    &:hover {
      background: var(--color-neutral-100);
    }

    &--active {
      background: var(--color-primary);
      color: white;
      border-color: var(--color-primary);
    }
  }

  &__date-range {
    font-size: 14px;
    font-weight: 500;
    color: var(--color-neutral-600);
  }

  &__content {
    flex: 1;
    position: relative;
    overflow: auto;
  }

  &__scale {
    display: flex;
    position: sticky;
    top: 0;
    z-index: 10;
    background: var(--color-neutral-50);
    border-bottom: 1px solid var(--color-border);
    height: 40px;
  }

  &__scale-period {
    display: flex;
    align-items: center;
    justify-content: center;
    border-right: 1px solid var(--color-border);
    font-size: 12px;
    font-weight: 500;
    color: var(--color-neutral-600);
    min-width: 0;

    &--day {
      min-width: 100px;
    }

    &--week {
      min-width: 140px;
    }

    &--month {
      min-width: 120px;
    }

    &--year {
      min-width: 200px;
    }
  }

  &__rows {
    position: relative;
    min-height: 400px;
  }

  &__dependencies {
    position: absolute;
    top: 40px;
    left: 0;
    pointer-events: none;
    z-index: 5;
  }

  &__milestones {
    position: absolute;
    top: 40px;
    left: 0;
    pointer-events: none;
    z-index: 6;
  }
}

// Mobile optimizations
@media (max-width: 768px) {
  .timeline-view {
    &__header {
      flex-direction: column;
      gap: 8px;
      padding: 8px 12px;
    }

    &__zoom-controls {
      width: 100%;
      justify-content: center;
    }

    &__zoom-btn {
      flex: 1;
      max-width: 80px;
    }

    &__scale-period {
      font-size: 10px;

      &--day {
        min-width: 60px;
      }

      &--week {
        min-width: 80px;
      }

      &--month {
        min-width: 70px;
      }

      &--year {
        min-width: 100px;
      }
    }
  }
}
</style>
