<template>
  <div class="drag-drop-dashboard">
    <div
      class="dashboard-grid"
      :class="{ 'dashboard-grid--edit-mode': editMode }"
    >
      <div
        v-for="item in layout"
        :key="item.i"
        class="dashboard-grid-item"
        :class="{
          'dashboard-grid-item--dragging': draggedItem === item.i,
          'dashboard-grid-item--edit-mode': editMode,
        }"
        :style="getItemStyle(item)"
        @mousedown="startDrag($event, item)"
        @touchstart="startDrag($event, item)"
      >
        <div class="dashboard-grid-item__content">
          <component
            :is="getWidgetComponent(item.widgetType)"
            :widget="getWidget(item.i)"
            :dashboard="dashboard"
            :loading="isWidgetLoading(item.i)"
            :edit-mode="editMode"
            :store-prefix="storePrefix"
            @delete-widget="handleDeleteWidget"
          />
        </div>

        <!-- Drag handle -->
        <div
          v-if="editMode"
          class="dashboard-grid-item__drag-handle"
          @mousedown.stop="startDrag($event, item)"
          @touchstart.stop="startDrag($event, item)"
        >
          <i class="fas fa-grip-vertical"></i>
        </div>

        <!-- Resize handle -->
        <div
          v-if="editMode"
          class="dashboard-grid-item__resize-handle"
          @mousedown.stop="startResize($event, item)"
          @touchstart.stop="startResize($event, item)"
        >
          <i class="fas fa-expand-arrows-alt"></i>
        </div>
      </div>
    </div>

    <!-- Add widget button for empty dashboard -->
    <div
      v-if="layout.length === 0 && editMode"
      class="drag-drop-dashboard__empty"
    >
      <div class="drag-drop-dashboard__empty-content">
        <i class="fas fa-plus-circle drag-drop-dashboard__empty-icon"></i>
        <h3 class="drag-drop-dashboard__empty-title">
          {{ $t('dashboard.addFirstWidget') }}
        </h3>
        <p class="drag-drop-dashboard__empty-description">
          {{ $t('dashboard.addFirstWidgetDescription') }}
        </p>
        <Button type="primary" size="large" @click="$emit('add-widget')">
          {{ $t('dashboard.addWidget') }}
        </Button>
      </div>
    </div>
  </div>
</template>

<script>
import SummaryWidget from '@baserow/modules/dashboard/components/widget/SummaryWidget'
import KPIWidget from '@baserow/modules/dashboard/components/widget/KPIWidget'
import EnhancedChartWidget from '@baserow/modules/dashboard/components/widget/EnhancedChartWidget'

