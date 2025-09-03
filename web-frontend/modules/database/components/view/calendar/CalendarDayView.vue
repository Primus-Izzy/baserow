<template>
  <div class="calendar-day-view">
    <!-- Day header -->
    <div class="calendar-day-view__header">
      <div class="calendar-day-view__time-column-header"></div>
      <div class="calendar-day-view__day-header">
        <div class="calendar-day-view__day-name">
          {{ currentDate.toLocaleDateString(undefined, { weekday: 'long' }) }}
        </div>
        <div class="calendar-day-view__day-number">
          {{ currentDate.getDate() }}
        </div>
        <div class="calendar-day-view__day-month">
          {{
            currentDate.toLocaleDateString(undefined, {
              month: 'long',
              year: 'numeric',
            })
          }}
        </div>
      </div>
    </div>

    <!-- Time grid -->
    <div class="calendar-day-view__grid" ref="grid">
      <!-- Time column -->
      <div class="calendar-day-view__time-column">
        <div
          v-for="hour in hours"
          :key="hour"
          class="calendar-day-view__time-slot"
        >
          <span class="calendar-day-view__time-label">
            {{ formatHour(hour) }}
          </span>
        </div>
      </div>

      <!-- Day column -->
      <div
        class="calendar-day-view__day-column"
        @click="handleDayClick"
        @dragover.prevent="handleDragOver"
        @drop="handleDrop"
      >
        <!-- Hour slots -->
        <div
          v-for="hour in hours"
          :key="hour"
          class="calendar-day-view__hour-slot"
          :data-hour="hour"
        >
          <!-- 15-minute markers -->
          <div class="calendar-day-view__quarter-hour"></div>
          <div class="calendar-day-view__quarter-hour"></div>
          <div class="calendar-day-view__quarter-hour"></div>
        </div>

        <!-- Events -->
        <CalendarEvent
          v-for="event in dayEvents"
          :key="event.id || `${event.pattern_id}-${event.date}`"
          :event="event"
          :fields="fields"
          :view="view"
          :table="table"
          :database="database"
          :read-only="readOnly"
          :store-prefix="storePrefix"
          :style="getEventStyle(event)"
          class="calendar-day-view__event"
          @click="$emit('event-click', $event)"
          @dragstart="handleEventDragStart(event, $event)"
        />

        <!-- Current time indicator -->
        <div
          v-if="isToday"
          class="calendar-day-view__current-time"
          :style="currentTimeStyle"
        >
          <div class="calendar-day-view__current-time-line"></div>
          <div class="calendar-day-view__current-time-dot"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CalendarEvent from './CalendarEvent'

