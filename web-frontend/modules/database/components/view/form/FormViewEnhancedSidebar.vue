<template>
  <div class="form-view-enhanced-sidebar">
    <div class="form-view-enhanced-sidebar__tabs">
      <div
        v-for="tab in tabs"
        :key="tab.key"
        class="form-view-enhanced-sidebar__tab"
        :class="{
          'form-view-enhanced-sidebar__tab--active': activeTab === tab.key,
        }"
        @click="activeTab = tab.key"
      >
        <i :class="tab.icon"></i>
        {{ tab.label }}
      </div>
    </div>

    <div class="form-view-enhanced-sidebar__content">
      <!-- Fields Tab -->
      <div
        v-if="activeTab === 'fields'"
        class="form-view-enhanced-sidebar__tab-content"
      >
        <FormViewSidebar
          :database="database"
          :table="table"
          :view="view"
          :fields="fields"
          :enabled-fields="enabledFields"
          :all-fields-in-table="allFields"
          :read-only="readOnly"
          :store-prefix="storePrefix"
          @ordered-fields="$emit('ordered-fields', $event)"
          @refresh="$emit('refresh', $event)"
        />
      </div>

      <!-- Conditional Logic Tab -->
      <div
        v-if="activeTab === 'conditional'"
        class="form-view-enhanced-sidebar__tab-content"
      >
        <div class="form-view-enhanced-sidebar__section">
          <h3>{{ $t('formViewEnhancedSidebar.conditionalLogic') }}</h3>
          <p class="form-view-enhanced-sidebar__section-description">
            {{ $t('formViewEnhancedSidebar.conditionalLogicDescription') }}
          </p>

          <div
            v-for="fieldOption in enabledFieldOptions"
            :key="fieldOption.field.id"
            class="form-view-enhanced-sidebar__field-conditional"
          >
            <div class="form-view-enhanced-sidebar__field-header">
              <h4>{{ fieldOption.field.name }}</h4>
            </div>
            <FormViewConditionalLogic
              :field-options="fieldOption"
              :fields="allFields"
              :read-only="readOnly"
              @update-conditional-logic="
                updateFieldConditionalLogic(fieldOption, $event)
              "
            />
          </div>
        </div>
      </div>

      <!-- Validation Tab -->
      <div
        v-if="activeTab === 'validation'"
        class="form-view-enhanced-sidebar__tab-content"
      >
        <div class="form-view-enhanced-sidebar__section">
          <h3>{{ $t('formViewEnhancedSidebar.validation') }}</h3>
          <p class="form-view-enhanced-sidebar__section-description">
            {{ $t('formViewEnhancedSidebar.validationDescription') }}
          </p>

          <div
            v-for="fieldOption in enabledFieldOptions"
            :key="fieldOption.field.id"
            class="form-view-enhanced-sidebar__field-validation"
          >
            <div class="form-view-enhanced-sidebar__field-header">
              <h4>{{ fieldOption.field.name }}</h4>
            </div>
            <FormViewValidationRules
              :field-options="fieldOption"
              :read-only="readOnly"
              @update-validation-rules="
                updateFieldValidationRules(fieldOption, $event)
              "
            />
          </div>
        </div>
      </div>

      <!-- Branding Tab -->
      <div
        v-if="activeTab === 'branding'"
        class="form-view-enhanced-sidebar__tab-content"
      >
        <FormViewCustomBranding
          :view="view"
          :read-only="readOnly"
          @update-branding="updateCustomBranding"
        />
      </div>

      <!-- Access Control Tab -->
      <div
        v-if="activeTab === 'access'"
        class="form-view-enhanced-sidebar__tab-content"
      >
        <div class="form-view-enhanced-sidebar__section">
          <h3>{{ $t('formViewEnhancedSidebar.accessControl') }}</h3>
          <p class="form-view-enhanced-sidebar__section-description">
            {{ $t('formViewEnhancedSidebar.accessControlDescription') }}
          </p>

          <FormGroup
            :label="$t('formViewEnhancedSidebar.publicAccess')"
            class="margin-bottom-2"
          >
            <Checkbox
              v-model="accessControl.public_access"
              @input="updateAccessControl"
            >
              {{ $t('formViewEnhancedSidebar.allowPublicAccess') }}
            </Checkbox>
          </FormGroup>

          <FormGroup
            :label="$t('formViewEnhancedSidebar.requireAuthentication')"
            class="margin-bottom-2"
          >
            <Checkbox
              v-model="accessControl.require_authentication"
              @input="updateAccessControl"
            >
              {{ $t('formViewEnhancedSidebar.requireAuthenticationLabel') }}
            </Checkbox>
          </FormGroup>

          <FormGroup
            v-if="!accessControl.require_authentication"
            :label="$t('formViewEnhancedSidebar.submissionLimit')"
            class="margin-bottom-2"
          >
            <FormInput
              v-model="accessControl.submission_limit"
              type="number"
              :placeholder="
                $t('formViewEnhancedSidebar.submissionLimitPlaceholder')
              "
              min="1"
              @input="updateAccessControl"
            />
          </FormGroup>
        </div>
      </div>

      <!-- Sharing Tab -->
      <div
        v-if="activeTab === 'sharing'"
        class="form-view-enhanced-sidebar__tab-content"
      >
        <FormViewShareableLinks
          :view="view"
          :read-only="readOnly"
          @create-shareable-link="createShareableLink"
          @update-shareable-link="updateShareableLink"
          @delete-shareable-link="deleteShareableLink"
          @edit-link="editShareableLink"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { debounce } from 'lodash'
