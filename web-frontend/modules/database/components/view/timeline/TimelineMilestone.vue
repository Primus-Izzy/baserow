<template>
  <div
    class="timeline-milestone"
    :class="{ 'timeline-milestone--active': milestone.is_active }"
    :style="getMilestoneStyle()"
    @click="$emit('milestone-clicked', milestone)"
    @mouseover="showTooltip = true"
    @mouseleave="showTooltip = false"
  >
    <!-- Milestone indicator -->
    <div class="timeline-milestone__indicator" :style="{ backgroundColor: milestone.color }">
      <i :class="milestone.icon || 'iconoir-flag'" class="timeline-milestone__icon"></i>
    </div>

    <!-- Milestone line -->
    <div class="timeline-milestone__line" :style="{ backgroundColor: milestone.color }"></div>

    <!-- Milestone label -->
    <div class="timeline-milestone__label">
      {{ milestone.name }}
    </div>

    <!-- Tooltip -->
    <div v-if="showTooltip" class="timeline-milestone__tooltip">
      <div class="milestone-tooltip">
        <div class="milestone-tooltip__title">{{ milestone.name }}</div>
        <div class="milestone-tooltip__date">{{ formatMilestoneDate() }}</div>
        <div v-if="milestone.description" class="milestone-tooltip__description">
          {{ milestone.description }}
        </div>
        <div v-if="milestone.row_id" class="milestone-tooltip__row">
          Linked to: {{ getLinkedRowTitle() }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TimelineMilestone',
  props: {
    milestone: {
      type: Object,
      required: true,
    },
    visibleDateRange: {
      type: Object,
      required: true,
    },
    zoomLevel: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      showTooltip: false,
    }
  },
  computed: {
    pixelsPerDay() {
      switch (this.zoomLevel) {
        case 'day': return 100
        case 'week': return 20
        case 'month': return 5
        case 'year': return 1
        default: return 20
      }
    },
    milestoneDate() {
      return this.getMilestoneDate()
    },
  },
  methods: {
    getMilestoneStyle() {
      const milestoneDate = this.getMilestoneDate()
      if (!milestoneDate) return { display: 'none' }
      
      const timelineStart = this.visibleDateRange.start
      const offset = ((milestoneDate - timelineStart) / (1000 * 60 * 60 * 24)) * this.pixelsPerDay + 200 // 200px for label column
      
      return {
        left: offset + 'px',
      }
    },
    getMilestoneDate() {
      if (this.milestone.row_id && this.milestone.date_field) {
        // Get the date from the linked row
        const row = this.getLinkedRow()
        if (row) {
          const fieldName = `field_${this.milestone.date_field.id}`
          return row[fieldName] ? new Date(row[fieldName]) : null
        }
      }
      
      // If no row is linked, milestone might have a fixed date
      return this.milestone.date ? new Date(this.milestone.date) : null
    },
    getLinkedRow() {
      if (!this.milestone.row_id) return null
      
      // This would need to be accessed from the parent component or store
      const allRows = this.$parent.allRows || []
      return allRows.find(row => row.id === this.milestone.row_id)
    },
    getLinkedRowTitle() {
      const row = this.getLinkedRow()
      if (!row) return 'Unknown'
      
      // Get the primary field or first text field
      const fields = this.$parent.fields || []
      const primaryField = fields.find(f => f.primary)
      if (primaryField) {
        return row[`field_${primaryField.id}`] || 'Untitled'
      }
      
      return `Row ${row.id}`
    },
    formatMilestoneDate() {
      const date = this.getMilestoneDate()
      if (!date) return 'No date'
      
      return date.toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })
    },
  },
}
</script>

<style lang="scss" scoped>
.timeline-milestone {
  position: absolute;
  top: 0;
  bottom: 0;
  cursor: pointer;
  z-index: 6;
  pointer-events: auto;

  &--active {
    .timeline-milestone__indicator {
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
    }
  }

  &__indicator {
    position: absolute;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: var(--color-primary);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 12px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: all 0.2s;
    z-index: 10;

    &:hover {
      transform: translateX(-50%) scale(1.1);
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
  }

  &__icon {
    font-size: 12px;
  }

  &__line {
    position: absolute;
    top: 44px;
    left: 50%;
    transform: translateX(-50%);
    width: 2px;
    bottom: 0;
    background: var(--color-primary);
    opacity: 0.6;
  }

  &__label {
    position: absolute;
    top: 50px;
    left: 50%;
    transform: translateX(-50%);
    background: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 500;
    color: var(--color-neutral-700);
    white-space: nowrap;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 1px solid var(--color-border);
    max-width: 120px;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  &__tooltip {
    position: absolute;
    top: -10px;
    left: 50%;
    transform: translateX(-50%) translateY(-100%);
    z-index: 20;
  }
}

.milestone-tooltip {
  background: var(--color-neutral-800);
  color: white;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  pointer-events: none;
  min-width: 200px;

  &__title {
    font-weight: 600;
    margin-bottom: 6px;
    font-size: 13px;
  }

  &__date {
    color: var(--color-neutral-300);
    margin-bottom: 6px;
    font-weight: 500;
  }

  &__description {
    color: var(--color-neutral-300);
    margin-bottom: 6px;
    line-height: 1.4;
  }

  &__row {
    font-size: 11px;
    color: var(--color-neutral-400);
    font-style: italic;
  }

  // Tooltip arrow
  &::after {
    content: '';
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: 6px solid transparent;
    border-top-color: var(--color-neutral-800);
  }
}

// Mobile optimizations
@media (max-width: 768px) {
  .timeline-milestone {
    &__indicator {
      width: 20px;
      height: 20px;
      font-size: 10px;
    }

    &__label {
      font-size: 10px;
      padding: 2px 6px;
      max-width: 80px;
    }
  }

  .milestone-tooltip {
    min-width: 150px;
    padding: 8px 12px;
    font-size: 11px;

    &__title {
      font-size: 12px;
    }
  }
}
</style>