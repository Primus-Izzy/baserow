<template>
  <div>
    <!-- Source Type Configuration -->
    <FormGroup
      small-label
      :error="fieldHasErrors('source_type')"
      :label="$t('fieldProgressBarSubForm.sourceTypeLabel')"
      class="margin-bottom-2"
      required
    >
      <Dropdown
        v-model="v$.values.source_type.$model"
        :error="fieldHasErrors('source_type')"
        :fixed-items="true"
        @hide="v$.values.source_type.$touch"
      >
        <DropdownItem
          :name="$t('fieldProgressBarSubForm.sourceTypeManual')"
          value="manual"
        />
        <DropdownItem
          :name="$t('fieldProgressBarSubForm.sourceTypeField')"
          value="field"
        />
        <DropdownItem
          :name="$t('fieldProgressBarSubForm.sourceTypeFormula')"
          value="formula"
          :disabled="true"
        />
      </Dropdown>
    </FormGroup>

    <!-- Source Field Selection (when source_type is 'field') -->
    <FormGroup
      v-if="values.source_type === 'field'"
      small-label
      :error="fieldHasErrors('source_field')"
      :label="$t('fieldProgressBarSubForm.sourceFieldLabel')"
      class="margin-bottom-2"
      required
    >
      <Dropdown
        v-model="v$.values.source_field.$model"
        :error="fieldHasErrors('source_field')"
        :fixed-items="false"
        @hide="v$.values.source_field.$touch"
      >
        <DropdownItem
          v-for="field in numericFields"
          :key="field.id"
          :name="field.name"
          :value="field.id"
        />
      </Dropdown>
    </FormGroup>

    <!-- Range Configuration -->
    <FormGroup
      small-label
      :label="$t('fieldProgressBarSubForm.rangeLabel')"
      class="margin-bottom-2"
    >
      <div class="flex">
        <FormInput
          v-model="v$.values.min_value.$model"
          :error="fieldHasErrors('min_value')"
          type="number"
          step="0.01"
          :placeholder="$t('fieldProgressBarSubForm.minValuePlaceholder')"
          @blur="v$.values.min_value.$touch"
        />
        <FormInput
          v-model="v$.values.max_value.$model"
          :error="fieldHasErrors('max_value')"
          type="number"
          step="0.01"
          :placeholder="$t('fieldProgressBarSubForm.maxValuePlaceholder')"
          @blur="v$.values.max_value.$touch"
        />
      </div>
    </FormGroup>

    <!-- Display Configuration -->
    <FormGroup class="margin-bottom-2">
      <Checkbox v-model="v$.values.show_percentage.$model">
        {{ $t('fieldProgressBarSubForm.showPercentage') }}
      </Checkbox>
    </FormGroup>

    <!-- Color Scheme Configuration -->
    <FormGroup
      small-label
      :error="fieldHasErrors('color_scheme')"
      :label="$t('fieldProgressBarSubForm.colorSchemeLabel')"
      class="margin-bottom-2"
    >
      <Dropdown
        v-model="v$.values.color_scheme.$model"
        :error="fieldHasErrors('color_scheme')"
        :fixed-items="true"
        @hide="v$.values.color_scheme.$touch"
      >
        <DropdownItem
          :name="$t('fieldProgressBarSubForm.colorSchemeDefault')"
          value="default"
        />
        <DropdownItem
          :name="$t('fieldProgressBarSubForm.colorSchemeSuccess')"
          value="success"
        />
        <DropdownItem
          :name="$t('fieldProgressBarSubForm.colorSchemeWarning')"
          value="warning"
        />
        <DropdownItem
          :name="$t('fieldProgressBarSubForm.colorSchemeDanger')"
          value="danger"
        />
        <DropdownItem
          :name="$t('fieldProgressBarSubForm.colorSchemeCustom')"
          value="custom"
        />
      </Dropdown>
    </FormGroup>

    <!-- Custom Colors (when color_scheme is 'custom') -->
    <div v-if="values.color_scheme === 'custom'" class="margin-bottom-2">
      <FormGroup
        small-label
        :label="$t('fieldProgressBarSubForm.customColorsLabel')"
      >
        <div class="flex">
          <div class="progress-bar-color-input">
            <label class="progress-bar-color-label">
              {{ $t('fieldProgressBarSubForm.startColor') }}
            </label>
            <input
              v-model="v$.values.custom_color_start.$model"
              type="color"
              class="progress-bar-color-picker"
              @change="v$.values.custom_color_start.$touch"
            />
          </div>
          <div class="progress-bar-color-input">
            <label class="progress-bar-color-label">
              {{ $t('fieldProgressBarSubForm.endColor') }}
            </label>
            <input
              v-model="v$.values.custom_color_end.$model"
              type="color"
              class="progress-bar-color-picker"
              @change="v$.values.custom_color_end.$touch"
            />
          </div>
        </div>
      </FormGroup>
    </div>

    <!-- Preview -->
    <FormGroup small-label :label="$t('fieldProgressBarSubForm.previewLabel')">
      <div class="progress-bar-preview">
        <ProgressBarDisplay
          :value="previewValue"
          :field="previewField"
          :show-percentage="values.show_percentage"
        />
      </div>
    </FormGroup>
  </div>