import FormViewSidebar from '@baserow/modules/database/components/view/form/FormViewSidebar'
import FormViewConditionalLogic from '@baserow/modules/database/components/view/form/FormViewConditionalLogic'
import FormViewValidationRules from '@baserow/modules/database/components/view/form/FormViewValidationRules'
import FormViewCustomBranding from '@baserow/modules/database/components/view/form/FormViewCustomBranding'
import FormViewShareableLinks from '@baserow/modules/database/components/view/form/FormViewShareableLinks'

export default {
  name: 'FormViewEnhancedSidebar',
  components: {
    FormViewSidebar,
    FormViewConditionalLogic,
    FormViewValidationRules,
    FormViewCustomBranding,
    FormViewShareableLinks,
  },
  props: {
    database: {
      type: Object,
      required: true,
    },
    table: {
      type: Object,
      required: true,
    },
    view: {
      type: Object,
      required: true,
    },
    fields: {
      type: Array,
      required: true,
    },
    enabledFields: {
      type: Array,
      required: true,
    },
    allFields: {
      type: Array,
      required: true,
    },
    readOnly: {
      type: Boolean,
      required: true,
    },
    storePrefix: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      activeTab: 'fields',
      accessControl: {
        public_access: true,
        require_authentication: false,
        submission_limit: null,
        ...this.view.access_control,
      },
    }
  },
  computed: {
    tabs() {
      return [
        {
          key: 'fields',
          label: this.$t('formViewEnhancedSidebar.tabs.fields'),
          icon: 'iconoir-list',
        },
        {
          key: 'conditional',
          label: this.$t('formViewEnhancedSidebar.tabs.conditional'),
          icon: 'iconoir-git-branch',
        },
        {
          key: 'validation',
          label: this.$t('formViewEnhancedSidebar.tabs.validation'),
          icon: 'iconoir-check-circle',
        },
        {
          key: 'branding',
          label: this.$t('formViewEnhancedSidebar.tabs.branding'),
          icon: 'iconoir-color-palette',
        },
        {
          key: 'access',
          label: this.$t('formViewEnhancedSidebar.tabs.access'),
          icon: 'iconoir-lock',
        },
        {
          key: 'sharing',
          label: this.$t('formViewEnhancedSidebar.tabs.sharing'),
          icon: 'iconoir-share',
        },
      ]
    },
    enabledFieldOptions() {
      // Return field options for enabled fields
      return this.enabledFields.map((field) => {
        const fieldOption = this.view.field_options?.find(
          (opt) => opt.field.id === field.id
        )
        return (
          fieldOption || { field, conditional_logic: {}, validation_rules: [] }
        )
      })
    },
  },
  created() {
    this.debouncedUpdateAccessControl = debounce(this.saveAccessControl, 1000)
  },
  methods: {
    updateAccessControl() {
      if (this.readOnly) return
      this.debouncedUpdateAccessControl()
    },
    async saveAccessControl() {
      try {
        await this.$emit('update-access-control', this.accessControl)
      } catch (error) {
        this.$store.dispatch('toast/error', {
          title: this.$t('formViewEnhancedSidebar.accessControlUpdateError'),
          message: error.response?.data?.error || error.message,
        })
      }
    },
    async updateCustomBranding(brandingData) {
      try {
        await this.$emit('update-custom-branding', brandingData)
      } catch (error) {
        this.$store.dispatch('toast/error', {
          title: this.$t('formViewEnhancedSidebar.brandingUpdateError'),
          message: error.response?.data?.error || error.message,
        })
      }
    },
    async updateFieldConditionalLogic(fieldOption, logicData) {
      try {
        await this.$emit(
          'update-field-conditional-logic',
          fieldOption.field.id,
          logicData
        )
      } catch (error) {
        this.$store.dispatch('toast/error', {
          title: this.$t('formViewEnhancedSidebar.conditionalLogicUpdateError'),
          message: error.response?.data?.error || error.message,
        })
      }
    },
    async updateFieldValidationRules(fieldOption, rulesData) {
      try {
        await this.$emit(
          'update-field-validation-rules',
          fieldOption.field.id,
          rulesData
        )
      } catch (error) {
        this.$store.dispatch('toast/error', {
          title: this.$t('formViewEnhancedSidebar.validationRulesUpdateError'),
          message: error.response?.data?.error || error.message,
        })
      }
    },
    async createShareableLink(linkData) {
      try {
        await this.$emit('create-shareable-link', linkData)
      } catch (error) {
        this.$store.dispatch('toast/error', {
          title: this.$t('formViewEnhancedSidebar.shareableLinkCreateError'),
          message: error.response?.data?.error || error.message,
        })
      }
    },
    async updateShareableLink(linkId, linkData) {
      try {
        await this.$emit('update-shareable-link', linkId, linkData)
      } catch (error) {
        this.$store.dispatch('toast/error', {
          title: this.$t('formViewEnhancedSidebar.shareableLinkUpdateError'),
          message: error.response?.data?.error || error.message,
        })
      }
    },
    async deleteShareableLink(linkId) {
      try {
        await this.$emit('delete-shareable-link', linkId)
      } catch (error) {
        this.$store.dispatch('toast/error', {
          title: this.$t('formViewEnhancedSidebar.shareableLinkDeleteError'),
          message: error.response?.data?.error || error.message,
        })
      }
    },
    editShareableLink(link) {
      // Switch to sharing tab and trigger edit mode
      this.activeTab = 'sharing'
      this.$nextTick(() => {
        this.$emit('edit-shareable-link', link)
      })
    },
  },
}
</script>

