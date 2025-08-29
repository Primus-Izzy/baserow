<template>
  <div class="timeline-view-mobile">
    <!-- Mobile Header -->
    <div class="mobile-header">
      <div class="header-actions">
        <button 
          class="action-button"
          @click="$emit('toggle-sidebar')"
        >
          <i class="fas fa-bars"></i>
        </button>
        <h1 class="header-title">{{ view.name }}</h1>
        <button 
          class="action-button"
          @click="$emit('show-options')"
        >
          <i class="fas fa-ellipsis-v"></i>
        </button>
      </div>
    </div>

    <!-- Mobile Content -->
    <div class="mobile-content">
      <!-- Timeline Controls -->
      <div class="timeline-controls">
        <div class="zoom-controls">
          <button
            v-for="zoom in zoomLevels"
            :key="zoom.value"
            class="zoom-btn touch-feedback"
            :class="{ active: currentZoom === zoom.value }"
            @click="setZoom(zoom.value)"
          >
            {{ zoom.label }}
          </button>
        </div>
        
        <div class="navigation-controls">
          <button 
            class="nav-btn touch-feedback"
            @click="previousPeriod"
          >
            <i class="fas fa-chevron-left"></i>
          </button>
          
          <div class="current-period">
            <span class="period-text">{{ currentPeriodText }}</span>
          </div>
          
          <button 
            class="nav-btn touch-feedback"
            @click="nextPeriod"
          >
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>
      </div>

      <!-- Timeline Content -->
      <div 
        class="timeline-content"
        @touchstart="handleTouchStart"
        @touchmove="handleTouchMove"
        @touchend="handleTouchEnd"
      >
        <!-- Timeline Header -->
        <div class="timeline-header">
          <div class="task-column-header">
            <span>Tasks</span>
          </div>
          <div 
            class="timeline-scale"
            :style="{ width: `${timelineWidth}px` }"
          >
            <div
              v-for="period in timePeriods"
              :key="period.key"
              class="time-period"
              :style="{ width: `${periodWidth}px` }"
            >
              <span class="period-label">{{ period.label }}</span>
            </div>
          </div>
        </div>

        <!-- Timeline Body -->
        <div class="timeline-body">
          <div class="tasks-list">
            <div
              v-for="task in tasks"
              :key="task.id"
              class="task-row"
              :class="{ 
                'selected': selectedTasks.has(task.id),
                'has-dependencies': task.dependencies.length > 0
              }"
            >
              <!-- Task Info -->
              <div class="task-info">
                <div class="task-header">
                  <button 
                    class="task-toggle"
                    v-if="task.subtasks && task.subtasks.length > 0"
                    @click="toggleTaskExpansion(task)"
                  >
                    <i 
                      class="fas"
                      :class="task.expanded ? 'fa-chevron-down' : 'fa-chevron-right'"
                    ></i>
                  </button>
                  
                  <span class="task-title">{{ task.title }}</span>
                  
                  <button 
                    class="task-menu-btn"
                    @click="showTaskMenu(task)"
                  >
                    <i class="fas fa-ellipsis-v"></i>
                  </button>
                </div>
                
                <div class="task-meta">
                  <span v-if="task.assignee" class="task-assignee">
                    <i class="fas fa-user"></i>
                    {{ task.assignee }}
                  </span>
                  <span class="task-duration">
                    {{ formatDuration(task.start_date, task.end_date) }}
                  </span>
                </div>
              </div>

              <!-- Timeline Bar -->
              <div 
                class="timeline-bar-container"
                :style="{ width: `${timelineWidth}px` }"
              >
                <div
                  class="timeline-bar"
                  :style="{
                    left: `${getTaskLeft(task)}px`,
                    width: `${getTaskWidth(task)}px`,
                    backgroundColor: getTaskColor(task)
                  }"
                  @click="selectTask(task)"
                  @touchstart="handleTaskTouchStart(task, $event)"
                >
                  <div class="bar-content">
                    <span class="bar-title">{{ task.title }}</span>
                    <div class="bar-progress" :style="{ width: `${task.progress || 0}%` }"></div>
                  </div>
                  
                  <!-- Resize Handles -->
                  <div 
                    class="resize-handle left"
                    @touchstart="startResize(task, 'start', $event)"
                  ></div>
                  <div 
                    class="resize-handle right"
                    @touchstart="startResize(task, 'end', $event)"
                  ></div>
                </div>

                <!-- Dependencies -->
                <svg 
                  v-if="task.dependencies.length > 0"
                  class="dependency-lines"
                  :style="{ width: `${timelineWidth}px`, height: '100%' }"
                >
                  <path
                    v-for="dep in task.dependencies"
                    :key="dep.id"
                    :d="getDependencyPath(task, dep)"
                    stroke="var(--color-primary)"
                    stroke-width="2"
                    fill="none"
                    marker-end="url(#arrowhead)"
                  />
                </svg>

                <!-- Milestones -->
                <div
                  v-for="milestone in getTaskMilestones(task)"
                  :key="milestone.id"
                  class="milestone"
                  :style="{
                    left: `${getMilestoneLeft(milestone)}px`,
                    backgroundColor: milestone.color
                  }"
                  @click="selectMilestone(milestone)"
                >
                  <i class="fas fa-flag"></i>
                  <span class="milestone-label">{{ milestone.title }}</span>
                </div>
              </div>

              <!-- Subtasks -->
              <div v-if="task.expanded && task.subtasks" class="subtasks">
                <div
                  v-for="subtask in task.subtasks"
                  :key="subtask.id"
                  class="subtask-row"
                >
                  <div class="subtask-info">
                    <span class="subtask-title">{{ subtask.title }}</span>
                    <span class="subtask-duration">
                      {{ formatDuration(subtask.start_date, subtask.end_date) }}
                    </span>
                  </div>
                  
                  <div 
                    class="timeline-bar-container"
                    :style="{ width: `${timelineWidth}px` }"
                  >
                    <div
                      class="timeline-bar subtask-bar"
                      :style="{
                        left: `${getTaskLeft(subtask)}px`,
                        width: `${getTaskWidth(subtask)}px`,
                        backgroundColor: getTaskColor(subtask)
                      }"
                      @click="selectTask(subtask)"
                    >
                      <div class="bar-content">
                        <span class="bar-title">{{ subtask.title }}</span>
                        <div class="bar-progress" :style="{ width: `${subtask.progress || 0}%` }"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Today Indicator -->
        <div 
          class="today-indicator"
          :style="{ left: `${getTodayPosition()}px` }"
        >
          <div class="today-line"></div>
          <div class="today-label">Today</div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="quick-actions">
        <button 
          class="quick-action-btn touch-feedback"
          @click="addTask"
        >
          <i class="fas fa-plus"></i>
          <span>Add Task</span>
        </button>
        <button 
          class="quick-action-btn touch-feedback"
          @click="showCriticalPath"
        >
          <i class="fas fa-route"></i>
          <span>Critical Path</span>
        </button>
        <button 
          class="quick-action-btn touch-feedback"
          @click="showFilters"
        >
          <i class="fas fa-filter"></i>
          <span>Filter</span>
        </button>
      </div>
    </div>

    <!-- Task Details Modal -->
    <div v-if="selectedTask" class="mobile-modal">
      <div class="modal-header">
        <h3 class="modal-title">Task Details</h3>
        <button class="close-button" @click="selectedTask = null">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <div class="modal-content">
        <div class="task-detail">
          <h4>{{ selectedTask.title }}</h4>
          <div class="task-info-grid">
            <div class="info-item">
              <label>Start Date</label>
              <span>{{ formatDate(selectedTask.start_date) }}</span>
            </div>
            <div class="info-item">
              <label>End Date</label>
              <span>{{ formatDate(selectedTask.end_date) }}</span>
            </div>
            <div class="info-item">
              <label>Duration</label>
              <span>{{ formatDuration(selectedTask.start_date, selectedTask.end_date) }}</span>
            </div>
            <div class="info-item">
              <label>Progress</label>
              <span>{{ selectedTask.progress || 0 }}%</span>
            </div>
            <div v-if="selectedTask.assignee" class="info-item">
              <label>Assignee</label>
              <span>{{ selectedTask.assignee }}</span>
            </div>
            <div v-if="selectedTask.dependencies.length > 0" class="info-item">
              <label>Dependencies</label>
              <span>{{ selectedTask.dependencies.length }} tasks</span>
            </div>
          </div>
          
          <div class="task-actions">
            <button 
              class="action-btn edit-btn"
              @click="editTask(selectedTask)"
            >
              <i class="fas fa-edit"></i>
              Edit
            </button>
            <button 
              class="action-btn dependency-btn"
              @click="manageDependencies(selectedTask)"
            >
              <i class="fas fa-link"></i>
              Dependencies
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile Navigation -->
    <div class="mobile-nav">
      <div class="nav-item" :class="{ active: currentTab === 'timeline' }">
        <i class="icon fas fa-chart-gantt"></i>
        <span>Timeline</span>
      </div>
      <div class="nav-item" :class="{ active: currentTab === 'tasks' }">
        <i class="icon fas fa-tasks"></i>
        <span>Tasks</span>
      </div>
      <div class="nav-item" :class="{ active: currentTab === 'settings' }">
        <i class="icon fas fa-cog"></i>
        <span>Settings</span>
      </div>
    </div>

    <!-- SVG Definitions -->
    <svg style="position: absolute; width: 0; height: 0;">
      <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" 
                refX="9" refY="3.5" orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" fill="var(--color-primary)" />
        </marker>
      </defs>
    </svg>
  </div>
