export const state = () => ({
  // User presence tracking
  activeUsers: {},
  userPresence: {},
  
  // Real-time collaboration state
  isConnected: false,
  webSocketId: null,
  currentTableId: null,
  currentViewId: null,
  
  // Live cursors and typing indicators
  liveCursors: {},
  typingIndicators: {},
  
  // Edit locks for conflict resolution
  editLocks: {},
  myEditLocks: {},
  
  // Comments system
  comments: {},
  commentThreads: {},
  
  // Activity log
  activityLog: [],
  
  // Connection management
  reconnectAttempts: 0,
  maxReconnectAttempts: 5,
  reconnectDelay: 1000,
})
expor
t const mutations = {
  SET_CONNECTION_STATE(state, { isConnected, webSocketId }) {
    state.isConnected = isConnected
    state.webSocketId = webSocketId
    if (!isConnected) {
      state.reconnectAttempts = 0
    }
  },

  SET_CURRENT_CONTEXT(state, { tableId, viewId }) {
    state.currentTableId = tableId
    state.currentViewId = viewId
  },

  SET_ACTIVE_USERS(state, { tableId, viewId, users }) {
    const key = viewId ? `view-${viewId}` : `table-${tableId}`
    state.activeUsers[key] = users
  },

  UPDATE_USER_PRESENCE(state, { userId, presence }) {
    state.userPresence[userId] = {
      ...state.userPresence[userId],
      ...presence,
      lastSeen: new Date().toISOString(),
    }
  },

  REMOVE_USER_PRESENCE(state, { userId }) {
    delete state.userPresence[userId]
  },

  SET_LIVE_CURSOR(state, { userId, cursorPosition }) {
    if (cursorPosition) {
      state.liveCursors[userId] = {
        ...cursorPosition,
        timestamp: Date.now(),
      }
    } else {
      delete state.liveCursors[userId]
    }
  },

  SET_TYPING_INDICATOR(state, { userId, fieldId, rowId, isTyping }) {
    const key = `${userId}-${fieldId}-${rowId}`
    if (isTyping) {
      state.typingIndicators[key] = {
        userId,
        fieldId,
        rowId,
        timestamp: Date.now(),
      }
    } else {
      delete state.typingIndicators[key]
    }
  },

  SET_EDIT_LOCK(state, { tableId, rowId, fieldId, userId, status, sessionId }) {
    const lockKey = `${tableId}-${rowId}-${fieldId}`
    if (status === 'acquired') {
      state.editLocks[lockKey] = {
        userId,
        sessionId,
        timestamp: Date.now(),
      }
      if (userId === state.currentUserId) {
        state.myEditLocks[lockKey] = sessionId
      }
    } else if (status === 'released') {
      delete state.editLocks[lockKey]
      delete state.myEditLocks[lockKey]
    }
  },

  ADD_COMMENT(state, { tableId, rowId, comment }) {
    const key = `${tableId}-${rowId}`
    if (!state.comments[key]) {
      state.comments[key] = []
    }
    state.comments[key].push(comment)
    
    // Update comment threads
    if (comment.parent) {
      if (!state.commentThreads[comment.parent]) {
        state.commentThreads[comment.parent] = []
      }
      state.commentThreads[comment.parent].push(comment)
    }
  },

  SET_COMMENTS(state, { tableId, rowId, comments }) {
    const key = `${tableId}-${rowId}`
    state.comments[key] = comments
    
    // Build comment threads
    comments.forEach(comment => {
      if (comment.parent) {
        if (!state.commentThreads[comment.parent]) {
          state.commentThreads[comment.parent] = []
        }
        state.commentThreads[comment.parent].push(comment)
      }
    })
  },

  UPDATE_COMMENT(state, { commentId, comment }) {
    // Find and update comment in all comment arrays
    Object.keys(state.comments).forEach(key => {
      const comments = state.comments[key]
      const index = comments.findIndex(c => c.id === commentId)
      if (index !== -1) {
        comments.splice(index, 1, comment)
      }
      
      // Also check replies
      comments.forEach(c => {
        if (c.replies) {
          const replyIndex = c.replies.findIndex(r => r.id === commentId)
          if (replyIndex !== -1) {
            c.replies.splice(replyIndex, 1, comment)
          }
        }
      })
    })
  },

  REMOVE_COMMENT(state, { commentId }) {
    // Remove comment from all comment arrays
    Object.keys(state.comments).forEach(key => {
      const comments = state.comments[key]
      const index = comments.findIndex(c => c.id === commentId)
      if (index !== -1) {
        comments.splice(index, 1)
      }
      
      // Also check replies
      comments.forEach(c => {
        if (c.replies) {
          const replyIndex = c.replies.findIndex(r => r.id === commentId)
          if (replyIndex !== -1) {
            c.replies.splice(replyIndex, 1)
          }
        }
      })
    })
    
    // Remove from comment threads
    delete state.commentThreads[commentId]
  },

  ADD_ACTIVITY_LOG_ENTRY(state, entry) {
    state.activityLog.unshift(entry)
    // Keep only last 100 entries
    if (state.activityLog.length > 100) {
      state.activityLog = state.activityLog.slice(0, 100)
    }
  },

  SET_ACTIVITY_LOG(state, entries) {
    state.activityLog = entries
  },

  CLEAR_ACTIVITY_LOG(state) {
    state.activityLog = []
  },

  SET_RECONNECT_ATTEMPTS(state, attempts) {
    state.reconnectAttempts = attempts
  },

  CLEAR_COLLABORATION_STATE(state) {
    state.activeUsers = {}
    state.userPresence = {}
    state.liveCursors = {}
    state.typingIndicators = {}
    state.editLocks = {}
    state.myEditLocks = {}
    state.comments = {}
    state.commentThreads = {}
    state.activityLog = []
  },
}

