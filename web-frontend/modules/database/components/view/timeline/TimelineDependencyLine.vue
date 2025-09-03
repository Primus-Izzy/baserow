<template>
  <g
    class="timeline-dependency-line"
    @click="$emit('dependency-clicked', dependency)"
  >
    <!-- Main dependency line -->
    <path
      :d="pathData"
      :stroke="lineColor"
      :stroke-width="lineWidth"
      fill="none"
      :stroke-dasharray="isDashed ? '5,5' : 'none'"
      class="timeline-dependency-line__path"
    />

    <!-- Arrow head -->
    <polygon
      :points="arrowPoints"
      :fill="lineColor"
      class="timeline-dependency-line__arrow"
    />

    <!-- Hover area for better interaction -->
    <path
      :d="pathData"
      stroke="transparent"
      :stroke-width="lineWidth + 10"
      fill="none"
      class="timeline-dependency-line__hover-area"
      @mouseover="showTooltip = true"
      @mouseleave="showTooltip = false"
    />

    <!-- Tooltip -->
    <foreignObject
      v-if="showTooltip"
      :x="tooltipPosition.x"
      :y="tooltipPosition.y"
      width="200"
      height="60"
      class="timeline-dependency-line__tooltip"
    >
      <div class="dependency-tooltip">
        <div class="dependency-tooltip__title">
          {{ getDependencyTypeLabel(dependency.dependency_type) }}
        </div>
        <div class="dependency-tooltip__details">
          {{ getPredecessorTitle() }} → {{ getSuccessorTitle() }}
        </div>
        <div v-if="dependency.lag_days !== 0" class="dependency-tooltip__lag">
          Lag: {{ dependency.lag_days }} days
        </div>
      </div>
    </foreignObject>
  </g>
</template>

