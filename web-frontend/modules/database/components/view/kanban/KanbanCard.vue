<template>
  <div
    class="kanban-card"
    :class="{
      'kanban-card--dragging': isDragging,
      'kanban-card--read-only': readOnly,
    }"
    :draggable="!readOnly"
    @dragstart="handleDragStart"
    @dragend="handleDragEnd"
    @click="handleClick"
    @touchstart="handleTouchStart"
    @touchmove="handleTouchMove"
    @touchend="handleTouchEnd"
  >
    <!-- Card color indicator -->
    <div 
      v-if="cardColor"
      class="kanban-card__color-bar"
      :style="{ backgroundColor: cardColor }"
    ></div>

    <!-- Card content -->
    <div class="kanban-card__content">
      <!-- Primary field (always shown) -->
      <div class="kanban-card__primary">
        <RowCardField
          :field="primaryField"
          :row="row"
          :read-only="true"
          class="kanban-card__primary-field"
        />
      </div>

      <!-- Additional visible fields -->
      <div class="kanban-card__fields">
        <div
          v-for="field in visibleFields"
          :key="field.id"
          class="kanban-card__field"
        >
          <div class="kanban-card__field-label">
            {{ field.name }}
          </div>
          <div class="kanban-card__field-value">
            <RowCardField
              :field="field"
              :row="row"
              :read-only="!canEditInline(field)"
              :decorations-by-place="decorationsByPlace"
              @updated="handleFieldUpdate"
            />
          </div>
        </div>
      </div>

      <!-- Card metadata -->
      <div class="kanban-card__metadata">
        <!-- Row ID -->
        <div class="kanban-card__id">
          #{{ row.id }}
        </div>
        
        <!-- Last modified -->
        <div v-if="row.updated_on" class="kanban-card__updated">
          {{ formatDate(row.updated_on) }}
        </div>
      </div>
    </div>

    <!-- Card actions -->
    <div v-if="!readOnly" class="kanban-card__actions">
      <button
        class="kanban-card__action"
        @click.stop="handleEdit"
        :title="$t('kanbanView.editCard')"
      >
        <i class="iconoir-edit-pencil"></i>
      </button>
    </div>
  </div>
</template>

<script>
import RowCardField from '@baserow/modules/database/components/card/RowCardField'
import { formatDate } from '@baserow/modules/core/utils/date'

