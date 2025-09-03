<template>
  <div class="row-card-field" :class="{ 'row-card-field--editing': isEditing }">
    <!-- Display mode -->
    <div
      v-if="!isEditing"
      class="row-card-field__display"
      @click="startEditing"
      @dblclick="startEditing"
    >
      <component
        :is="getCardComponent(field)"
        :row="row"
        :field="field"
        :value="value"
        :workspace-id="workspaceId"
      />
    </div>

    <!-- Edit mode -->
    <div v-else class="row-card-field__edit">
      <component
        :is="getFieldComponent(field)"
        ref="fieldComponent"
        :field="field"
        :value="value"
        @input="handleInput"
        @blur="finishEditing"
        @keydown.enter="finishEditing"
        @keydown.escape="cancelEditing"
      />
    </div>
  </div>
</template>

<script>
export default {
  name: 'RowCardField',
  props: {
    field: {
      type: Object,
      required: true,
    },
    row: {
      type: Object,
      required: true,
    },
    value: {
      required: true,
    },
    readOnly: {
      type: Boolean,
      default: false,
    },
    workspaceId: {
      type: Number,
      required: false,
      default: null,
    },
    decorationsByPlace: {
      type: Object,
      required: false,
      default: () => ({}),
    },
  },
  data() {
    return {
      isEditing: false,
      editValue: null,
      originalValue: null,
    }
  },
  computed: {
    /**
     * Determines if this field type supports inline editing.
     */
    canEdit() {
      if (this.readOnly) return false

      const inlineEditableTypes = [
        'text',
        'long_text',
        'number',
        'rating',
        'boolean',
        'single_select',
        'multiple_select',
        'date',
        'url',
        'email',
        'phone_number',
      ]
      return inlineEditableTypes.includes(this.field.type)
    },
  },
  methods: {
    /**
     * Gets the appropriate card component for displaying the field value.
     */
    getCardComponent(field) {
      const fieldType = this.$registry.get('field', field.type)
      return fieldType.getCardComponent(field)
    },
    /**
     * Gets the appropriate field component for editing.
     */
    getFieldComponent(field) {
      const fieldType = this.$registry.get('field', field.type)
      return fieldType.getRowEditFieldComponent(field)
    },
    /**
     * Starts inline editing mode.
     */
    startEditing() {
      if (!this.canEdit) return

      this.originalValue = this.value
      this.editValue = this.value
      this.isEditing = true

      this.$nextTick(() => {
        if (this.$refs.fieldComponent && this.$refs.fieldComponent.focus) {
          this.$refs.fieldComponent.focus()
        }
      })
    },
    /**
     * Handles input changes during editing.
     */
    handleInput(value) {
      this.editValue = value
    },
    /**
     * Finishes editing and saves the value.
     */
    finishEditing() {
      if (!this.isEditing) return

      const newValue = this.editValue
      const oldValue = this.originalValue

      this.isEditing = false

      if (newValue !== oldValue) {
        this.$emit('updated', {
          field: this.field,
          row: this.row,
          value: newValue,
          oldValue,
        })
      }
    },
    /**
     * Cancels editing and reverts to original value.
     */
    cancelEditing() {
      this.isEditing = false
      this.editValue = this.originalValue
    },
  },
}
</script>

<style lang="scss" scoped>
.row-card-field {
  &--editing {
    .row-card-field__display {
      display: none;
    }
  }

  &__display {
    cursor: pointer;
    min-height: 20px;

    &:hover {
      background-color: rgba(0, 0, 0, 0.05);
      border-radius: 4px;
    }
  }

  &__edit {
    .field-text,
    .field-number,
    .field-url,
    .field-email,
    .field-phone-number {
      input {
        border: 1px solid #3b82f6;
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 13px;
        width: 100%;

        &:focus {
          outline: none;
          box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
        }
      }
    }
  }
}
</style>
