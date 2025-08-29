<template>
  <Modal @close="$emit('close')">
    <template #header>
      <h2 class="modal__title">
        {{ $t('calendarView.recurringEvent') }}
      </h2>
    </template>
    
    <template #content>
      <div class="recurring-event-modal">
        <div class="recurring-event-modal__info">
          <h3>{{ eventTitle }}</h3>
          <p class="recurring-event-modal__date">
            {{ formatDate(event.date) }}
          </p>
        </div>

        <div class="recurring-event-modal__actions">
          <p class="recurring-event-modal__question">
            {{ $t('calendarView.recurringEventQuestion') }}
          </p>

          <div class="recurring-event-modal__buttons">
            <button
              class="button button--large"
              @click="editThisEvent"
            >
              {{ $t('calendarView.editThisEvent') }}
            </button>

            <button
              class="button button--large button--ghost"
              @click="editAllEvents"
            >
              {{ $t('calendarView.editAllEvents') }}
            </button>

            <button
              class="button button--large button--error"
              @click="deleteThisEvent"
            >
              {{ $t('calendarView.deleteThisEvent') }}
            </button>

            <button
              class="button button--large button--error button--ghost"
              @click="deleteAllEvents"
            >
              {{ $t('calendarView.deleteAllEvents') }}
            </button>
          </div>
        </div>

        <!-- Recurring pattern info -->
        <div v-if="recurringPattern" class="recurring-event-modal__pattern">
          <h4>{{ $t('calendarView.recurringPattern') }}</h4>
          <div class="recurring-event-modal__pattern-details">
            <p>
              <strong>{{ $t('calendarView.patternType') }}:</strong>
              {{ getPatternTypeLabel(recurringPattern.pattern_type) }}
            </p>
            <p>
              <strong>{{ $t('calendarView.interval') }}:</strong>
              {{ recurringPattern.interval }}
            </p>
            <p v-if="recurringPattern.end_date">
              <strong>{{ $t('calendarView.endDate') }}:</strong>
              {{ formatDate(recurringPattern.end_date) }}
            </p>
            <p v-if="recurringPattern.max_occurrences">
              <strong>{{ $t('calendarView.maxOccurrences') }}:</strong>
              {{ recurringPattern.max_occurrences }}
            </p>
          </div>
        </div>
      </div>
    </template>
  </Modal>
</template>

<script>
import Modal from '@baserow/modules/core/components/Modal'

export default {
  name: 'CalendarRecurringEventModal',
  components: {
    Modal,
  },
  props: {
    event: {
      type: Object,
      required: true,
    },
    view: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      recurringPattern: null,
    }
  },
  computed: {
    eventTitle() {
      if (this.view.event_title_field && this.event[`field_${this.view.event_title_field}`]) {
        return this.event[`field_${this.view.event_title_field}`]
      }
      return this.event.title || `Event ${this.event.id}`
    },
  },
  async mounted() {
    if (this.event.pattern_id) {
      await this.fetchRecurringPattern()
    }
  },
  methods: {
    async fetchRecurringPattern() {
      try {
        // This would fetch the recurring pattern details from the API
        // For now, we'll use mock data
        this.recurringPattern = {
          pattern_type: 'weekly',
          interval: 1,
          end_date: null,
          max_occurrences: null,
        }
      } catch (error) {
        console.error('Error fetching recurring pattern:', error)
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString(undefined, {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    },
    
    getPatternTypeLabel(patternType) {
      const labels = {
        daily: this.$t('calendarView.daily'),
        weekly: this.$t('calendarView.weekly'),
        monthly: this.$t('calendarView.monthly'),
        yearly: this.$t('calendarView.yearly'),
      }
      return labels[patternType] || patternType
    },
    
    editThisEvent() {
      // Create an exception for this occurrence and edit it
      this.$emit('edit-occurrence', {
        event: this.event,
        editType: 'this',
      })
      this.$emit('close')
    },
    
    editAllEvents() {
      // Edit the original recurring event
      this.$emit('edit-series', {
        event: this.event,
        editType: 'all',
      })
      this.$emit('close')
    },
    
    deleteThisEvent() {
      // Add this date to the exceptions list
      this.$emit('delete-occurrence', {
        event: this.event,
        deleteType: 'this',
      })
      this.$emit('close')
    },
    
    deleteAllEvents() {
      // Delete the entire recurring series
      this.$emit('delete-series', {
        event: this.event,
        deleteType: 'all',
      })
      this.$emit('close')
    },
  },
}
</script>

<style lang="scss" scoped>
.recurring-event-modal {
  padding: 20px;

  &__info {
    margin-bottom: 24px;
    text-align: center;

    h3 {
      font-size: 20px;
      font-weight: 600;
      color: $color-neutral-800;
      margin-bottom: 8px;
    }
  }

  &__date {
    font-size: 14px;
    color: $color-neutral-600;
    margin: 0;
  }

  &__actions {
    margin-bottom: 24px;
  }

  &__question {
    font-size: 16px;
    color: $color-neutral-700;
    text-align: center;
    margin-bottom: 20px;
  }

  &__buttons {
    display: flex;
    flex-direction: column;
    gap: 12px;
    max-width: 300px;
    margin: 0 auto;
  }

  &__pattern {
    border-top: 1px solid $color-neutral-200;
    padding-top: 20px;

    h4 {
      font-size: 16px;
      font-weight: 600;
      color: $color-neutral-800;
      margin-bottom: 12px;
    }
  }

  &__pattern-details {
    p {
      margin-bottom: 8px;
      font-size: 14px;
      color: $color-neutral-700;

      &:last-child {
        margin-bottom: 0;
      }

      strong {
        color: $color-neutral-800;
      }
    }
  }
}

@media (max-width: 480px) {
  .recurring-event-modal {
    padding: 16px;

    &__buttons {
      max-width: none;
    }
  }
}
</style>