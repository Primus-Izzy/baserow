<template>
  <div
    :class="[
      'delay-node',
      { selected: selected, error: hasError, configured: isConfigured },
    ]"
  >
    <div class="node-header">
      <div class="node-icon">
        <i class="iconoir-timer"></i>
      </div>
      <div class="node-title">
        <h4>{{ $t('visualBuilder.delay') }}</h4>
        <span class="node-type">{{ $t('visualBuilder.timing') }}</span>
      </div>
      <div class="node-actions">
        <button
          @click="$emit('configure', id)"
          class="action-btn configure-btn"
          :title="$t('visualBuilder.configure')"
        >
          <i class="iconoir-settings"></i>
        </button>
        <button
          v-if="!data.readOnly"
          @click="$emit('delete', id)"
          class="action-btn delete-btn"
          :title="$t('visualBuilder.delete')"
        >
          <i class="iconoir-bin"></i>
        </button>
      </div>
    </div>

    <div class="node-content">
      <div v-if="delayConfig" class="delay-summary">
        <div class="delay-type">
          <span class="label">{{ $t('visualBuilder.delayType') }}:</span>
          <span class="value">{{
            formatDelayType(delayConfig.delay_type)
          }}</span>
        </div>

        <div v-if="delayConfig.delay_type === 'fixed'" class="delay-duration">
          <span class="label">{{ $t('visualBuilder.duration') }}:</span>
          <span class="value">{{
            formatDuration(delayConfig.delay_duration)
          }}</span>
        </div>

        <div
          v-else-if="delayConfig.delay_type === 'until_date'"
          class="delay-until"
        >
          <span class="label">{{ $t('visualBuilder.until') }}:</span>
          <span class="value">{{
            truncateText(delayConfig.delay_until_template, 25)
          }}</span>
        </div>

        <div
          v-else-if="delayConfig.delay_type === 'until_condition'"
          class="delay-condition"
        >
          <span class="label">{{ $t('visualBuilder.condition') }}:</span>
          <span class="value">{{
            truncateText(delayConfig.condition_template, 25)
          }}</span>
          <div v-if="delayConfig.max_wait_duration" class="max-wait">
            <span class="label">{{ $t('visualBuilder.maxWait') }}:</span>
            <span class="value">{{
              formatDuration(delayConfig.max_wait_duration)
            }}</span>
          </div>
        </div>

        <div class="delay-visualization">
          <div class="timeline">
            <div class="timeline-start">
              <i class="iconoir-play"></i>
            </div>
            <div class="timeline-delay">
              <div class="delay-indicator">
                <i class="iconoir-timer"></i>
                <span>{{ getDelayDisplayText() }}</span>
              </div>
            </div>
            <div class="timeline-end">
              <i class="iconoir-check"></i>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="not-configured">
        <i class="iconoir-warning-triangle"></i>
        <span>{{ $t('visualBuilder.notConfigured') }}</span>
      </div>
    </div>

    <div class="node-status">
      <div v-if="hasError" class="status-indicator error">
        <i class="iconoir-warning-triangle"></i>
        <span>{{ $t('visualBuilder.error') }}</span>
      </div>
      <div v-else-if="isConfigured" class="status-indicator success">
        <i class="iconoir-check"></i>
        <span>{{ $t('visualBuilder.configured') }}</span>
      </div>
      <div v-else class="status-indicator warning">
        <i class="iconoir-info-circle"></i>
        <span>{{ $t('visualBuilder.needsConfig') }}</span>
      </div>
    </div>

    <!-- Connection Points -->
    <div class="connection-point input" data-connection="input">
      <div class="connection-dot"></div>
    </div>
    <div class="connection-point output" data-connection="output">
      <div class="connection-dot"></div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DelayNode',
  props: {
    id: {
      type: String,
      required: true,
    },
    data: {
      type: Object,
      required: true,
    },
    selected: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    delayConfig() {
      return this.data.service || null
    },

    isConfigured() {
      return (
        this.delayConfig &&
        this.delayConfig.delay_type &&
        this.isDelayConfigValid()
      )
    },

    hasError() {
      return this.delayConfig && !this.isDelayConfigValid()
    },
  },
  methods: {
    isDelayConfigValid() {
      if (!this.delayConfig) return false

      const {
        delay_type,
        delay_duration,
        delay_until_template,
        condition_template,
      } = this.delayConfig

      switch (delay_type) {
        case 'fixed':
          return !!delay_duration
        case 'until_date':
          return !!delay_until_template
        case 'until_condition':
          return !!condition_template
        default:
          return false
      }
    },

    formatDelayType(type) {
      const typeMap = {
        fixed: this.$t('visualBuilder.fixedDuration'),
        until_date: this.$t('visualBuilder.untilDate'),
        until_condition: this.$t('visualBuilder.untilCondition'),
      }
      return typeMap[type] || type
    },

    formatDuration(duration) {
      if (!duration) return ''

      // Parse ISO 8601 duration format (e.g., "PT1H30M" for 1 hour 30 minutes)
      const match = duration.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/)
      if (!match) return duration

      const hours = parseInt(match[1]) || 0
      const minutes = parseInt(match[2]) || 0
      const seconds = parseInt(match[3]) || 0

      const parts = []
      if (hours > 0) parts.push(`${hours}h`)
      if (minutes > 0) parts.push(`${minutes}m`)
      if (seconds > 0) parts.push(`${seconds}s`)

      return parts.join(' ') || '0s'
    },

    truncateText(text, maxLength) {
      if (!text) return ''
      return text.length > maxLength
        ? `${text.substring(0, maxLength)}...`
        : text
    },

    getDelayDisplayText() {
      if (!this.delayConfig) return ''

      const {
        delay_type,
        delay_duration,
        delay_until_template,
        condition_template,
      } = this.delayConfig

      switch (delay_type) {
        case 'fixed':
          return this.formatDuration(delay_duration)
        case 'until_date':
          return this.$t('visualBuilder.untilDate')
        case 'until_condition':
          return this.$t('visualBuilder.untilCondition')
        default:
          return ''
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.delay-node {
  min-width: 320px;
  max-width: 380px;
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
  border: 2px solid transparent;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  color: #333;
  position: relative;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
  }

  &.selected {
    border-color: #ffd700;
    box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.3);
  }

  &.error {
    border-color: #ff6b6b;
  }

  &.configured {
    border-color: #51cf66;
  }
}

