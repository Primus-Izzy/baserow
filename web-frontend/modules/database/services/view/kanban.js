import ViewService from '@baserow/modules/database/services/view'

export default {
  ...ViewService,
  
  /**
   * Fetches the rows for a Kanban view.
   */
  fetchRows(
    viewId,
    limit = 100,
    offset = null,
    cancelToken = null,
    search = null,
    searchMode = null,
    publicAuthToken = null,
    orderBy = null,
    filters = null,
    includeFieldOptions = false,
    userFieldNames = false
  ) {
    const config = {
      params: {
        limit,
        user_field_names: userFieldNames,
      },
    }

    if (offset !== null) {
      config.params.offset = offset
    }

    if (cancelToken !== null) {
      config.cancelToken = cancelToken
    }

    if (search !== null) {
      config.params.search = search
    }

    if (searchMode !== null) {
      config.params.search_mode = searchMode
    }

    if (orderBy !== null) {
      config.params.order_by = orderBy
    }

    if (filters !== null) {
      config.params.filters = filters
    }

    if (includeFieldOptions) {
      config.params.include_field_options = includeFieldOptions
    }

    if (publicAuthToken !== null) {
      config.headers = { Authorization: `JWT ${publicAuthToken}` }
    }

    return this.$client.get(`/database/views/kanban/${viewId}/`, config)
  },

  /**
   * Creates a new row in a Kanban view.
   */
  createRow(
    viewId,
    values = {},
    userFieldNames = false,
    publicAuthToken = null
  ) {
    const config = {
      params: {
        user_field_names: userFieldNames,
      },
    }

    if (publicAuthToken !== null) {
      config.headers = { Authorization: `JWT ${publicAuthToken}` }
    }

    return this.$client.post(
      `/database/views/kanban/${viewId}/`,
      values,
      config
    )
  },

  /**
   * Updates an existing row in a Kanban view.
   */
  updateRow(
    viewId,
    rowId,
    values = {},
    userFieldNames = false,
    publicAuthToken = null
  ) {
    const config = {
      params: {
        user_field_names: userFieldNames,
      },
    }

    if (publicAuthToken !== null) {
      config.headers = { Authorization: `JWT ${publicAuthToken}` }
    }

    return this.$client.patch(
      `/database/views/kanban/${viewId}/${rowId}/`,
      values,
      config
    )
  },

  /**
   * Moves a row to a different position within the Kanban view.
   */
  moveRow(
    viewId,
    rowId,
    beforeRowId = null,
    publicAuthToken = null
  ) {
    const data = {}
    
    if (beforeRowId !== null) {
      data.before_id = beforeRowId
    }

    const config = {}
    if (publicAuthToken !== null) {
      config.headers = { Authorization: `JWT ${publicAuthToken}` }
    }

    return this.$client.patch(
      `/database/views/kanban/${viewId}/${rowId}/move/`,
      data,
      config
    )
  },
}