export default {
  name: 'DragDropDashboard',
  components: {
    SummaryWidget,
    KPIWidget,
    EnhancedChartWidget,
  },
  props: {
    dashboard: {
      type: Object,
      required: true,
    },
    widgets: {
      type: Array,
      default: () => [],
    },
    editMode: {
      type: Boolean,
      default: false,
    },
    storePrefix: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      layout: [],
      gridColumns: 12,
      rowHeight: 60,
      cellWidth: 0,
      layoutUpdateTimeout: null,

      // Drag and drop state
      draggedItem: null,
      dragOffset: { x: 0, y: 0 },
      isDragging: false,
      isResizing: false,
      resizedItem: null,

      // Grid dimensions
      containerWidth: 0,
      containerHeight: 0,
    }
  },
  computed: {
    isDraggable() {
      return this.editMode
    },
    isResizable() {
      return this.editMode
    },
  },
  watch: {
    widgets: {
      handler: 'updateLayout',
      immediate: true,
    },
    editMode(newValue) {
      if (!newValue) {
        this.saveLayoutToServer()
      }
    },
  },
  async mounted() {
    await this.loadDashboardLayout()
    this.calculateGridDimensions()
    window.addEventListener('resize', this.calculateGridDimensions)

    // Add global event listeners for drag and drop
    document.addEventListener('mousemove', this.handleMouseMove)
    document.addEventListener('mouseup', this.handleMouseUp)
    document.addEventListener('touchmove', this.handleTouchMove)
    document.addEventListener('touchend', this.handleTouchEnd)
  },

  beforeDestroy() {
    window.removeEventListener('resize', this.calculateGridDimensions)
    document.removeEventListener('mousemove', this.handleMouseMove)
    document.removeEventListener('mouseup', this.handleMouseUp)
    document.removeEventListener('touchmove', this.handleTouchMove)
    document.removeEventListener('touchend', this.handleTouchEnd)
  },
  methods: {
    async loadDashboardLayout() {
      try {
        const { data } = await this.$axios.get(
          `/api/dashboard/enhanced/dashboard/${this.dashboard.id}/layout/`
        )

        if (data.layout_data && data.layout_data.length > 0) {
          this.layout = data.layout_data
          this.gridColumns = data.grid_columns || 12
          this.rowHeight = data.grid_row_height || 60

          if (data.breakpoints) {
            this.breakpoints = { ...this.breakpoints, ...data.breakpoints }
          }
        } else {
          this.generateDefaultLayout()
        }
      } catch (error) {
        console.error('Error loading dashboard layout:', error)
        this.generateDefaultLayout()
      }
    },

    generateDefaultLayout() {
      this.layout = this.widgets.map((widget, index) => ({
        i: widget.id.toString(),
        x: (index * 6) % this.gridColumns,
        y: Math.floor((index * 6) / this.gridColumns) * 4,
        w: 6,
        h: 4,
        minW: 3,
        minH: 2,
        widgetType: widget.type,
      }))
    },

    updateLayout() {
      // Update layout when widgets change
      const existingIds = this.layout.map((item) => item.i)
      const widgetIds = this.widgets.map((widget) => widget.id.toString())

      // Add new widgets to layout
      this.widgets.forEach((widget, index) => {
        const widgetId = widget.id.toString()
        if (!existingIds.includes(widgetId)) {
          const newItem = {
            i: widgetId,
            x: (index * 6) % this.gridColumns,
            y: Math.floor((index * 6) / this.gridColumns) * 4,
            w: 6,
            h: 4,
            minW: 3,
            minH: 2,
            widgetType: widget.type,
          }
          this.layout.push(newItem)
        }
      })

      // Remove deleted widgets from layout
      this.layout = this.layout.filter((item) => widgetIds.includes(item.i))

      // Update widget types
      this.layout.forEach((item) => {
        const widget = this.widgets.find((w) => w.id.toString() === item.i)
        if (widget) {
          item.widgetType = widget.type
        }
      })
    },

    debouncedSaveLayout() {
      if (this.layoutUpdateTimeout) {
        clearTimeout(this.layoutUpdateTimeout)
      }

      this.layoutUpdateTimeout = setTimeout(() => {
        this.saveLayoutToServer()
      }, 1000) // Save after 1 second of no changes
    },

    async saveLayoutToServer() {
      if (!this.editMode) return

      try {
        await this.$axios.post(
          `/api/dashboard/enhanced/dashboard/${this.dashboard.id}/layout/`,
          {
            layout_data: this.layout,
          }
        )
      } catch (error) {
        console.error('Error saving dashboard layout:', error)
      }
    },

    getWidget(widgetId) {
      return this.widgets.find((widget) => widget.id.toString() === widgetId)
    },

    getWidgetComponent(widgetType) {
      const componentMap = {
        summary: 'SummaryWidget',
        kpi: 'KPIWidget',
        enhanced_chart: 'EnhancedChartWidget',
        chart: 'EnhancedChartWidget', // Fallback for existing chart widgets
      }

      return componentMap[widgetType] || 'SummaryWidget'
    },

    isWidgetLoading(widgetId) {
      // Check if widget data is loading
      const widget = this.getWidget(widgetId)
      if (!widget) return false

      // This would integrate with the store to check loading state
      return false
    },

    handleDeleteWidget(widget) {
      this.$emit('delete-widget', widget)

      // Remove from layout
      this.layout = this.layout.filter(
        (item) => item.i !== widget.id.toString()
      )
      this.saveLayoutToServer()
    },

    addWidgetToLayout(widget) {
      // Find a good position for the new widget
      const maxY = Math.max(...this.layout.map((item) => item.y + item.h), 0)

      const newItem = {
        i: widget.id.toString(),
        x: 0,
        y: maxY,
        w: 6,
        h: 4,
        minW: 3,
        minH: 2,
        widgetType: widget.type,
      }

      this.layout.push(newItem)
      this.saveLayoutToServer()
    },

    // Grid calculations
    calculateGridDimensions() {
      const container = this.$el?.querySelector('.dashboard-grid')
      if (container) {
        this.containerWidth = container.clientWidth
        this.containerHeight = container.clientHeight
        this.cellWidth =
          (this.containerWidth - (this.gridColumns - 1) * 10) / this.gridColumns
      }
    },

    getItemStyle(item) {
      const x = item.x * (this.cellWidth + 10)
      const y = item.y * (this.rowHeight + 10)
      const width = item.w * this.cellWidth + (item.w - 1) * 10
      const height = item.h * this.rowHeight + (item.h - 1) * 10

      return {
        position: 'absolute',
        left: `${x}px`,
        top: `${y}px`,
        width: `${width}px`,
        height: `${height}px`,
        zIndex: this.draggedItem === item.i ? 1000 : 1,
      }
    },

    // Drag and drop methods
    startDrag(event, item) {
      if (!this.editMode) return

      event.preventDefault()
      this.isDragging = true
      this.draggedItem = item.i

      const clientX = event.clientX || event.touches[0].clientX
      const clientY = event.clientY || event.touches[0].clientY

      const rect = event.currentTarget.getBoundingClientRect()
      this.dragOffset = {
        x: clientX - rect.left,
        y: clientY - rect.top,
      }
    },

    startResize(event, item) {
      if (!this.editMode) return

      event.preventDefault()
      this.isResizing = true
      this.resizedItem = item.i
    },

    handleMouseMove(event) {
      if (this.isDragging) {
        this.updateDragPosition(event.clientX, event.clientY)
      } else if (this.isResizing) {
        this.updateResizePosition(event.clientX, event.clientY)
      }
    },

    handleTouchMove(event) {
      if (this.isDragging || this.isResizing) {
        event.preventDefault()
        const touch = event.touches[0]
        if (this.isDragging) {
          this.updateDragPosition(touch.clientX, touch.clientY)
        } else if (this.isResizing) {
          this.updateResizePosition(touch.clientX, touch.clientY)
        }
      }
    },

    handleMouseUp() {
      this.endDragOrResize()
    },

    handleTouchEnd() {
      this.endDragOrResize()
    },

    updateDragPosition(clientX, clientY) {
      if (!this.draggedItem) return

      const container = this.$el?.querySelector('.dashboard-grid')
      if (!container) return

      const containerRect = container.getBoundingClientRect()
      const x = clientX - containerRect.left - this.dragOffset.x
      const y = clientY - containerRect.top - this.dragOffset.y

      // Convert pixel position to grid position
      const gridX = Math.round(x / (this.cellWidth + 10))
      const gridY = Math.round(y / (this.rowHeight + 10))

      // Update item position
      const item = this.layout.find((item) => item.i === this.draggedItem)
      if (item) {
        item.x = Math.max(0, Math.min(gridX, this.gridColumns - item.w))
        item.y = Math.max(0, gridY)
      }
    },

    updateResizePosition(clientX, clientY) {
      if (!this.resizedItem) return

      const container = this.$el?.querySelector('.dashboard-grid')
      if (!container) return

      const item = this.layout.find((item) => item.i === this.resizedItem)
      if (!item) return

      const containerRect = container.getBoundingClientRect()
      const x = clientX - containerRect.left
      const y = clientY - containerRect.top

      // Calculate new size based on mouse position
      const itemLeft = item.x * (this.cellWidth + 10)
      const itemTop = item.y * (this.rowHeight + 10)

      const newWidth = Math.max(
        item.minW || 2,
        Math.round((x - itemLeft) / (this.cellWidth + 10))
      )
      const newHeight = Math.max(
        item.minH || 2,
        Math.round((y - itemTop) / (this.rowHeight + 10))
      )

      item.w = Math.min(newWidth, this.gridColumns - item.x)
      item.h = newHeight
    },

    endDragOrResize() {
      if (this.isDragging || this.isResizing) {
        this.isDragging = false
        this.isResizing = false
        this.draggedItem = null
        this.resizedItem = null

        // Save layout after drag/resize
        this.debouncedSaveLayout()
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.drag-drop-dashboard {
  position: relative;
  min-height: 400px;
}

.dashboard-grid {
  position: relative;
  width: 100%;
  min-height: 400px;

  &--edit-mode {
    background: linear-gradient(
      90deg,
      transparent 0%,
      transparent calc(100% / 12 - 1px),
      rgba(81, 144, 239, 0.1) calc(100% / 12 - 1px),
      rgba(81, 144, 239, 0.1) calc(100% / 12),
      transparent calc(100% / 12)
    );
    background-size: calc(100% / 12 * 12) 60px;
  }
}

.dashboard-grid-item {
  background: #fff;
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
  cursor: default;

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  &--edit-mode {
    cursor: move;

    &:hover {
      border-color: #5190ef;
      box-shadow: 0 4px 12px rgba(81, 144, 239, 0.2);
    }
  }

  &--dragging {
    z-index: 1000;
    transform: rotate(2deg);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    opacity: 0.9;
  }

  &__content {
    height: 100%;
    width: 100%;
    overflow: hidden;
    border-radius: 8px;
    pointer-events: auto;
  }

  &__drag-handle {
    position: absolute;
    top: 8px;
    left: 8px;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #666;
    cursor: move;
    opacity: 0;
    transition: opacity 0.2s ease;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 4px;
    z-index: 10;

    &:hover {
      opacity: 1;
      color: #5190ef;
      background: rgba(81, 144, 239, 0.1);
    }
  }

  &__resize-handle {
    position: absolute;
    bottom: 4px;
    right: 4px;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #666;
    cursor: se-resize;
    opacity: 0;
    transition: opacity 0.2s ease;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 4px;
    z-index: 10;

    &:hover {
      opacity: 1;
      color: #5190ef;
      background: rgba(81, 144, 239, 0.1);
    }
  }

  &--edit-mode:hover &__drag-handle,
  &--edit-mode:hover &__resize-handle {
    opacity: 0.7;
  }
}

.drag-drop-dashboard__empty {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  background: linear-gradient(
    135deg,
    rgba(81, 144, 239, 0.05) 0%,
    rgba(81, 144, 239, 0.02) 100%
  );
  border: 2px dashed rgba(81, 144, 239, 0.2);
  border-radius: 12px;

  &__content {
    text-align: center;
    max-width: 400px;
    padding: 40px 20px;
  }

  &__icon {
    font-size: 64px;
    color: rgba(81, 144, 239, 0.3);
    margin-bottom: 24px;
  }

  &__title {
    font-size: 24px;
    font-weight: 600;
    color: #333;
    margin-bottom: 12px;
  }

  &__description {
    font-size: 16px;
    color: #666;
    margin-bottom: 32px;
    line-height: 1.5;
  }
}

// Custom grid system styles
.dashboard-grid {
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    pointer-events: none;
    z-index: 0;
  }
}

@media (max-width: 768px) {
  .drag-drop-dashboard__empty {
    min-height: 300px;

    &__content {
      padding: 30px 15px;
    }

    &__icon {
      font-size: 48px;
      margin-bottom: 20px;
    }

    &__title {
      font-size: 20px;
      margin-bottom: 10px;
    }

    &__description {
      font-size: 14px;
      margin-bottom: 24px;
    }
  }
}
</style>
