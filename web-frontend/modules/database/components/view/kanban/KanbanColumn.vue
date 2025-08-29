<template>
  <div 
    class="kanban-column"
    :class="{
      'kanban-column--dragging-over': isDraggingOver,
      'kanban-column--empty': rows.length === 0
    }"
    :data-column-id="column.id"
    @dragover.prevent="handleDragOver"
    @dragleave="handleDragLeave"
    @drop="handleDrop"
  >
    <!-- Column header -->
    <div class="kanban-column__header">
      <div class="kanban-column__title">
        <div 
          class="kanban-column__color-indicator"
          :style="{ backgroundColor: getColumnColor(column.color) }"
        ></div>
        <span class="kanban-column__name">{{ column.name }}</span>
        <span class="kanban-column__count">({{ rows.length }})</span>
      </div>
      
      <!-- Column actions -->
      <div class="kanban-column__actions">
        <button
          v-if="!readOnly && $hasPermission('database.table.create_row', table, database.workspace.id)"
          class="kanban-column__add-card"
          @click="addCard"
          :title="$t('kanbanView.addCard')"
        >
          <i class="iconoir-plus"></i>
        </button>
      </div>
    </div>

    <!-- Column content -->
    <div 
      class="kanban-column__content"
      ref="columnContent"
    >
      <!-- Cards -->
      <KanbanCard
        v-for="row in rows"
        :key="row.id"
        :row="row"
        :fields="fields"
        :column="column"
        :database="database"
        :table="table"
        :view="view"
        :read-only="readOnly"
        :decorations-by-place="decorationsByPlace"
        @click="$emit('row-clicked', row)"
        @updated="$emit('row-updated', $event)"
        @drag-start="handleCardDragStart"
        @drag-end="handleCardDragEnd"
      />
      
      <!-- Empty state -->
      <div v-if="rows.length === 0" class="kanban-column__empty">
        <div class="kanban-column__empty-icon">
          <i class="iconoir-page"></i>
        </div>
        <div class="kanban-column__empty-text">
          {{ $t('kanbanView.noCards') }}
        </div>
        <button
          v-if="!readOnly && $hasPermission('database.table.create_row', table, database.workspace.id)"
          class="kanban-column__empty-add"
          @click="addCard"
        >
          {{ $t('kanbanView.addFirstCard') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import KanbanCard from '@baserow/modules/database/components/view/kanban/KanbanCard'

export default {
  name: 'KanbanColumn',
  components: {
    KanbanCard,
  },
  props: {
    column: {
      type: Object,
      required: true,
    },
    fields: {
      type: Array,
      required: true,
    },
    rows: {
      type: Array,
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
    storePrefix: {
      type: String,
      required: true,
    },
    decorationsByPlace: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      isDraggingOver: false,
      dragCounter: 0,
    }
  },
  methods: {
    /**
     * Returns the color for the column based on the select option color.
     */
    getColumnColor(colorName) {
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
     * Handles adding a new card to this column.
     */
    addCard() {
      // Create a new row with the column's status value pre-filled
      const statusField = this.fields.find(f => f.id === this.view.single_select_field)
      if (!statusField) return
      
      const initialValues = {}
      if (!this.column.isNull) {
        initialValues[`field_${statusField.id}`] = this.column.value
      }
      
      // Emit to parent to show the row create modal with pre-filled values
      this.$emit('add-card', {
        column: this.column,
        initialValues,
      })
    },
    /**
     * Handles drag over events for the column.
     */
    handleDragOver(event) {
      event.preventDefault()
      event.dataTransfer.dropEffect = 'move'
      
      if (!this.isDraggingOver) {
        this.isDraggingOver = true
        this.dragCounter = 1
      }
    },
    /**
     * Handles drag leave events for the column.
     */
    handleDragLeave(event) {
      // Only decrease counter if leaving the column itself, not child elements
      if (!this.$el.contains(event.relatedTarget)) {
        this.isDraggingOver = false
        this.dragCounter = 0
      }
    },
    /**
     * Handles drop events for the column.
     */
    handleDrop(event) {
      event.preventDefault()
      this.isDraggingOver = false
      this.dragCounter = 0
      
      try {
        const dragData = JSON.parse(event.dataTransfer.getData('text/plain'))
        if (dragData.type === 'kanban-card' && dragData.row) {
          this.$emit('row-moved', {
            row: dragData.row,
            targetColumn: this.column,
          })
        }
      } catch (error) {
        // Invalid drag data, ignore
      }
    },
    /**
     * Handles card drag start events.
     */
    handleCardDragStart(event) {
      this.dragCounter++
    },
    /**
     * Handles card drag end events.
     */
    handleCardDragEnd(event) {
      this.dragCounter = 0
      this.isDraggingOver = false
    },
  },
}
</script>