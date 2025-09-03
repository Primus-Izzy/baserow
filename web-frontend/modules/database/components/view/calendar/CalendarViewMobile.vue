<template>
  <div class="calendar-view-mobile">
    <!-- Mobile Header -->
    <div class="mobile-header">
      <div class="header-actions">
        <button class="action-button" @click="$emit('toggle-sidebar')">
          <i class="fas fa-bars"></i>
        </button>
        <h1 class="header-title">{{ view.name }}</h1>
        <button class="action-button" @click="$emit('show-options')">
          <i class="fas fa-ellipsis-v"></i>
        </button>
      </div>
    </div>

    <!-- Mobile Content -->
    <div class="mobile-content">
      <!-- Calendar Navigation -->
      <div class="calendar-navigation">
        <div class="nav-controls">
          <button class="nav-btn touch-feedback" @click="previousPeriod">
            <i class="fas fa-chevron-left"></i>
          </button>

          <div class="current-period">
            <h2 class="period-title">{{ currentPeriodTitle }}</h2>
            <span class="period-subtitle">{{ currentPeriodSubtitle }}</span>
          </div>

          <button class="nav-btn touch-feedback" @click="nextPeriod">
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>

        <!-- View Mode Toggle -->
        <div class="view-mode-toggle">
          <button
            v-for="mode in viewModes"
            :key="mode.value"
            class="mode-btn touch-feedback"
            :class="{ active: currentViewMode === mode.value }"
            @click="setViewMode(mode.value)"
          >
            <i :class="mode.icon"></i>
            <span>{{ mode.label }}</span>
          </button>
        </div>
      </div>

      <!-- Calendar Content -->
      <div
        class="calendar-content"
        @touchstart="handleTouchStart"
        @touchmove="handleTouchMove"
        @touchend="handleTouchEnd"
      >
        <!-- Month View -->
        <div v-if="currentViewMode === 'month'" class="month-view">
          <!-- Weekday Headers -->
          <div class="weekday-headers">
            <div v-for="day in weekdays" :key="day" class="weekday-header">
              {{ day }}
            </div>
          </div>

          <!-- Calendar Grid -->
          <div class="calendar-grid">
            <div
              v-for="date in monthDates"
              :key="date.dateString"
              class="calendar-day"
              :class="{
                'other-month': !date.isCurrentMonth,
                today: date.isToday,
                selected: selectedDate === date.dateString,
                'has-events': date.events.length > 0,
              }"
              @click="selectDate(date)"
            >
              <div class="day-number">{{ date.day }}</div>
              <div class="day-events">
                <div
                  v-for="(event, index) in date.events.slice(0, 2)"
                  :key="event.id"
                  class="event-dot"
                  :style="{ backgroundColor: event.color }"
                  @click.stop="selectEvent(event)"
                ></div>
                <div v-if="date.events.length > 2" class="more-events">
                  +{{ date.events.length - 2 }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Week View -->
        <div v-if="currentViewMode === 'week'" class="week-view">
          <!-- Week Header -->
          <div class="week-header">
            <div
              v-for="date in weekDates"
              :key="date.dateString"
              class="week-day-header"
              :class="{ today: date.isToday }"
            >
              <div class="day-name">{{ date.dayName }}</div>
              <div class="day-number">{{ date.day }}</div>
            </div>
          </div>

          <!-- Week Timeline -->
          <div class="week-timeline">
            <div class="time-slots">
              <div v-for="hour in timeSlots" :key="hour" class="time-slot">
                <span class="time-label">{{ formatHour(hour) }}</span>
              </div>
            </div>

            <div class="week-events">
              <div
                v-for="date in weekDates"
                :key="date.dateString"
                class="day-column"
              >
                <div
                  v-for="event in date.events"
                  :key="event.id"
                  class="week-event"
                  :style="{
                    top: `${getEventTop(event)}px`,
                    height: `${getEventHeight(event)}px`,
                    backgroundColor: event.color,
                  }"
                  @click="selectEvent(event)"
                >
                  <div class="event-title">{{ event.title }}</div>
                  <div class="event-time">{{ formatEventTime(event) }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Day View -->
        <div v-if="currentViewMode === 'day'" class="day-view">
          <!-- Day Header -->
          <div class="day-header">
            <h3 class="day-title">{{ selectedDateFormatted }}</h3>
            <span class="day-subtitle"
              >{{ selectedDayEvents.length }} events</span
            >
          </div>

          <!-- Day Events List -->
          <div class="day-events-list">
            <div
              v-for="event in selectedDayEvents"
              :key="event.id"
              class="day-event touch-feedback"
              :style="{ borderLeftColor: event.color }"
              @click="selectEvent(event)"
            >
              <div class="event-time">{{ formatEventTime(event) }}</div>
              <div class="event-details">
                <h4 class="event-title">{{ event.title }}</h4>
                <p v-if="event.description" class="event-description">
                  {{ event.description }}
                </p>
                <div class="event-meta">
                  <span v-if="event.location" class="event-location">
                    <i class="fas fa-map-marker-alt"></i>
                    {{ event.location }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Empty State -->
            <div v-if="selectedDayEvents.length === 0" class="empty-day">
              <i class="fas fa-calendar-day"></i>
              <p>No events scheduled</p>
              <button
                class="add-event-btn touch-feedback"
                @click="addEvent(selectedDate)"
              >
                Add Event
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="quick-actions">
        <button class="quick-action-btn touch-feedback" @click="goToToday">
          <i class="fas fa-calendar-day"></i>
          <span>Today</span>
        </button>
        <button
          class="quick-action-btn touch-feedback"
          @click="addEvent(selectedDate || getCurrentDate())"
        >
          <i class="fas fa-plus"></i>
          <span>Add Event</span>
        </button>
        <button class="quick-action-btn touch-feedback" @click="showFilters">
          <i class="fas fa-filter"></i>
          <span>Filter</span>
        </button>
      </div>
    </div>

    <!-- Event Details Modal -->
    <div v-if="selectedEvent" class="mobile-modal">
      <div class="modal-header">
        <h3 class="modal-title">Event Details</h3>
        <button class="close-button" @click="selectedEvent = null">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <div class="modal-content">
        <div class="event-detail">
          <h4>{{ selectedEvent.title }}</h4>
          <div class="event-info">
            <div class="info-item">
              <i class="fas fa-clock"></i>
              <span>{{ formatEventTime(selectedEvent) }}</span>
            </div>
            <div v-if="selectedEvent.location" class="info-item">
              <i class="fas fa-map-marker-alt"></i>
              <span>{{ selectedEvent.location }}</span>
            </div>
            <div v-if="selectedEvent.description" class="info-item">
              <i class="fas fa-align-left"></i>
              <span>{{ selectedEvent.description }}</span>
            </div>
          </div>
          <div class="event-actions">
            <button
              class="action-btn edit-btn"
              @click="editEvent(selectedEvent)"
            >
              <i class="fas fa-edit"></i>
              Edit
            </button>
            <button
              class="action-btn delete-btn"
              @click="deleteEvent(selectedEvent)"
            >
              <i class="fas fa-trash"></i>
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile Navigation -->
    <div class="mobile-nav">
      <div class="nav-item" :class="{ active: currentTab === 'calendar' }">
        <i class="icon fas fa-calendar"></i>
        <span>Calendar</span>
      </div>
      <div class="nav-item" :class="{ active: currentTab === 'events' }">
        <i class="icon fas fa-list"></i>
        <span>Events</span>
      </div>
      <div class="nav-item" :class="{ active: currentTab === 'settings' }">
        <i class="icon fas fa-cog"></i>
        <span>Settings</span>
      </div>
    </div>
  </div>
</template>

<script>
import mobileResponsive from '@baserow/modules/core/mixins/mobileResponsive'

export default {
  name: 'CalendarViewMobile',
  mixins: [mobileResponsive],
  props: {
    view: {
      type: Object,
      required: true,
    },
    events: {
      type: Array,
      default: () => [],
    },
    fields: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      currentViewMode: 'month',
      currentDate: new Date(),
      selectedDate: null,
      selectedEvent: null,
      currentTab: 'calendar',
      viewModes: [
        { value: 'month', label: 'Month', icon: 'fas fa-calendar' },
        { value: 'week', label: 'Week', icon: 'fas fa-calendar-week' },
        { value: 'day', label: 'Day', icon: 'fas fa-calendar-day' },
      ],
      weekdays: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
      timeSlots: Array.from({ length: 24 }, (_, i) => i),
      swipeThreshold: 50,
    }
  },
  computed: {
    currentPeriodTitle() {
      const options = {
        year: 'numeric',
        month: 'long',
      }
      if (this.currentViewMode === 'day') {
        options.day = 'numeric'
      }
      return this.currentDate.toLocaleDateString('en-US', options)
    },

    currentPeriodSubtitle() {
      if (this.currentViewMode === 'week') {
        const startOfWeek = this.getStartOfWeek(this.currentDate)
        const endOfWeek = new Date(startOfWeek)
        endOfWeek.setDate(startOfWeek.getDate() + 6)
        return `${startOfWeek.getDate()} - ${endOfWeek.getDate()}`
      }
      return ''
    },

    monthDates() {
      const dates = []
      const startOfMonth = new Date(
        this.currentDate.getFullYear(),
        this.currentDate.getMonth(),
        1
      )
      const endOfMonth = new Date(
        this.currentDate.getFullYear(),
        this.currentDate.getMonth() + 1,
        0
      )
      const startOfCalendar = this.getStartOfWeek(startOfMonth)

      for (let i = 0; i < 42; i++) {
        const date = new Date(startOfCalendar)
        date.setDate(startOfCalendar.getDate() + i)

        dates.push({
          date,
          day: date.getDate(),
          dateString: this.formatDateString(date),
          isCurrentMonth: date.getMonth() === this.currentDate.getMonth(),
          isToday: this.isToday(date),
          events: this.getEventsForDate(date),
        })
      }

      return dates
    },

    weekDates() {
      const dates = []
      const startOfWeek = this.getStartOfWeek(this.currentDate)

      for (let i = 0; i < 7; i++) {
        const date = new Date(startOfWeek)
        date.setDate(startOfWeek.getDate() + i)

        dates.push({
          date,
          day: date.getDate(),
          dayName: date.toLocaleDateString('en-US', { weekday: 'short' }),
          dateString: this.formatDateString(date),
          isToday: this.isToday(date),
          events: this.getEventsForDate(date),
        })
      }

      return dates
    },

    selectedDayEvents() {
      if (!this.selectedDate) return []
      const date = new Date(this.selectedDate)
      return this.getEventsForDate(date)
    },

    selectedDateFormatted() {
      if (!this.selectedDate) return ''
      const date = new Date(this.selectedDate)
      return date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    },
  },
  methods: {
    setViewMode(mode) {
      this.currentViewMode = mode
    },

    previousPeriod() {
      const newDate = new Date(this.currentDate)
      if (this.currentViewMode === 'month') {
        newDate.setMonth(newDate.getMonth() - 1)
      } else if (this.currentViewMode === 'week') {
        newDate.setDate(newDate.getDate() - 7)
      } else if (this.currentViewMode === 'day') {
        newDate.setDate(newDate.getDate() - 1)
      }
      this.currentDate = newDate
    },

    nextPeriod() {
      const newDate = new Date(this.currentDate)
      if (this.currentViewMode === 'month') {
        newDate.setMonth(newDate.getMonth() + 1)
      } else if (this.currentViewMode === 'week') {
        newDate.setDate(newDate.getDate() + 7)
      } else if (this.currentViewMode === 'day') {
        newDate.setDate(newDate.getDate() + 1)
      }
      this.currentDate = newDate
    },

    goToToday() {
      this.currentDate = new Date()
      this.selectedDate = this.formatDateString(new Date())
    },

    selectDate(dateObj) {
      this.selectedDate = dateObj.dateString
      if (this.currentViewMode === 'month' && dateObj.events.length > 0) {
        this.setViewMode('day')
      }
    },

    selectEvent(event) {
      this.selectedEvent = event
    },

    addEvent(date) {
      this.$emit('add-event', date)
    },

    editEvent(event) {
      this.$emit('edit-event', event)
      this.selectedEvent = null
    },

    deleteEvent(event) {
      this.$emit('delete-event', event)
      this.selectedEvent = null
    },

    showFilters() {
      this.$emit('show-filters')
    },

    getStartOfWeek(date) {
      const startOfWeek = new Date(date)
      startOfWeek.setDate(date.getDate() - date.getDay())
      return startOfWeek
    },

    isToday(date) {
      const today = new Date()
      return date.toDateString() === today.toDateString()
    },

    formatDateString(date) {
      return date.toISOString().split('T')[0]
    },

    getCurrentDate() {
      return this.formatDateString(new Date())
    },

    getEventsForDate(date) {
      const dateString = this.formatDateString(date)
      return this.events.filter((event) => {
        const eventDate = new Date(event.date)
        return this.formatDateString(eventDate) === dateString
      })
    },

    formatHour(hour) {
      const ampm = hour >= 12 ? 'PM' : 'AM'
      const displayHour = hour % 12 || 12
      return `${displayHour} ${ampm}`
    },

    formatEventTime(event) {
      const startTime = new Date(event.start_time)
      const endTime = new Date(event.end_time)
      return `${this.formatTime(startTime)} - ${this.formatTime(endTime)}`
    },

    formatTime(date) {
      return date.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true,
      })
    },

    getEventTop(event) {
      const startTime = new Date(event.start_time)
      const hours = startTime.getHours()
      const minutes = startTime.getMinutes()
      return (hours * 60 + minutes) * 0.5 // 0.5px per minute
    },

    getEventHeight(event) {
      const startTime = new Date(event.start_time)
      const endTime = new Date(event.end_time)
      const duration = (endTime - startTime) / (1000 * 60) // duration in minutes
      return Math.max(duration * 0.5, 20) // minimum 20px height
    },

    handleTouchMove(event) {
      const touchX = event.touches[0].clientX
      const deltaX = touchX - this.touchStartX

      if (Math.abs(deltaX) > this.swipeThreshold) {
        if (deltaX > 0) {
          this.previousPeriod()
        } else {
          this.nextPeriod()
        }
        this.touchStartX = touchX
      }
    },
  },

  mounted() {
    this.selectedDate = this.getCurrentDate()

    // Handle swipe gestures
    this.$on('swipe-left', () => {
      this.nextPeriod()
    })

    this.$on('swipe-right', () => {
      this.previousPeriod()
    })
  },
}
</script>

