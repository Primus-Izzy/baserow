<template>
  <div
    :class="[
      'enhanced-trigger-node',
      { 'selected': selected, 'error': hasError, 'configured': isConfigured }
    ]"
  >
    <div class="node-header">
      <div class="node-icon">
        <i :class="nodeType.iconClass || 'iconoir-flash'"></i>
      </div>
      <div class="node-title">
        <h4>{{ nodeType.name }}</h4>
        <span class="node-type">{{ $t('visualBuilder.trigger') }}</span>
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
      <div v-if="triggerConfig" class="trigger-summary">
        <div class="config-item" v-for="(value, key) in displayConfig" :key="key">
          <span class="config-label">{{ key }}:</span>
          <span class="config-value">{{ value }}</span>
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
    <div class="connection-point output" data-connection="output">
      <div class="connection-dot"></div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EnhancedTriggerNode',
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
    nodeType() {
      return this.$registry.get('node', this.data.type) || {
        name: 'Unknown Trigger',
        iconClass: 'iconoir-flash',
      }
    },
    
    triggerConfig() {
      return this.data.service || null
    },
    
    isConfigured() {
      return this.triggerConfig && Object.keys(this.triggerConfig).length > 0
    },
    
    hasError() {
      return this.nodeType.isInError && this.nodeType.isInError({ service: this.triggerConfig })
    },
    
    displayConfig() {
      if (!this.triggerConfig) return {}
      
      const config = {}
      
      // Display key configuration items based on trigger type
      if (this.data.type === 'date_based_trigger') {
        if (this.triggerConfig.date_field_id) {
          config['Date Field'] = this.getFieldName(this.triggerConfig.date_field_id)
        }
        if (this.triggerConfig.condition_type) {
          config['Condition'] = this.triggerConfig.condition_type.replace('_', ' ')
        }
        if (this.triggerConfig.days_offset) {
          config['Days Offset'] = this.triggerConfig.days_offset
        }
      } else if (this.data.type === 'webhook_trigger') {
        if (this.triggerConfig.webhook_url_path) {
          config['Webhook Path'] = this.triggerConfig.webhook_url_path
        }
        if (this.triggerConfig.auth_type) {
          config['Auth Type'] = this.triggerConfig.auth_type
        }
      } else if (this.data.type === 'linked_record_change_trigger') {
        if (this.triggerConfig.link_field_id) {
          config['Link Field'] = this.getFieldName(this.triggerConfig.link_field_id)
        }
        if (this.triggerConfig.change_type) {
          config['Change Type'] = this.triggerConfig.change_type.replace('_', ' ')
        }
      }
      
      return config
    },
  },
  methods: {
    getFieldName(fieldId) {
      // This would typically fetch the field name from the store
      // For now, return a placeholder
      return `Field ${fieldId}`
    },
  },
}
</script>

<style lang="scss" scoped>
.enhanced-trigger-node {
  min-width: 280px;
  max-width: 320px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: 2px solid transparent;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  color: white;
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
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.node-icon {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 0.75rem;
  
  i {
    font-size: 1.5rem;
  }
}

.node-title {
  flex: 1;
  
  h4 {
    margin: 0;
    font-size: 1rem;
    font-weight: 600;
  }
  
  .node-type {
    font-size: 0.75rem;
    opacity: 0.8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
}

.node-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.3);
  }
  
  &.delete-btn:hover {
    background: #ff6b6b;
  }
  
  i {
    font-size: 0.9rem;
  }
}

.node-content {
  padding: 1rem;
  min-height: 60px;
}

.trigger-summary {
  .config-item {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  .config-label {
    opacity: 0.8;
    font-weight: 500;
  }
  
  .config-value {
    font-weight: 600;
    text-align: right;
  }
}

.not-configured {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  opacity: 0.7;
  font-size: 0.9rem;
  
  i {
    font-size: 1.1rem;
  }
}

.node-status {
  padding: 0.75rem 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
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
    color: #ffd43b;
  }
  
  i {
    font-size: 0.9rem;
  }
}

.connection-point {
  position: absolute;
  width: 16px;
  height: 16px;
  
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
  border: 2px solid #667eea;
  border-radius: 50%;
  transition: all 0.2s ease;
  
  &:hover {
    transform: scale(1.2);
    box-shadow: 0 0 8px rgba(255, 255, 255, 0.6);
  }
}
</style>