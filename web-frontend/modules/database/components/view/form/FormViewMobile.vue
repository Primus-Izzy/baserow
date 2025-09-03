<template>
  <div class="form-view-mobile">
    <!-- Mobile Header -->
    <div class="mobile-header">
      <div class="header-actions">
        <button class="action-button" @click="$emit('close-form')">
          <i class="fas fa-times"></i>
        </button>
        <h1 class="header-title">{{ form.title || 'Form' }}</h1>
        <button
          v-if="!isPublicForm"
          class="action-button"
          @click="$emit('show-options')"
        >
          <i class="fas fa-ellipsis-v"></i>
        </button>
      </div>
    </div>

    <!-- Mobile Content -->
    <div class="mobile-content">
      <!-- Form Progress -->
      <div v-if="showProgress" class="form-progress">
        <div class="progress-bar">
          <div
            class="progress-fill"
            :style="{ width: `${progressPercentage}%` }"
          ></div>
        </div>
        <span class="progress-text">
          {{ currentStep }} of {{ totalSteps }} completed
        </span>
      </div>

      <!-- Form Header -->
      <div v-if="form.description || form.cover_image" class="form-header">
        <div
          v-if="form.cover_image"
          class="cover-image"
          :style="{ backgroundImage: `url(${form.cover_image})` }"
        ></div>
        <div class="form-intro">
          <h2 v-if="form.title" class="form-title">{{ form.title }}</h2>
          <p v-if="form.description" class="form-description">
            {{ form.description }}
          </p>
        </div>
      </div>

      <!-- Form Fields -->
      <form @submit.prevent="submitForm" class="mobile-form">
        <div class="form-fields">
          <div
            v-for="(field, index) in visibleFields"
            :key="field.id"
            class="form-field-container"
            :class="{
              'field-error': hasFieldError(field.id),
              'field-hidden': !isFieldVisible(field),
              'field-required': field.required,
            }"
          >
            <!-- Field Label -->
            <label :for="`field-${field.id}`" class="field-label">
              {{ field.name }}
              <span v-if="field.required" class="required-indicator">*</span>
            </label>

            <!-- Field Description -->
            <p v-if="field.description" class="field-description">
              {{ field.description }}
            </p>

            <!-- Field Input -->
            <div class="field-input-container">
              <component
                :is="getFieldComponent(field.type)"
                :id="`field-${field.id}`"
                :field="field"
                :value="formData[`field_${field.id}`]"
                :mobile="true"
                :readonly="field.readonly"
                :required="field.required"
                :error="getFieldError(field.id)"
                @input="handleFieldInput(field, $event)"
                @change="handleFieldChange(field, $event)"
                @focus="handleFieldFocus(field)"
                @blur="handleFieldBlur(field)"
              />
            </div>

            <!-- Field Error -->
            <div v-if="hasFieldError(field.id)" class="field-error-message">
              <i class="fas fa-exclamation-circle"></i>
              {{ getFieldError(field.id) }}
            </div>

            <!-- Field Help Text -->
            <div v-if="field.help_text" class="field-help-text">
              <i class="fas fa-info-circle"></i>
              {{ field.help_text }}
            </div>
          </div>
        </div>

        <!-- Form Actions -->
        <div class="form-actions">
          <button
            v-if="hasPreviousStep"
            type="button"
            class="btn-secondary touch-feedback"
            @click="previousStep"
            :disabled="submitting"
          >
            <i class="fas fa-chevron-left"></i>
            Previous
          </button>

          <button
            v-if="hasNextStep"
            type="button"
            class="btn-primary touch-feedback"
            @click="nextStep"
            :disabled="!canProceedToNext || submitting"
          >
            Next
            <i class="fas fa-chevron-right"></i>
          </button>

          <button
            v-else
            type="submit"
            class="btn-primary touch-feedback"
            :disabled="!isFormValid || submitting"
          >
            <i v-if="submitting" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-paper-plane"></i>
            {{ submitting ? 'Submitting...' : 'Submit' }}
          </button>
        </div>
      </form>

      <!-- Success Message -->
      <div v-if="submitted" class="success-message">
        <div class="success-icon">
          <i class="fas fa-check-circle"></i>
        </div>
        <h3>{{ form.success_message || 'Thank you!' }}</h3>
        <p>Your form has been submitted successfully.</p>

        <div v-if="form.redirect_url" class="success-actions">
          <a :href="form.redirect_url" class="btn-primary touch-feedback">
            Continue
          </a>
        </div>
      </div>
    </div>

    <!-- Mobile Navigation (for multi-step forms) -->
    <div v-if="isMultiStep" class="mobile-nav">
      <div
        v-for="(step, index) in formSteps"
        :key="index"
        class="nav-item"
        :class="{
          active: currentStepIndex === index,
          completed: index < currentStepIndex,
          disabled: index > currentStepIndex,
        }"
        @click="goToStep(index)"
      >
        <div class="step-indicator">
          <i v-if="index < currentStepIndex" class="fas fa-check"></i>
          <span v-else>{{ index + 1 }}</span>
        </div>
        <span class="step-label">{{ step.name }}</span>
      </div>
    </div>

    <!-- Floating Action Button (for adding attachments) -->
    <button
      v-if="hasFileFields && !submitted"
      class="fab touch-feedback"
      @click="triggerFileUpload"
    >
      <i class="fas fa-paperclip"></i>
    </button>

    <!-- Hidden file input -->
    <input
      ref="fileInput"
      type="file"
      multiple
      accept="image/*,application/pdf,.doc,.docx"
      style="display: none"
      @change="handleFileUpload"
    />
  </div>
