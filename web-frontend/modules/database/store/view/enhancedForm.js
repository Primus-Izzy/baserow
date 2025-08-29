import EnhancedFormService from '@baserow/modules/database/services/view/enhancedForm'

export const state = () => ({
  customBranding: {},
  accessControl: {},
  validationConfig: {},
  shareableLinks: [],
  fieldConditionalLogic: {},
  fieldValidationRules: {},
  formAnalytics: {},
  conditionalFieldsVisibility: {},
  validationErrors: {},
})

export const mutations = {
  SET_CUSTOM_BRANDING(state, branding) {
    state.customBranding = branding
  },
  SET_ACCESS_CONTROL(state, accessControl) {
    state.accessControl = accessControl
  },
  SET_VALIDATION_CONFIG(state, validationConfig) {
    state.validationConfig = validationConfig
  },
  SET_SHAREABLE_LINKS(state, links) {
    state.shareableLinks = links
  },
  ADD_SHAREABLE_LINK(state, link) {
    state.shareableLinks.push(link)
  },
  UPDATE_SHAREABLE_LINK(state, { linkId, linkData }) {
    const index = state.shareableLinks.findIndex(link => link.id === linkId)
    if (index !== -1) {
      state.shareableLinks.splice(index, 1, { ...state.shareableLinks[index], ...linkData })
    }
  },
  REMOVE_SHAREABLE_LINK(state, linkId) {
    const index = state.shareableLinks.findIndex(link => link.id === linkId)
    if (index !== -1) {
      state.shareableLinks.splice(index, 1)
    }
  },
  SET_FIELD_CONDITIONAL_LOGIC(state, { fieldId, logic }) {
    state.fieldConditionalLogic = {
      ...state.fieldConditionalLogic,
      [fieldId]: logic,
    }
  },
  SET_FIELD_VALIDATION_RULES(state, { fieldId, rules }) {
    state.fieldValidationRules = {
      ...state.fieldValidationRules,
      [fieldId]: rules,
    }
  },
  SET_FORM_ANALYTICS(state, analytics) {
    state.formAnalytics = analytics
  },
  SET_CONDITIONAL_FIELDS_VISIBILITY(state, visibility) {
    state.conditionalFieldsVisibility = visibility
  },
  SET_VALIDATION_ERRORS(state, errors) {
    state.validationErrors = errors
  },
  CLEAR_VALIDATION_ERRORS(state) {
    state.validationErrors = {}
  },
}