<style lang="scss" scoped>
.form-view-enhanced-sidebar {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #f8f9fa;

  &__tabs {
    display: flex;
    border-bottom: 1px solid #e1e5e9;
    background-color: white;
    overflow-x: auto;
  }

  &__tab {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 16px;
    font-size: 14px;
    font-weight: 500;
    color: #718096;
    cursor: pointer;
    border-bottom: 2px solid transparent;
    white-space: nowrap;
    transition: all 0.2s ease;

    &:hover {
      color: #2d3748;
      background-color: #f7fafc;
    }

    &--active {
      color: #3182ce;
      border-bottom-color: #3182ce;
      background-color: #ebf8ff;
    }

    i {
      font-size: 16px;
    }
  }

  &__content {
    flex: 1;
    overflow-y: auto;
    padding: 0;
  }

  &__tab-content {
    padding: 20px;
  }

  &__section {
    margin-bottom: 32px;

    h3 {
      margin: 0 0 8px 0;
      font-size: 18px;
      font-weight: 600;
      color: #2d3748;
    }
  }

  &__section-description {
    margin: 0 0 20px 0;
    font-size: 14px;
    color: #718096;
  }

  &__field-conditional,
  &__field-validation {
    margin-bottom: 24px;
    padding: 16px;
    background-color: white;
    border: 1px solid #e1e5e9;
    border-radius: 8px;
  }

  &__field-header {
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid #e1e5e9;

    h4 {
      margin: 0;
      font-size: 14px;
      font-weight: 600;
      color: #2d3748;
    }
  }
}
</style>