</template>

<script>
import mobileResponsive from '@baserow/modules/core/mixins/mobileResponsive'

export default {
  name: 'FormViewMobile',
  mixins: [mobileResponsive],
  props: {
    form: {
      type: Object,
      required: true,
    },
    fields: {
      type: Array,
      default: () => [],
    },
    isPublicForm: {
      type: Boolean,
      default: false,
    },
    initialData: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      formData: { ...this.initialData },
      errors: {},
      submitting: false,
      submitted: false,
      currentStepIndex: 0,
      focusedField: null,
      validationRules: {},
    }
  },
  computed: {
    visibleFields() {
      return this.fields.filter(
        (field) =>
          this.isFieldVisible(field) && this.isFieldInCurrentStep(field)
      )
    },

    formSteps() {
      if (!this.isMultiStep) return []
      // Group fields by step configuration
      const steps = []
      let currentStep = { name: 'Step 1', fields: [] }

      this.fields.forEach((field) => {
        if (field.step_break) {
          steps.push(currentStep)
          currentStep = {
            name: field.step_name || `Step ${steps.length + 1}`,
            fields: [],
          }
        }
        currentStep.fields.push(field)
      })

      if (currentStep.fields.length > 0) {
        steps.push(currentStep)
      }

      return steps
    },

    isMultiStep() {
      return this.formSteps.length > 1
    },

    currentStep() {
      return this.currentStepIndex + 1
    },

    totalSteps() {
      return this.isMultiStep ? this.formSteps.length : 1
    },

    progressPercentage() {
      if (!this.isMultiStep) {
        const completedFields = this.fields.filter(
          (field) =>
            this.formData[`field_${field.id}`] !== undefined &&
            this.formData[`field_${field.id}`] !== ''
        ).length
        return (completedFields / this.fields.length) * 100
      }
      return (this.currentStepIndex / this.totalSteps) * 100
    },

    showProgress() {
      return this.form.show_progress !== false
    },

    hasPreviousStep() {
      return this.isMultiStep && this.currentStepIndex > 0
    },

    hasNextStep() {
      return (
        this.isMultiStep && this.currentStepIndex < this.formSteps.length - 1
      )
    },

    canProceedToNext() {
      if (!this.isMultiStep) return true
      const currentStepFields = this.formSteps[this.currentStepIndex].fields
      return currentStepFields.every((field) => {
        if (!field.required) return true
        const value = this.formData[`field_${field.id}`]
        return value !== undefined && value !== '' && value !== null
      })
    },

    isFormValid() {
      return (
        this.fields.every((field) => {
          if (!field.required) return true
          const value = this.formData[`field_${field.id}`]
          return value !== undefined && value !== '' && value !== null
        }) && Object.keys(this.errors).length === 0
      )
    },

    hasFileFields() {
      return this.fields.some((field) => field.type === 'file')
    },
  },
  methods: {
    isFieldVisible(field) {
      // Check conditional logic
      if (!field.conditions || field.conditions.length === 0) return true

      return field.conditions.every((condition) => {
        const conditionField = this.fields.find(
          (f) => f.id === condition.field_id
        )
        if (!conditionField) return true

        const fieldValue = this.formData[`field_${condition.field_id}`]

        switch (condition.operator) {
          case 'equals':
            return fieldValue === condition.value
          case 'not_equals':
            return fieldValue !== condition.value
          case 'contains':
            return String(fieldValue).includes(condition.value)
          case 'not_empty':
            return (
              fieldValue !== undefined &&
              fieldValue !== '' &&
              fieldValue !== null
            )
          case 'empty':
            return (
              fieldValue === undefined ||
              fieldValue === '' ||
              fieldValue === null
            )
          default:
            return true
        }
      })
    },

    isFieldInCurrentStep(field) {
      if (!this.isMultiStep) return true
      const currentStepFields =
        this.formSteps[this.currentStepIndex]?.fields || []
      return currentStepFields.includes(field)
    },

    getFieldComponent(fieldType) {
      const componentMap = {
        text: 'FormFieldText',
        long_text: 'FormFieldLongText',
        number: 'FormFieldNumber',
        email: 'FormFieldEmail',
        url: 'FormFieldUrl',
        phone_number: 'FormFieldPhone',
        date: 'FormFieldDate',
        boolean: 'FormFieldBoolean',
        single_select: 'FormFieldSingleSelect',
        multiple_select: 'FormFieldMultipleSelect',
        file: 'FormFieldFile',
        rating: 'FormFieldRating',
      }
      return componentMap[fieldType] || 'FormFieldText'
    },

    handleFieldInput(field, value) {
      this.formData[`field_${field.id}`] = value
      this.clearFieldError(field.id)
      this.validateField(field, value)
    },

    handleFieldChange(field, value) {
      this.formData[`field_${field.id}`] = value
      this.validateField(field, value)
      this.$emit('field-change', { field, value })
    },

    handleFieldFocus(field) {
      this.focusedField = field.id
    },

    handleFieldBlur(field) {
      this.focusedField = null
      this.validateField(field, this.formData[`field_${field.id}`])
    },

    validateField(field, value) {
      const errors = []

      // Required validation
      if (
        field.required &&
        (value === undefined || value === '' || value === null)
      ) {
        errors.push('This field is required')
      }

      // Type-specific validation
      if (value && value !== '') {
        switch (field.type) {
          case 'email':
            if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
              errors.push('Please enter a valid email address')
            }
            break
          case 'url':
            try {
              new URL(value)
            } catch {
              errors.push('Please enter a valid URL')
            }
            break
          case 'phone_number':
            if (
              !/^[\+]?[1-9][\d]{0,15}$/.test(value.replace(/[\s\-\(\)]/g, ''))
            ) {
              errors.push('Please enter a valid phone number')
            }
            break
          case 'number':
            if (isNaN(value)) {
              errors.push('Please enter a valid number')
            } else {
              if (field.number_negative === false && parseFloat(value) < 0) {
                errors.push('Negative numbers are not allowed')
              }
              if (
                field.min_value !== undefined &&
                parseFloat(value) < field.min_value
              ) {
                errors.push(`Value must be at least ${field.min_value}`)
              }
              if (
                field.max_value !== undefined &&
                parseFloat(value) > field.max_value
              ) {
                errors.push(`Value must be at most ${field.max_value}`)
              }
            }
            break
        }
      }

      // Custom validation rules
      if (field.validation_rules) {
        field.validation_rules.forEach((rule) => {
          if (!this.validateRule(value, rule)) {
            errors.push(rule.error_message || 'Invalid value')
          }
        })
      }

      if (errors.length > 0) {
        this.errors[field.id] = errors[0]
      } else {
        delete this.errors[field.id]
      }
    },

    validateRule(value, rule) {
      switch (rule.type) {
        case 'min_length':
          return !value || value.length >= rule.value
        case 'max_length':
          return !value || value.length <= rule.value
        case 'pattern':
          return !value || new RegExp(rule.value).test(value)
        default:
          return true
      }
    },

    hasFieldError(fieldId) {
      return !!this.errors[fieldId]
    },

    getFieldError(fieldId) {
      return this.errors[fieldId]
    },

    clearFieldError(fieldId) {
      delete this.errors[fieldId]
    },

    nextStep() {
      if (this.hasNextStep && this.canProceedToNext) {
        this.currentStepIndex++
        this.scrollToTop()
      }
    },

    previousStep() {
      if (this.hasPreviousStep) {
        this.currentStepIndex--
        this.scrollToTop()
      }
    },

    goToStep(stepIndex) {
      if (stepIndex <= this.currentStepIndex || this.canProceedToNext) {
        this.currentStepIndex = stepIndex
        this.scrollToTop()
      }
    },

    scrollToTop() {
      const content = document.querySelector('.mobile-content')
      if (content) {
        content.scrollTo({ top: 0, behavior: 'smooth' })
      }
    },

    async submitForm() {
      if (!this.isFormValid || this.submitting) return

      this.submitting = true

      try {
        await this.$emit('submit', this.formData)
        this.submitted = true
        this.scrollToTop()

        // Haptic feedback if available
        if (navigator.vibrate) {
          navigator.vibrate([100, 50, 100])
        }
      } catch (error) {
        console.error('Form submission error:', error)
        // Handle submission errors
        if (
          error.response &&
          error.response.data &&
          error.response.data.errors
        ) {
          this.errors = { ...this.errors, ...error.response.data.errors }
        }
      } finally {
        this.submitting = false
      }
    },

    triggerFileUpload() {
      this.$refs.fileInput.click()
    },

    handleFileUpload(event) {
      const files = Array.from(event.target.files)
      this.$emit('file-upload', files)
    },
  },

  mounted() {
    // Auto-focus first field on mobile
    if (this.isMobileDevice) {
      this.$nextTick(() => {
        const firstInput = document.querySelector(
          '.field-input-container input, .field-input-container textarea, .field-input-container select'
        )
        if (firstInput && !this.isPublicForm) {
          firstInput.focus()
        }
      })
    }
  },
}
</script>