export default {
  name: 'KanbanCard',
  components: {
    RowCardField,
  },
  props: {
    row: {
      type: Object,
      required: true,
    },
    fields: {
      type: Array,
      required: true,
    },
    column: {
      type: Object,
      required: true,
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
    readOnly: {
      type: Boolean,
      required: true,
    },
    decorationsByPlace: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      isDragging: false,
      touchStartTime: 0,
      touchStartPos: { x: 0, y: 0 },
    }
  },
  computed: {
    /**
     * Returns the primary field (first field in the table).
     */
    primaryField() {
      return this.fields.find(field => field.primary) || this.fields[0]
    },
    /**
     * Returns the visible fields for the card (excluding primary and status fields).
     */
    visibleFields() {
      const statusFieldId = this.view.single_select_field
      return this.fields.filter(field => 
        !field.primary && 
        field.id !== statusFieldId &&
        this.shouldShowField(field)
      ).slice(0, 3) // Limit to 3 additional fields for card readability
    },
    /**
     * Returns the color for the card based on field values or column.
     */
    cardColor() {
      // Check if there's a color field configured (using card_cover_image_field for now)
      const colorFieldId = this.view.card_cover_image_field
      if (colorFieldId) {
        const colorField = this.fields.find(f => f.id === colorFieldId)
        if (colorField && colorField.type === 'single_select') {
          const value = this.row[`field_${colorField.id}`]
          const option = colorField.select_options?.find(opt => opt.value === value)
          if (option) {
            return this.getSelectOptionColor(option.color)
          }
        }
      }
      
      // Fallback to column color
      return this.getSelectOptionColor(this.column.color)
    },
  },
  methods: {
    /**
     * Determines if a field should be shown on the card.
     */
    shouldShowField(field) {
      // Show fields that are not hidden and have meaningful content
      const value = this.row[`field_${field.id}`]
      return value !== null && value !== undefined && value !== ''
    },
    /**
     * Determines if a field can be edited inline.
     */
    canEditInline(field) {
      // Allow inline editing for simple field types
      const inlineEditableTypes = ['text', 'long_text', 'number', 'rating', 'boolean']
      return !this.readOnly && inlineEditableTypes.includes(field.type)
    },
    /**
     * Returns the color for a select option.
     */
    getSelectOptionColor(colorName) {
      const colorMap = {
        blue: '#3498db',
        green: '#2ecc71',
        red: '#e74c3c',
        yellow: '#f1c40f',
        orange: '#e67e22',
        purple: '#9b59b6',
        pink: '#e91e63',
        brown: '#8d6e63',
        gray: '#95a5a6',
        neutral: '#bdc3c7',
      }
      return colorMap[colorName] || colorMap.neutral
    },
    /**
     * Formats a date for display.
     */
    formatDate(dateString) {
      return formatDate(dateString, 'DD/MM/YYYY')
    },
    /**
     * Handles drag start events.
     */
    handleDragStart(event) {
      if (this.readOnly) {
        event.preventDefault()
        return
      }
      
      this.isDragging = true
      
      // Set drag data
      const dragData = {
        type: 'kanban-card',
        row: this.row,
        column: this.column,
      }
      
      event.dataTransfer.setData('text/plain', JSON.stringify(dragData))
      event.dataTransfer.effectAllowed = 'move'
      
      // Add drag image
      const dragImage = this.$el.cloneNode(true)
      dragImage.style.transform = 'rotate(5deg)'
      dragImage.style.opacity = '0.8'
      document.body.appendChild(dragImage)
      event.dataTransfer.setDragImage(dragImage, 0, 0)
      
      // Clean up drag image after a short delay
      setTimeout(() => {
        document.body.removeChild(dragImage)
      }, 0)
      
      this.$emit('drag-start', event)
    },
    /**
     * Handles drag end events.
     */
    handleDragEnd(event) {
      this.isDragging = false
      this.$emit('drag-end', event)
    },
    /**
     * Handles card click events.
     */
    handleClick(event) {
      // Don't trigger click if we're dragging or clicking on an action button
      if (this.isDragging || event.target.closest('.kanban-card__action')) {
        return
      }
      
      this.$emit('click', this.row)
    },
    /**
     * Handles edit button click.
     */
    handleEdit(event) {
      event.stopPropagation()
      this.$emit('click', this.row)
    },
    /**
     * Handles field updates.
     */
    handleFieldUpdate(event) {
      this.$emit('updated', event)
    },
    /**
     * Handles touch start for mobile drag support.
     */
    handleTouchStart(event) {
      if (this.readOnly) return
      
      this.touchStartTime = Date.now()
      this.touchStartPos = {
        x: event.touches[0].clientX,
        y: event.touches[0].clientY,
      }
      
      // Add visual feedback for touch
      this.$el.classList.add('kanban-card--touch-active')
    },
    /**
     * Handles touch move for mobile drag support.
     */
    handleTouchMove(event) {
      if (this.readOnly) return
      
      const touch = event.touches[0]
      const deltaX = Math.abs(touch.clientX - this.touchStartPos.x)
      const deltaY = Math.abs(touch.clientY - this.touchStartPos.y)
      
      // If moved significantly, start drag mode
      if (deltaX > 15 || deltaY > 15) {
        event.preventDefault()
        this.$el.classList.add('kanban-card--touch-dragging')
        
        // Create a visual drag indicator
        this.createTouchDragIndicator(touch)
      }
    },
    /**
     * Handles touch end for mobile drag support.
     */
    handleTouchEnd(event) {
      if (this.readOnly) return
      
      const touchDuration = Date.now() - this.touchStartTime
      const touch = event.changedTouches[0]
      const deltaX = Math.abs(touch.clientX - this.touchStartPos.x)
      const deltaY = Math.abs(touch.clientY - this.touchStartPos.y)
      
      // Clean up touch classes
      this.$el.classList.remove('kanban-card--touch-active', 'kanban-card--touch-dragging')
      this.removeTouchDragIndicator()
      
      // If it was a quick tap with minimal movement, treat as click
      if (touchDuration < 300 && deltaX < 15 && deltaY < 15) {
        this.handleClick(event)
      } else if (deltaX > 15 || deltaY > 15) {
        // Handle touch drag end - find target column
        this.handleTouchDragEnd(touch)
      }
    },
    /**
     * Creates a visual indicator for touch dragging.
     */
    createTouchDragIndicator(touch) {
      // This would create a visual feedback element following the touch
      // For now, we'll just add a CSS class for styling
    },
    /**
     * Removes the touch drag indicator.
     */
    removeTouchDragIndicator() {
      // Clean up any drag indicators
    },
    /**
     * Handles the end of a touch drag operation.
     */
    handleTouchDragEnd(touch) {
      // Find the element under the touch point
      const elementBelow = document.elementFromPoint(touch.clientX, touch.clientY)
      const targetColumn = elementBelow?.closest('.kanban-column')
      
      if (targetColumn) {
        // Extract column data and emit move event
        const columnId = targetColumn.dataset.columnId
        if (columnId && columnId !== this.column.id) {
          // Find the target column object
          const targetColumnData = this.findColumnById(columnId)
          if (targetColumnData) {
            this.$emit('drag-end', {
              row: this.row,
              targetColumn: targetColumnData,
            })
          }
        }
      }
    },
    /**
     * Helper to find column by ID (would need to be passed from parent).
     */
    findColumnById(columnId) {
      // This would need to be implemented with access to all columns
      // For now, return null
      return null
    },
  },
}
</script>