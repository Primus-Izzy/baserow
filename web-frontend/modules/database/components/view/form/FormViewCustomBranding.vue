<template>
  <div class="form-view-custom-branding">
    <div class="form-view-custom-branding__header">
      <h3>{{ $t('formViewCustomBranding.title') }}</h3>
      <p class="form-view-custom-branding__description">
        {{ $t('formViewCustomBranding.description') }}
      </p>
    </div>

    <div class="form-view-custom-branding__sections">
      <!-- Logo Section -->
      <div class="form-view-custom-branding__section">
        <h4>{{ $t('formViewCustomBranding.logoSection') }}</h4>
        
        <FormGroup
          :label="$t('formViewCustomBranding.logoUrl')"
          :error="errors.logo_url"
          class="margin-bottom-2"
        >
          <FormInput
            v-model="branding.logo_url"
            :placeholder="$t('formViewCustomBranding.logoUrlPlaceholder')"
            @input="updateBranding"
          />
        </FormGroup>

        <FormGroup
          :label="$t('formViewCustomBranding.logoAlt')"
          :error="errors.logo_alt"
          class="margin-bottom-2"
        >
          <FormInput
            v-model="branding.logo_alt"
            :placeholder="$t('formViewCustomBranding.logoAltPlaceholder')"
            @input="updateBranding"
          />
        </FormGroup>
      </div>

      <!-- Colors Section -->
      <div class="form-view-custom-branding__section">
        <h4>{{ $t('formViewCustomBranding.colorsSection') }}</h4>
        
        <div class="form-view-custom-branding__color-grid">
          <FormGroup
            :label="$t('formViewCustomBranding.primaryColor')"
            :error="errors.primary_color"
          >
            <div class="form-view-custom-branding__color-input">
              <input
                v-model="branding.primary_color"
                type="color"
                class="form-view-custom-branding__color-picker"
                @input="updateBranding"
              />
              <FormInput
                v-model="branding.primary_color"
                :placeholder="#007bff"
                @input="updateBranding"
              />
            </div>
          </FormGroup>

          <FormGroup
            :label="$t('formViewCustomBranding.secondaryColor')"
            :error="errors.secondary_color"
          >
            <div class="form-view-custom-branding__color-input">
              <input
                v-model="branding.secondary_color"
                type="color"
                class="form-view-custom-branding__color-picker"
                @input="updateBranding"
              />
              <FormInput
                v-model="branding.secondary_color"
                :placeholder="#6c757d"
                @input="updateBranding"
              />
            </div>
          </FormGroup>

          <FormGroup
            :label="$t('formViewCustomBranding.backgroundColor')"
            :error="errors.background_color"
          >
            <div class="form-view-custom-branding__color-input">
              <input
                v-model="branding.background_color"
                type="color"
                class="form-view-custom-branding__color-picker"
                @input="updateBranding"
              />
              <FormInput
                v-model="branding.background_color"
                :placeholder="#ffffff"
                @input="updateBranding"
              />
            </div>
          </FormGroup>

          <FormGroup
            :label="$t('formViewCustomBranding.textColor')"
            :error="errors.text_color"
          >
            <div class="form-view-custom-branding__color-input">
              <input
                v-model="branding.text_color"
                type="color"
                class="form-view-custom-branding__color-picker"
                @input="updateBranding"
              />
              <FormInput
                v-model="branding.text_color"
                :placeholder="#212529"
                @input="updateBranding"
              />
            </div>
          </FormGroup>
        </div>
      </div>

      <!-- Thank You Message Section -->
      <div class="form-view-custom-branding__section">
        <h4>{{ $t('formViewCustomBranding.thankYouSection') }}</h4>
        
        <FormGroup
          :label="$t('formViewCustomBranding.thankYouTitle')"
          :error="errors.thank_you_title"
          class="margin-bottom-2"
        >
          <FormInput
            v-model="branding.thank_you_title"
            :placeholder="$t('formViewCustomBranding.thankYouTitlePlaceholder')"
            @input="updateBranding"
          />
        </FormGroup>

        <FormGroup
          :label="$t('formViewCustomBranding.thankYouMessage')"
          :error="errors.thank_you_message"
          class="margin-bottom-2"
        >
          <FormTextarea
            v-model="branding.thank_you_message"
            :placeholder="$t('formViewCustomBranding.thankYouMessagePlaceholder')"
            :rows="4"
            @input="updateBranding"
          />
        </FormGroup>
      </div>

      <!-- Custom CSS Section -->
      <div class="form-view-custom-branding__section">
        <h4>{{ $t('formViewCustomBranding.customCssSection') }}</h4>
        <p class="form-view-custom-branding__section-description">
          {{ $t('formViewCustomBranding.customCssDescription') }}
        </p>
        
        <FormGroup
          :label="$t('formViewCustomBranding.customCss')"
          :error="errors.custom_css"
        >
          <FormTextarea
            v-model="branding.custom_css"
            :placeholder="$t('formViewCustomBranding.customCssPlaceholder')"
            :rows="8"
            class="form-view-custom-branding__css-textarea"
            @input="updateBranding"
          />
        </FormGroup>
      </div>
    </div>

    <!-- Preview Section -->
    <div class="form-view-custom-branding__preview">
      <h4>{{ $t('formViewCustomBranding.preview') }}</h4>
      <div 
        class="form-view-custom-branding__preview-container"
        :style="previewStyles"
      >
        <div v-if="branding.logo_url" class="form-view-custom-branding__preview-logo">
          <img 
            :src="branding.logo_url" 
            :alt="branding.logo_alt || 'Logo'"
            class="form-view-custom-branding__preview-logo-img"
          />
        </div>
        <h3 class="form-view-custom-branding__preview-title">
          {{ branding.thank_you_title || $t('formViewCustomBranding.defaultThankYouTitle') }}
        </h3>
        <p class="form-view-custom-branding__preview-message">
          {{ branding.thank_you_message || $t('formViewCustomBranding.defaultThankYouMessage') }}
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { debounce } from 'lodash'