export default {
  name: 'CalendarDayView',
  components: {
    CalendarEvent,
  },
  props: {
    events: {
      type: Array,
      required: true,
    },
    currentDate: {
      type: Date,
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
      hours: Array.from({ length: 24 }, (_, i) => i),
      draggedEvent: null,
      currentTime: new Date(),
      timeUpdateInterval: null,
    }
  },
  computed: {
    isToday() {
      const today = new Date()
      return (
        this.currentDate.getDate() === today.getDate() &&
        this.currentDate.getMonth() === today.getMonth() &&
        this.currentDate.getFullYear() === today.getFullYear()
      )
    },

    dayEvents() {
      const dateStr = this.currentDate.toISOString().split('T')[0]
      return this.events.filter((event) => {
        if (!event.date) return false
        const eventDate = new Date(event.date).toISOString().split('T')[0]
        return eventDate === dateStr
      })
    },

    currentTimeStyle() {
      if (!this.isToday) return {}

      const now = new Date()
      const hour = now.getHours()
      const minutes = now.getMinutes()
      const top = hour * 80 + (minutes * 80) / 60 // 80px per hour

      return {
        top: `${top}px`,
      }
    },
  },
  mounted() {
    // Update current time every minute
    this.timeUpdateInterval = setInterval(() => {
      this.currentTime = new Date()
    }, 60000)

    // Scroll to current time if today
    if (this.isToday) {
      this.$nextTick(() => {
        this.scrollToCurrentTime()
      })
    }
  },
  beforeDestroy() {
    if (this.timeUpdateInterval) {
      clearInterval(this.timeUpdateInterval)
    }
  },
  methods: {
    formatHour(hour) {
      const date = new Date()
      date.setHours(hour, 0, 0, 0)
      return date.toLocaleTimeString(undefined, {
        hour: 'numeric',
        hour12: true,
      })
    },

    scrollToCurrentTime() {
      const now = new Date()
      const hour = now.getHours()
      const scrollTop = Math.max(0, (hour - 2) * 80) // Scroll to 2 hours before current time

      if (this.$refs.grid) {
        this.$refs.grid.scrollTop = scrollTop
      }
    },

    getEventStyle(event) {
      let top = 0
      let height = 80 // Default height (1 hour)
      let width = '95%'
      let left = '2.5%'

      if (event.date && event.date.includes('T')) {
        // Has time information
        const eventTime = new Date(event.date)
        const hour = eventTime.getHours()
        const minutes = eventTime.getMinutes()

        top = hour * 80 + (minutes * 80) / 60 // 80px per hour

        // If there's an end time, calculate duration
        if (event.end_date && event.end_date.includes('T')) {
          const endTime = new Date(event.end_date)
          const duration = (endTime - eventTime) / (1000 * 60) // Duration in minutes
          height = Math.max(20, (duration * 80) / 60) // Minimum 20px height
        }
      } else {
        // All-day event - position at top
        top = 0
        height = 30
        width = '100%'
        left = '0'
      }

      // Handle overlapping events
      const overlappingEvents = this.getOverlappingEvents(event)
      if (overlappingEvents.length > 1) {
        const eventIndex = overlappingEvents.findIndex((e) => e.id === event.id)
        const eventWidth = 95 / overlappingEvents.length
        width = `${eventWidth}%`
        left = `${2.5 + eventIndex * eventWidth}%`
      }

      return {
        position: 'absolute',
        top: `${top}px`,
        height: `${height}px`,
        width,
        left,
        zIndex: 10,
      }
    },

    getOverlappingEvents(targetEvent) {
      if (!targetEvent.date || !targetEvent.date.includes('T')) {
        return [targetEvent]
      }

      const targetStart = new Date(targetEvent.date)
      const targetEnd = targetEvent.end_date
        ? new Date(targetEvent.end_date)
        : new Date(targetStart.getTime() + 60 * 60 * 1000)

      return this.dayEvents.filter((event) => {
        if (
          event.id === targetEvent.id ||
          !event.date ||
          !event.date.includes('T')
        ) {
          return event.id === targetEvent.id
        }

        const eventStart = new Date(event.date)
        const eventEnd = event.end_date
          ? new Date(event.end_date)
          : new Date(eventStart.getTime() + 60 * 60 * 1000)

        // Check for overlap
        return targetStart < eventEnd && targetEnd > eventStart
      })
    },

    handleDayClick(event) {
      if (this.readOnly) return

      // Calculate the time based on click position
      const rect = event.currentTarget.getBoundingClientRect()
      const y = event.clientY - rect.top
      const hour = Math.floor(y / 80) // 80px per hour
      const minutes = Math.round((((y % 80) / 80) * 60) / 15) * 15 // Round to 15-minute intervals

      const clickDate = new Date(this.currentDate)
      clickDate.setHours(hour, minutes, 0, 0)

      this.$emit('date-click', clickDate)
    },

    handleEventDragStart(event, dragEvent) {
      if (this.readOnly) {
        dragEvent.preventDefault()
        return
      }

      this.draggedEvent = event
      dragEvent.dataTransfer.effectAllowed = 'move'
      dragEvent.dataTransfer.setData(
        'text/plain',
        JSON.stringify({
          eventId: event.id,
          originalDate: event.date,
        })
      )
    },

    handleDragOver(event) {
      if (this.readOnly || !this.draggedEvent) return

      event.preventDefault()
      event.dataTransfer.dropEffect = 'move'
    },

    handleDrop(event) {
      event.preventDefault()

      if (this.readOnly || !this.draggedEvent) return

      // Calculate the time based on drop position
      const rect = event.currentTarget.getBoundingClientRect()
      const y = event.clientY - rect.top
      const hour = Math.floor(y / 80)
      const minutes = Math.round((((y % 80) / 80) * 60) / 15) * 15

      const dropDate = new Date(this.currentDate)
      dropDate.setHours(hour, minutes, 0, 0)

      this.$emit('event-move', this.draggedEvent, dropDate)
      this.draggedEvent = null
    },
  },
}
</script>