<style lang="scss" scoped>
@import '@baserow/modules/core/assets/scss/components/mobile/responsive.scss';

.form-view-mobile {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-neutral-50);
}

.form-progress {
  padding: $mobile-spacing-md;
  background: var(--color-neutral-100);
  border-bottom: 1px solid var(--color-neutral-200);

  .progress-bar {
    width: 100%;
    height: 6px;
    background: var(--color-neutral-200);
    border-radius: 3px;
    overflow: hidden;
    margin-bottom: $mobile-spacing-sm;

    .progress-fill {
      height: 100%;
      background: var(--color-primary);
      transition: width 0.3s ease;
    }
  }

  .progress-text {
    font-size: $mobile-font-size-sm;
    color: var(--color-neutral-600);
    text-align: center;
    display: block;
  }
}

.form-header {
  .cover-image {
    width: 100%;
    height: 200px;
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
  }

  .form-intro {
    padding: $mobile-spacing-lg $mobile-spacing-md;
    text-align: center;

    .form-title {
      margin: 0 0 $mobile-spacing-md 0;
      font-size: $mobile-font-size-xl;
      font-weight: 700;
      color: var(--color-neutral-900);
    }

    .form-description {
      margin: 0;
      font-size: $mobile-font-size-md;
      color: var(--color-neutral-600);
      line-height: 1.5;
    }
  }
}

