<template>
  <div class="grid-view-conditional-formatting">
    <div class="grid-view-conditional-formatting__header">
      <h3>{{ $t('gridView.conditionalFormatting.title') }}</h3>
      <Button
        v-if="!readOnly"
        type="primary"
        size="small"
        @click="showCreateModal = true"
      >
        <i class="iconoir-plus"></i>
        {{ $t('gridView.conditionalFormatting.addRule') }}
      </Button>
    </div>

    <div class="grid-view-conditional-formatting__rules">
      <div
        v-for="rule in conditionalFormattingRules"
        :key="rule.id"
        class="grid-view-conditional-formatting__rule"
        :class="{
          'grid-view-conditional-formatting__rule--inactive': !rule.is_active,
        }"
      >
        <div class="grid-view-conditional-formatting__rule-preview">
          <div
            class="grid-view-conditional-formatting__rule-sample"
            :style="{
              backgroundColor: rule.background_color,
              color: rule.text_color,
            }"
          >
            {{ $t('gridView.conditionalFormatting.sampleText') }}
          </div>
        </div>

        <div class="grid-view-conditional-formatting__rule-details">
          <div class="grid-view-conditional-formatting__rule-name">
            {{ rule.name }}
          </div>
          <div class="grid-view-conditional-formatting__rule-condition">
            {{ getFieldName(rule.field) }}
            {{ getConditionText(rule.condition_type) }} "{{
              rule.condition_value
            }}"
          </div>
        </div>

        <div class="grid-view-conditional-formatting__rule-actions">
          <Button
            v-if="!readOnly"
            type="ghost"
            size="small"
            @click="toggleRuleActive(rule)"
          >
            <i :class="rule.is_active ? 'iconoir-eye' : 'iconoir-eye-off'"></i>
          </Button>
          <Button
            v-if="!readOnly"
            type="ghost"
            size="small"
            @click="editRule(rule)"
          >
            <i class="iconoir-edit-pencil"></i>
          </Button>
          <Button
            v-if="!readOnly"
            type="ghost"
            size="small"
            @click="deleteRule(rule)"
          >
            <i class="iconoir-bin"></i>
          </Button>
        </div>
      </div>

      <div
        v-if="conditionalFormattingRules.length === 0"
        class="grid-view-conditional-formatting__empty"
      >
        <i class="iconoir-color-picker"></i>
        <p>{{ $t('gridView.conditionalFormatting.noRules') }}</p>
      </div>
    </div>

    <!-- Create/Edit Rule Modal -->
    <Modal v-if="showCreateModal || editingRule" @hidden="closeModal">
      <h2 slot="title">
        {{
          editingRule
            ? $t('gridView.conditionalFormatting.editRule')
            : $t('gridView.conditionalFormatting.createRule')
        }}
      </h2>

      <form @submit.prevent="saveRule">
        <FormGroup
          :label="$t('gridView.conditionalFormatting.ruleName')"
          required
        >
          <FormInput
            v-model="ruleForm.name"
            :placeholder="
              $t('gridView.conditionalFormatting.ruleNamePlaceholder')
            "
            required
          />
        </FormGroup>

        <FormGroup :label="$t('gridView.conditionalFormatting.field')" required>
          <Dropdown v-model="ruleForm.field">
            <DropdownItem
              v-for="field in availableFields"
              :key="field.id"
              :name="field.name"
              :value="field.id"
            />
          </Dropdown>
        </FormGroup>

        <FormGroup
          :label="$t('gridView.conditionalFormatting.condition')"
          required
        >
          <Dropdown v-model="ruleForm.condition_type">
            <DropdownItem
              v-for="condition in availableConditions"
              :key="condition.value"
              :name="condition.name"
              :value="condition.value"
            />
          </Dropdown>
        </FormGroup>

        <FormGroup :label="$t('gridView.conditionalFormatting.value')" required>
          <FormInput
            v-model="ruleForm.condition_value"
            :placeholder="$t('gridView.conditionalFormatting.valuePlaceholder')"
            required
          />
        </FormGroup>

        <div class="grid-view-conditional-formatting__colors">
          <FormGroup
            :label="$t('gridView.conditionalFormatting.backgroundColor')"
          >
            <ColorPicker v-model="ruleForm.background_color" />
          </FormGroup>

          <FormGroup :label="$t('gridView.conditionalFormatting.textColor')">
            <ColorPicker v-model="ruleForm.text_color" />
          </FormGroup>
        </div>

        <div class="grid-view-conditional-formatting__preview">
          <div
            class="grid-view-conditional-formatting__preview-sample"
            :style="{
              backgroundColor: ruleForm.background_color,
              color: ruleForm.text_color,
            }"
          >
            {{ $t('gridView.conditionalFormatting.previewText') }}
          </div>
        </div>

        <div class="modal__actions">
          <Button type="secondary" @click="closeModal">
            {{ $t('action.cancel') }}
          </Button>
          <Button type="primary" :loading="saving" @click="saveRule">
            {{ editingRule ? $t('action.save') : $t('action.create') }}
          </Button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<script>
import { notifyIf } from '@baserow/modules/core/utils/error'
import GridViewService from '@baserow/modules/database/services/view/grid'