.node-header {
  display: flex;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.node-icon {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 0.75rem;

  i {
    font-size: 1.5rem;
    color: #ff6b35;
  }
}

.node-title {
  flex: 1;

  h4 {
    margin: 0;
    font-size: 1rem;
    font-weight: 600;
    color: #333;
  }

  .node-type {
    font-size: 0.75rem;
    opacity: 0.7;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #666;
  }
}

.node-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.3);
  border: none;
  border-radius: 6px;
  color: #333;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.5);
  }

  &.delete-btn:hover {
    background: #ff6b6b;
    color: white;
  }

  i {
    font-size: 0.9rem;
  }
}

.node-content {
  padding: 1rem;
  min-height: 100px;
}

.delay-summary {
  .delay-type,
  .delay-duration,
  .delay-until,
  .delay-condition {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.75rem;
    font-size: 0.9rem;

    .label {
      font-weight: 600;
      color: #666;
    }

    .value {
      font-weight: 500;
      color: #333;
      text-align: right;
      max-width: 180px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }

  .max-wait {
    margin-top: 0.5rem;
    padding-top: 0.5rem;
    border-top: 1px solid rgba(0, 0, 0, 0.1);
    display: flex;
    justify-content: space-between;
    font-size: 0.85rem;

    .label {
      color: #888;
    }

    .value {
      color: #666;
    }
  }
}

.delay-visualization {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.timeline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;

  &::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(to right, #ff6b35, #ffa726, #ff6b35);
    z-index: 1;
  }
}

.timeline-start,
.timeline-end {
  width: 32px;
  height: 32px;
  background: white;
  border: 2px solid #ff6b35;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
  position: relative;

  i {
    font-size: 1rem;
    color: #ff6b35;
  }
}

.timeline-delay {
  flex: 1;
  display: flex;
  justify-content: center;
  z-index: 2;
  position: relative;
}

.delay-indicator {
  background: white;
  border: 2px solid #ffa726;
  border-radius: 20px;
  padding: 0.5rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

  i {
    font-size: 1rem;
    color: #ffa726;
    animation: pulse 2s infinite;
  }

  span {
    font-size: 0.8rem;
    font-weight: 600;
    color: #333;
  }
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.not-configured {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  opacity: 0.7;
  font-size: 0.9rem;
  color: #666;

  i {
    font-size: 1.1rem;
  }
}

.node-status {
  padding: 0.75rem 1rem;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  font-weight: 500;

  &.success {
    color: #51cf66;
  }

  &.error {
    color: #ff6b6b;
  }

  &.warning {
    color: #ffa726;
  }

  i {
    font-size: 0.9rem;
  }
}

.connection-point {
  position: absolute;
  width: 16px;
  height: 16px;

  &.input {
    top: -8px;
    left: 50%;
    transform: translateX(-50%);
  }

  &.output {
    bottom: -8px;
    left: 50%;
    transform: translateX(-50%);
  }
}

.connection-dot {
  width: 100%;
  height: 100%;
  background: white;
  border: 2px solid #ff6b35;
  border-radius: 50%;
  transition: all 0.2s ease;

  &:hover {
    transform: scale(1.2);
    box-shadow: 0 0 8px rgba(255, 107, 53, 0.6);
  }
}
</style>