.mobile-form {
  flex: 1;
  display: flex;
  flex-direction: column;

  .form-fields {
    flex: 1;
    padding: $mobile-spacing-md;

    .form-field-container {
      margin-bottom: $mobile-spacing-lg;

      &.field-hidden {
        display: none;
      }

      &.field-error {
        .field-input-container {
          border-color: var(--color-error);
        }
      }

      .field-label {
        display: block;
        font-size: $mobile-font-size-md;
        font-weight: 600;
        color: var(--color-neutral-900);
        margin-bottom: $mobile-spacing-sm;

        .required-indicator {
          color: var(--color-error);
          margin-left: 2px;
        }
      }

      .field-description {
        font-size: $mobile-font-size-sm;
        color: var(--color-neutral-600);
        margin: 0 0 $mobile-spacing-sm 0;
        line-height: 1.4;
      }

      .field-input-container {
        margin-bottom: $mobile-spacing-sm;

        :deep(input),
        :deep(textarea),
        :deep(select) {
          @include touch-friendly;
          width: 100%;
          border: 2px solid var(--color-neutral-300);
          border-radius: 8px;
          padding: $mobile-spacing-md;
          font-size: $mobile-font-size-md;
          background: var(--color-neutral-50);

          &:focus {
            outline: none;
            border-color: var(--color-primary);
            box-shadow: 0 0 0 3px var(--color-primary-100);
          }

          &:disabled {
            background: var(--color-neutral-100);
            color: var(--color-neutral-500);
          }
        }

        :deep(textarea) {
          min-height: 100px;
          resize: vertical;
        }

        :deep(.checkbox-container),
        :deep(.radio-container) {
          @include touch-friendly;
          display: flex;
          align-items: center;
          gap: $mobile-spacing-sm;

          input[type='checkbox'],
          input[type='radio'] {
            width: 20px;
            height: 20px;
            margin: 0;
          }

          label {
            font-size: $mobile-font-size-md;
            margin: 0;
          }
        }
      }

      .field-error-message {
        display: flex;
        align-items: center;
        gap: $mobile-spacing-sm;
        color: var(--color-error);
        font-size: $mobile-font-size-sm;
        margin-bottom: $mobile-spacing-sm;

        .fas {
          font-size: 14px;
        }
      }

      .field-help-text {
        display: flex;
        align-items: flex-start;
        gap: $mobile-spacing-sm;
        color: var(--color-neutral-600);
        font-size: $mobile-font-size-sm;
        line-height: 1.4;

        .fas {
          font-size: 14px;
          margin-top: 2px;
          flex-shrink: 0;
        }
      }
    }
  }

  .form-actions {
    padding: $mobile-spacing-md;
    background: var(--color-neutral-100);
    border-top: 1px solid var(--color-neutral-200);
    display: flex;
    gap: $mobile-spacing-md;

    button {
      @include touch-friendly;
      flex: 1;
      border: none;
      border-radius: 8px;
      padding: $mobile-spacing-md $mobile-spacing-lg;
      font-size: $mobile-font-size-md;
      font-weight: 600;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: $mobile-spacing-sm;

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }

      &.btn-primary {
        background: var(--color-primary);
        color: white;

        &:not(:disabled):active {
          background: var(--color-primary-dark);
        }
      }

      &.btn-secondary {
        background: var(--color-neutral-200);
        color: var(--color-neutral-700);

        &:not(:disabled):active {
          background: var(--color-neutral-300);
        }
      }
    }
  }
}

