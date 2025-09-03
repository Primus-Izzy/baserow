<template>
  <div class="form-view-conditional-logic">
    <div class="form-view-conditional-logic__header">
      <h3>{{ $t('formViewConditionalLogic.title') }}</h3>
      <p class="form-view-conditional-logic__description">
        {{ $t('formViewConditionalLogic.description') }}
      </p>
    </div>

    <div class="form-view-conditional-logic__toggle">
      <Checkbox
        v-model="conditionalLogic.enabled"
        @input="updateConditionalLogic"
      >
        {{ $t('formViewConditionalLogic.enableConditionalLogic') }}
      </Checkbox>
    </div>

    <div
      v-if="conditionalLogic.enabled"
      class="form-view-conditional-logic__config"
    >
      <div class="form-view-conditional-logic__logic-type">
        <label class="control__label">
          {{ $t('formViewConditionalLogic.logicType') }}
        </label>
        <RadioButton
          v-model="conditionalLogic.logic_type"
          value="AND"
          @input="updateConditionalLogic"
        >
          {{ $t('formViewConditionalLogic.allConditions') }}
        </RadioButton>
        <RadioButton
          v-model="conditionalLogic.logic_type"
          value="OR"
          @input="updateConditionalLogic"
        >
          {{ $t('formViewConditionalLogic.anyCondition') }}
        </RadioButton>
      </div>

      <div class="form-view-conditional-logic__show-when">
        <label class="control__label">
          {{ $t('formViewConditionalLogic.showWhen') }}
        </label>
        <RadioButton
          v-model="conditionalLogic.show_when_true"
          :value="true"
          @input="updateConditionalLogic"
        >
          {{ $t('formViewConditionalLogic.conditionsTrue') }}
        </RadioButton>
        <RadioButton
          v-model="conditionalLogic.show_when_true"
          :value="false"
          @input="updateConditionalLogic"
        >
          {{ $t('formViewConditionalLogic.conditionsFalse') }}
        </RadioButton>
      </div>

      <div class="form-view-conditional-logic__conditions">
        <div class="form-view-conditional-logic__conditions-header">
          <h4>{{ $t('formViewConditionalLogic.conditions') }}</h4>
          <Button
            type="secondary"
            size="small"
            icon="iconoir-plus"
            @click="addCondition"
          >
            {{ $t('formViewConditionalLogic.addCondition') }}
          </Button>
        </div>

        <div
          v-for="(condition, index) in conditionalLogic.conditions"
          :key="index"
          class="form-view-conditional-logic__condition"
        >
          <div class="form-view-conditional-logic__condition-field">
            <Dropdown
              v-model="condition.field_id"
              :show-search="false"
              @input="updateConditionalLogic"
            >
              <DropdownItem
                v-for="field in availableFields"
                :key="field.id"
                :name="field.name"
                :value="field.id"
              />
            </Dropdown>
          </div>

          <div class="form-view-conditional-logic__condition-operator">
            <Dropdown
              v-model="condition.operator"
              :show-search="false"
              @input="updateConditionalLogic"
            >
              <DropdownItem
                v-for="operator in availableOperators"
                :key="operator.value"
                :name="operator.label"
                :value="operator.value"
              />
            </Dropdown>
          </div>

          <div class="form-view-conditional-logic__condition-value">
            <FormInput
              v-if="!isEmptyOperator(condition.operator)"
              v-model="condition.value"
              :placeholder="$t('formViewConditionalLogic.valuePlaceholder')"
              @input="updateConditionalLogic"
            />
          </div>

          <div class="form-view-conditional-logic__condition-actions">
            <Button
              type="danger"
              size="small"
              icon="iconoir-bin"
              @click="removeCondition(index)"
            />
          </div>
        </div>

        <div
          v-if="conditionalLogic.conditions.length === 0"
          class="form-view-conditional-logic__no-conditions"
        >
          <p>{{ $t('formViewConditionalLogic.noConditions') }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'FormViewConditionalLogic',
  props: {
    fieldOptions: {
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
      conditionalLogic: {
        enabled: false,
        logic_type: 'AND',
        show_when_true: true,
        conditions: [],
        ...this.fieldOptions.conditional_logic,
      },
    }
  },
  computed: {
    availableFields() {
      // Return fields that can be used in conditions (excluding current field)
      return this.fields.filter(
        (field) => field.id !== this.fieldOptions.field.id
      )
    },
    availableOperators() {
      return [
        {
          value: 'equals',
          label: this.$t('formViewConditionalLogic.operators.equals'),
        },
        {
          value: 'not_equals',
          label: this.$t('formViewConditionalLogic.operators.notEquals'),
        },
        {
          value: 'contains',
          label: this.$t('formViewConditionalLogic.operators.contains'),
        },
        {
          value: 'not_contains',
          label: this.$t('formViewConditionalLogic.operators.notContains'),
        },
        {
          value: 'is_empty',
          label: this.$t('formViewConditionalLogic.operators.isEmpty'),
        },
        {
          value: 'is_not_empty',
          label: this.$t('formViewConditionalLogic.operators.isNotEmpty'),
        },
        {
          value: 'greater_than',
          label: this.$t('formViewConditionalLogic.operators.greaterThan'),
        },
        {
          value: 'less_than',
          label: this.$t('formViewConditionalLogic.operators.lessThan'),
        },
      ]
    },
  },
  methods: {
    addCondition() {
      this.conditionalLogic.conditions.push({
        field_id: null,
        operator: 'equals',
        value: '',
      })
      this.updateConditionalLogic()
    },
    removeCondition(index) {
      this.conditionalLogic.conditions.splice(index, 1)
      this.updateConditionalLogic()
    },
    isEmptyOperator(operator) {
      return ['is_empty', 'is_not_empty'].includes(operator)
    },
    async updateConditionalLogic() {
      if (this.readOnly) return

      try {
        await this.$emit('update-conditional-logic', this.conditionalLogic)
      } catch (error) {
        this.$store.dispatch('toast/error', {
          title: this.$t('formViewConditionalLogic.updateError'),
          message: error.response?.data?.error || error.message,
        })
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.form-view-conditional-logic {
  padding: 20px;
  border: 1px solid #e1e5e9;
  border-radius: 6px;
  background-color: #f8f9fa;

  &__header {
    margin-bottom: 20px;

    h3 {
      margin: 0 0 8px 0;
      font-size: 16px;
      font-weight: 600;
      color: #2d3748;
    }
  }

  &__description {
    margin: 0;
    font-size: 14px;
    color: #718096;
  }

  &__toggle {
    margin-bottom: 20px;
  }

  &__config {
    margin-top: 20px;
  }

  &__logic-type,
  &__show-when {
    margin-bottom: 20px;

    .control__label {
      display: block;
      margin-bottom: 8px;
      font-weight: 500;
      color: #2d3748;
    }
  }

  &__conditions {
    margin-top: 20px;
  }

  &__conditions-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    h4 {
      margin: 0;
      font-size: 14px;
      font-weight: 600;
      color: #2d3748;
    }
  }

  &__condition {
    display: grid;
    grid-template-columns: 1fr 120px 1fr auto;
    gap: 12px;
    align-items: center;
    padding: 12px;
    margin-bottom: 8px;
    background-color: white;
    border: 1px solid #e1e5e9;
    border-radius: 4px;
  }

  &__no-conditions {
    padding: 20px;
    text-align: center;
    color: #718096;
    font-style: italic;
  }
}
</style>