<script>
export default {
  name: 'TimelineDependencyLine',
  props: {
    dependency: {
      type: Object,
      required: true,
    },
    rows: {
      type: Array,
      required: true,
    },
    visibleDateRange: {
      type: Object,
      required: true,
    },
    zoomLevel: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      showTooltip: false,
    }
  },
  computed: {
    predecessorRow() {
      return this.rows.find(
        (row) => row.id === this.dependency.predecessor_row_id
      )
    },
    successorRow() {
      return this.rows.find(
        (row) => row.id === this.dependency.successor_row_id
      )
    },
    lineColor() {
      switch (this.dependency.dependency_type) {
        case 'finish_to_start':
          return '#3B82F6' // Blue
        case 'start_to_start':
          return '#10B981' // Green
        case 'finish_to_finish':
          return '#F59E0B' // Yellow
        case 'start_to_finish':
          return '#EF4444' // Red
        default:
          return '#6B7280' // Gray
      }
    },
    lineWidth() {
      return 2
    },
    isDashed() {
      // Show dashed line for future dependencies or conditional ones
      return this.dependency.lag_days < 0
    },
    pixelsPerDay() {
      switch (this.zoomLevel) {
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
    pathData() {
      if (!this.predecessorRow || !this.successorRow) return ''

      const startPoint = this.getConnectionPoint(this.predecessorRow, 'end')
      const endPoint = this.getConnectionPoint(this.successorRow, 'start')

      if (!startPoint || !endPoint) return ''

      // Create a curved path for better visual appeal
      const midX = (startPoint.x + endPoint.x) / 2
      const controlOffset = Math.min(
        50,
        Math.abs(endPoint.x - startPoint.x) / 4
      )

      return `M ${startPoint.x} ${startPoint.y} 
              C ${startPoint.x + controlOffset} ${startPoint.y}, 
                ${endPoint.x - controlOffset} ${endPoint.y}, 
                ${endPoint.x - 8} ${endPoint.y}`
    },
    arrowPoints() {
      if (!this.predecessorRow || !this.successorRow) return ''

      const endPoint = this.getConnectionPoint(this.successorRow, 'start')
      if (!endPoint) return ''

      // Create arrow pointing to the right
      const arrowSize = 6
      return `${endPoint.x},${endPoint.y} 
              ${endPoint.x - arrowSize},${endPoint.y - arrowSize / 2} 
              ${endPoint.x - arrowSize},${endPoint.y + arrowSize / 2}`
    },
    tooltipPosition() {
      if (!this.predecessorRow || !this.successorRow) return { x: 0, y: 0 }

      const startPoint = this.getConnectionPoint(this.predecessorRow, 'end')
      const endPoint = this.getConnectionPoint(this.successorRow, 'start')

      if (!startPoint || !endPoint) return { x: 0, y: 0 }

      return {
        x: (startPoint.x + endPoint.x) / 2 - 100,
        y: (startPoint.y + endPoint.y) / 2 - 30,
      }
    },
  },
  methods: {
    getConnectionPoint(row, side) {
      if (!row) return null

      // Find the row's position in the timeline
      const rowIndex = this.rows.findIndex((r) => r.id === row.id)
      if (rowIndex === -1) return null

      const rowY = rowIndex * 48 + 24 // 48px row height, center vertically

      // Get the row's date range
      const startDate = this.getRowDate(row, 'start')
      const endDate = this.getRowDate(row, 'end')

      if (!startDate && !endDate) return null

      const timelineStart = this.visibleDateRange.start
      let connectionDate

      switch (this.dependency.dependency_type) {
        case 'finish_to_start':
          connectionDate =
            side === 'end' ? endDate || startDate : startDate || endDate
          break
        case 'start_to_start':
          connectionDate = startDate || endDate
          break
        case 'finish_to_finish':
          connectionDate = endDate || startDate
          break
        case 'start_to_finish':
          connectionDate =
            side === 'end' ? startDate || endDate : endDate || startDate
          break
        default:
          connectionDate =
            side === 'end' ? endDate || startDate : startDate || endDate
      }

      if (!connectionDate) return null

      const connectionX =
        ((connectionDate - timelineStart) / (1000 * 60 * 60 * 24)) *
          this.pixelsPerDay +
        200 // 200px for label column

      return {
        x: connectionX,
        y: rowY,
      }
    },
    getRowDate(row, type) {
      // This would need to be passed from parent or accessed from store
      // For now, assume we have access to the field IDs
      const startFieldId = this.$parent.view?.start_date_field
      const endFieldId = this.$parent.view?.end_date_field

      if (type === 'start' && startFieldId) {
        const value = row[`field_${startFieldId}`]
        return value ? new Date(value) : null
      } else if (type === 'end' && endFieldId) {
        const value = row[`field_${endFieldId}`]
        return value ? new Date(value) : null
      }

      return null
    },
    getDependencyTypeLabel(type) {
      switch (type) {
        case 'finish_to_start':
          return 'Finish to Start'
        case 'start_to_start':
          return 'Start to Start'
        case 'finish_to_finish':
          return 'Finish to Finish'
        case 'start_to_finish':
          return 'Start to Finish'
        default:
          return 'Dependency'
      }
    },
    getPredecessorTitle() {
      if (!this.predecessorRow) return 'Unknown'

      // Get the primary field or first text field
      const primaryField = this.$parent.fields?.find((f) => f.primary)
      if (primaryField) {
        return this.predecessorRow[`field_${primaryField.id}`] || 'Untitled'
      }

      return `Row ${this.predecessorRow.id}`
    },
    getSuccessorTitle() {
      if (!this.successorRow) return 'Unknown'

      // Get the primary field or first text field
      const primaryField = this.$parent.fields?.find((f) => f.primary)
      if (primaryField) {
        return this.successorRow[`field_${primaryField.id}`] || 'Untitled'
      }

      return `Row ${this.successorRow.id}`
    },
  },
}
</script>

<style lang="scss" scoped>
.timeline-dependency-line {
  cursor: pointer;

  &__path {
    transition: stroke-width 0.2s;
  }

  &__arrow {
    transition: fill 0.2s;
  }

  &__hover-area {
    cursor: pointer;
  }

  &:hover {
    .timeline-dependency-line__path {
      stroke-width: 3;
    }
  }
}

.dependency-tooltip {
  background: var(--color-neutral-800);
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  pointer-events: none;

  &__title {
    font-weight: 600;
    margin-bottom: 4px;
  }

  &__details {
    color: var(--color-neutral-300);
    margin-bottom: 2px;
  }

  &__lag {
    font-size: 11px;
    color: var(--color-neutral-400);
  }
}
</style>
