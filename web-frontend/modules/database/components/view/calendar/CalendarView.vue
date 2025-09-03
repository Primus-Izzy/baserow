<template>
  <div class="calendar-view">
    <div class="calendar-view__loading" v-if="loading">
      <div class="loading"></div>
    </div>
    <div v-else class="calendar-view__container">
      <!-- Calendar navigation -->
      <div class="calendar-view__navigation">
        <div class="calendar-view__nav-controls">
          <button
            class="calendar-view__nav-btn"
            @click="navigatePrevious"
            :disabled="loading"
          >
            <i class="iconoir-nav-arrow-left"></i>
          </button>
          <div class="calendar-view__current-period">
            {{ currentPeriodLabel }}
          </div>
          <button
            class="calendar-view__nav-btn"
            @click="navigateNext"
            :disabled="loading"
          >
            <i class="iconoir-nav-arrow-right"></i>
          </button>
        </div>

        <div class="calendar-view__view-modes">
          <button
            v-for="mode in viewModes"
            :key="mode.value"
            class="calendar-view__mode-btn"
            :class="{
              'calendar-view__mode-btn--active': displayMode === mode.value,
            }"
            @click="setDisplayMode(mode.value)"
          >
            {{ mode.label }}
          </button>
        </div>

        <div class="calendar-view__actions">
          <button class="calendar-view__today-btn" @click="goToToday">
            {{ $t('calendarView.today') }}
          </button>
        </div>
      </div>

      <!-- Calendar grid -->
      <div
        class="calendar-view__grid"
        :class="`calendar-view__grid--${displayMode}`"
      >
        <!-- Month view -->
        <CalendarMonthView
          v-if="displayMode === 'month'"
          :events="events"
          :current-date="currentDate"
          :fields="visibleFields"
          :view="view"
          :table="table"
          :database="database"
          :read-only="readOnly"
          :store-prefix="storePrefix"
          @event-click="handleEventClick"
          @event-move="handleEventMove"
          @date-click="handleDateClick"
          @event-create="handleEventCreate"
        />

        <!-- Week view -->
        <CalendarWeekView
          v-else-if="displayMode === 'week'"
          :events="events"
          :current-date="currentDate"
          :fields="visibleFields"
          :view="view"
          :table="table"
          :database="database"
          :read-only="readOnly"
          :store-prefix="storePrefix"
          @event-click="handleEventClick"
          @event-move="handleEventMove"
          @date-click="handleDateClick"
          @event-create="handleEventCreate"
        />

        <!-- Day view -->
        <CalendarDayView
          v-else-if="displayMode === 'day'"
          :events="events"
          :current-date="currentDate"
          :fields="visibleFields"
          :view="view"
          :table="table"
          :database="database"
          :read-only="readOnly"
          :store-prefix="storePrefix"
          @event-click="handleEventClick"
          @event-move="handleEventMove"
          @date-click="handleDateClick"
          @event-create="handleEventCreate"
        />
      </div>
    </div>

    <!-- Row create modal -->
    <RowCreateModal
      v-if="
        !readOnly &&
        $hasPermission(
          'database.table.create_row',
          table,
          database.workspace.id
        )
      "
      ref="rowCreateModal"
      :database="database"
      :table="table"
      :view="view"
      :primary-is-sortable="true"
      :visible-fields="visibleFields"
      :hidden-fields="hiddenFields"
      :show-hidden-fields="showHiddenFieldsInRowModal"
      :default-values="defaultValues"
      @created="rowCreated"
    />

    <!-- Row edit modal -->
    <RowEditModal
      ref="rowEditModal"
      :database="database"
      :table="table"
      :view="view"
      :fields="allFields"
      :visible-fields="visibleFields"
      :hidden-fields="hiddenFields"
      :show-hidden-fields="showHiddenFieldsInRowModal"
      :read-only="readOnly"
      @updated="rowUpdated"
      @deleted="rowDeleted"
    />

    <!-- Recurring event modal -->
    <CalendarRecurringEventModal
      v-if="showRecurringModal"
      :event="selectedEvent"
      :view="view"
      @close="showRecurringModal = false"
      @updated="handleRecurringEventUpdate"
    />
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import RowCreateModal from '@baserow/modules/database/components/row/RowCreateModal'
import RowEditModal from '@baserow/modules/database/components/row/RowEditModal'
import CalendarMonthView from './CalendarMonthView'
import CalendarWeekView from './CalendarWeekView'
import CalendarDayView from './CalendarDayView'
import CalendarRecurringEventModal from './CalendarRecurringEventModal'
import { notifyIf } from '@baserow/modules/core/utils/error'

