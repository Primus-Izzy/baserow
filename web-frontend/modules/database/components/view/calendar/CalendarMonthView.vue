<template>
  <div class="calendar-month-view">
    <!-- Day headers -->
    <div class="calendar-month-view__headers">
      <div
        v-for="day in dayHeaders"
        :key="day"
        class="calendar-month-view__header"
      >
        {{ day }}
      </div>
    </div>

    <!-- Calendar grid -->
    <div class="calendar-month-view__grid">
      <CalendarDayCell
        v-for="day in calendarDays"
        :key="day.date.toISOString()"
        :date="day.date"
        :is-current-month="day.isCurrentMonth"
        :is-today="day.isToday"
        :events="getEventsForDay(day.date)"
        :fields="fields"
        :view="view"
        :table="table"
        :database="database"
        :read-only="readOnly"
        :store-prefix="storePrefix"
        @event-click="$emit('event-click', $event)"
        @event-move="handleEventMove"
        @date-click="$emit('date-click', $event)"
        @event-create="$emit('event-create', $event)"
      />
    </div>
  </div>
</template>

<script>
import CalendarDayCell from './CalendarDayCell'

export default {
  name: 'CalendarMonthView',
  components: {
    CalendarDayCell,
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
  computed: {
    dayHeaders() {
      const days = []
      const startDate = new Date(2023, 0, 2) // Monday

      for (let i = 0; i < 7; i++) {
        const date = new Date(startDate)
        date.setDate(startDate.getDate() + i)
        days.push(date.toLocaleDateString(undefined, { weekday: 'short' }))
      }

      return days
    },

    calendarDays() {
      const days = []
      const year = this.currentDate.getFullYear()
      const month = this.currentDate.getMonth()

      // Get first day of month and adjust to Monday start
      const firstDay = new Date(year, month, 1)
      const startDate = this.getStartOfWeek(firstDay)

      // Generate 42 days (6 weeks)
      for (let i = 0; i < 42; i++) {
        const date = new Date(startDate)
        date.setDate(startDate.getDate() + i)

        days.push({
          date,
          isCurrentMonth: date.getMonth() === month,
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

    getEventsForDay(date) {
      const dateStr = date.toISOString().split('T')[0]
      return this.events.filter((event) => {
        if (!event.date) return false
        const eventDate = new Date(event.date).toISOString().split('T')[0]
        return eventDate === dateStr
      })
    },

    handleEventMove(event, newDate) {
      this.$emit('event-move', event, newDate)
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@baserow/modules/core/assets/scss/colors.scss';

.calendar-month-view {
  display: flex;
  flex-direction: column;
  height: 100%;

  &__headers {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    border-bottom: 1px solid $color-neutral-200;
    background-color: $color-neutral-50;
  }

  &__header {
    padding: 12px 8px;
    text-align: center;
    font-weight: 600;
    font-size: 12px;
    color: $color-neutral-600;
    text-transform: uppercase;
    border-right: 1px solid $color-neutral-200;

    &:last-child {
      border-right: none;
    }
  }

  &__grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    grid-template-rows: repeat(6, 1fr);
    flex: 1;
    min-height: 0;
  }
}

@media (max-width: 768px) {
  .calendar-month-view {
    &__header {
      padding: 8px 4px;
      font-size: 11px;
    }
  }
}
</style>
