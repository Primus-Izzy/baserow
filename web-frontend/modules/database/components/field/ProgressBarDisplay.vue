<template>
  <div
    class="progress-bar-display"
    :class="{ 'progress-bar-display--mobile': isMobile }"
  >
    <div
      class="progress-bar-container"
      :style="containerStyle"
      role="progressbar"
      :aria-valuenow="percentage"
      :aria-valuemin="0"
      :aria-valuemax="100"
      :aria-valuetext="`${percentage}% complete`"
      :aria-label="`Progress: ${percentage}%`"
    >
      <div class="progress-bar-fill" :style="fillStyle" />
      <div
        v-if="showPercentage && field.show_percentage"
        class="progress-bar-text"
        :style="textStyle"
        aria-hidden="true"
      >
        {{ percentageText }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProgressBarDisplay',
  props: {
    value: {
      type: [Number, String],
      default: null,
    },
    field: {
      type: Object,
      required: true,
    },
    showPercentage: {
      type: Boolean,
      default: true,
    },
    isMobile: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    /**
     * Calculate the percentage value based on field configuration
     */
    percentage() {
      if (
        this.value === null ||
        this.value === undefined ||
        this.value === ''
      ) {
        return 0
      }

      const numValue = parseFloat(this.value)
      if (isNaN(numValue)) {
        return 0
      }

      const range = this.field.max_value - this.field.min_value
      if (range <= 0) {
        return 0
      }

      const clampedValue = Math.max(
        this.field.min_value,
        Math.min(this.field.max_value, numValue)
      )
      const percentage = ((clampedValue - this.field.min_value) / range) * 100
      return Math.round(percentage * 100) / 100 // Round to 2 decimal places
    },
    /**
     * Get the color scheme configuration
     */
    colorScheme() {
      const colorSchemes = {
        default: { start: '#3b82f6', end: '#1d4ed8' },
        success: { start: '#10b981', end: '#059669' },
        warning: { start: '#f59e0b', end: '#d97706' },
        danger: { start: '#ef4444', end: '#dc2626' },
        custom: {
          start: this.field.custom_color_start || '#3b82f6',
          end: this.field.custom_color_end || '#1d4ed8',
        },
      }

      return colorSchemes[this.field.color_scheme] || colorSchemes.default
    },
    /**
     * Container styles for the progress bar
     */
    containerStyle() {
      return {
        height: this.isMobile ? '24px' : '20px',
        backgroundColor: '#e5e7eb',
        borderRadius: '10px',
        position: 'relative',
        overflow: 'hidden',
        minWidth: this.isMobile ? '120px' : '100px',
      }
    },
    /**
     * Fill styles for the progress bar
     */
    fillStyle() {
      const gradient = `linear-gradient(90deg, ${this.colorScheme.start} 0%, ${this.colorScheme.end} 100%)`

      return {
        width: `${this.percentage}%`,
        height: '100%',
        background: gradient,
        borderRadius: '10px',
        transition: 'width 0.3s ease-in-out',
        position: 'relative',
      }
    },
    /**
     * Text styles for the percentage display
     */
    textStyle() {
      const isLightBackground = this.percentage < 50

      return {
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        fontSize: this.isMobile ? '11px' : '10px',
        fontWeight: '600',
        color: isLightBackground ? '#374151' : '#ffffff',
        textShadow: isLightBackground ? 'none' : '0 1px 2px rgba(0, 0, 0, 0.3)',
        whiteSpace: 'nowrap',
        zIndex: 1,
      }
    },
    /**
     * Formatted percentage text
     */
    percentageText() {
      return `${this.percentage}%`
    },
  },
}
</script>

<style lang="scss" scoped>
.progress-bar-display {
  display: flex;
  align-items: center;
  width: 100%;

  &--mobile {
    .progress-bar-container {
      min-width: 120px;
      height: 24px;
    }
  }
}

.progress-bar-container {
  position: relative;
  flex: 1;
  max-width: 200px;
}

.progress-bar-fill {
  position: relative;

  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(
      90deg,
      rgba(255, 255, 255, 0.2) 0%,
      rgba(255, 255, 255, 0.1) 50%,
      rgba(255, 255, 255, 0.2) 100%
    );
    border-radius: inherit;
  }
}

.progress-bar-text {
  user-select: none;
  pointer-events: none;
}

// Responsive adjustments
@media (max-width: 768px) {
  .progress-bar-display {
    .progress-bar-container {
      min-width: 100px;
      height: 22px;
    }

    .progress-bar-text {
      font-size: 10px;
    }
  }
}
</style>
