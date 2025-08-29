<template>
  <div class="timeline-row" :class="{ 'timeline-row--dragging': isDragging }">
    <!-- Row label/info -->
    <div class="timeline-row__label">
      <div class="timeline-row__title" @click="$emit('row-clicked', row)">
        {{ getRowTitle(row) }}
      </div>
      <div class="timeline-row__info">
        <span v-if="startDate && endDate" class="timeline-row__duration">
          {{ formatDuration(startDate, endDate) }}
        </span>
      </div>
    </div>

    <!-- Timeline bar -->
    <div class="timeline-row__timeline" ref="timeline">
      <div
        v-if="startDate || endDate"
        class="timeline-row__bar"
        :class="[
          'timeline-row__bar--' + getBarType(),
          { 'timeline-row__bar--critical': isOnCriticalPath }
        ]"
        :style="getBarStyle()"
        @mousedown="startDrag"
        @click="$emit('row-clicked', row)"
      >
        <!-- Progress indicator -->
        <div
          v-if="progressPercentage !== null"
          class="timeline-row__progress"
          :style="{ width: progressPercentage + '%' }"
        ></div>

        <!-- Bar content -->
        <div class="timeline-row__bar-content">
          <span class="timeline-row__bar-title">{{ getRowTitle(row) }}</span>
          <span v-if="progressPercentage !== null" class="timeline-row__bar-progress">
            {{ Math.round(progressPercentage) }}%
          </span>
        </div>

        <!-- Resize handles -->
        <div
          v-if="!readOnly && startDate"
          class="timeline-row__resize-handle timeline-row__resize-handle--start"
          @mousedown.stop="startResize('start')"
        ></div>
        <div
          v-if="!readOnly && endDate"
          class="timeline-row__resize-handle timeline-row__resize-handle--end"
          @mousedown.stop="startResize('end')"
        ></div>
      </div>

      <!-- Milestone indicators -->
      <div
        v-for="milestone in milestones"
        :key="milestone.id"
        class="timeline-row__milestone"
        :style="getMilestoneStyle(milestone)"
        :title="milestone.name"
        @click="$emit('milestone-clicked', milestone)"
      >
        <i :class="milestone.icon || 'iconoir-flag'" :style="{ color: milestone.color }"></i>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TimelineRow',
  props: {
    row: {
      type: Object,
      required: true,
    },
    fields: {
      type: Array,
      required: true,
    },
    startDateField: {
      type: Number,
      required: false,
      default: null,
    },
    endDateField: {
      type: Number,
      required: false,
      default: null,
    },
    visibleDateRange: {
      type: Object,
      required: true,
    },
    zoomLevel: {
      type: String,
      required: true,
    },
    dependencies: {
      type: Array,
      required: false,
      default: () => [],
    },
    milestones: {
      type: Array,
      required: false,
      default: () => [],
    },
    readOnly: {
      type: Boolean,
      required: false,
      default: false,
    },
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
    storePrefix: {
      type: String,
      required: false,
      default: '',
    },
  },
  data() {
    return {
      isDragging: false,
      isResizing: false,
      resizeType: null,
      dragStartX: 0,
      dragStartDate: null,
      originalStartDate: null,
      originalEndDate: null,
    }
  },
  computed: {
    startDate() {
      return this.getRowDate(this.startDateField)
    },
    endDate() {
      return this.getRowDate(this.endDateField)
    },
    progressPercentage() {
      const progressField = this.fields.find(f => f.type === 'number' && f.name.toLowerCase().includes('progress'))
      if (progressField) {
        const value = this.row[`field_${progressField.id}`]
        return value !== null && value !== undefined ? Math.min(100, Math.max(0, value)) : null
      }
      return null
    },
    isOnCriticalPath() {
      // This would be determined by the backend critical path calculation
      return false
    },
    pixelsPerDay() {
      switch (this.zoomLevel) {
        case 'day': return 100
        case 'week': return 20
        case 'month': return 5
        case 'year': return 1
        default: return 20
      }
    },
  },
  mounted() {
    this.setupEventListeners()
  },
  beforeDestroy() {
    this.removeEventListeners()
  },
  methods: {
    setupEventListeners() {
      document.addEventListener('mousemove', this.handleMouseMove)
      document.addEventListener('mouseup', this.handleMouseUp)
    },
    removeEventListeners() {
      document.removeEventListener('mousemove', this.handleMouseMove)
      document.removeEventListener('mouseup', this.handleMouseUp)
    },
    getRowDate(fieldId) {
      if (!fieldId) return null
      const fieldName = `field_${fieldId}`
      return this.row[fieldName] ? new Date(this.row[fieldName]) : null
    },
    getRowTitle(row) {
      // Get the primary field value or first text field
      const primaryField = this.fields.find(f => f.primary)
      if (primaryField) {
        return row[`field_${primaryField.id}`] || 'Untitled'
      }
      
      const textField = this.fields.find(f => f.type === 'text')
      if (textField) {
        return row[`field_${textField.id}`] || 'Untitled'
      }
      
      return `Row ${row.id}`
    },
    formatDuration(startDate, endDate) {
      if (!startDate || !endDate) return ''
      
      const diffTime = Math.abs(endDate - startDate)
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      
      if (diffDays === 1) return '1 day'
      if (diffDays < 7) return `${diffDays} days`
      if (diffDays < 30) return `${Math.round(diffDays / 7)} weeks`
      return `${Math.round(diffDays / 30)} months`
    },
    getBarType() {
      if (this.startDate && this.endDate) return 'task'
      if (this.startDate && !this.endDate) return 'milestone'
      if (!this.startDate && this.endDate) return 'deadline'
      return 'task'
    },
    getBarStyle() {
      const style = {}
      
      if (!this.startDate && !this.endDate) return style
      
      const timelineStart = this.visibleDateRange.start
      const timelineEnd = this.visibleDateRange.end
      const timelineWidth = (timelineEnd - timelineStart) / (1000 * 60 * 60 * 24) * this.pixelsPerDay
      
      let barStart = this.startDate || this.endDate
      let barEnd = this.endDate || this.startDate
      
      // Calculate position and width
      const startOffset = (barStart - timelineStart) / (1000 * 60 * 60 * 24) * this.pixelsPerDay
      const barWidth = Math.max(20, (barEnd - barStart) / (1000 * 60 * 60 * 24) * this.pixelsPerDay)
      
      style.left = Math.max(0, startOffset) + 'px'
      style.width = barWidth + 'px'
      
      // Color coding based on status or field values
      const colorField = this.fields.find(f => f.type === 'single_select' && f.name.toLowerCase().includes('status'))
      if (colorField) {
        const value = this.row[`field_${colorField.id}`]
        if (value && value.color) {
          style.backgroundColor = value.color
        }
      }
      
      return style
    },
    getMilestoneStyle(milestone) {
      const milestoneDate = this.getMilestoneDate(milestone)
      if (!milestoneDate) return { display: 'none' }
      
      const timelineStart = this.visibleDateRange.start
      const offset = (milestoneDate - timelineStart) / (1000 * 60 * 60 * 24) * this.pixelsPerDay
      
      return {
        left: offset + 'px',
        color: milestone.color,
      }
    },
    getMilestoneDate(milestone) {
      if (milestone.row_id === this.row.id && milestone.date_field) {
        return this.getRowDate(milestone.date_field.id)
      }
      return null
    },
    startDrag(event) {
      if (this.readOnly) return
      
      this.isDragging = true
      this.dragStartX = event.clientX
      this.originalStartDate = this.startDate
      this.originalEndDate = this.endDate
      
      event.preventDefault()
    },
    startResize(type) {
      if (this.readOnly) return
      
      this.isResizing = true
      this.resizeType = type
      this.originalStartDate = this.startDate
      this.originalEndDate = this.endDate
    },
    handleMouseMove(event) {
      if (!this.isDragging && !this.isResizing) return
      
      const deltaX = event.clientX - this.dragStartX
      const daysDelta = deltaX / this.pixelsPerDay
      
      if (this.isDragging) {
        // Move both start and end dates
        if (this.originalStartDate) {
          const newStartDate = new Date(this.originalStartDate)
          newStartDate.setDate(newStartDate.getDate() + daysDelta)
          this.updateDate('start', newStartDate)
        }
        
        if (this.originalEndDate) {
          const newEndDate = new Date(this.originalEndDate)
          newEndDate.setDate(newEndDate.getDate() + daysDelta)
          this.updateDate('end', newEndDate)
        }
      } else if (this.isResizing) {
        // Resize start or end date
        if (this.resizeType === 'start' && this.originalStartDate) {
          const newStartDate = new Date(this.originalStartDate)
          newStartDate.setDate(newStartDate.getDate() + daysDelta)
          this.updateDate('start', newStartDate)
        } else if (this.resizeType === 'end' && this.originalEndDate) {
          const newEndDate = new Date(this.originalEndDate)
          newEndDate.setDate(newEndDate.getDate() + daysDelta)
          this.updateDate('end', newEndDate)
        }
      }
    },
    handleMouseUp() {
      if (this.isDragging || this.isResizing) {
        this.isDragging = false
        this.isResizing = false
        this.resizeType = null
        
        // Emit final date changes
        if (this.startDate !== this.originalStartDate) {
          this.emitDateChange('start', this.startDate)
        }
        if (this.endDate !== this.originalEndDate) {
          this.emitDateChange('end', this.endDate)
        }
      }
    },
    updateDate(type, newDate) {
      const field = type === 'start' 
        ? this.fields.find(f => f.id === this.startDateField)
        : this.fields.find(f => f.id === this.endDateField)
      
      if (field) {
        // Update the row data locally for immediate feedback
        const fieldName = `field_${field.id}`
        this.$set(this.row, fieldName, newDate.toISOString())
      }
    },
    emitDateChange(type, newDate) {
      const field = type === 'start' 
        ? this.fields.find(f => f.id === this.startDateField)
        : this.fields.find(f => f.id === this.endDateField)
      
      if (field) {
        this.$emit('date-changed', this.row, field, newDate)
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.timeline-row {
  display: flex;
  align-items: center;
  min-height: 48px;
  border-bottom: 1px solid var(--color-border);
  position: relative;

  &--dragging {
    opacity: 0.8;
    z-index: 10;
  }

  &__label {
    width: 200px;
    min-width: 200px;
    padding: 8px 12px;
    border-right: 1px solid var(--color-border);
    background: var(--color-neutral-50);
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  &__title {
    font-weight: 500;
    font-size: 14px;
    cursor: pointer;
    color: var(--color-neutral-800);
    
    &:hover {
      color: var(--color-primary);
    }
  }

  &__info {
    font-size: 12px;
    color: var(--color-neutral-600);
  }

  &__duration {
    font-size: 11px;
    color: var(--color-neutral-500);
  }

  &__timeline {
    flex: 1;
    position: relative;
    height: 48px;
    overflow: visible;
  }

  &__bar {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    height: 24px;
    background: var(--color-primary);
    border-radius: 4px;
    cursor: move;
    display: flex;
    align-items: center;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: box-shadow 0.2s;

    &:hover {
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
    }

    &--task {
      background: var(--color-primary);
    }

    &--milestone {
      background: var(--color-warning);
      border-radius: 50%;
      width: 24px !important;
      min-width: 24px;
    }

    &--deadline {
      background: var(--color-error);
    }

    &--critical {
      background: var(--color-error);
      box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.3);
    }
  }

  &__progress {
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    background: rgba(255, 255, 255, 0.3);
    border-radius: 4px 0 0 4px;
    transition: width 0.3s;
  }

  &__bar-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    padding: 0 8px;
    color: white;
    font-size: 12px;
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
  }

  &__bar-title {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  &__bar-progress {
    margin-left: 8px;
    font-size: 10px;
    opacity: 0.9;
  }

  &__resize-handle {
    position: absolute;
    top: 0;
    width: 8px;
    height: 100%;
    cursor: ew-resize;
    background: rgba(255, 255, 255, 0.3);
    opacity: 0;
    transition: opacity 0.2s;

    &--start {
      left: 0;
      border-radius: 4px 0 0 4px;
    }

    &--end {
      right: 0;
      border-radius: 0 4px 4px 0;
    }

    &:hover {
      opacity: 1;
    }
  }

  &__bar:hover &__resize-handle {
    opacity: 0.7;
  }

  &__milestone {
    position: absolute;
    top: 50%;
    transform: translate(-50%, -50%);
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: white;
    border: 2px solid currentColor;
    border-radius: 50%;
    cursor: pointer;
    font-size: 12px;
    z-index: 5;

    &:hover {
      transform: translate(-50%, -50%) scale(1.1);
    }
  }
}

// Mobile optimizations
@media (max-width: 768px) {
  .timeline-row {
    &__label {
      width: 150px;
      min-width: 150px;
      padding: 6px 8px;
    }

    &__title {
      font-size: 13px;
    }

    &__info {
      font-size: 11px;
    }

    &__bar {
      height: 20px;
    }

    &__bar-content {
      padding: 0 6px;
      font-size: 11px;
    }

    &__resize-handle {
      width: 12px;
    }
  }
}
</style>