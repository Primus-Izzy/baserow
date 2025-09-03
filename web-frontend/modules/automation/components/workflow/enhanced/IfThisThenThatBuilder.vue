<template>
  <div class="ifttt-builder">
    <div class="builder-header">
      <h3>{{ $t('visualBuilder.iftttBuilder') }}</h3>
      <p class="builder-description">
        {{ $t('visualBuilder.iftttDescription') }}
      </p>
    </div>

    <div class="rule-builder">
      <!-- IF Section -->
      <div class="rule-section if-section">
        <div class="section-header">
          <div class="section-icon if-icon">
            <i class="iconoir-flash"></i>
          </div>
          <h4>{{ $t('visualBuilder.if') }}</h4>
        </div>

        <div class="trigger-selector">
          <div v-if="!selectedTrigger" class="selector-placeholder">
            <button @click="showTriggerSelector = true" class="select-btn">
              <i class="iconoir-plus"></i>
              {{ $t('visualBuilder.chooseTrigger') }}
            </button>
          </div>

          <div v-else class="selected-trigger">
            <div class="trigger-card">
              <div class="trigger-info">
                <i :class="selectedTrigger.iconClass"></i>
                <div class="trigger-details">
                  <h5>{{ selectedTrigger.name }}</h5>
                  <p>{{ selectedTrigger.description }}</p>
                </div>
              </div>
              <button @click="removeTrigger" class="remove-btn">
                <i class="iconoir-cancel"></i>
              </button>
            </div>

            <!-- Trigger Configuration -->
            <div class="trigger-config">
              <component
                :is="selectedTrigger.configComponent"
                v-if="selectedTrigger.configComponent"
                v-model="triggerConfiguration"
                :trigger-type="selectedTrigger"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- THEN Section -->
      <div class="rule-section then-section">
        <div class="section-header">
          <div class="section-icon then-icon">
            <i class="iconoir-play"></i>
          </div>
          <h4>{{ $t('visualBuilder.then') }}</h4>
        </div>

        <div class="actions-list">
          <div
            v-for="(action, index) in selectedActions"
            :key="index"
            class="action-item"
          >
            <div class="action-card">
              <div class="action-info">
                <i :class="action.iconClass"></i>
                <div class="action-details">
                  <h5>{{ action.name }}</h5>
                  <p>{{ action.description }}</p>
                </div>
              </div>
              <div class="action-controls">
                <button @click="configureAction(index)" class="config-btn">
                  <i class="iconoir-settings"></i>
                </button>
                <button @click="removeAction(index)" class="remove-btn">
                  <i class="iconoir-cancel"></i>
                </button>
              </div>
            </div>

            <!-- Action Configuration -->
            <div v-if="action.showConfig" class="action-config">
              <component
                :is="action.configComponent"
                v-if="action.configComponent"
                v-model="action.configuration"
                :action-type="action"
              />
            </div>
          </div>

          <div class="add-action">
            <button @click="showActionSelector = true" class="select-btn">
              <i class="iconoir-plus"></i>
              {{ $t('visualBuilder.addAction') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Rule Preview -->
    <div class="rule-preview">
      <h4>{{ $t('visualBuilder.rulePreview') }}</h4>
      <div class="preview-text">
        <span class="if-text">
          {{ $t('visualBuilder.if') }}
          <strong>{{
            selectedTrigger?.name || $t('visualBuilder.somethingHappens')
          }}</strong>
        </span>
        <span class="then-text">
          {{ $t('visualBuilder.then') }}
          <span v-if="selectedActions.length === 0">
            <strong>{{ $t('visualBuilder.doSomething') }}</strong>
          </span>
          <span v-else>
            <strong v-for="(action, index) in selectedActions" :key="index">
              {{ action.name
              }}{{ index < selectedActions.length - 1 ? ', ' : '' }}
            </strong>
          </span>
        </span>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="builder-actions">
      <button
        @click="saveRule"
        :disabled="!canSaveRule"
        class="btn btn-primary"
      >
        <i class="iconoir-check"></i>
        {{ $t('visualBuilder.saveRule') }}
      </button>
      <button
        @click="testRule"
        :disabled="!canTestRule"
        class="btn btn-secondary"
      >
        <i class="iconoir-play"></i>
        {{ $t('visualBuilder.testRule') }}
      </button>
      <button @click="resetBuilder" class="btn btn-ghost">
        <i class="iconoir-refresh"></i>
        {{ $t('visualBuilder.reset') }}
      </button>
    </div>

    <!-- Trigger Selector Modal -->
    <Modal v-if="showTriggerSelector" @close="showTriggerSelector = false">
      <template #header>
        <h3>{{ $t('visualBuilder.selectTrigger') }}</h3>
      </template>
      <template #content>
        <TriggerSelector
          @select="selectTrigger"
          @close="showTriggerSelector = false"
        />
      </template>
    </Modal>

    <!-- Action Selector Modal -->
    <Modal v-if="showActionSelector" @close="showActionSelector = false">
      <template #header>
        <h3>{{ $t('visualBuilder.selectAction') }}</h3>
      </template>
      <template #content>
        <ActionSelector
          @select="selectAction"
          @close="showActionSelector = false"
        />
      </template>
    </Modal>
  </div>
</template>

<script>
import Modal from '@baserow/modules/core/components/Modal'
import TriggerSelector from './selectors/TriggerSelector.vue'
import ActionSelector from './selectors/ActionSelector.vue'

export default {
  name: 'IfThisThenThatBuilder',
  components: {
    Modal,
    TriggerSelector,
    ActionSelector,
  },
  props: {
    workflow: {
      type: Object,
      required: true,
    },
    existingRule: {
      type: Object,
      default: null,
    },
  },
  data() {
    return {
      selectedTrigger: null,
      triggerConfiguration: {},
      selectedActions: [],
      showTriggerSelector: false,
      showActionSelector: false,
    }
  },
  computed: {
    canSaveRule() {
      return (
        this.selectedTrigger &&
        this.selectedActions.length > 0 &&
        this.isConfigurationValid()
      )
    },

    canTestRule() {
      return this.canSaveRule
    },
  },
  methods: {
    selectTrigger(trigger) {
      this.selectedTrigger = {
        ...trigger,
        configComponent: this.getTriggerConfigComponent(trigger.type),
      }
      this.triggerConfiguration = {}
      this.showTriggerSelector = false
    },

    removeTrigger() {
      this.selectedTrigger = null
      this.triggerConfiguration = {}
    },

    selectAction(action) {
      const actionWithConfig = {
        ...action,
        configComponent: this.getActionConfigComponent(action.type),
        configuration: {},
        showConfig: false,
      }

      this.selectedActions.push(actionWithConfig)
      this.showActionSelector = false
    },

    removeAction(index) {
      this.selectedActions.splice(index, 1)
    },

    configureAction(index) {
      this.selectedActions[index].showConfig =
        !this.selectedActions[index].showConfig
    },

    getTriggerConfigComponent(triggerType) {
      // Map trigger types to their configuration components
      const componentMap = {
        date_based_trigger: 'DateBasedTriggerConfig',
        webhook_trigger: 'WebhookTriggerConfig',
        linked_record_change_trigger: 'LinkedRecordChangeTriggerConfig',
        conditional_trigger: 'ConditionalTriggerConfig',
        rows_created: 'RowsCreatedTriggerConfig',
        rows_updated: 'RowsUpdatedTriggerConfig',
        rows_deleted: 'RowsDeletedTriggerConfig',
      }

      return componentMap[triggerType] || null
    },

    getActionConfigComponent(actionType) {
      // Map action types to their configuration components
      const componentMap = {
        notification_action: 'NotificationActionConfig',
        webhook_action: 'WebhookActionConfig',
        status_change_action: 'StatusChangeActionConfig',
        conditional_branch: 'ConditionalBranchConfig',
        delay: 'DelayActionConfig',
        create_row: 'CreateRowActionConfig',
        update_row: 'UpdateRowActionConfig',
        delete_row: 'DeleteRowActionConfig',
      }

      return componentMap[actionType] || null
    },

    isConfigurationValid() {
      // Check if trigger configuration is valid
      if (this.selectedTrigger && this.selectedTrigger.requiresConfig) {
        if (
          !this.triggerConfiguration ||
          Object.keys(this.triggerConfiguration).length === 0
        ) {
          return false
        }
      }

      // Check if all actions are properly configured
      for (const action of this.selectedActions) {
        if (action.requiresConfig) {
          if (
            !action.configuration ||
            Object.keys(action.configuration).length === 0
          ) {
            return false
          }
        }
      }

      return true
    },

    async saveRule() {
      try {
        const ruleData = {
          trigger: {
            type: this.selectedTrigger.type,
            configuration: this.triggerConfiguration,
          },
          actions: this.selectedActions.map((action) => ({
            type: action.type,
            configuration: action.configuration,
          })),
        }

        await this.$store.dispatch('automationWorkflow/createFromIftttRule', {
          workflowId: this.workflow.id,
          ruleData,
        })

        this.$emit('rule-saved', ruleData)
        this.resetBuilder()

        this.$toast.success(this.$t('visualBuilder.ruleSaved'))
      } catch (error) {
        console.error('Failed to save rule:', error)
        this.$toast.error(this.$t('visualBuilder.ruleSaveFailed'))
      }
    },

    async testRule() {
      try {
        const ruleData = {
          trigger: {
            type: this.selectedTrigger.type,
            configuration: this.triggerConfiguration,
          },
          actions: this.selectedActions.map((action) => ({
            type: action.type,
            configuration: action.configuration,
          })),
        }

        const result = await this.$store.dispatch(
          'automationWorkflow/testIftttRule',
          {
            workflowId: this.workflow.id,
            ruleData,
          }
        )

        this.$emit('rule-tested', result)
        this.$toast.success(this.$t('visualBuilder.ruleTestSuccess'))
      } catch (error) {
        console.error('Failed to test rule:', error)
        this.$toast.error(this.$t('visualBuilder.ruleTestFailed'))
      }
    },

    resetBuilder() {
      this.selectedTrigger = null
      this.triggerConfiguration = {}
      this.selectedActions = []
      this.showTriggerSelector = false
      this.showActionSelector = false
    },

    loadExistingRule() {
      if (this.existingRule) {
        // Load existing rule data
        if (this.existingRule.trigger) {
          this.selectedTrigger = {
            type: this.existingRule.trigger.type,
            name: this.getTriggerName(this.existingRule.trigger.type),
            configComponent: this.getTriggerConfigComponent(
              this.existingRule.trigger.type
            ),
          }
          this.triggerConfiguration =
            this.existingRule.trigger.configuration || {}
        }

        if (this.existingRule.actions) {
          this.selectedActions = this.existingRule.actions.map((action) => ({
            type: action.type,
            name: this.getActionName(action.type),
            configComponent: this.getActionConfigComponent(action.type),
            configuration: action.configuration || {},
            showConfig: false,
          }))
        }
      }
    },

    getTriggerName(triggerType) {
      const triggerTypes = this.$registry
        .getOrderedList('node')
        .filter((type) => type.isTrigger)
      const trigger = triggerTypes.find((t) => t.getType() === triggerType)
      return trigger ? trigger.name : triggerType
    },

    getActionName(actionType) {
      const actionTypes = this.$registry
        .getOrderedList('node')
        .filter((type) => type.isWorkflowAction)
      const action = actionTypes.find((a) => a.getType() === actionType)
      return action ? action.name : actionType
    },
  },

  mounted() {
    this.loadExistingRule()
  },

  watch: {
    existingRule: {
      handler() {
        this.loadExistingRule()
      },
      deep: true,
    },
  },
}
</script>

<style lang="scss" scoped>
.ifttt-builder {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.builder-header {
  text-align: center;
  margin-bottom: 2rem;

  h3 {
    margin: 0 0 0.5rem 0;
    font-size: 1.5rem;
    font-weight: 700;
    color: #333;
  }

  .builder-description {
    margin: 0;
    color: #666;
    font-size: 1rem;
  }
}

.rule-builder {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  margin-bottom: 2rem;
}

.rule-section {
  border: 2px solid #e9ecef;
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;

  &.if-section {
    border-color: #667eea;
    background: linear-gradient(
      135deg,
      rgba(102, 126, 234, 0.05) 0%,
      rgba(118, 75, 162, 0.05) 100%
    );
  }

  &.then-section {
    border-color: #4facfe;
    background: linear-gradient(
      135deg,
      rgba(79, 172, 254, 0.05) 0%,
      rgba(0, 242, 254, 0.05) 100%
    );
  }
}

.section-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;

  h4 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
  }
}

.section-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;

  &.if-icon {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
  }

  &.then-icon {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    color: white;
  }

  i {
    font-size: 1.5rem;
  }
}