export default {
  name: 'GridViewConditionalFormatting',
  props: {
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
      default: false,
    },
  },
  data() {
    return {
      conditionalFormattingRules: [],
      showCreateModal: false,
      editingRule: null,
      saving: false,
      ruleForm: {
        name: '',
        field: null,
        condition_type: 'equals',
        condition_value: '',
        background_color: '#ffeb3b',
        text_color: '#000000',
        is_active: true,
      },
    }
  },
  computed: {
    availableFields() {
      return this.fields.filter((field) =>
        [
          'text',
          'long_text',
          'number',
          'rating',
          'single_select',
          'multiple_select',
          'boolean',
        ].includes(field.type)
      )
    },
    availableConditions() {
      return [
        {
          value: 'equals',
          name: this.$t('gridView.conditionalFormatting.conditions.equals'),
        },
        {
          value: 'not_equals',
          name: this.$t('gridView.conditionalFormatting.conditions.notEquals'),
        },
        {
          value: 'contains',
          name: this.$t('gridView.conditionalFormatting.conditions.contains'),
        },
        {
          value: 'not_contains',
          name: this.$t(
            'gridView.conditionalFormatting.conditions.notContains'
          ),
        },
        {
          value: 'starts_with',
          name: this.$t('gridView.conditionalFormatting.conditions.startsWith'),
        },
        {
          value: 'ends_with',
          name: this.$t('gridView.conditionalFormatting.conditions.endsWith'),
        },
        {
          value: 'greater_than',
          name: this.$t(
            'gridView.conditionalFormatting.conditions.greaterThan'
          ),
        },
        {
          value: 'less_than',
          name: this.$t('gridView.conditionalFormatting.conditions.lessThan'),
        },
        {
          value: 'is_empty',
          name: this.$t('gridView.conditionalFormatting.conditions.isEmpty'),
        },
        {
          value: 'is_not_empty',
          name: this.$t('gridView.conditionalFormatting.conditions.isNotEmpty'),
        },
      ]
    },
  },
  async mounted() {
    await this.loadConditionalFormattingRules()
  },
  methods: {
    async loadConditionalFormattingRules() {
      try {
        const { data } = await GridViewService(
          this.$client
        ).getConditionalFormatting(this.view.id)
        this.conditionalFormattingRules = data
      } catch (error) {
        notifyIf(error, 'view')
      }
    },
    getFieldName(fieldId) {
      const field = this.fields.find((f) => f.id === fieldId)
      return field ? field.name : ''
    },
    getConditionText(conditionType) {
      const condition = this.availableConditions.find(
        (c) => c.value === conditionType
      )
      return condition ? condition.name : conditionType
    },
    async toggleRuleActive(rule) {
      try {
        await GridViewService(this.$client).updateConditionalFormatting(
          this.view.id,
          rule.id,
          { is_active: !rule.is_active }
        )
        rule.is_active = !rule.is_active
        this.$emit('rules-updated', this.conditionalFormattingRules)
      } catch (error) {
        notifyIf(error, 'view')
      }
    },
    editRule(rule) {
      this.editingRule = rule
      this.ruleForm = { ...rule }
    },
    async deleteRule(rule) {
      if (confirm(this.$t('gridView.conditionalFormatting.confirmDelete'))) {
        try {
          await GridViewService(this.$client).deleteConditionalFormatting(
            this.view.id,
            rule.id
          )
          this.conditionalFormattingRules =
            this.conditionalFormattingRules.filter((r) => r.id !== rule.id)
          this.$emit('rules-updated', this.conditionalFormattingRules)
        } catch (error) {
          notifyIf(error, 'view')
        }
      }
    },
    async saveRule() {
      this.saving = true
      try {
        if (this.editingRule) {
          const { data } = await GridViewService(
            this.$client
          ).updateConditionalFormatting(
            this.view.id,
            this.editingRule.id,
            this.ruleForm
          )
          const index = this.conditionalFormattingRules.findIndex(
            (r) => r.id === this.editingRule.id
          )
          this.conditionalFormattingRules.splice(index, 1, data)
        } else {
          const { data } = await GridViewService(
            this.$client
          ).createConditionalFormatting(this.view.id, this.ruleForm)
          this.conditionalFormattingRules.push(data)
        }
        this.$emit('rules-updated', this.conditionalFormattingRules)
        this.closeModal()
      } catch (error) {
        notifyIf(error, 'view')
      } finally {
        this.saving = false
      }
    },
    closeModal() {
      this.showCreateModal = false
      this.editingRule = null
      this.ruleForm = {
        name: '',
        field: null,
        condition_type: 'equals',
        condition_value: '',
        background_color: '#ffeb3b',
        text_color: '#000000',
        is_active: true,
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.grid-view-conditional-formatting {
  &__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
    }
  }

  &__rules {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  &__rule {
    display: flex;
    align-items: center;
    padding: 12px;
    border: 1px solid #e1e5e9;
    border-radius: 6px;
    background: #fff;

    &--inactive {
      opacity: 0.6;
    }
  }

  &__rule-preview {
    margin-right: 12px;
  }

  &__rule-sample {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
    min-width: 60px;
    text-align: center;
  }

  &__rule-details {
    flex: 1;

    &-name {
      font-weight: 600;
      margin-bottom: 2px;
    }

    &-condition {
      font-size: 12px;
      color: #666;
    }
  }

  &__rule-actions {
    display: flex;
    gap: 4px;
  }

  &__empty {
    text-align: center;
    padding: 40px 20px;
    color: #666;

    i {
      font-size: 48px;
      margin-bottom: 16px;
      opacity: 0.5;
    }

    p {
      margin: 0;
      font-size: 14px;
    }
  }

  &__colors {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin: 16px 0;
  }

  &__preview {
    margin: 16px 0;

    &-sample {
      padding: 8px 16px;
      border-radius: 4px;
      text-align: center;
      font-weight: 500;
    }
  }
}

.grid-view__head--sticky {
  position: sticky;
  top: 0;
  z-index: 10;
  background: #fff;
  border-bottom: 1px solid #e1e5e9;
}
</style>
