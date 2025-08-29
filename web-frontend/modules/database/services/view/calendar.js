import ViewService from '@baserow/modules/database/services/view'

export default {
  ...ViewService,
  
  /**
   * Fetches events for a calendar view within a date range.
   */
  async fetchEvents(
    viewId,
    startDate,
    endDate,
    includeRecurring = true,
    cancelToken = null,
    publicAuthToken = null
  ) {
    const config = {
      method: 'POST',
      url: `database/views/calendar/${viewId}/events/`,
      data: {
        start_date: startDate,
        end_date: endDate,
        include_recurring: includeRecurring,
      },
    }

    if (cancelToken !== null) {
      config.cancelToken = cancelToken
    }

    if (publicAuthToken !== null) {
      config.headers = {
        Authorization: `JWT ${publicAuthToken}`,
      }
    }

    const { data } = await this.client.request(config)
    return data
  },

  /**
   * Moves a calendar event to a new date.
   */
  async moveEvent(
    viewId,
    rowId,
    newDate,
    updateEndDate = false,
    cancelToken = null,
    publicAuthToken = null
  ) {
    const config = {
      method: 'POST',
      url: `database/views/calendar/${viewId}/move-event/`,
      data: {
        row_id: rowId,
        new_date: newDate,
        update_end_date: updateEndDate,
      },
    }

    if (cancelToken !== null) {
      config.cancelToken = cancelToken
    }

    if (publicAuthToken !== null) {
      config.headers = {
        Authorization: `JWT ${publicAuthToken}`,
      }
    }

    const { data } = await this.client.request(config)
    return data
  },

  /**
   * Creates a recurring pattern for an event.
   */
  async createRecurringPattern(
    viewId,
    patternData,
    cancelToken = null,
    publicAuthToken = null
  ) {
    const config = {
      method: 'POST',
      url: `database/views/calendar/${viewId}/recurring-patterns/`,
      data: patternData,
    }

    if (cancelToken !== null) {
      config.cancelToken = cancelToken
    }

    if (publicAuthToken !== null) {
      config.headers = {
        Authorization: `JWT ${publicAuthToken}`,
      }
    }

    const { data } = await this.client.request(config)
    return data
  },

  /**
   * Updates a recurring pattern.
   */
  async updateRecurringPattern(
    viewId,
    patternId,
    patternData,
    cancelToken = null,
    publicAuthToken = null
  ) {
    const config = {
      method: 'PATCH',
      url: `database/views/calendar/${viewId}/recurring-patterns/${patternId}/`,
      data: patternData,
    }

    if (cancelToken !== null) {
      config.cancelToken = cancelToken
    }

    if (publicAuthToken !== null) {
      config.headers = {
        Authorization: `JWT ${publicAuthToken}`,
      }
    }

    const { data } = await this.client.request(config)
    return data
  },

  /**
   * Deletes a recurring pattern.
   */
  async deleteRecurringPattern(
    viewId,
    patternId,
    cancelToken = null,
    publicAuthToken = null
  ) {
    const config = {
      method: 'DELETE',
      url: `database/views/calendar/${viewId}/recurring-patterns/${patternId}/`,
    }

    if (cancelToken !== null) {
      config.cancelToken = cancelToken
    }

    if (publicAuthToken !== null) {
      config.headers = {
        Authorization: `JWT ${publicAuthToken}`,
      }
    }

    await this.client.request(config)
  },

  /**
   * Fetches external sync configurations for a calendar view.
   */
  async getExternalSyncs(
    viewId,
    cancelToken = null,
    publicAuthToken = null
  ) {
    const config = {
      method: 'GET',
      url: `database/views/calendar/${viewId}/external-sync/`,
    }

    if (cancelToken !== null) {
      config.cancelToken = cancelToken
    }

    if (publicAuthToken !== null) {
      config.headers = {
        Authorization: `JWT ${publicAuthToken}`,
      }
    }

    const { data } = await this.client.request(config)
    return data
  },

  /**
   * Creates an external sync configuration.
   */
  async createExternalSync(
    viewId,
    syncData,
    cancelToken = null,
    publicAuthToken = null
  ) {
    const config = {
      method: 'POST',
      url: `database/views/calendar/${viewId}/external-sync/`,
      data: syncData,
    }

    if (cancelToken !== null) {
      config.cancelToken = cancelToken
    }

    if (publicAuthToken !== null) {
      config.headers = {
        Authorization: `JWT ${publicAuthToken}`,
      }
    }

    const { data } = await this.client.request(config)
    return data
  },

  /**
   * Updates an external sync configuration.
   */
  async updateExternalSync(
    viewId,
    syncId,
    syncData,
    cancelToken = null,
    publicAuthToken = null
  ) {
    const config = {
      method: 'PATCH',
      url: `database/views/calendar/${viewId}/external-sync/${syncId}/`,
      data: syncData,
    }

    if (cancelToken !== null) {
      config.cancelToken = cancelToken
    }

    if (publicAuthToken !== null) {
      config.headers = {
        Authorization: `JWT ${publicAuthToken}`,
      }
    }

    const { data } = await this.client.request(config)
    return data
  },

  /**
   * Deletes an external sync configuration.
   */
  async deleteExternalSync(
    viewId,
    syncId,
    cancelToken = null,
    publicAuthToken = null
  ) {
    const config = {
      method: 'DELETE',
      url: `database/views/calendar/${viewId}/external-sync/${syncId}/`,
    }

    if (cancelToken !== null) {
      config.cancelToken = cancelToken
    }

    if (publicAuthToken !== null) {
      config.headers = {
        Authorization: `JWT ${publicAuthToken}`,
      }
    }

    await this.client.request(config)
  },

  /**
   * Triggers synchronization with an external calendar.
   */
  async triggerExternalSync(
    viewId,
    syncId,
    cancelToken = null,
    publicAuthToken = null
  ) {
    const config = {
      method: 'POST',
      url: `database/views/calendar/${viewId}/external-sync/${syncId}/sync/`,
    }

    if (cancelToken !== null) {
      config.cancelToken = cancelToken
    }

    if (publicAuthToken !== null) {
      config.headers = {
        Authorization: `JWT ${publicAuthToken}`,
      }
    }

    const { data } = await this.client.request(config)
    return data
  },

  /**
   * Gets calendar view configuration.
   */
  async getCalendarView(
    viewId,
    cancelToken = null,
    publicAuthToken = null
  ) {
    const config = {
      method: 'GET',
      url: `database/views/calendar/${viewId}/`,
    }

    if (cancelToken !== null) {
      config.cancelToken = cancelToken
    }

    if (publicAuthToken !== null) {
      config.headers = {
        Authorization: `JWT ${publicAuthToken}`,
      }
    }

    const { data } = await this.client.request(config)
    return data
  },

  /**
   * Updates calendar view configuration.
   */
  async updateCalendarView(
    viewId,
    values,
    cancelToken = null,
    publicAuthToken = null
  ) {
    const config = {
      method: 'PATCH',
      url: `database/views/calendar/${viewId}/`,
      data: values,
    }

    if (cancelToken !== null) {
      config.cancelToken = cancelToken
    }

    if (publicAuthToken !== null) {
      config.headers = {
        Authorization: `JWT ${publicAuthToken}`,
      }
    }

    const { data } = await this.client.request(config)
    return data
  },
}