<style lang="scss" scoped>
@import '@baserow/modules/core/assets/scss/components/mobile/responsive.scss';

.calendar-view-mobile {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-neutral-50);
}

.calendar-navigation {
  background: var(--color-neutral-100);
  border-bottom: 1px solid var(--color-neutral-200);

  .nav-controls {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: $mobile-spacing-md;

    .nav-btn {
      @include touch-friendly;
      background: var(--color-neutral-50);
      border: 1px solid var(--color-neutral-300);
      border-radius: 50%;
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .current-period {
      text-align: center;
      flex: 1;

      .period-title {
        margin: 0;
        font-size: $mobile-font-size-lg;
        font-weight: 600;
      }

      .period-subtitle {
        font-size: $mobile-font-size-sm;
        color: var(--color-neutral-600);
      }
    }
  }

  .view-mode-toggle {
    display: flex;
    padding: 0 $mobile-spacing-md $mobile-spacing-md;
    gap: $mobile-spacing-sm;

    .mode-btn {
      @include touch-friendly;
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      background: var(--color-neutral-50);
      border: 1px solid var(--color-neutral-300);
      border-radius: 8px;
      padding: $mobile-spacing-sm;

      &.active {
        background: var(--color-primary);
        color: white;
        border-color: var(--color-primary);
      }

      .fas {
        margin-bottom: 4px;
        font-size: 16px;
      }

      span {
        font-size: $mobile-font-size-xs;
      }
    }
  }
}

.calendar-content {
  flex: 1;
  overflow: hidden;
}

.month-view {
  height: 100%;
  display: flex;
  flex-direction: column;

  .weekday-headers {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    background: var(--color-neutral-100);
    border-bottom: 1px solid var(--color-neutral-200);

    .weekday-header {
      padding: $mobile-spacing-sm;
      text-align: center;
      font-size: $mobile-font-size-sm;
      font-weight: 600;
      color: var(--color-neutral-600);
    }
  }

  .calendar-grid {
    flex: 1;
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    grid-template-rows: repeat(6, 1fr);

    .calendar-day {
      border: 1px solid var(--color-neutral-200);
      padding: $mobile-spacing-sm;
      display: flex;
      flex-direction: column;
      cursor: pointer;

      &.other-month {
        opacity: 0.5;
        background: var(--color-neutral-25);
      }

      &.today {
        background: var(--color-primary-50);

        .day-number {
          background: var(--color-primary);
          color: white;
          border-radius: 50%;
          width: 24px;
          height: 24px;
          display: flex;
          align-items: center;
          justify-content: center;
        }
      }

      &.selected {
        background: var(--color-primary-100);
      }

      &.has-events {
        background: var(--color-neutral-100);
      }

      .day-number {
        font-size: $mobile-font-size-sm;
        font-weight: 600;
        margin-bottom: 4px;
      }

      .day-events {
        display: flex;
        flex-wrap: wrap;
        gap: 2px;

        .event-dot {
          width: 6px;
          height: 6px;
          border-radius: 50%;
        }

        .more-events {
          font-size: 10px;
          color: var(--color-neutral-600);
        }
      }
    }
  }
}

.week-view {
  height: 100%;
  display: flex;
  flex-direction: column;

  .week-header {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    background: var(--color-neutral-100);
    border-bottom: 1px solid var(--color-neutral-200);

    .week-day-header {
      padding: $mobile-spacing-sm;
      text-align: center;

      &.today {
        background: var(--color-primary-50);

        .day-number {
          background: var(--color-primary);
          color: white;
          border-radius: 50%;
          width: 24px;
          height: 24px;
          display: inline-flex;
          align-items: center;
          justify-content: center;
        }
      }

      .day-name {
        font-size: $mobile-font-size-xs;
        color: var(--color-neutral-600);
      }

      .day-number {
        font-size: $mobile-font-size-sm;
        font-weight: 600;
      }
    }
  }

  .week-timeline {
    flex: 1;
    display: flex;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;

    .time-slots {
      width: 60px;
      background: var(--color-neutral-100);
      border-right: 1px solid var(--color-neutral-200);

      .time-slot {
        height: 60px;
        border-bottom: 1px solid var(--color-neutral-200);
        display: flex;
        align-items: center;
        justify-content: center;

        .time-label {
          font-size: $mobile-font-size-xs;
          color: var(--color-neutral-600);
        }
      }
    }

    .week-events {
      flex: 1;
      display: grid;
      grid-template-columns: repeat(7, 1fr);
      position: relative;

      .day-column {
        border-right: 1px solid var(--color-neutral-200);
        position: relative;

        &:last-child {
          border-right: none;
        }
      }

      .week-event {
        position: absolute;
        left: 2px;
        right: 2px;
        border-radius: 4px;
        padding: 2px 4px;
        color: white;
        font-size: $mobile-font-size-xs;
        cursor: pointer;

        .event-title {
          font-weight: 600;
          line-height: 1.2;
        }

        .event-time {
          opacity: 0.9;
        }
      }
    }
  }
}

.day-view {
  height: 100%;
  display: flex;
  flex-direction: column;

  .day-header {
    padding: $mobile-spacing-md;
    background: var(--color-neutral-100);
    border-bottom: 1px solid var(--color-neutral-200);
    text-align: center;

    .day-title {
      margin: 0;
      font-size: $mobile-font-size-lg;
      font-weight: 600;
    }

    .day-subtitle {
      font-size: $mobile-font-size-sm;
      color: var(--color-neutral-600);
    }
  }

  .day-events-list {
    flex: 1;
    overflow-y: auto;
    padding: $mobile-spacing-md;
    -webkit-overflow-scrolling: touch;

    .day-event {
      background: var(--color-neutral-50);
      border: 1px solid var(--color-neutral-200);
      border-left: 4px solid var(--color-primary);
      border-radius: 8px;
      padding: $mobile-spacing-md;
      margin-bottom: $mobile-spacing-md;
      display: flex;
      gap: $mobile-spacing-md;

      .event-time {
        font-size: $mobile-font-size-sm;
        font-weight: 600;
        color: var(--color-primary);
        min-width: 80px;
      }

      .event-details {
        flex: 1;

        .event-title {
          margin: 0 0 4px 0;
          font-size: $mobile-font-size-md;
          font-weight: 600;
        }

        .event-description {
          margin: 0 0 8px 0;
          font-size: $mobile-font-size-sm;
          color: var(--color-neutral-600);
          line-height: 1.4;
        }

        .event-meta {
          .event-location {
            font-size: $mobile-font-size-xs;
            color: var(--color-neutral-600);

            .fas {
              margin-right: 4px;
            }
          }
        }
      }
    }

    .empty-day {
      text-align: center;
      padding: $mobile-spacing-xl;
      color: var(--color-neutral-600);

      .fas {
        font-size: 48px;
        margin-bottom: $mobile-spacing-md;
        opacity: 0.5;
      }

      p {
        margin-bottom: $mobile-spacing-md;
        font-size: $mobile-font-size-md;
      }

      .add-event-btn {
        @include touch-friendly;
        background: var(--color-primary);
        color: white;
        border: none;
        border-radius: 8px;
        padding: $mobile-spacing-sm $mobile-spacing-md;
      }
    }
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
  .event-detail {
    h4 {
      margin: 0 0 $mobile-spacing-md 0;
      font-size: $mobile-font-size-lg;
    }

    .event-info {
      margin-bottom: $mobile-spacing-lg;

      .info-item {
        display: flex;
        align-items: center;
        margin-bottom: $mobile-spacing-sm;

        .fas {
          width: 20px;
          margin-right: $mobile-spacing-sm;
          color: var(--color-neutral-600);
        }

        span {
          font-size: $mobile-font-size-sm;
        }
      }
    }

    .event-actions {
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

        &.delete-btn {
          background: var(--color-error);
          color: white;
        }
      }
    }
  }
}
</style>