export const actions = {
  /**
   * Initialize collaboration connection for a table/view
   */
  async initializeCollaboration({ commit, dispatch }, { tableId, viewId }) {
    commit('SET_CURRENT_CONTEXT', { tableId, viewId })
    
    // Connect to WebSocket if not already connected
    if (!this.$ws.isConnected()) {
      await this.$ws.connect()
    }
    
    // Subscribe to collaboration page
    const pageType = viewId ? 'collaboration_view' : 'collaboration_table'
    const pageParams = viewId 
      ? { table_id: tableId, view_id: viewId }
      : { table_id: tableId }
    
    await this.$ws.subscribePage(pageType, pageParams)
    
    // Request current active users
    await dispatch('requestActiveUsers', { tableId, viewId })
  },

  /**
   * Disconnect from collaboration
   */
  async disconnectCollaboration({ commit, state }) {
    if (state.currentTableId) {
      const pageType = state.currentViewId ? 'collaboration_view' : 'collaboration_table'
      const pageParams = state.currentViewId 
        ? { table_id: state.currentTableId, view_id: state.currentViewId }
        : { table_id: state.currentTableId }
      
      await this.$ws.unsubscribePage(pageType, pageParams)
    }
    
    commit('CLEAR_COLLABORATION_STATE')
    commit('SET_CURRENT_CONTEXT', { tableId: null, viewId: null })
  },

  /**
   * Update user presence information
   */
  async updatePresence({ state }, { cursorPosition }) {
    if (!state.isConnected || !state.currentTableId) return
    
    await this.$ws.send({
      type: 'update_presence',
      table_id: state.currentTableId,
      view_id: state.currentViewId,
      cursor_position: cursorPosition,
    })
  },

  /**
   * Start typing indicator
   */
  async startTyping({ state }, { fieldId, rowId }) {
    if (!state.isConnected || !state.currentTableId) return
    
    await this.$ws.send({
      type: 'start_typing',
      table_id: state.currentTableId,
      field_id: fieldId,
      row_id: rowId,
    })
  },

  /**
   * Stop typing indicator
   */
  async stopTyping({ state }) {
    if (!state.isConnected || !state.currentTableId) return
    
    await this.$ws.send({
      type: 'stop_typing',
      table_id: state.currentTableId,
    })
  },

  /**
   * Update cursor position
   */
  async updateCursor({ state }, { cursorPosition }) {
    if (!state.isConnected || !state.currentTableId) return
    
    await this.$ws.send({
      type: 'cursor_move',
      table_id: state.currentTableId,
      cursor_position: cursorPosition,
    })
  },

  /**
   * Acquire edit lock for conflict resolution
   */
  async acquireEditLock({ state }, { rowId, fieldId, lockData }) {
    if (!state.isConnected || !state.currentTableId) return false
    
    return new Promise((resolve) => {
      const handleResponse = (message) => {
        if (message.type === 'lock_acquired' && 
            message.row_id === rowId && 
            message.field_id === fieldId) {
          this.$ws.off('message', handleResponse)
          resolve(true)
        } else if (message.type === 'lock_failed' && 
                   message.row_id === rowId && 
                   message.field_id === fieldId) {
          this.$ws.off('message', handleResponse)
          resolve(false)
        }
      }
      
      this.$ws.on('message', handleResponse)
      
      this.$ws.send({
        type: 'acquire_lock',
        table_id: state.currentTableId,
        row_id: rowId,
        field_id: fieldId,
        lock_data: lockData,
      })
      
      // Timeout after 5 seconds
      setTimeout(() => {
        this.$ws.off('message', handleResponse)
        resolve(false)
      }, 5000)
    })
  },

  /**
   * Release edit lock
   */
  async releaseEditLock({ state }, { rowId, fieldId }) {
    if (!state.isConnected || !state.currentTableId) return
    
    await this.$ws.send({
      type: 'release_lock',
      table_id: state.currentTableId,
      row_id: rowId,
      field_id: fieldId,
    })
  },

  /**
   * Load comments for a row
   */
  async loadComments({ commit }, { tableId, rowId, includeResolved = true, userId = null }) {
    try {
      const params = new URLSearchParams()
      if (!includeResolved) {
        params.append('include_resolved', 'false')
      }
      if (userId) {
        params.append('user_id', userId)
      }
      
      const response = await this.$axios.get(
        `/api/database/collaboration/tables/${tableId}/rows/${rowId}/comments/?${params}`
      )
      
      commit('SET_COMMENTS', {
        tableId,
        rowId,
        comments: response.data.results || response.data,
      })
      
      return response.data
    } catch (error) {
      console.error('Failed to load comments:', error)
      throw error
    }
  },

  /**
   * Create a comment
   */
  async createComment({ commit, state }, { tableId, rowId, content, parentId }) {
    try {
      const response = await this.$axios.post(
        `/api/database/collaboration/tables/${tableId}/rows/${rowId}/comments/`,
        {
          content,
          parent: parentId,
        }
      )
      
      commit('ADD_COMMENT', {
        tableId,
        rowId,
        comment: response.data,
      })
      
      // Also send via WebSocket for real-time updates
      if (state.isConnected) {
        await this.$ws.send({
          type: 'comment_created',
          table_id: tableId,
          row_id: rowId,
          comment: response.data,
        })
      }
      
      return response.data
    } catch (error) {
      console.error('Failed to create comment:', error)
      throw error
    }
  },

  /**
   * Update a comment
   */
  async updateComment({ commit, state }, { commentId, content }) {
    try {
      const response = await this.$axios.patch(
        `/api/database/collaboration/comments/${commentId}/`,
        { content }
      )
      
      commit('UPDATE_COMMENT', {
        commentId,
        comment: response.data,
      })
      
      // Send via WebSocket for real-time updates
      if (state.isConnected) {
        await this.$ws.send({
          type: 'comment_updated',
          comment_id: commentId,
          comment: response.data,
        })
      }
      
      return response.data
    } catch (error) {
      console.error('Failed to update comment:', error)
      throw error
    }
  },

  /**
   * Delete a comment
   */
  async deleteComment({ commit, state }, { commentId }) {
    try {
      await this.$axios.delete(`/api/database/collaboration/comments/${commentId}/`)
      
      commit('REMOVE_COMMENT', { commentId })
      
      // Send via WebSocket for real-time updates
      if (state.isConnected) {
        await this.$ws.send({
          type: 'comment_deleted',
          comment_id: commentId,
        })
      }
    } catch (error) {
      console.error('Failed to delete comment:', error)
      throw error
    }
  },

  /**
   * Toggle comment resolution
   */
  async toggleCommentResolution({ commit, state }, { commentId }) {
    try {
      const response = await this.$axios.post(
        `/api/database/collaboration/comments/${commentId}/toggle-resolution/`
      )
      
      commit('UPDATE_COMMENT', {
        commentId,
        comment: response.data,
      })
      
      // Send via WebSocket for real-time updates
      if (state.isConnected) {
        await this.$ws.send({
          type: 'comment_resolved',
          comment_id: commentId,
          comment: response.data,
        })
      }
      
      return response.data
    } catch (error) {
      console.error('Failed to toggle comment resolution:', error)
      throw error
    }
  },

  /**
   * Request active users list
   */
  async requestActiveUsers({ state }, { tableId, viewId }) {
    if (!state.isConnected) return
    
    await this.$ws.send({
      type: 'get_active_users',
      table_id: tableId || state.currentTableId,
      view_id: viewId || state.currentViewId,
    })
  },

  /**
   * Handle WebSocket messages
   */
  handleWebSocketMessage({ commit, state }, message) {
    switch (message.type) {
      case 'collaboration_connected':
        commit('SET_CONNECTION_STATE', {
          isConnected: true,
          webSocketId: message.web_socket_id,
        })
        break

      case 'active_users':
        commit('SET_ACTIVE_USERS', {
          tableId: message.table_id,
          viewId: message.view_id,
          users: message.users,
        })
        break

      case 'presence_updated':
        commit('UPDATE_USER_PRESENCE', {
          userId: message.user_id,
          presence: {
            userName: message.user_name,
            cursorPosition: message.cursor_position,
            isTyping: message.is_typing,
            lastSeen: message.last_seen,
          },
        })
        break

      case 'typing_indicator':
        commit('SET_TYPING_INDICATOR', {
          userId: message.user_id,
          fieldId: message.field_id,
          rowId: message.row_id,
          isTyping: message.is_typing,
        })
        break

      case 'cursor_updated':
        commit('SET_LIVE_CURSOR', {
          userId: message.user_id,
          cursorPosition: message.cursor_position,
        })
        break

      case 'lock_status_changed':
        commit('SET_EDIT_LOCK', {
          tableId: state.currentTableId,
          rowId: message.row_id,
          fieldId: message.field_id,
          userId: message.user_id,
          status: message.status,
          sessionId: message.session_id,
        })
        break

      case 'comment_created':
        commit('ADD_COMMENT', {
          tableId: state.currentTableId,
          rowId: message.row_id,
          comment: message.comment,
        })
        break

      case 'comment_updated':
        commit('UPDATE_COMMENT', {
          commentId: message.comment_id,
          comment: message.comment,
        })
        break

      case 'comment_deleted':
        commit('REMOVE_COMMENT', {
          commentId: message.comment_id,
        })
        break

      case 'comment_resolved':
        commit('UPDATE_COMMENT', {
          commentId: message.comment_id,
          comment: message.comment,
        })
        break

      case 'activity_logged':
        commit('ADD_ACTIVITY_LOG_ENTRY', message.activity)
        break
    }
  },

  /**
   * Handle WebSocket connection events
   */
  handleWebSocketConnect({ commit }) {
    commit('SET_CONNECTION_STATE', { isConnected: true, webSocketId: null })
    commit('SET_RECONNECT_ATTEMPTS', 0)
  },

  /**
   * Handle WebSocket disconnection
   */
  handleWebSocketDisconnect({ commit, dispatch, state }) {
    commit('SET_CONNECTION_STATE', { isConnected: false, webSocketId: null })
    
    // Attempt to reconnect if we were previously connected
    if (state.currentTableId && state.reconnectAttempts < state.maxReconnectAttempts) {
      setTimeout(() => {
        commit('SET_RECONNECT_ATTEMPTS', state.reconnectAttempts + 1)
        dispatch('initializeCollaboration', {
          tableId: state.currentTableId,
          viewId: state.currentViewId,
        })
      }, state.reconnectDelay * Math.pow(2, state.reconnectAttempts))
    }
  },

  /**
   * Load activity log for a table
   */
  async loadActivityLog({ commit }, { tableId, params = {} }) {
    try {
      const CommentsService = this.$registry.get('service', 'comments')
      const response = await CommentsService(this.$client).getActivityLog(tableId, params)
      
      if (params.page === 1 || !params.page) {
        // Reset activity log for first page
        commit('SET_ACTIVITY_LOG', response.data.results)
      } else {
        // Append for pagination
        response.data.results.forEach(entry => {
          commit('ADD_ACTIVITY_LOG_ENTRY', entry)
        })
      }
      
      return response.data
    } catch (error) {
      console.error('Failed to load activity log:', error)
      throw error
    }
  },

  /**
   * Clear activity log
   */
  clearActivityLog({ commit }) {
    commit('CLEAR_ACTIVITY_LOG')
  },
}