<style lang="scss" scoped>
.calendar-day-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;

  &__header {
    display: grid;
    grid-template-columns: 80px 1fr;
    border-bottom: 1px solid $palette-neutral-200;
    background-color: $palette-neutral-50;
    flex-shrink: 0;
  }

  &__time-column-header {
    border-right: 1px solid $palette-neutral-200;
  }

  &__day-header {
    padding: 16px;
    text-align: center;
  }

  &__day-name {
    font-size: 14px;
    font-weight: 600;
    color: $color-neutral-600;
    text-transform: uppercase;
    margin-bottom: 4px;
  }

  &__day-number {
    font-size: 32px;
    font-weight: 700;
    color: $color-neutral-800;
    margin-bottom: 4px;
  }

  &__day-month {
    font-size: 14px;
    color: $color-neutral-600;
  }

  &__grid {
    display: grid;
    grid-template-columns: 80px 1fr;
    flex: 1;
    overflow-y: auto;
    min-height: 0;
  }

  &__time-column {
    border-right: 1px solid $palette-neutral-200;
    background-color: $color-neutral-25;
  }

  &__time-slot {
    height: 80px;
    display: flex;
    align-items: flex-start;
    justify-content: center;
    padding-top: 8px;
    border-bottom: 1px solid $color-neutral-100;
  }

  &__time-label {
    font-size: 12px;
    color: $color-neutral-600;
    font-weight: 500;
  }

  &__day-column {
    position: relative;
    cursor: pointer;

    &:hover {
      background-color: $color-neutral-25;
    }
  }

  &__hour-slot {
    height: 80px;
    border-bottom: 1px solid $color-neutral-100;
    position: relative;

    &:hover {
      background-color: $palette-neutral-50;
    }
  }

  &__quarter-hour {
    height: 20px;
    border-bottom: 1px solid $palette-neutral-50;

    &:last-child {
      border-bottom: none;
    }
  }

  &__event {
    border-radius: 4px;
    overflow: hidden;
  }

  &__current-time {
    position: absolute;
    left: 0;
    right: 0;
    z-index: 20;
    pointer-events: none;
  }

  &__current-time-line {
    height: 2px;
    background-color: $color-error-600;
    position: relative;
  }

  &__current-time-dot {
    position: absolute;
    left: -6px;
    top: -5px;
    width: 12px;
    height: 12px;
    background-color: $color-error-600;
    border-radius: 50%;
  }
}

@media (max-width: 768px) {
  .calendar-day-view {
    &__header {
      grid-template-columns: 60px 1fr;
    }

    &__day-header {
      padding: 12px;
    }

    &__day-name {
      font-size: 12px;
    }

    &__day-number {
      font-size: 24px;
    }

    &__day-month {
      font-size: 12px;
    }

    &__grid {
      grid-template-columns: 60px 1fr;
    }

    &__time-label {
      font-size: 10px;
    }

    &__hour-slot {
      height: 60px;
    }

    &__time-slot {
      height: 60px;
    }

    &__quarter-hour {
      height: 15px;
    }
  }
}
</style>
