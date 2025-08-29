<template>
  <div
    class="calendar-event"
    :class="{
      'calendar-event--compact': isCompact,
      'calendar-event--recurring': event.is_recurring,
      'calendar-event--dragging': isDragging,
    }"
    :style="eventStyle"
    :draggable="!readOnly"
    @click="handleClick"
    @dragstart="handleDragStart"
    @dragend="handleDragEnd"
  >
    <!-- Event indicator -->
    <div class="calendar-event__indicator" :style="{ backgroundColor: eventColor }"></div>
    
    <!-- Event content -->
    <div class="calendar-event__content">
      <div class="calendar-event__title">
        {{ eventTitle }}
      </div>
      
      <!-- Additional fields (non-compact mode) -->
      <div v-if="!isCompact && visibleFields.length > 0" class="calendar-event__fields">
        <div
          v-for="field in visibleFields"
          :key="field.id"
          class="calendar-event__field"
        >
          <span class="calendar-event__field-label">{{ field.name }}:</span>
          <span class="calendar-event__field-value">
            {{ getFieldValue(field) }}
          </span>
        </div>
      </div>
      
      <!-- Recurring indicator -->
      <div v-if="event.is_recurring" class="calendar-event__recurring-icon">
        <i class="iconoir-repeat"></i>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CalendarEvent',
  props: {
    event: {
      type: Object,
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
    isCompact: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      isDragging: false,
    }
  },
  computed: {
    eventTitle() {
      if (this.view.event_title_field && this.event[`field_${this.view.event_title_field}`]) {
        return this.event[`field_${this.view.event_title_field}`]
      }
      return this.event.title || `Event ${this.event.id}`
    },
    
    eventColor() {
      if (this.event.color) {
        return this.event.color
      }
      
      if (this.view.event_color_field) {
        const colorValue = this.event[`field_${this.view.event_color_field}`]
        return this.getColorFromValue(colorValue)
      }
      
      return '#3174ad' // Default blue
    },
    
    eventStyle() {
      return {
        borderLeftColor: this.eventColor,
      }
    },
    
    visibleFields() {
      return this.fields.filter(field => {
        // Don't show the title field or date field in additional fields
        if (field.id === this.view.event_title_field || field.id === this.view.date_field) {
          return false
        }
        
        const fieldOptions = this.$store.getters[
          this.storePrefix + 'view/calendar/getFieldOptions'
        ](field)
        
        return fieldOptions ? fieldOptions.show_in_event : false
      }).slice(0, 3) // Limit to 3 additional fields
    },
  },
  methods: {
    handleClick(event) {
      event.stopPropagation()
      this.$emit('click', this.event)
    },
    
    handleDragStart(event) {
      if (this.readOnly) {
        event.preventDefault()
        return
      }
      
      this.isDragging = true
      this.$emit('dragstart', this.event, event)
    },
    
    handleDragEnd(event) {
      this.isDragging = false
      this.$emit('dragend', event)
    },
    
    getFieldValue(field) {
      const value = this.event[`field_${field.id}`]
      
      if (value === null || value === undefined) {
        return '-'
      }
      
      // Handle different field types
      switch (field.type) {
        case 'date':
          return new Date(value).toLocaleDateString()
        case 'datetime':
          return new Date(value).toLocaleString()
        case 'number':
          return Number(value).toLocaleString()
        case 'boolean':
          return value ? this.$t('common.yes') : this.$t('common.no')
        case 'single_select':
          return value?.value || value
        case 'multiple_select':
          return Array.isArray(value) ? value.map(v => v.value || v).join(', ') : value
        default:
          return String(value).substring(0, 50) + (String(value).length > 50 ? '...' : '')
      }
    },
    
    getColorFromValue(value) {
      if (!value) {
        return '#3174ad'
      }
      
      // Handle single select options
      if (typeof value === 'object' && value.color) {
        return value.color
      }
      
      // Handle color field
      if (typeof value === 'string' && value.startsWith('#')) {
        return value
      }
      
      // Generate color from string
      return this.stringToColor(String(value))
    },
    
    stringToColor(str) {
      let hash = 0
      for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash)
      }
      
      const hue = hash % 360
      return `hsl(${hue}, 70%, 50%)`
    },
  },
}
</script>

<style lang="scss" scoped>
.calendar-event {
  position: relative;
  background-color: $color-neutral-0;
  border: 1px solid $color-neutral-200;
  border-left: 3px solid $color-primary-600;
  border-radius: 3px;
  padding: 4px 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 12px;
  line-height: 1.3;

  &:hover {
    background-color: $color-neutral-25;
    border-color: $color-neutral-300;
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  &--compact {
    padding: 2px 4px;
    font-size: 11px;
    min-height: 18px;
  }

  &--recurring {
    border-style: dashed;
    
    &::before {
      content: '';
      position: absolute;
      top: 2px;
      right: 2px;
      width: 4px;
      height: 4px;
      background-color: $color-warning-600;
      border-radius: 50%;
    }
  }

  &--dragging {
    opacity: 0.5;
    transform: rotate(2deg);
  }

  &__indicator {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 3px;
    background-color: $color-primary-600;
    border-radius: 3px 0 0 3px;
  }

  &__content {
    position: relative;
    z-index: 1;
  }

  &__title {
    font-weight: 500;
    color: $color-neutral-800;
    margin-bottom: 2px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__fields {
    margin-top: 4px;
  }

  &__field {
    display: flex;
    align-items: center;
    margin-bottom: 2px;
    font-size: 10px;

    &:last-child {
      margin-bottom: 0;
    }
  }

  &__field-label {
    color: $color-neutral-600;
    margin-right: 4px;
    font-weight: 500;
    min-width: 0;
    flex-shrink: 0;
  }

  &__field-value {
    color: $color-neutral-800;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    flex: 1;
  }

  &__recurring-icon {
    position: absolute;
    top: 2px;
    right: 2px;
    color: $color-warning-600;
    font-size: 10px;
  }
}

@media (max-width: 768px) {
  .calendar-event {
    padding: 2px 4px;
    font-size: 10px;

    &__title {
      margin-bottom: 0;
    }

    &__fields {
      display: none; // Hide additional fields on mobile
    }
  }
}
</style>