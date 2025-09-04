<template>
  <div class="calendar-week-view">
    <!-- Time column and day headers -->
    <div class="calendar-week-view__header">
      <div class="calendar-week-view__time-column-header"></div>
      <div
        v-for="day in weekDays"
        :key="day.date.toISOString()"
        class="calendar-week-view__day-header"
        :class="{ 'calendar-week-view__day-header--today': day.isToday }"
      >
        <div class="calendar-week-view__day-name">{{ day.dayName }}</div>
        <div class="calendar-week-view__day-number">
          {{ day.date.getDate() }}
        </div>
      </div>
    </div>

    <!-- Time grid -->
    <div class="calendar-week-view__grid" ref="grid">
      <!-- Time column -->
      <div class="calendar-week-view__time-column">
        <div
          v-for="hour in hours"
          :key="hour"
          class="calendar-week-view__time-slot"
        >
          <span class="calendar-week-view__time-label">
            {{ formatHour(hour) }}
          </span>
        </div>
      </div>

      <!-- Day columns -->
      <div
        v-for="day in weekDays"
        :key="day.date.toISOString()"
        class="calendar-week-view__day-column"
        :class="{ 'calendar-week-view__day-column--today': day.isToday }"
        @click="handleDayClick(day.date, $event)"
        @dragover.prevent="handleDragOver"
        @drop="handleDrop(day.date, $event)"
      >
        <!-- Hour slots -->
        <div
          v-for="hour in hours"
          :key="hour"
          class="calendar-week-view__hour-slot"
          :data-hour="hour"
        ></div>

        <!-- Events -->
        <CalendarEvent
          v-for="event in getEventsForDay(day.date)"
          :key="event.id || `${event.pattern_id}-${event.date}`"
          :event="event"
          :fields="fields"
          :view="view"
          :table="table"
          :database="database"
          :read-only="readOnly"
          :store-prefix="storePrefix"
          :style="getEventStyle(event)"
          class="calendar-week-view__event"
          @click="$emit('event-click', $event)"
          @dragstart="handleEventDragStart(event, $event)"
        />
      </div>
    </div>
  </div>
</template>

<script>
import CalendarEvent from './CalendarEvent'

export default {
  name: 'CalendarWeekView',
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
    }
  },
  computed: {
    weekDays() {
      const days = []
      const startOfWeek = this.getStartOfWeek(this.currentDate)

      for (let i = 0; i < 7; i++) {
        const date = new Date(startOfWeek)
        date.setDate(startOfWeek.getDate() + i)

        days.push({
          date,
          dayName: date.toLocaleDateString(undefined, { weekday: 'short' }),
          isToday: this.isToday(date),
        })
      }

      return days
    },
  },
  methods: {
    getStartOfWeek(date) {
      const start = new Date(date)
      const day = start.getDay()
      const diff = start.getDate() - day + (day === 0 ? -6 : 1) // Monday as first day
      start.setDate(diff)
      start.setHours(0, 0, 0, 0)
      return start
    },

    isToday(date) {
      const today = new Date()
      return (
        date.getDate() === today.getDate() &&
        date.getMonth() === today.getMonth() &&
        date.getFullYear() === today.getFullYear()
      )
    },

    formatHour(hour) {
      const date = new Date()
      date.setHours(hour, 0, 0, 0)
      return date.toLocaleTimeString(undefined, {
        hour: 'numeric',
        hour12: true,
      })
    },

    getEventsForDay(date) {
      const dateStr = date.toISOString().split('T')[0]
      return this.events.filter((event) => {
        if (!event.date) return false
        const eventDate = new Date(event.date).toISOString().split('T')[0]
        return eventDate === dateStr
      })
    },

    getEventStyle(event) {
      // Position event based on time if datetime field is used
      let top = 0
      let height = 60 // Default height

      if (event.date && event.date.includes('T')) {
        // Has time information
        const eventTime = new Date(event.date)
        const hour = eventTime.getHours()
        const minutes = eventTime.getMinutes()

        top = hour * 60 + minutes // 60px per hour

        // If there's an end time, calculate duration
        if (event.end_date && event.end_date.includes('T')) {
          const endTime = new Date(event.end_date)
          const duration = (endTime - eventTime) / (1000 * 60) // Duration in minutes
          height = Math.max(30, duration) // Minimum 30px height
        }
      }

      return {
        position: 'absolute',
        top: `${top}px`,
        height: `${height}px`,
        left: '4px',
        right: '4px',
        zIndex: 10,
      }
    },

    handleDayClick(date, event) {
      if (this.readOnly) return

      // Calculate the time based on click position
      const rect = event.currentTarget.getBoundingClientRect()
      const y = event.clientY - rect.top
      const hour = Math.floor(y / 60) // 60px per hour
      const minutes = Math.round(y % 60)

      const clickDate = new Date(date)
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

    handleDrop(date, event) {
      event.preventDefault()

      if (this.readOnly || !this.draggedEvent) return

      // Calculate the time based on drop position
      const rect = event.currentTarget.getBoundingClientRect()
      const y = event.clientY - rect.top
      const hour = Math.floor(y / 60)
      const minutes = Math.round(y % 60)

      const dropDate = new Date(date)
      dropDate.setHours(hour, minutes, 0, 0)

      this.$emit('event-move', this.draggedEvent, dropDate)
      this.draggedEvent = null
    },
  },
}
</script>

