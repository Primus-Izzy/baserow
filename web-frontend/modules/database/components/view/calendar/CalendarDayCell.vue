<template>
  <div
    class="calendar-day-cell"
    :class="{
      'calendar-day-cell--other-month': !isCurrentMonth,
      'calendar-day-cell--today': isToday,
      'calendar-day-cell--has-events': events.length > 0,
      'calendar-day-cell--dragging-over': isDraggingOver,
    }"
    @click="handleDateClick"
    @dragover.prevent="handleDragOver"
    @dragleave="handleDragLeave"
    @drop="handleDrop"
  >
    <!-- Day number -->
    <div class="calendar-day-cell__header">
      <span class="calendar-day-cell__day-number">
        {{ date.getDate() }}
      </span>
    </div>

    <!-- Events -->
    <div class="calendar-day-cell__events">
      <CalendarEvent
        v-for="(event, index) in visibleEvents"
        :key="event.id || `${event.pattern_id}-${event.date}`"
        :event="event"
        :fields="fields"
        :view="view"
        :table="table"
        :database="database"
        :read-only="readOnly"
        :store-prefix="storePrefix"
        :is-compact="true"
        @click="handleEventClick(event)"
        @dragstart="handleEventDragStart(event, $event)"
        @dragend="handleEventDragEnd"
      />
      
      <!-- More events indicator -->
      <div
        v-if="hiddenEventsCount > 0"
        class="calendar-day-cell__more-events"
        @click.stop="showAllEvents = !showAllEvents"
      >
        <span v-if="!showAllEvents">
          +{{ hiddenEventsCount }} {{ $t('calendarView.moreEvents') }}
        </span>
        <span v-else>
          {{ $t('calendarView.showLess') }}
        </span>
      </div>
    </div>

    <!-- Add event button (mobile) -->
    <button
      v-if="!readOnly && isMobile"
      class="calendar-day-cell__add-btn"
      @click.stop="handleAddEvent"
    >
      <i class="iconoir-plus"></i>
    </button>
  </div>
</template>

<script>
import CalendarEvent from './CalendarEvent'

export default {
  name: 'CalendarDayCell',
  components: {
    CalendarEvent,
  },
  props: {
    date: {
      type: Date,
      required: true,
    },
    isCurrentMonth: {
      type: Boolean,
      required: true,
    },
    isToday: {
      type: Boolean,
      required: true,
    },
    events: {
      type: Array,
      required: true,
    },
    fields: {
      type: Array,
      required: true,
    },
    view: {
      type: Object,
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
      required: true,
    },
    storePrefix: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      isDraggingOver: false,
      draggedEvent: null,
      showAllEvents: false,
      maxVisibleEvents: 3,
    }
  },
  computed: {
    isMobile() {
      return window.innerWidth <= 768
    },
    
    visibleEvents() {
      if (this.showAllEvents || this.events.length <= this.maxVisibleEvents) {
        return this.events
      }
      return this.events.slice(0, this.maxVisibleEvents)
    },
    
    hiddenEventsCount() {
      return Math.max(0, this.events.length - this.maxVisibleEvents)
    },
  },
  methods: {
    handleDateClick() {
      if (!this.readOnly) {
        this.$emit('date-click', this.date)
      }
    },
    
    handleEventClick(event) {
      this.$emit('event-click', event)
    },
    
    handleAddEvent() {
      this.$emit('event-create', this.date)
    },
    
    handleEventDragStart(event, dragEvent) {
      if (this.readOnly) {
        dragEvent.preventDefault()
        return
      }
      
      this.draggedEvent = event
      dragEvent.dataTransfer.effectAllowed = 'move'
      dragEvent.dataTransfer.setData('text/plain', JSON.stringify({
        eventId: event.id,
        originalDate: event.date,
      }))
      
      // Add visual feedback
      dragEvent.target.style.opacity = '0.5'
    },
    
    handleEventDragEnd(dragEvent) {
      dragEvent.target.style.opacity = '1'
      this.draggedEvent = null
    },
    
    handleDragOver(event) {
      if (this.readOnly || !this.draggedEvent) {
        return
      }
      
      event.preventDefault()
      event.dataTransfer.dropEffect = 'move'
      this.isDraggingOver = true
    },
    
    handleDragLeave() {
      this.isDraggingOver = false
    },
    
    handleDrop(event) {
      event.preventDefault()
      this.isDraggingOver = false
      
      if (this.readOnly || !this.draggedEvent) {
        return
      }
      
      try {
        const data = JSON.parse(event.dataTransfer.getData('text/plain'))
        const originalDate = new Date(data.originalDate)
        
        // Only move if the date is different
        if (originalDate.toDateString() !== this.date.toDateString()) {
          this.$emit('event-move', this.draggedEvent, this.date)
        }
      } catch (error) {
        console.error('Error parsing drag data:', error)
      }
      
      this.draggedEvent = null
    },
  },
}
</script>

<style lang="scss" scoped>
.calendar-day-cell {
  position: relative;
  border-right: 1px solid $color-neutral-200;
  border-bottom: 1px solid $color-neutral-200;
  background-color: $color-neutral-0;
  min-height: 120px;
  cursor: pointer;
  transition: background-color 0.2s ease;

  &:hover {
    background-color: $color-neutral-25;
  }

  &--other-month {
    background-color: $color-neutral-50;
    color: $color-neutral-400;

    .calendar-day-cell__day-number {
      color: $color-neutral-400;
    }
  }

  &--today {
    background-color: $color-primary-50;

    .calendar-day-cell__day-number {
      background-color: $color-primary-600;
      color: $color-neutral-0;
      border-radius: 50%;
      width: 24px;
      height: 24px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 600;
    }
  }

  &--dragging-over {
    background-color: $color-primary-100;
    border-color: $color-primary-300;
  }

  &__header {
    padding: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  &__day-number {
    font-size: 14px;
    font-weight: 500;
    color: $color-neutral-800;
  }

  &__events {
    padding: 0 4px 4px;
    display: flex;
    flex-direction: column;
    gap: 2px;
    max-height: calc(100% - 40px);
    overflow: hidden;
  }

  &__more-events {
    font-size: 11px;
    color: $color-neutral-600;
    cursor: pointer;
    padding: 2px 4px;
    border-radius: 2px;
    text-align: center;
    background-color: $color-neutral-100;
    transition: background-color 0.2s ease;

    &:hover {
      background-color: $color-neutral-200;
    }
  }

  &__add-btn {
    position: absolute;
    top: 8px;
    right: 8px;
    width: 20px;
    height: 20px;
    border: none;
    background-color: $color-primary-600;
    color: $color-neutral-0;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    opacity: 0;
    transition: opacity 0.2s ease;

    i {
      font-size: 12px;
    }
  }

  &:hover &__add-btn {
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .calendar-day-cell {
    min-height: 80px;

    &__header {
      padding: 4px;
    }

    &__day-number {
      font-size: 12px;
    }

    &__events {
      padding: 0 2px 2px;
    }

    &__add-btn {
      opacity: 1;
      width: 16px;
      height: 16px;
      top: 4px;
      right: 4px;

      i {
        font-size: 10px;
      }
    }
  }
}
</style>