</template>

<script>
import mobileResponsive from '@baserow/modules/core/mixins/mobileResponsive'

export default {
  name: 'TimelineViewMobile',
  mixins: [mobileResponsive],
  props: {
    view: {
      type: Object,
      required: true
    },
    tasks: {
      type: Array,
      default: () => []
    },
    fields: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      currentZoom: 'week',
      currentDate: new Date(),
      selectedTask: null,
      selectedTasks: new Set(),
      currentTab: 'timeline',
      resizing: null,
      zoomLevels: [
        { value: 'day', label: 'Day' },
        { value: 'week', label: 'Week' },
        { value: 'month', label: 'Month' },
        { value: 'quarter', label: 'Quarter' }
      ],
      timelineWidth: 800,
      periodWidth: 100
    }
  },
  computed: {
    currentPeriodText() {
      const options = { year: 'numeric', month: 'long' }
      if (this.currentZoom === 'day') {
        options.day = 'numeric'
      }
      return this.currentDate.toLocaleDateString('en-US', options)
    },
    
    timePeriods() {
      const periods = []
      const startDate = this.getTimelineStartDate()
      const periodsCount = Math.ceil(this.timelineWidth / this.periodWidth)
      
      for (let i = 0; i < periodsCount; i++) {
        const periodDate = new Date(startDate)
        
        if (this.currentZoom === 'day') {
          periodDate.setDate(startDate.getDate() + i)
          periods.push({
            key: `day-${i}`,
            label: periodDate.getDate().toString(),
            date: new Date(periodDate)
          })
        } else if (this.currentZoom === 'week') {
          periodDate.setDate(startDate.getDate() + (i * 7))
          periods.push({
            key: `week-${i}`,
            label: `W${this.getWeekNumber(periodDate)}`,
            date: new Date(periodDate)
          })
        } else if (this.currentZoom === 'month') {
          periodDate.setMonth(startDate.getMonth() + i)
          periods.push({
            key: `month-${i}`,
            label: periodDate.toLocaleDateString('en-US', { month: 'short' }),
            date: new Date(periodDate)
          })
        }
      }
      
      return periods
    }
  },
  methods: {
    setZoom(zoom) {
      this.currentZoom = zoom
      this.updateTimelineWidth()
    },
    
    previousPeriod() {
      const newDate = new Date(this.currentDate)
      if (this.currentZoom === 'day') {
        newDate.setDate(newDate.getDate() - 7)
      } else if (this.currentZoom === 'week') {
        newDate.setDate(newDate.getDate() - 28)
      } else if (this.currentZoom === 'month') {
        newDate.setMonth(newDate.getMonth() - 3)
      }
      this.currentDate = newDate
    },
    
    nextPeriod() {
      const newDate = new Date(this.currentDate)
      if (this.currentZoom === 'day') {
        newDate.setDate(newDate.getDate() + 7)
      } else if (this.currentZoom === 'week') {
        newDate.setDate(newDate.getDate() + 28)
      } else if (this.currentZoom === 'month') {
        newDate.setMonth(newDate.getMonth() + 3)
      }
      this.currentDate = newDate
    },
    
    getTimelineStartDate() {
      const startDate = new Date(this.currentDate)
      if (this.currentZoom === 'week') {
        startDate.setDate(startDate.getDate() - startDate.getDay())
      } else if (this.currentZoom === 'month') {
        startDate.setDate(1)
      }
      return startDate
    },
    
    updateTimelineWidth() {
      // Adjust timeline width based on screen size and zoom level
      const baseWidth = this.screenWidth - 200 // Account for task column
      const multiplier = {
        day: 2,
        week: 1.5,
        month: 1,
        quarter: 0.8
      }
      this.timelineWidth = Math.max(baseWidth, 600) * multiplier[this.currentZoom]
    },
    
    getTaskLeft(task) {
      const startDate = this.getTimelineStartDate()
      const taskStart = new Date(task.start_date)
      const daysDiff = Math.floor((taskStart - startDate) / (1000 * 60 * 60 * 24))
      
      if (this.currentZoom === 'day') {
        return daysDiff * this.periodWidth
      } else if (this.currentZoom === 'week') {
        return (daysDiff / 7) * this.periodWidth
      } else if (this.currentZoom === 'month') {
        return (daysDiff / 30) * this.periodWidth
      }
      return 0
    },
    
    getTaskWidth(task) {
      const taskStart = new Date(task.start_date)
      const taskEnd = new Date(task.end_date)
      const duration = Math.floor((taskEnd - taskStart) / (1000 * 60 * 60 * 24))
      
      if (this.currentZoom === 'day') {
        return Math.max(duration * this.periodWidth, 20)
      } else if (this.currentZoom === 'week') {
        return Math.max((duration / 7) * this.periodWidth, 20)
      } else if (this.currentZoom === 'month') {
        return Math.max((duration / 30) * this.periodWidth, 20)
      }
      return 20
    },
    
    getTaskColor(task) {
      const colors = {
        'not-started': '#e0e0e0',
        'in-progress': '#2196f3',
        'completed': '#4caf50',
        'overdue': '#f44336'
      }
      return colors[task.status] || colors['not-started']
    },
    
    getTodayPosition() {
      const startDate = this.getTimelineStartDate()
      const today = new Date()
      const daysDiff = Math.floor((today - startDate) / (1000 * 60 * 60 * 24))
      
      if (this.currentZoom === 'day') {
        return daysDiff * this.periodWidth
      } else if (this.currentZoom === 'week') {
        return (daysDiff / 7) * this.periodWidth
      } else if (this.currentZoom === 'month') {
        return (daysDiff / 30) * this.periodWidth
      }
      return 0
    },
    
    selectTask(task) {
      this.selectedTask = task
    },
    
    toggleTaskExpansion(task) {
      task.expanded = !task.expanded
    },
    
    handleTaskTouchStart(task, event) {
      this.handleLongPress(event, () => {
        this.toggleTaskSelection(task)
      })
    },
    
    toggleTaskSelection(task) {
      if (this.selectedTasks.has(task.id)) {
        this.selectedTasks.delete(task.id)
      } else {
        this.selectedTasks.add(task.id)
      }
      this.$emit('selection-change', Array.from(this.selectedTasks))
    },
    
    startResize(task, handle, event) {
      this.resizing = { task, handle }
      event.preventDefault()
    },
    
    handleTouchMove(event) {
      if (this.resizing) {
        // Handle task resize
        return
      }
      
      // Handle timeline pan
      const touchX = event.touches[0].clientX
      const deltaX = touchX - this.touchStartX
      
      if (Math.abs(deltaX) > 50) {
        if (deltaX > 0) {
          this.previousPeriod()
        } else {
          this.nextPeriod()
        }
        this.touchStartX = touchX
      }
    },
    
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        year: 'numeric'
      })
    },
    
    formatDuration(startDate, endDate) {
      const start = new Date(startDate)
      const end = new Date(endDate)
      const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24))
      
      if (days === 1) return '1 day'
      if (days < 7) return `${days} days`
      if (days < 30) return `${Math.ceil(days / 7)} weeks`
      return `${Math.ceil(days / 30)} months`
    },
    
    getWeekNumber(date) {
      const startOfYear = new Date(date.getFullYear(), 0, 1)
      const pastDaysOfYear = (date - startOfYear) / 86400000
      return Math.ceil((pastDaysOfYear + startOfYear.getDay() + 1) / 7)
    },
    
    getTaskMilestones(task) {
      return task.milestones || []
    },
    
    getMilestoneLeft(milestone) {
      const startDate = this.getTimelineStartDate()
      const milestoneDate = new Date(milestone.date)
      const daysDiff = Math.floor((milestoneDate - startDate) / (1000 * 60 * 60 * 24))
      
      if (this.currentZoom === 'day') {
        return daysDiff * this.periodWidth
      } else if (this.currentZoom === 'week') {
        return (daysDiff / 7) * this.periodWidth
      } else if (this.currentZoom === 'month') {
        return (daysDiff / 30) * this.periodWidth
      }
      return 0
    },
    
    getDependencyPath(task, dependency) {
      // Simplified dependency line calculation
      const taskLeft = this.getTaskLeft(task)
      const depLeft = this.getTaskLeft(dependency)
      return `M ${depLeft} 20 L ${taskLeft} 20`
    },
    
    showTaskMenu(task) {
      this.$emit('show-task-menu', task)
    },
    
    selectMilestone(milestone) {
      this.$emit('select-milestone', milestone)
    },
    
    addTask() {
      this.$emit('add-task')
    },
    
    editTask(task) {
      this.$emit('edit-task', task)
      this.selectedTask = null
    },
    
    manageDependencies(task) {
      this.$emit('manage-dependencies', task)
      this.selectedTask = null
    },
    
    showCriticalPath() {
      this.$emit('show-critical-path')
    },
    
    showFilters() {
      this.$emit('show-filters')
    }
  },
  
  mounted() {
    this.updateTimelineWidth()
    
    // Handle swipe gestures
    this.$on('swipe-left', () => {
      this.nextPeriod()
    })
    
    this.$on('swipe-right', () => {
      this.previousPeriod()
    })
  }
}
</script>

