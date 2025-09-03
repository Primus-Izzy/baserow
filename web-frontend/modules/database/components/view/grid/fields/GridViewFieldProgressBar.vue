<template>
  <div
    class="grid-view__cell active"
    :class="{
      editing: editing,
      invalid: editing && !valid,
      'grid-view__cell--readonly': isReadOnly,
    }"
    @contextmenu="stopContextIfEditing($event)"
  >
    <!-- Display mode -->
    <div v-show="!editing" class="grid-field-progress-bar">
      <ProgressBarDisplay
        :value="value"
        :field="field"
        :show-percentage="true"
      />
    </div>

    <!-- Edit mode (only for manual input) -->
    <template v-if="editing && !isReadOnly">
      <input
        ref="input"
        v-model="copy"
        type="number"
        :step="0.01"
        :min="field.min_value"
        :max="field.max_value"
        class="grid-field-progress-bar__input"
        @keydown.enter="$emit('edit-next')"
        @keydown.escape="$emit('edit-cancel')"
        @blur="$emit('edit-save', copy)"
      />
      <div v-show="!valid" class="grid-view__cell-error align-right">
        {{ error }}
      </div>
    </template>
  </div>
</template>

<script>
import gridField from '@baserow/modules/database/mixins/gridField'
import gridFieldInput from '@baserow/modules/database/mixins/gridFieldInput'
import ProgressBarDisplay from '@baserow/modules/database/components/field/ProgressBarDisplay'

export default {
  name: 'GridViewFieldProgressBar',
  components: {
    ProgressBarDisplay,
  },
  mixins: [gridField, gridFieldInput],
  computed: {
    /**
     * Check if this field is read-only (not manual input)
     */
    isReadOnly() {
      return this.field.source_type !== 'manual'
    },
  },
  watch: {
    value: {
      handler(newVal) {
        if (!this.editing) {
          this.copy = this.prepareCopy(newVal)
        }
      },
      immediate: true,
    },
    editing: {
      handler(newVal, oldVal) {
        if (newVal && !oldVal && !this.isReadOnly) {
          this.$nextTick(() => {
            const input = this.$refs.input
            if (input) {
              input.focus()
              input.select()
            }
          })
        }
      },
    },
  },
  methods: {
    /**
     * Prepare the copy value for editing
     */
    prepareCopy(value) {
      if (value === null || value === undefined || value === '') {
        return ''
      }
      return String(value)
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
          max: this.field.max_value,
        })
        return false
      }

      return true
    },
  },
}
</script>

<style lang="scss" scoped>
.grid-field-progress-bar {
  display: flex;
  align-items: center;
  width: 100%;
  height: 100%;
  padding: 4px 8px;

  .progress-bar-display {
    width: 100%;
  }
}

.grid-field-progress-bar__input {
  width: 100%;
  height: 100%;
  border: none;
  outline: none;
  background: transparent;
  font-size: 13px;
  padding: 0 8px;

  &:focus {
    background: #fff;
    border: 1px solid #3b82f6;
    border-radius: 2px;
  }
}

.grid-view__cell--readonly {
  cursor: default;

  &:hover {
    background-color: transparent;
  }
}

// Mobile responsive adjustments
@media (max-width: 768px) {
  .grid-field-progress-bar {
    padding: 6px 8px;

    .progress-bar-display {
      --progress-bar-height: 22px;
    }
  }

  .grid-field-progress-bar__input {
    font-size: 14px;
    padding: 4px 8px;
  }
}
</style>