<style lang="scss" scoped>
.calendar-week-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;

  &__header {
    display: grid;
    grid-template-columns: 60px repeat(7, 1fr);
    border-bottom: 1px solid $color-neutral-200;
    background-color: $color-neutral-50;
    flex-shrink: 0;
  }

  &__time-column-header {
    border-right: 1px solid $color-neutral-200;
  }

  &__day-header {
    padding: 12px 8px;
    text-align: center;
    border-right: 1px solid $color-neutral-200;

    &--today {
      background-color: $color-primary-50;
    }

    &:last-child {
      border-right: none;
    }
  }

  &__day-name {
    font-size: 12px;
    font-weight: 600;
    color: $color-neutral-600;
    text-transform: uppercase;
    margin-bottom: 4px;
  }

  &__day-number {
    font-size: 18px;
    font-weight: 600;
    color: $color-neutral-800;
  }

  &__grid {
    display: grid;
    grid-template-columns: 60px repeat(7, 1fr);
    flex: 1;
    overflow-y: auto;
    min-height: 0;
  }

  &__time-column {
    border-right: 1px solid $color-neutral-200;
    background-color: $color-neutral-10;
  }

  &__time-slot {
    height: 60px;
    display: flex;
    align-items: flex-start;
    justify-content: center;
    padding-top: 4px;
    border-bottom: 1px solid $color-neutral-100;
  }

  &__time-label {
    font-size: 11px;
    color: $color-neutral-600;
    font-weight: 500;
  }

  &__day-column {
    position: relative;
    border-right: 1px solid $color-neutral-200;
    cursor: pointer;

    &--today {
      background-color: $color-primary-100;
    }

    &:last-child {
      border-right: none;
    }

    &:hover {
      background-color: $color-neutral-10;
    }
  }

  &__hour-slot {
    height: 60px;
    border-bottom: 1px solid $color-neutral-100;
    position: relative;

    &:hover {
      background-color: $color-neutral-50;
    }
  }

  &__event {
    border-radius: 4px;
    overflow: hidden;
  }
}

@media (max-width: 768px) {
  .calendar-week-view {
    &__header {
      grid-template-columns: 40px repeat(7, 1fr);
    }

    &__day-header {
      padding: 8px 4px;
    }

    &__day-name {
      font-size: 10px;
      margin-bottom: 2px;
    }

    &__day-number {
      font-size: 14px;
    }

    &__grid {
      grid-template-columns: 40px repeat(7, 1fr);
    }

    &__time-label {
      font-size: 9px;
    }

    &__hour-slot {
      height: 40px;
    }

    &__time-slot {
      height: 40px;
    }
  }
}
</style>