export default {
  name: 'CalendarView',
  components: {
    RowCreateModal,
    RowEditModal,
    CalendarMonthView,
    CalendarWeekView,
    CalendarDayView,
    CalendarRecurringEventModal,
  },
  props: {
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
    fields: {
      type: Array,
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
      required: false,
      default: () => ({}),
    },
  },
  data() {
    return {
      currentDate: new Date(),
      displayMode: 'month',
      showRecurringModal: false,
      selectedEvent: null,
      defaultValues: {},
      viewModes: [
        { value: 'month', label: this.$t('calendarView.month') },
        { value: 'week', label: this.$t('calendarView.week') },
        { value: 'day', label: this.$t('calendarView.day') },
      ],
    }
  },
  computed: {
    ...mapGetters({
      loading: 'view/calendar/getLoading',
      events: 'view/calendar/getEvents',
      allFields: 'field/getAll',
    }),

    visibleFields() {
      return this.fields.filter((field) => {
        const fieldOptions =
          this.$store.getters[
            this.storePrefix + 'view/calendar/getFieldOptions'
          ](field)
        return fieldOptions ? !fieldOptions.hidden : true
      })
    },

    hiddenFields() {
      return this.fields.filter((field) => {
        const fieldOptions =
          this.$store.getters[
            this.storePrefix + 'view/calendar/getFieldOptions'
          ](field)
        return fieldOptions ? fieldOptions.hidden : false
      })
    },

    showHiddenFieldsInRowModal() {
      return this.$store.getters['view/getShowHiddenFieldsInRowModal']
    },

    currentPeriodLabel() {
      const options = { year: 'numeric', month: 'long' }
      if (this.displayMode === 'day') {
        options.day = 'numeric'
        options.weekday = 'long'
      } else if (this.displayMode === 'week') {
        // For week view, show the week range
        const startOfWeek = this.getStartOfWeek(this.currentDate)
        const endOfWeek = this.getEndOfWeek(this.currentDate)
        return `${startOfWeek.toLocaleDateString()} - ${endOfWeek.toLocaleDateString()}`
      }
      return this.currentDate.toLocaleDateString(undefined, options)
    },
  },
  watch: {
    currentDate: {
      handler() {
        this.fetchEvents()
      },
      immediate: true,
    },
    displayMode() {
      this.fetchEvents()
    },
    'view.date_field'() {
      this.fetchEvents()
    },
  },
  mounted() {
    // Set initial display mode from view configuration
    if (this.view.display_mode) {
      this.displayMode = this.view.display_mode
    }

    // Add keyboard shortcuts
    this.addKeyboardShortcuts()

    // Add touch event listeners for mobile
    this.addTouchListeners()
  },
  beforeDestroy() {
    this.removeKeyboardShortcuts()
    this.removeTouchListeners()
  },
  methods: {
    async fetchEvents() {
      if (!this.view.date_field) {
        return
      }

      const { startDate, endDate } = this.getDateRange()

      try {
        await this.$store.dispatch(
          this.storePrefix + 'view/calendar/fetchEvents',
          {
            viewId: this.view.id,
            startDate: startDate.toISOString().split('T')[0],
            endDate: endDate.toISOString().split('T')[0],
            includeRecurring: this.view.enable_recurring_events,
          }
        )
      } catch (error) {
        notifyIf(error, 'view')
      }
    },

    getDateRange() {
      let startDate, endDate

      switch (this.displayMode) {
        case 'month':
          startDate = new Date(
            this.currentDate.getFullYear(),
            this.currentDate.getMonth(),
            1
          )
          endDate = new Date(
            this.currentDate.getFullYear(),
            this.currentDate.getMonth() + 1,
            0
          )
          // Extend to show full weeks
          startDate = this.getStartOfWeek(startDate)
          endDate = this.getEndOfWeek(endDate)
          break
        case 'week':
          startDate = this.getStartOfWeek(this.currentDate)
          endDate = this.getEndOfWeek(this.currentDate)
          break
        case 'day':
          startDate = new Date(this.currentDate)
          endDate = new Date(this.currentDate)
          break
      }

      return { startDate, endDate }
    },

    getStartOfWeek(date) {
      const start = new Date(date)
      const day = start.getDay()
      const diff = start.getDate() - day + (day === 0 ? -6 : 1) // Monday as first day
      start.setDate(diff)
      start.setHours(0, 0, 0, 0)
      return start
    },

    getEndOfWeek(date) {
      const end = new Date(date)
      const day = end.getDay()
      const diff = end.getDate() + (7 - day) + (day === 0 ? -7 : 0)
      end.setDate(diff)
      end.setHours(23, 59, 59, 999)
      return end
    },

    navigatePrevious() {
      const newDate = new Date(this.currentDate)

      switch (this.displayMode) {
        case 'month':
          newDate.setMonth(newDate.getMonth() - 1)
          break
        case 'week':
          newDate.setDate(newDate.getDate() - 7)
          break
        case 'day':
          newDate.setDate(newDate.getDate() - 1)
          break
      }

      this.currentDate = newDate
    },

    navigateNext() {
      const newDate = new Date(this.currentDate)

      switch (this.displayMode) {
        case 'month':
          newDate.setMonth(newDate.getMonth() + 1)
          break
        case 'week':
          newDate.setDate(newDate.getDate() + 7)
          break
        case 'day':
          newDate.setDate(newDate.getDate() + 1)
          break
      }

      this.currentDate = newDate
    },

    goToToday() {
      this.currentDate = new Date()
    },

    setDisplayMode(mode) {
      this.displayMode = mode
      // Update view configuration
      this.$store.dispatch('view/update', {
        view: this.view,
        values: { display_mode: mode },
      })
    },

    handleEventClick(event) {
      if (this.readOnly) {
        return
      }

      if (event.is_recurring) {
        this.selectedEvent = event
        this.showRecurringModal = true
      } else {
        this.$refs.rowEditModal.show(event.id)
      }
    },

    async handleEventMove(event, newDate) {
      if (this.readOnly) {
        return
      }

      try {
        await this.$store.dispatch(
          this.storePrefix + 'view/calendar/moveEvent',
          {
            viewId: this.view.id,
            rowId: event.id,
            newDate: newDate.toISOString().split('T')[0],
            updateEndDate: true,
          }
        )

        // Refresh events to show the updated position
        await this.fetchEvents()
      } catch (error) {
        notifyIf(error, 'view')
      }
    },

    handleDateClick(date) {
      if (this.readOnly || !this.view.date_field) {
        return
      }

      // Set default date value for new event
      this.defaultValues = {
        [`field_${this.view.date_field}`]: date.toISOString().split('T')[0],
      }

      this.$refs.rowCreateModal.show()
    },

    handleEventCreate(date) {
      this.handleDateClick(date)
    },

    handleRecurringEventUpdate() {
      this.showRecurringModal = false
      this.fetchEvents()
    },

    rowCreated() {
      this.fetchEvents()
    },

    rowUpdated() {
      this.fetchEvents()
    },

    rowDeleted() {
      this.fetchEvents()
    },

    addKeyboardShortcuts() {
      this.keyboardHandler = (event) => {
        if (
          event.target.tagName === 'INPUT' ||
          event.target.tagName === 'TEXTAREA'
        ) {
          return
        }

        switch (event.key) {
          case 'ArrowLeft':
            event.preventDefault()
            this.navigatePrevious()
            break
          case 'ArrowRight':
            event.preventDefault()
            this.navigateNext()
            break
          case 't':
            event.preventDefault()
            this.goToToday()
            break
          case 'm':
            event.preventDefault()
            this.setDisplayMode('month')
            break
          case 'w':
            event.preventDefault()
            this.setDisplayMode('week')
            break
          case 'd':
            event.preventDefault()
            this.setDisplayMode('day')
            break
        }
      }

      document.addEventListener('keydown', this.keyboardHandler)
    },

    removeKeyboardShortcuts() {
      if (this.keyboardHandler) {
        document.removeEventListener('keydown', this.keyboardHandler)
      }
    },

    addTouchListeners() {
      // Add swipe gestures for mobile navigation
      let startX = 0
      let startY = 0

      this.touchStartHandler = (event) => {
        startX = event.touches[0].clientX
        startY = event.touches[0].clientY
      }

      this.touchEndHandler = (event) => {
        if (!startX || !startY) {
          return
        }

        const endX = event.changedTouches[0].clientX
        const endY = event.changedTouches[0].clientY
        const diffX = startX - endX
        const diffY = startY - endY

        // Only handle horizontal swipes
        if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
          if (diffX > 0) {
            // Swipe left - next period
            this.navigateNext()
          } else {
            // Swipe right - previous period
            this.navigatePrevious()
          }
        }

        startX = 0
        startY = 0
      }

      this.$el.addEventListener('touchstart', this.touchStartHandler, {
        passive: true,
      })
      this.$el.addEventListener('touchend', this.touchEndHandler, {
        passive: true,
      })
    },

    removeTouchListeners() {
      if (this.touchStartHandler) {
        this.$el.removeEventListener('touchstart', this.touchStartHandler)
      }
      if (this.touchEndHandler) {
        this.$el.removeEventListener('touchend', this.touchEndHandler)
      }
    },
  },
}
</script>
