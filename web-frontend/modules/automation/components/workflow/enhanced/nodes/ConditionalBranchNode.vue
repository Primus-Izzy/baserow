<template>
  <div
    :class="[
      'conditional-branch-node',
      { 'selected': selected, 'error': hasError, 'configured': isConfigured }
    ]"
  >
    <div class="node-header">
      <div class="node-icon">
        <i class="iconoir-git-fork"></i>
      </div>
      <div class="node-title">
        <h4>{{ $t('visualBuilder.conditionalBranch') }}</h4>
        <span class="node-type">{{ $t('visualBuilder.logic') }}</span>
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
      <div v-if="conditionConfig" class="condition-summary">
        <div class="condition-display">
          <span class="condition-text">{{ conditionText }}</span>
        </div>
        <div class="branch-paths">
          <div class="branch-path true-path">
            <i class="iconoir-check"></i>
            <span>{{ $t('visualBuilder.ifTrue') }}</span>
          </div>
          <div class="branch-path false-path">
            <i class="iconoir-cancel"></i>
            <span>{{ $t('visualBuilder.ifFalse') }}</span>
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
    <div class="connection-point output-true" data-connection="output-true">
      <div class="connection-dot true"></div>
      <span class="connection-label">{{ $t('visualBuilder.true') }}</span>
    </div>
    <div class="connection-point output-false" data-connection="output-false">
      <div class="connection-dot false"></div>
      <span class="connection-label">{{ $t('visualBuilder.false') }}</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ConditionalBranchNode',
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
    conditionConfig() {
      return this.data.service || null
    },
    
    isConfigured() {
      return this.conditionConfig && 
             this.conditionConfig.condition_template &&
             this.conditionConfig.condition_type
    },
    
    hasError() {
      // Check if condition configuration is invalid
      return this.conditionConfig && 
             (!this.conditionConfig.condition_template || 
              !this.conditionConfig.condition_type)
    },
    
    conditionText() {
      if (!this.conditionConfig) return ''
      
      const template = this.conditionConfig.condition_template || ''
      const type = this.conditionConfig.condition_type || 'equals'
      const comparison = this.conditionConfig.comparison_value_template || ''
      
      // Create a human-readable condition text
      if (template && comparison) {
        const operatorMap = {
          'equals': '=',
          'not_equals': '≠',
          'greater_than': '>',
          'less_than': '<',
          'contains': 'contains',
          'starts_with': 'starts with',
          'ends_with': 'ends with',
          'is_empty': 'is empty',
          'is_not_empty': 'is not empty',
        }
        
        const operator = operatorMap[type] || type
        
        if (type === 'is_empty' || type === 'is_not_empty') {
          return `${template} ${operator}`
        }
        
        return `${template} ${operator} ${comparison}`
      }
      
      return template || 'No condition set'
    },
  },
}
</script>

<style lang="scss" scoped>
.conditional-branch-node {
  min-width: 300px;
  max-width: 350px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
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
  min-height: 80px;
}

.condition-summary {
  .condition-display {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 6px;
    padding: 0.75rem;
    margin-bottom: 1rem;
    
    .condition-text {
      font-size: 0.9rem;
      font-weight: 500;
      font-family: monospace;
      word-break: break-all;
    }
  }
  
  .branch-paths {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
  }
  
  .branch-path {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.8rem;
    font-weight: 500;
    
    &.true-path {
      color: #51cf66;
    }
    
    &.false-path {
      color: #ff6b6b;
    }
    
    i {
      font-size: 1rem;
    }
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
  display: flex;
  align-items: center;
  gap: 0.25rem;
  
  &.input {
    top: -8px;
    left: 50%;
    transform: translateX(-50%);
  }
  
  &.output-true {
    bottom: -8px;
    left: 25%;
    transform: translateX(-50%);
  }
  
  &.output-false {
    bottom: -8px;
    right: 25%;
    transform: translateX(50%);
  }
}

.connection-dot {
  width: 16px;
  height: 16px;
  background: white;
  border: 2px solid #f093fb;
  border-radius: 50%;
  transition: all 0.2s ease;
  
  &.true {
    border-color: #51cf66;
  }
  
  &.false {
    border-color: #ff6b6b;
  }
  
  &:hover {
    transform: scale(1.2);
    box-shadow: 0 0 8px rgba(255, 255, 255, 0.6);
  }
}

.connection-label {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}
</style>