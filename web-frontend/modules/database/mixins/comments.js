/**
 * Mixin for adding comment functionality to components
 */
export default {
  data() {
    return {
      commentsVisible: false,
      selectedRowId: null,
    }
  },
  
  computed: {
    commentsService() {
      return this.$services.comments
    },
  },
  
  methods: {
    /**
     * Show comments for a specific row
     */
    showComments(rowId) {
      this.selectedRowId = rowId
      this.commentsVisible = true
      
      // Load comments if not already loaded
      this.loadRowComments(rowId)
    },
    
    /**
     * Hide comments panel
     */
    hideComments() {
      this.commentsVisible = false
      this.selectedRowId = null
    },
    
    /**
     * Toggle comments visibility for a row
     */
    toggleComments(rowId) {
      if (this.commentsVisible && this.selectedRowId === rowId) {
        this.hideComments()
      } else {
        this.showComments(rowId)
      }
    },
    
    /**
     * Load comments for a specific row
     */
    async loadRowComments(rowId, options = {}) {
      if (!this.table?.id) return
      
      try {
        await this.$store.dispatch('database/collaboration/loadComments', {
          tableId: this.table.id,
          rowId,
          includeResolved: options.includeResolved !== false,
          userId: options.userId,
        })
      } catch (error) {
        console.error('Failed to load comments:', error)
        this.$toast.error('Failed to load comments')
      }
    },
    
    /**
     * Create a new comment
     */
    async createComment(rowId, content, parentId = null) {
      if (!this.table?.id) return
      
      try {
        await this.$store.dispatch('database/collaboration/createComment', {
          tableId: this.table.id,
          rowId,
          content,
          parentId,
        })
        
        this.$toast.success('Comment added successfully')
      } catch (error) {
        console.error('Failed to create comment:', error)
        this.$toast.error('Failed to add comment')
        throw error
      }
    },
    
    /**
     * Update an existing comment
     */
    async updateComment(commentId, content) {
      try {
        await this.$store.dispatch('database/collaboration/updateComment', {
          commentId,
          content,
        })
        
        this.$toast.success('Comment updated successfully')
      } catch (error) {
        console.error('Failed to update comment:', error)
        this.$toast.error('Failed to update comment')
        throw error
      }
    },
    
    /**
     * Delete a comment
     */
    async deleteComment(commentId) {
      try {
        await this.$store.dispatch('database/collaboration/deleteComment', {
          commentId,
        })
        
        this.$toast.success('Comment deleted successfully')
      } catch (error) {
        console.error('Failed to delete comment:', error)
        this.$toast.error('Failed to delete comment')
        throw error
      }
    },
    
    /**
     * Toggle comment resolution status
     */
    async toggleCommentResolution(commentId) {
      try {
        await this.$store.dispatch('database/collaboration/toggleCommentResolution', {
          commentId,
        })
      } catch (error) {
        console.error('Failed to toggle comment resolution:', error)
        this.$toast.error('Failed to update comment status')
        throw error
      }
    },
    
    /**
     * Get comments for a specific row
     */
    getRowComments(rowId) {
      if (!this.table?.id) return []
      
      return this.$store.getters['database/collaboration/commentsForRow'](
        this.table.id,
        rowId
      )
    },
    
    /**
     * Get comment count for a row
     */
    getRowCommentCount(rowId) {
      const comments = this.getRowComments(rowId)
      return comments.length
    },
    
    /**
     * Check if a row has unresolved comments
     */
    hasUnresolvedComments(rowId) {
      const comments = this.getRowComments(rowId)
      return comments.some(comment => !comment.is_resolved)
    },
    
    /**
     * Get unresolved comment count for a row
     */
    getUnresolvedCommentCount(rowId) {
      const comments = this.getRowComments(rowId)
      return comments.filter(comment => !comment.is_resolved).length
    },
    
    /**
     * Format comment content for display
     */
    formatCommentContent(content) {
      // Basic formatting - convert line breaks and mentions
      let formatted = content.replace(/\n/g, '<br>')
      
      // Convert @mentions to readable format
      formatted = formatted.replace(/@(\d+)/g, (match, userId) => {
        // Try to get user name from active users or mentions
        const activeUsers = this.$store.getters['database/collaboration/activeUsersForContext'](
          this.table?.id,
          this.view?.id
        )
        const user = activeUsers.find(u => u.user_id === parseInt(userId))
        
        if (user) {
          return `@${user.user_name}`
        }
        
        return match
      })
      
      return formatted
    },
    
    /**
     * Check if current user can comment on the table
     */
    canComment() {
      // Check if user has permission to comment
      // This would depend on the table permissions
      return this.table && this.$hasPermission('database.table.create_comment', this.table)
    },
    
    /**
     * Check if current user can edit a specific comment
     */
    canEditComment(comment) {
      return comment.user === this.$auth.user.id
    },
    
    /**
     * Check if current user can delete a specific comment
     */
    canDeleteComment(comment) {
      return comment.user === this.$auth.user.id || 
             this.$hasPermission('database.table.delete_comment', this.table)
    },
    
    /**
     * Check if current user can resolve comments
     */
    canResolveComments() {
      return this.$hasPermission('database.table.resolve_comment', this.table)
    },
  },
}