export const actions = {
  /**
   * Updates custom branding configuration for a form view.
   */
  async updateCustomBranding({ commit }, { viewId, brandingData }) {
    const { data } = await EnhancedFormService(this.$client).updateCustomBranding(viewId, brandingData)
    commit('SET_CUSTOM_BRANDING', data.custom_branding)
    return data
  },

  /**
   * Updates access control settings for a form view.
   */
  async updateAccessControl({ commit }, { viewId, accessData }) {
    const { data } = await EnhancedFormService(this.$client).updateAccessControl(viewId, accessData)
    commit('SET_ACCESS_CONTROL', data.access_control)
    return data
  },

  /**
   * Updates validation configuration for a form view.
   */
  async updateValidationConfig({ commit }, { viewId, validationData }) {
    const { data } = await EnhancedFormService(this.$client).updateValidationConfig(viewId, validationData)
    commit('SET_VALIDATION_CONFIG', data.validation_config)
    return data
  },

  /**
   * Loads all shareable links for a form view.
   */
  async loadShareableLinks({ commit }, { viewId }) {
    const { data } = await EnhancedFormService(this.$client).listShareableLinks(viewId)
    commit('SET_SHAREABLE_LINKS', data)
    return data
  },

  /**
   * Creates a new shareable link for a form view.
   */
  async createShareableLink({ commit }, { viewId, linkData }) {
    const { data } = await EnhancedFormService(this.$client).createShareableLink(viewId, linkData)
    commit('ADD_SHAREABLE_LINK', data)
    return data
  },

  /**
   * Updates an existing shareable link.
   */
  async updateShareableLink({ commit }, { viewId, linkId, linkData }) {
    const { data } = await EnhancedFormService(this.$client).updateShareableLink(viewId, linkId, linkData)
    commit('UPDATE_SHAREABLE_LINK', { linkId, linkData: data })
    return data
  },

  /**
   * Deletes a shareable link.
   */
  async deleteShareableLink({ commit }, { viewId, linkId }) {
    await EnhancedFormService(this.$client).deleteShareableLink(viewId, linkId)
    commit('REMOVE_SHAREABLE_LINK', linkId)
  },

  /**
   * Updates conditional logic for a form field.
   */
  async updateFieldConditionalLogic({ commit }, { viewId, fieldId, logicData }) {
    const { data } = await EnhancedFormService(this.$client).updateFieldOptions(viewId, fieldId, {
      conditional_logic: logicData,
    })
    commit('SET_FIELD_CONDITIONAL_LOGIC', { fieldId, logic: data.conditional_logic })
    return data
  },

  /**
   * Updates validation rules for a form field.
   */
  async updateFieldValidationRules({ commit }, { viewId, fieldId, rulesData }) {
    const { data } = await EnhancedFormService(this.$client).updateFieldOptions(viewId, fieldId, {
      validation_rules: rulesData,
    })
    commit('SET_FIELD_VALIDATION_RULES', { fieldId, rules: data.validation_rules })
    return data
  },

  /**
   * Evaluates conditional logic for form fields based on current form data.
   */
  async evaluateConditionalLogic({ commit }, { viewId, formData }) {
    const { data } = await EnhancedFormService(this.$client).evaluateConditionalLogic(viewId, formData)
    commit('SET_CONDITIONAL_FIELDS_VISIBILITY', data.field_visibility)
    return data
  },

  /**
   * Validates form field values against custom validation rules.
   */
  async validateFieldValues({ commit }, { viewId, fieldValues }) {
    try {
      const { data } = await EnhancedFormService(this.$client).validateFieldValues(viewId, fieldValues)
      commit('SET_VALIDATION_ERRORS', data.errors || {})
      return data
    } catch (error) {
      if (error.response?.status === 400) {
        commit('SET_VALIDATION_ERRORS', error.response.data.field_errors || {})
      }
      throw error
    }
  },

  /**
   * Submits form with enhanced validation and conditional logic processing.
   */
  async submitEnhancedForm({ commit }, { slug, formData, options = {} }) {
    try {
      commit('CLEAR_VALIDATION_ERRORS')
      const { data } = await EnhancedFormService(this.$client).submitEnhancedForm(slug, formData, options)
      return data
    } catch (error) {
      if (error.response?.status === 400) {
        commit('SET_VALIDATION_ERRORS', error.response.data.field_errors || {})
      }
      throw error
    }
  },

  /**
   * Gets form configuration including enhanced features for public access.
   */
  async getPublicFormConfig({ commit }, { slug, options = {} }) {
    const { data } = await EnhancedFormService(this.$client).getPublicFormConfig(slug, options)
    
    // Update store with form configuration
    if (data.custom_branding) {
      commit('SET_CUSTOM_BRANDING', data.custom_branding)
    }
    if (data.access_control) {
      commit('SET_ACCESS_CONTROL', data.access_control)
    }
    if (data.validation_config) {
      commit('SET_VALIDATION_CONFIG', data.validation_config)
    }
    
    return data
  },

  /**
   * Loads form analytics data.
   */
  async loadFormAnalytics({ commit }, { viewId, options = {} }) {
    const { data } = await EnhancedFormService(this.$client).getFormAnalytics(viewId, options)
    commit('SET_FORM_ANALYTICS', data)
    return data
  },

  /**
   * Clears all validation errors.
   */
  clearValidationErrors({ commit }) {
    commit('CLEAR_VALIDATION_ERRORS')
  },

  /**
   * Resets the enhanced form state.
   */
  reset({ commit }) {
    commit('SET_CUSTOM_BRANDING', {})
    commit('SET_ACCESS_CONTROL', {})
    commit('SET_VALIDATION_CONFIG', {})
    commit('SET_SHAREABLE_LINKS', [])
    commit('SET_FIELD_CONDITIONAL_LOGIC', {})
    commit('SET_FIELD_VALIDATION_RULES', {})
    commit('SET_FORM_ANALYTICS', {})
    commit('SET_CONDITIONAL_FIELDS_VISIBILITY', {})
    commit('CLEAR_VALIDATION_ERRORS')
  },
}

export const getters = {
  getCustomBranding: (state) => state.customBranding,
  getAccessControl: (state) => state.accessControl,
  getValidationConfig: (state) => state.validationConfig,
  getShareableLinks: (state) => state.shareableLinks,
  getFieldConditionalLogic: (state) => (fieldId) => state.fieldConditionalLogic[fieldId] || {},
  getFieldValidationRules: (state) => (fieldId) => state.fieldValidationRules[fieldId] || [],
  getFormAnalytics: (state) => state.formAnalytics,
  isFieldVisible: (state) => (fieldId) => {
    return state.conditionalFieldsVisibility[fieldId] !== false
  },
  getFieldValidationErrors: (state) => (fieldId) => state.validationErrors[fieldId] || [],
  hasValidationErrors: (state) => Object.keys(state.validationErrors).length > 0,
}