<style lang="scss" scoped>
@import '@baserow/modules/core/assets/scss/components/mobile/responsive.scss';

.timeline-view-mobile {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-neutral-50);
}

.timeline-controls {
  background: var(--color-neutral-100);
  border-bottom: 1px solid var(--color-neutral-200);
  
  .zoom-controls {
    display: flex;
    padding: $mobile-spacing-sm $mobile-spacing-md;
    gap: $mobile-spacing-sm;
    
    .zoom-btn {
      @include touch-friendly;
      flex: 1;
      background: var(--color-neutral-50);
      border: 1px solid var(--color-neutral-300);
      border-radius: 6px;
      padding: $mobile-spacing-sm;
      font-size: $mobile-font-size-sm;
      
      &.active {
        background: var(--color-primary);
        color: white;
        border-color: var(--color-primary);
      }
    }
  }
  
  .navigation-controls {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: $mobile-spacing-sm $mobile-spacing-md;
    
    .nav-btn {
      @include touch-friendly;
      background: var(--color-neutral-50);
      border: 1px solid var(--color-neutral-300);
      border-radius: 50%;
      width: 36px;
      height: 36px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .current-period {
      flex: 1;
      text-align: center;
      
      .period-text {
        font-size: $mobile-font-size-md;
        font-weight: 600;
      }
    }
  }
}

.timeline-content {
  flex: 1;
  overflow: auto;
  position: relative;
  -webkit-overflow-scrolling: touch;
}

.timeline-header {
  display: flex;
  background: var(--color-neutral-100);
  border-bottom: 2px solid var(--color-neutral-300);
  position: sticky;
  top: 0;
  z-index: 10;
  
  .task-column-header {
    width: 200px;
    padding: $mobile-spacing-md;
    font-weight: 600;
    border-right: 1px solid var(--color-neutral-300);
    background: var(--color-neutral-200);
  }
  
  .timeline-scale {
    display: flex;
    
    .time-period {
      border-right: 1px solid var(--color-neutral-300);
      display: flex;
      align-items: center;
      justify-content: center;
      
      .period-label {
        font-size: $mobile-font-size-sm;
        font-weight: 600;
        color: var(--color-neutral-700);
      }
    }
  }
}

.timeline-body {
  .tasks-list {
    .task-row {
      display: flex;
      border-bottom: 1px solid var(--color-neutral-200);
      position: relative;
      
      &.selected {
        background: var(--color-primary-50);
      }
      
      .task-info {
        width: 200px;
        padding: $mobile-spacing-md;
        border-right: 1px solid var(--color-neutral-300);
        background: var(--color-neutral-50);
        
        .task-header {
          display: flex;
          align-items: center;
          margin-bottom: $mobile-spacing-sm;
          
          .task-toggle {
            @include touch-friendly;
            background: none;
            border: none;
            padding: 2px;
            margin-right: $mobile-spacing-sm;
            color: var(--color-neutral-600);
          }
          
          .task-title {
            flex: 1;
            font-size: $mobile-font-size-sm;
            font-weight: 600;
            line-height: 1.3;
          }
          
          .task-menu-btn {
            @include touch-friendly;
            background: none;
            border: none;
            padding: 2px;
            color: var(--color-neutral-600);
          }
        }
        
        .task-meta {
          display: flex;
          flex-direction: column;
          gap: 2px;
          
          .task-assignee,
          .task-duration {
            font-size: $mobile-font-size-xs;
            color: var(--color-neutral-600);
            
            .fas {
              margin-right: 4px;
            }
          }
        }
      }
      
      .timeline-bar-container {
        position: relative;
        height: 60px;
        
        .timeline-bar {
          position: absolute;
          top: 15px;
          height: 30px;
          border-radius: 4px;
          cursor: pointer;
          display: flex;
          align-items: center;
          color: white;
          font-size: $mobile-font-size-xs;
          
          &.subtask-bar {
            height: 20px;
            top: 20px;
          }
          
          .bar-content {
            padding: 0 8px;
            flex: 1;
            position: relative;
            
            .bar-title {
              font-weight: 600;
              white-space: nowrap;
              overflow: hidden;
              text-overflow: ellipsis;
            }
            
            .bar-progress {
              position: absolute;
              bottom: 0;
              left: 0;
              height: 3px;
              background: rgba(255, 255, 255, 0.8);
              border-radius: 0 0 4px 4px;
            }
          }
          
          .resize-handle {
            position: absolute;
            top: 0;
            bottom: 0;
            width: 8px;
            cursor: ew-resize;
            
            &.left {
              left: 0;
              border-left: 2px solid rgba(255, 255, 255, 0.8);
            }
            
            &.right {
              right: 0;
              border-right: 2px solid rgba(255, 255, 255, 0.8);
            }
          }
        }
        
        .dependency-lines {
          position: absolute;
          top: 0;
          left: 0;
          pointer-events: none;
        }
        
        .milestone {
          position: absolute;
          top: 10px;
          width: 20px;
          height: 20px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 10px;
          cursor: pointer;
          
          .milestone-label {
            position: absolute;
            top: 25px;
            left: 50%;
            transform: translateX(-50%);
            font-size: $mobile-font-size-xs;
            white-space: nowrap;
            color: var(--color-neutral-700);
          }
        }
      }
      
      .subtasks {
        .subtask-row {
          display: flex;
          background: var(--color-neutral-25);
          border-top: 1px solid var(--color-neutral-200);
          
          .subtask-info {
            width: 200px;
            padding: $mobile-spacing-sm $mobile-spacing-md;
            border-right: 1px solid var(--color-neutral-300);
            
            .subtask-title {
              font-size: $mobile-font-size-xs;
              font-weight: 500;
              display: block;
              margin-bottom: 2px;
            }
            
            .subtask-duration {
              font-size: 10px;
              color: var(--color-neutral-600);
            }
          }
        }
      }
    }
  }
}

.today-indicator {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 2px;
  z-index: 5;
  pointer-events: none;
  
  .today-line {
    width: 100%;
    height: 100%;
    background: var(--color-error);
  }
  
  .today-label {
    position: absolute;
    top: -20px;
    left: 50%;
    transform: translateX(-50%);
    font-size: $mobile-font-size-xs;
    color: var(--color-error);
    font-weight: 600;
    background: var(--color-neutral-50);
    padding: 2px 4px;
    border-radius: 4px;
  }
}

.quick-actions {
  display: flex;
  padding: $mobile-spacing-sm $mobile-spacing-md;
  gap: $mobile-spacing-sm;
  background: var(--color-neutral-100);
  border-top: 1px solid var(--color-neutral-200);
  
  .quick-action-btn {
    @include touch-friendly;
    display: flex;
    flex-direction: column;
    align-items: center;
    background: var(--color-neutral-50);
    border: 1px solid var(--color-neutral-300);
    border-radius: 8px;
    padding: $mobile-spacing-sm;
    flex: 1;
    
    .fas {
      margin-bottom: 4px;
      font-size: 16px;
    }
    
    span {
      font-size: $mobile-font-size-xs;
    }
  }
}

.mobile-modal {
  .task-detail {
    h4 {
      margin: 0 0 $mobile-spacing-md 0;
      font-size: $mobile-font-size-lg;
    }
    
    .task-info-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: $mobile-spacing-md;
      margin-bottom: $mobile-spacing-lg;
      
      .info-item {
        label {
          display: block;
          font-size: $mobile-font-size-xs;
          color: var(--color-neutral-600);
          margin-bottom: 2px;
          font-weight: 600;
        }
        
        span {
          font-size: $mobile-font-size-sm;
        }
      }
    }
    
    .task-actions {
      display: flex;
      gap: $mobile-spacing-md;
      
      .action-btn {
        @include touch-friendly;
        flex: 1;
        border: none;
        border-radius: 8px;
        padding: $mobile-spacing-sm $mobile-spacing-md;
        font-weight: 600;
        
        .fas {
          margin-right: 4px;
        }
        
        &.edit-btn {
          background: var(--color-primary);
          color: white;
        }
        
        &.dependency-btn {
          background: var(--color-neutral-200);
          color: var(--color-neutral-700);
        }
      }
    }
  }
}
</style>