.selector-placeholder {
  text-align: center;
  padding: 2rem;
}

.select-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 2rem;
  background: #f8f9fa;
  border: 2px dashed #dee2e6;
  border-radius: 8px;
  color: #6c757d;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background: #e9ecef;
    border-color: #007bff;
    color: #007bff;
  }

  i {
    font-size: 1.2rem;
  }
}

.selected-trigger,
.action-item {
  margin-bottom: 1rem;
}

.trigger-card,
.action-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.trigger-info,
.action-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;

  i {
    font-size: 1.5rem;
    color: #007bff;
  }
}

.trigger-details,
.action-details {
  h5 {
    margin: 0 0 0.25rem 0;
    font-size: 1rem;
    font-weight: 600;
    color: #333;
  }

  p {
    margin: 0;
    font-size: 0.9rem;
    color: #666;
  }
}

.action-controls {
  display: flex;
  gap: 0.5rem;
}

.config-btn,
.remove-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;

  i {
    font-size: 1rem;
  }
}

.config-btn {
  background: #e9ecef;
  color: #6c757d;

  &:hover {
    background: #007bff;
    color: white;
  }
}

.remove-btn {
  background: #f8d7da;
  color: #721c24;

  &:hover {
    background: #dc3545;
    color: white;
  }
}

.trigger-config,
.action-config {
  margin-top: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.actions-list {
  .add-action {
    text-align: center;
    margin-top: 1rem;
  }
}

.rule-preview {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;

  h4 {
    margin: 0 0 1rem 0;
    font-size: 1.1rem;
    font-weight: 600;
    color: #333;
  }
}

.preview-text {
  font-size: 1.1rem;
  line-height: 1.6;

  .if-text,
  .then-text {
    display: block;
    margin-bottom: 0.5rem;

    strong {
      color: #007bff;
      font-weight: 600;
    }
  }
}

.builder-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  &.btn-primary {
    background: #007bff;
    color: white;

    &:hover:not(:disabled) {
      background: #0056b3;
    }
  }

  &.btn-secondary {
    background: #6c757d;
    color: white;

    &:hover:not(:disabled) {
      background: #545b62;
    }
  }

  &.btn-ghost {
    background: transparent;
    color: #6c757d;
    border: 1px solid #6c757d;

    &:hover:not(:disabled) {
      background: #6c757d;
      color: white;
    }
  }
}
</style>
