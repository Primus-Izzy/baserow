export default (client) => {
  return {
    /**
     * Updates custom branding configuration for a form view.
     */
    updateCustomBranding(viewId, brandingData) {
      return client.patch(`/database/views/form/${viewId}/custom-branding/`, brandingData)
    },

    /**
     * Updates access control settings for a form view.
     */
    updateAccessControl(viewId, accessData) {
      return client.patch(`/database/views/form/${viewId}/access-control/`, accessData)
    },

    /**
     * Updates validation configuration for a form view.
     */
    updateValidationConfig(viewId, validationData) {
      return client.patch(`/database/views/form/${viewId}/validation-config/`, validationData)
    },

    /**
     * Lists all shareable links for a form view.
     */
    listShareableLinks(viewId) {
      return client.get(`/database/views/form/${viewId}/shareable-links/`)
    },

    /**
     * Creates a new shareable link for a form view.
     */
    createShareableLink(viewId, linkData) {
      return client.post(`/database/views/form/${viewId}/shareable-links/`, linkData)
    },

    /**
     * Updates an existing shareable link.
     */
    updateShareableLink(viewId, linkId, linkData) {
      return client.patch(`/database/views/form/${viewId}/shareable-links/${linkId}/`, linkData)
    },

    /**
     * Deletes a shareable link.
     */
    deleteShareableLink(viewId, linkId) {
      return client.delete(`/database/views/form/${viewId}/shareable-links/${linkId}/`)
    },

    /**
     * Updates conditional logic and validation rules for a form field.
     */
    updateFieldOptions(viewId, fieldId, optionsData) {
      return client.patch(`/database/views/form/${viewId}/field-options/${fieldId}/`, optionsData)
    },

    /**
     * Evaluates conditional logic for form fields based on current form data.
     */
    evaluateConditionalLogic(viewId, formData) {
      return client.post(`/database/views/form/${viewId}/evaluate-conditions/`, { form_data: formData })
    },

    /**
     * Validates form field values against custom validation rules.
     */
    validateFieldValues(viewId, fieldValues) {
      return client.post(`/database/views/form/${viewId}/validate-fields/`, { field_values: fieldValues })
    },

    /**
     * Submits form with enhanced validation and conditional logic processing.
     */
    submitEnhancedForm(slug, formData, options = {}) {
      const config = {
        url: `/database/views/form/${slug}/submit/`,
        method: 'POST',
        data: formData,
      }

      if (options.token) {
        config.params = { token: options.token }
      }

      if (options.linkId) {
        config.headers = { 'X-Shareable-Link-ID': options.linkId }
      }

      return client.request(config)
    },

    /**
     * Gets form configuration including enhanced features for public access.
     */
    getPublicFormConfig(slug, options = {}) {
      const config = {
        url: `/database/views/form/${slug}/config/`,
        method: 'GET',
      }

      if (options.token) {
        config.params = { token: options.token }
      }

      return client.request(config)
    },

    /**
     * Tracks form submission analytics.
     */
    trackFormSubmission(viewId, submissionData) {
      return client.post(`/database/views/form/${viewId}/track-submission/`, submissionData)
    },

    /**
     * Gets form submission statistics and analytics.
     */
    getFormAnalytics(viewId, options = {}) {
      return client.get(`/database/views/form/${viewId}/analytics/`, { params: options })
    },
  }
}