</template>

<script>
import { useVuelidate } from '@vuelidate/core'
import { required, minValue, maxValue } from '@vuelidate/validators'
import form from '@baserow/modules/core/mixins/form'
import fieldSubForm from '@baserow/modules/database/mixins/fieldSubForm'
import ProgressBarDisplay from '@baserow/modules/database/components/field/ProgressBarDisplay'

export default {
  name: 'FieldProgressBarSubForm',
  components: {
    ProgressBarDisplay,
  },
  mixins: [form, fieldSubForm],
  setup() {
    return { v$: useVuelidate({ $lazy: true }) }
  },
  data() {
    return {
      allowedValues: [
        'source_type',
        'source_field',
        'source_formula',
        'min_value',
        'max_value',
        'show_percentage',
        'color_scheme',
        'custom_color_start',
        'custom_color_end',
      ],
      values: {
        source_type: 'manual',
        source_field: null,
        source_formula: '',
        min_value: 0,
        max_value: 100,
        show_percentage: true,
        color_scheme: 'default',
        custom_color_start: '#3b82f6',
        custom_color_end: '#1d4ed8',
      },
    }
  },
  computed: {
    /**
     * Get all numeric fields from the current table for source field selection
     */
    numericFields() {
      if (!this.table || !this.table.fields) {
        return []
      }

      return this.table.fields.filter((field) => {
        const numericTypes = [
          'number',
          'rating',
          'autonumber',
          'formula',
          'count',
          'rollup',
        ]
        return (
          numericTypes.includes(field.type) &&
          field.id !== this.defaultValues.id
        )
      })
    },
    /**
     * Create a preview field object for the progress bar preview
     */
    previewField() {
      return {
        ...this.values,
        type: 'progress_bar',
      }
    },
    /**
     * Calculate preview value based on the range
     */
    previewValue() {
      const range = this.values.max_value - this.values.min_value
      return this.values.min_value + range * 0.65 // Show 65% progress
    },
  },
  validations() {
    return {
      values: {
        source_type: { required },
        source_field: {
          required: (value) => {
            return this.values.source_type !== 'field' || value !== null
          },
        },
        min_value: {
          required,
          minValue: minValue(-999999),
          maxValue: (value) => {
            return value < this.values.max_value
          },
        },
        max_value: {
          required,
          minValue: (value) => {
            return value > this.values.min_value
          },
          maxValue: maxValue(999999),
        },
        show_percentage: {},
        color_scheme: { required },
        custom_color_start: {
          required: (value) => {
            return (
              this.values.color_scheme !== 'custom' ||
              (value && value.length > 0)
            )
          },
        },
        custom_color_end: {
          required: (value) => {
            return (
              this.values.color_scheme !== 'custom' ||
              (value && value.length > 0)
            )
          },
        },
      },
    }
  },
  watch: {
    'values.source_type'(newValue) {
      if (newValue !== 'field') {
        this.values.source_field = null
      }
      if (newValue !== 'custom') {
        this.values.custom_color_start = '#3b82f6'
        this.values.custom_color_end = '#1d4ed8'
      }
    },
    'values.color_scheme'(newValue) {
      if (newValue !== 'custom') {
        this.values.custom_color_start = '#3b82f6'
        this.values.custom_color_end = '#1d4ed8'
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.progress-bar-color-input {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 0 8px;

  .progress-bar-color-label {
    font-size: 12px;
    color: #666;
    margin-bottom: 4px;
  }

  .progress-bar-color-picker {
    width: 40px;
    height: 30px;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;

    &::-webkit-color-swatch-wrapper {
      padding: 0;
    }

    &::-webkit-color-swatch {
      border: none;
      border-radius: 3px;
    }
  }
}

.progress-bar-preview {
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}
</style>
