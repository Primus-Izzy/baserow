<template>
  <FormGroup :error="touched && !valid">
    <!-- Read-only display for field/formula sources -->
    <div v-if="isReadOnly" class="row-edit-progress-bar-readonly">
      <ProgressBarDisplay
        :value="value"
        :field="field"
        :show-percentage="true"
      />
    </div>
    
    <!-- Editable input for manual source -->
    <div v-else class="row-edit-progress-bar-editable">
      <div class="row-edit-progress-bar-input-group">
        <FormInput
          ref="input"
          :value="copy"
          size="large"
          type="number"
          :step="0.01"
          :min="field.min_value"
          :max="field.max_value"
          :error="touched && !valid"
          :disabled="readOnly"
          :placeholder="$t('rowEditFieldProgressBar.placeholder', { 
            min: field.min_value, 
            max: field.max_value 
          })"
          @keyup.enter="
            onBlur()
            $refs.input.blur()
          "
          @focus="
            onFocus()
            select()
          "
          @blur="
            onBlur()
            unselect()
          "
          @input="handleInput"
        />
        <div class="row-edit-progress-bar-range">
          {{ field.min_value }} - {{ field.max_value }}
        </div>
      </div>
      
      <!-- Progress bar preview -->
      <div class="row-edit-progress-bar-preview">
        <ProgressBarDisplay
          :value="copy || value"
          :field="field"
          :show-percentage="true"
        />
      </div>
    </div>

    <template #error>
      <span v-show="touched && !valid">
        {{ error }}
      </span>
    </template>
  </FormGroup>
</template>

<script>
import rowEditField from '@baserow/modules/database/mixins/rowEditField'
import rowEditFieldInput from '@baserow/modules/database/mixins/rowEditFieldInput'
import ProgressBarDisplay from '@baserow/modules/database/components/field/ProgressBarDisplay'

export default {
  name: 'RowEditFieldProgressBar',
  components: {
    ProgressBarDisplay,
  },
  mixins: [rowEditField, rowEditFieldInput],
  computed: {
    /**
     * Check if this field is read-only (not manual input)
     */
    isReadOnly() {
      return this.field.source_type !== 'manual'
    },
  },
  watch: {
    field: {
      immediate: true,
      handler() {
        this.initCopy(this.value)
      },
    },
    value: {
      handler(newValue) {
        this.initCopy(newValue)
      },
    },
  },
  methods: {
    /**
     * Initialize the copy value
     */
    initCopy(value) {
      if (value === null || value === undefined || value === '') {
        this.copy = ''
      } else {
        this.copy = String(value)
      }
    },
    
    /**
     * Handle input changes
     */
    handleInput(newCopy) {
      this.copy = newCopy
      this.$emit('input', this.copy)
    },
    
    /**
     * Validate the input value
     */
    isValid(value) {
      if (this.isReadOnly) {
        return true
      }
      
      if (value === null || value === undefined || value === '') {
        return true // Allow empty values
      }
      
      const numValue = parseFloat(value)
      if (isNaN(numValue)) {
        this.error = this.$t('fieldErrors.invalidNumber')
        return false
      }
      
      if (numValue < this.field.min_value || numValue > this.field.max_value) {
        this.error = this.$t('fieldErrors.numberOutOfRange', {
          min: this.field.min_value,
          max: this.field.max_value
        })
        return false
      }
      
      return true
    },
  },
}
</script>

<style lang="scss" scoped>
.row-edit-progress-bar-readonly {
  padding: 12px 0;
}

.row-edit-progress-bar-editable {
  .row-edit-progress-bar-input-group {
    position: relative;
    margin-bottom: 12px;
    
    .row-edit-progress-bar-range {
      position: absolute;
      right: 8px;
      top: 50%;
      transform: translateY(-50%);
      font-size: 11px;
      color: #6b7280;
      background: #f9fafb;
      padding: 2px 6px;
      border-radius: 3px;
      pointer-events: none;
    }
  }
  
  .row-edit-progress-bar-preview {
    padding: 8px 12px;
    background-color: #f8f9fa;
    border-radius: 6px;
    border: 1px solid #e9ecef;
  }
}

// Mobile responsive adjustments
@media (max-width: 768px) {
  .row-edit-progress-bar-editable {
    .row-edit-progress-bar-input-group {
      .row-edit-progress-bar-range {
        position: static;
        transform: none;
        display: block;
        text-align: center;
        margin-top: 4px;
        background: transparent;
        padding: 0;
      }
    }
    
    .row-edit-progress-bar-preview {
      padding: 12px;
    }
  }
}
</style>