export default {
  name: 'FormViewCustomBranding',
  props: {
    view: {
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
      branding: {
        logo_url: '',
        logo_alt: '',
        primary_color: '#007bff',
        secondary_color: '#6c757d',
        background_color: '#ffffff',
        text_color: '#212529',
        thank_you_title: '',
        thank_you_message: '',
        custom_css: '',
        ...this.view.custom_branding,
      },
      errors: {},
    }
  },
  computed: {
    previewStyles() {
      return {
        backgroundColor: this.branding.background_color || '#ffffff',
        color: this.branding.text_color || '#212529',
        '--primary-color': this.branding.primary_color || '#007bff',
        '--secondary-color': this.branding.secondary_color || '#6c757d',
      }
    },
  },
  created() {
    this.debouncedUpdate = debounce(this.saveBranding, 1000)
  },
  methods: {
    updateBranding() {
      if (this.readOnly) return
      this.debouncedUpdate()
    },
    async saveBranding() {
      try {
        await this.$emit('update-branding', this.branding)
        this.errors = {}
      } catch (error) {
        if (error.response?.data?.error === 'ERROR_REQUEST_BODY_VALIDATION') {
          this.errors = error.response.data.detail || {}
        } else {
          this.$store.dispatch('toast/error', {
            title: this.$t('formViewCustomBranding.updateError'),
            message: error.response?.data?.error || error.message,
          })
        }
      }
    },
    validateColor(color) {
      const hexColorRegex = /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/
      return hexColorRegex.test(color)
    },
  },
}
</script>

<style lang="scss" scoped>
.form-view-custom-branding {
  &__header {
    margin-bottom: 24px;

    h3 {
      margin: 0 0 8px 0;
      font-size: 18px;
      font-weight: 600;
      color: #2d3748;
    }
  }

  &__description {
    margin: 0;
    font-size: 14px;
    color: #718096;
  }

  &__sections {
    display: flex;
    flex-direction: column;
    gap: 32px;
  }

  &__section {
    h4 {
      margin: 0 0 16px 0;
      font-size: 16px;
      font-weight: 600;
      color: #2d3748;
    }
  }

  &__section-description {
    margin: 0 0 16px 0;
    font-size: 14px;
    color: #718096;
  }

  &__color-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
  }

  &__color-input {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  &__color-picker {
    width: 40px;
    height: 40px;
    border: 1px solid #e1e5e9;
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

  &__css-textarea {
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 12px;
  }

  &__preview {
    margin-top: 32px;
    padding-top: 32px;
    border-top: 1px solid #e1e5e9;

    h4 {
      margin: 0 0 16px 0;
      font-size: 16px;
      font-weight: 600;
      color: #2d3748;
    }
  }

  &__preview-container {
    padding: 24px;
    border: 1px solid #e1e5e9;
    border-radius: 8px;
    text-align: center;
  }

  &__preview-logo {
    margin-bottom: 16px;
  }

  &__preview-logo-img {
    max-width: 200px;
    max-height: 80px;
    object-fit: contain;
  }

  &__preview-title {
    margin: 0 0 12px 0;
    font-size: 24px;
    font-weight: 600;
    color: var(--primary-color);
  }

  &__preview-message {
    margin: 0;
    font-size: 16px;
    line-height: 1.5;
  }
}
</style>