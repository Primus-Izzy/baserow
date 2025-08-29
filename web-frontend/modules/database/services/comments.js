export default (client) => {
  return {
    /**
     * Get comments for a specific row
     */
    getComments(tableId, rowId, params = {}) {
      const queryParams = new URLSearchParams()
      
      if (params.includeResolved !== undefined) {
        queryParams.append('include_resolved', params.includeResolved)
      }
      if (params.userId) {
        queryParams.append('user_id', params.userId)
      }
      if (params.page) {
        queryParams.append('page', params.page)
      }
      if (params.pageSize) {
        queryParams.append('page_size', params.pageSize)
      }
      
      const url = `/database/collaboration/tables/${tableId}/rows/${rowId}/comments/`
      return client.get(queryParams.toString() ? `${url}?${queryParams}` : url)
    },

    /**
     * Create a new comment
     */
    createComment(tableId, rowId, data) {
      return client.post(
        `/database/collaboration/tables/${tableId}/rows/${rowId}/comments/`,
        data
      )
    },

    /**
     * Update an existing comment
     */
    updateComment(commentId, data) {
      return client.patch(`/database/collaboration/comments/${commentId}/`, data)
    },

    /**
     * Delete a comment
     */
    deleteComment(commentId) {
      return client.delete(`/database/collaboration/comments/${commentId}/`)
    },

    /**
     * Toggle comment resolution status
     */
    toggleCommentResolution(commentId) {
      return client.post(`/database/collaboration/comments/${commentId}/toggle-resolution/`)
    },

    /**
     * Get active users for mentions
     */
    getActiveUsers(tableId, viewId = null) {
      const params = new URLSearchParams()
      if (viewId) {
        params.append('view_id', viewId)
      }
      
      const url = `/database/collaboration/tables/${tableId}/active-users/`
      return client.get(params.toString() ? `${url}?${params}` : url)
    },

    /**
     * Get activity log for a table
     */
    getActivityLog(tableId, params = {}) {
      const queryParams = new URLSearchParams()
      
      if (params.userId) {
        queryParams.append('user_id', params.userId)
      }
      if (params.actionTypes) {
        queryParams.append('action_types', params.actionTypes.join(','))
      }
      if (params.page) {
        queryParams.append('page', params.page)
      }
      if (params.pageSize) {
        queryParams.append('page_size', params.pageSize)
      }
      
      const url = `/database/collaboration/tables/${tableId}/activity-log/`
      return client.get(queryParams.toString() ? `${url}?${queryParams}` : url)
    },

    /**
     * Get collaboration statistics
     */
    getCollaborationStats(tableId) {
      return client.get(`/database/collaboration/tables/${tableId}/collaboration-stats/`)
    },
  }
}