export const getters = {
  isConnected: (state) => state.isConnected,
  
  activeUsersForContext: (state) => (tableId, viewId) => {
    const key = viewId ? `view-${viewId}` : `table-${tableId}`
    return state.activeUsers[key] || []
  },
  
  userPresence: (state) => (userId) => state.userPresence[userId],
  
  liveCursors: (state) => state.liveCursors,
  
  typingIndicatorsForField: (state) => (fieldId, rowId) => {
    return Object.values(state.typingIndicators).filter(
      indicator => indicator.fieldId === fieldId && indicator.rowId === rowId
    )
  },
  
  isFieldLocked: (state) => (tableId, rowId, fieldId) => {
    const lockKey = `${tableId}-${rowId}-${fieldId}`
    return !!state.editLocks[lockKey]
  },
  
  fieldLockOwner: (state) => (tableId, rowId, fieldId) => {
    const lockKey = `${tableId}-${rowId}-${fieldId}`
    return state.editLocks[lockKey]?.userId
  },
  
  hasEditLock: (state) => (tableId, rowId, fieldId) => {
    const lockKey = `${tableId}-${rowId}-${fieldId}`
    return !!state.myEditLocks[lockKey]
  },
  
  commentsForRow: (state) => (tableId, rowId) => {
    const key = `${tableId}-${rowId}`
    return state.comments[key] || []
  },
  
  commentThreads: (state) => (parentId) => {
    return state.commentThreads[parentId] || []
  },
  
  activityLog: (state) => state.activityLog,
  
  connectionStatus: (state) => ({
    isConnected: state.isConnected,
    reconnectAttempts: state.reconnectAttempts,
    maxReconnectAttempts: state.maxReconnectAttempts,
  }),
}