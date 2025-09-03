<template>
  <div class="form-view-validation-rules">
    <div class="form-view-validation-rules__header">
      <h3>{{ $t('formViewValidationRules.title') }}</h3>
      <p class="form-view-validation-rules__description">
        {{ $t('formViewValidationRules.description') }}
      </p>
    </div>

    <div class="form-view-validation-rules__rules">
      <div class="form-view-validation-rules__rules-header">
        <h4>{{ $t('formViewValidationRules.customRules') }}</h4>
        <Button
          type="secondary"
          size="small"
          icon="iconoir-plus"
          @click="addRule"
        >
          {{ $t('formViewValidationRules.addRule') }}
        </Button>
      </div>

      <div
        v-for="(rule, index) in validationRules"
        :key="index"
        class="form-view-validation-rules__rule"
      >
        <div class="form-view-validation-rules__rule-type">
          <label class="control__label">
            {{ $t('formViewValidationRules.ruleType') }}
          </label>
          <Dropdown
            v-model="rule.type"
            :show-search="false"
            @input="updateValidationRules"
          >
            <DropdownItem
              v-for="ruleType in availableRuleTypes"
              :key="ruleType.value"
              :name="ruleType.label"
              :value="ruleType.value"
            />
          </Dropdown>
        </div>

        <div
          v-if="ruleRequiresValue(rule.type)"
          class="form-view-validation-rules__rule-value"
        >
          <label class="control__label">
            {{ getRuleValueLabel(rule.type) }}
          </label>
          <FormInput
            v-model="rule.value"
            :placeholder="getRuleValuePlaceholder(rule.type)"
            :type="getRuleValueInputType(rule.type)"
            @input="updateValidationRules"
          />
        </div>

        <div class="form-view-validation-rules__rule-message">
          <label class="control__label">
            {{ $t('formViewValidationRules.errorMessage') }}
          </label>
          <FormInput
            v-model="rule.error_message"
            :placeholder="getDefaultErrorMessage(rule.type)"
            @input="updateValidationRules"
          />
        </div>

        <div class="form-view-validation-rules__rule-actions">
          <Button
            type="danger"
            size="small"
            icon="iconoir-bin"
            @click="removeRule(index)"
          />
        </div>
      </div>

      <div
        v-if="validationRules.length === 0"
        class="form-view-validation-rules__no-rules"
      >
        <p>{{ $t('formViewValidationRules.noRules') }}</p>
      </div>
    </div>

    <!-- Preview Section -->
    <div class="form-view-validation-rules__preview">
      <h4>{{ $t('formViewValidationRules.preview') }}</h4>
      <div class="form-view-validation-rules__preview-container">
        <FormInput
          v-model="previewValue"
          :placeholder="$t('formViewValidationRules.previewPlaceholder')"
          :error="previewErrors.length > 0"
          @input="validatePreview"
        />
        <div
          v-if="previewErrors.length > 0"
          class="form-view-validation-rules__preview-errors"
        >
          <div
            v-for="(error, index) in previewErrors"
            :key="index"
            class="form-view-validation-rules__preview-error"
          >
            {{ error }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FormViewValidationRules',
  props: {
    fieldOptions: {
      type: Object,
      required: true,
    },
    readOnly: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      validationRules: [...(this.fieldOptions.validation_rules || [])],
      previewValue: '',
      previewErrors: [],
    }
  },
  computed: {
    availableRuleTypes() {
      return [
        {
          value: 'required',
          label: this.$t('formViewValidationRules.ruleTypes.required'),
        },
        {
          value: 'min_length',
          label: this.$t('formViewValidationRules.ruleTypes.minLength'),
        },
        {
          value: 'max_length',
          label: this.$t('formViewValidationRules.ruleTypes.maxLength'),
        },
        {
          value: 'pattern',
          label: this.$t('formViewValidationRules.ruleTypes.pattern'),
        },
        {
          value: 'email',
          label: this.$t('formViewValidationRules.ruleTypes.email'),
        },
        {
          value: 'url',
          label: this.$t('formViewValidationRules.ruleTypes.url'),
        },
        {
          value: 'numeric',
          label: this.$t('formViewValidationRules.ruleTypes.numeric'),
        },
        {
          value: 'min_value',
          label: this.$t('formViewValidationRules.ruleTypes.minValue'),
        },
        {
          value: 'max_value',
          label: this.$t('formViewValidationRules.ruleTypes.maxValue'),
        },
      ]
    },
  },
  methods: {
    addRule() {
      this.validationRules.push({
        type: 'required',
        value: '',
        error_message: this.getDefaultErrorMessage('required'),
      })
      this.updateValidationRules()
    },
    removeRule(index) {
      this.validationRules.splice(index, 1)
      this.updateValidationRules()
    },
    ruleRequiresValue(ruleType) {
      return !['required', 'email', 'url', 'numeric'].includes(ruleType)
    },
    getRuleValueLabel(ruleType) {
      const labels = {
        min_length: this.$t('formViewValidationRules.valueLabels.minLength'),
        max_length: this.$t('formViewValidationRules.valueLabels.maxLength'),
        pattern: this.$t('formViewValidationRules.valueLabels.pattern'),
        min_value: this.$t('formViewValidationRules.valueLabels.minValue'),
        max_value: this.$t('formViewValidationRules.valueLabels.maxValue'),
      }
      return labels[ruleType] || this.$t('formViewValidationRules.value')
    },
    getRuleValuePlaceholder(ruleType) {
      const placeholders = {
        min_length: '5',
        max_length: '100',
        pattern: '^[A-Za-z]+$',
        min_value: '0',
        max_value: '100',
      }
      return placeholders[ruleType] || ''
    },
    getRuleValueInputType(ruleType) {
      return ['min_length', 'max_length', 'min_value', 'max_value'].includes(
        ruleType
      )
        ? 'number'
        : 'text'
    },
    getDefaultErrorMessage(ruleType) {
      const messages = {
        required: this.$t('formViewValidationRules.defaultMessages.required'),
        min_length: this.$t(
          'formViewValidationRules.defaultMessages.minLength'
        ),
        max_length: this.$t(
          'formViewValidationRules.defaultMessages.maxLength'
        ),
        pattern: this.$t('formViewValidationRules.defaultMessages.pattern'),
        email: this.$t('formViewValidationRules.defaultMessages.email'),
        url: this.$t('formViewValidationRules.defaultMessages.url'),
        numeric: this.$t('formViewValidationRules.defaultMessages.numeric'),
        min_value: this.$t('formViewValidationRules.defaultMessages.minValue'),
        max_value: this.$t('formViewValidationRules.defaultMessages.maxValue'),
      }
      return (
        messages[ruleType] ||
        this.$t('formViewValidationRules.defaultMessages.default')
      )
    },
    async updateValidationRules() {
      if (this.readOnly) return

      try {
        await this.$emit('update-validation-rules', this.validationRules)
        this.validatePreview()
      } catch (error) {
        this.$store.dispatch('toast/error', {
          title: this.$t('formViewValidationRules.updateError'),
          message: error.response?.data?.error || error.message,
        })
      }
    },
    validatePreview() {
      this.previewErrors = []

      for (const rule of this.validationRules) {
        if (!this.validateRule(rule, this.previewValue)) {
          this.previewErrors.push(
            rule.error_message || this.getDefaultErrorMessage(rule.type)
          )
        }
      }
    },
    validateRule(rule, value) {
      switch (rule.type) {
        case 'required':
          return Boolean(value)
        case 'min_length':
          return String(value).length >= parseInt(rule.value || 0)
        case 'max_length':
          return String(value).length <= parseInt(rule.value || 0)
        case 'pattern':
          try {
            const regex = new RegExp(rule.value)
            return regex.test(String(value))
          } catch {
            return true // Invalid regex, skip validation
          }
        case 'email':
          const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
          return emailRegex.test(String(value))
        case 'url':
          const urlRegex = /^https?:\/\/[^\s/$.?#].[^\s]*$/
          return urlRegex.test(String(value))
        case 'numeric':
          return !isNaN(parseFloat(value)) && isFinite(value)
        case 'min_value':
          return parseFloat(value) >= parseFloat(rule.value || 0)
        case 'max_value':
          return parseFloat(value) <= parseFloat(rule.value || 0)
        default:
          return true
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.form-view-validation-rules {
  &__header {
    margin-bottom: 24px;

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

  &__rules {
    margin-bottom: 32px;
  }

  &__rules-header {
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

  &__rule {
    display: grid;
    grid-template-columns: 200px 1fr 2fr auto;
    gap: 16px;
    align-items: end;
    padding: 16px;
    margin-bottom: 12px;
    background-color: #f8f9fa;
    border: 1px solid #e1e5e9;
    border-radius: 6px;

    .control__label {
      display: block;
      margin-bottom: 4px;
      font-size: 12px;
      font-weight: 500;
      color: #4a5568;
    }
  }

  &__no-rules {
    padding: 20px;
    text-align: center;
    color: #718096;
    font-style: italic;
    background-color: #f8f9fa;
    border: 1px solid #e1e5e9;
    border-radius: 6px;
  }

  &__preview {
    padding-top: 24px;
    border-top: 1px solid #e1e5e9;

    h4 {
      margin: 0 0 16px 0;
      font-size: 14px;
      font-weight: 600;
      color: #2d3748;
    }
  }

  &__preview-container {
    max-width: 400px;
  }

  &__preview-errors {
    margin-top: 8px;
  }

  &__preview-error {
    padding: 4px 8px;
    margin-bottom: 4px;
    font-size: 12px;
    color: #e53e3e;
    background-color: #fed7d7;
    border: 1px solid #feb2b2;
    border-radius: 4px;
  }
}
</style>