.success-message {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: $mobile-spacing-xl;
  text-align: center;

  .success-icon {
    font-size: 64px;
    color: var(--color-success);
    margin-bottom: $mobile-spacing-lg;
  }

  h3 {
    margin: 0 0 $mobile-spacing-md 0;
    font-size: $mobile-font-size-xl;
    color: var(--color-neutral-900);
  }

  p {
    margin: 0 0 $mobile-spacing-lg 0;
    font-size: $mobile-font-size-md;
    color: var(--color-neutral-600);
    line-height: 1.5;
  }

  .success-actions {
    .btn-primary {
      @include touch-friendly;
      background: var(--color-primary);
      color: white;
      border: none;
      border-radius: 8px;
      padding: $mobile-spacing-md $mobile-spacing-lg;
      font-size: $mobile-font-size-md;
      font-weight: 600;
      text-decoration: none;
      display: inline-block;
    }
  }
}

.mobile-nav {
  display: flex;
  background: var(--color-neutral-100);
  border-top: 1px solid var(--color-neutral-200);
  padding: $mobile-spacing-sm;
  gap: $mobile-spacing-sm;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;

  .nav-item {
    @include touch-friendly;
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 80px;
    padding: $mobile-spacing-sm;
    border-radius: 8px;
    cursor: pointer;

    &.active {
      background: var(--color-primary);
      color: white;
    }

    &.completed {
      background: var(--color-success-100);
      color: var(--color-success);
    }

    &.disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .step-indicator {
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: var(--color-neutral-300);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: $mobile-font-size-sm;
      font-weight: 600;
      margin-bottom: 4px;

      .nav-item.active & {
        background: white;
        color: var(--color-primary);
      }

      .nav-item.completed & {
        background: var(--color-success);
        color: white;
      }
    }

    .step-label {
      font-size: $mobile-font-size-xs;
      text-align: center;
      line-height: 1.2;
    }
  }
}

.fab {
  position: fixed;
  bottom: 80px;
  right: $mobile-spacing-md;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  z-index: 100;

  &:active {
    transform: scale(0.95);
  }
}
</style>
