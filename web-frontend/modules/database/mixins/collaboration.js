/**
 * Mixin for adding real-time collaboration features to table views
 */
export default {
  data() {
    return {
      collaborationInitialized: false,
      cursorUpdateThrottle: null,
      typingTimeout: null,
      isTyping: false,
    }
  },
  
  computed: {
    collaborationEnabled() {
      return this.$store.getters['database/collaboration/isConnected']
    },
  },
  
  async mounted() {
    if (this.table && this.table.id) {
      await this.initializeCollaboration()
    }
  },
  
  beforeDestroy() {
    this.cleanupCollaboration()
  },
  
  methods: {
    /**
     * Initialize collaboration for the current table/view
     */
    async initializeCollaboration() {
      if (this.collaborationInitialized) return
      
      try {
        await this.$store.dispatch('database/collaboration/initializeCollaboration', {
          tableId: this.table.id,
          viewId: this.view?.id,
        })
        
        this.collaborationInitialized = true
        this.setupCollaborationEventListeners()
      } catch (error) {
        console.error('Failed to initialize collaboration:', error)
      }
    },
    
    /**
     * Clean up collaboration when component is destroyed
     */
    async cleanupCollaboration() {
      if (!this.collaborationInitialized) return
      
      try {
        await this.$store.dispatch('database/collaboration/disconnectCollaboration')
        this.collaborationInitialized = false
        this.cleanupEventListeners()
      } catch (error) {
        console.error('Failed to cleanup collaboration:', error)
      }
    },
    
    /**
     * Set up event listeners for collaboration features
     */
    setupCollaborationEventListeners() {
      // Track mouse movement for live cursors
      document.addEventListener('mousemove', this.handleMouseMove)
      
      // Track focus events for presence
      window.addEventListener('focus', this.handleWindowFocus)
      window.addEventListener('blur', this.handleWindowBlur)
    },
    
    /**
     * Clean up event listeners
     */
    cleanupEventListeners() {
      document.removeEventListener('mousemove', this.handleMouseMove)
      window.removeEventListener('focus', this.handleWindowFocus)
      window.removeEventListener('blur', this.handleWindowBlur)
      
      if (this.cursorUpdateThrottle) {
        clearTimeout(this.cursorUpdateThrottle)
      }
      
      if (this.typingTimeout) {
        clearTimeout(this.typingTimeout)
      }
    },
    
    /**
     * Handle mouse movement for live cursors
     */
    handleMouseMove(event) {
      if (!this.collaborationEnabled) return
      
      // Throttle cursor updates to avoid overwhelming the server
      if (this.cursorUpdateThrottle) {
        clearTimeout(this.cursorUpdateThrottle)
      }
      
      this.cursorUpdateThrottle = setTimeout(() => {
        this.$store.dispatch('database/collaboration/updateCursor', {
          cursorPosition: {
            x: event.clientX,
            y: event.clientY,
          },
        })
      }, 100) // Update every 100ms
    },
    
    /**
     * Handle window focus for presence updates
     */
    handleWindowFocus() {
      if (this.collaborationEnabled) {
        this.$store.dispatch('database/collaboration/updatePresence', {
          cursorPosition: { active: true },
        })
      }
    },
    
    /**
     * Handle window blur for presence updates
     */
    handleWindowBlur() {
      if (this.collaborationEnabled) {
        this.$store.dispatch('database/collaboration/updatePresence', {
          cursorPosition: { active: false },
        })
      }
    },
    
    /**
     * Start typing indicator for a specific field
     */
    async startTypingIndicator(fieldId, rowId) {
      if (!this.collaborationEnabled || this.isTyping) return
      
      this.isTyping = true
      
      try {
        await this.$store.dispatch('database/collaboration/startTyping', {
          fieldId,
          rowId,
        })
      } catch (error) {
        console.error('Failed to start typing indicator:', error)
      }
    },
    
    /**
     * Stop typing indicator
     */
    async stopTypingIndicator() {
      if (!this.collaborationEnabled || !this.isTyping) return
      
      this.isTyping = false
      
      // Clear any existing timeout
      if (this.typingTimeout) {
        clearTimeout(this.typingTimeout)
      }
      
      try {
        await this.$store.dispatch('database/collaboration/stopTyping')
      } catch (error) {
        console.error('Failed to stop typing indicator:', error)
      }
    },
    
    /**
     * Handle typing in a field with automatic timeout
     */
    handleFieldTyping(fieldId, rowId) {
      // Start typing indicator if not already active
      if (!this.isTyping) {
        this.startTypingIndicator(fieldId, rowId)
      }
      
      // Reset the timeout
      if (this.typingTimeout) {
        clearTimeout(this.typingTimeout)
      }
      
      // Stop typing after 3 seconds of inactivity
      this.typingTimeout = setTimeout(() => {
        this.stopTypingIndicator()
      }, 3000)
    },
    
    /**
     * Acquire edit lock for a field
     */
    async acquireEditLock(rowId, fieldId, lockData = {}) {
      if (!this.collaborationEnabled) return true
      
      try {
        const acquired = await this.$store.dispatch('database/collaboration/acquireEditLock', {
          rowId,
          fieldId,
          lockData,
        })
        
        if (!acquired) {
          this.$toast.error('This field is currently being edited by another user')
        }
        
        return acquired
      } catch (error) {
        console.error('Failed to acquire edit lock:', error)
        return false
      }
    },
    
    /**
     * Release edit lock for a field
     */
    async releaseEditLock(rowId, fieldId) {
      if (!this.collaborationEnabled) return
      
      try {
        await this.$store.dispatch('database/collaboration/releaseEditLock', {
          rowId,
          fieldId,
        })
      } catch (error) {
        console.error('Failed to release edit lock:', error)
      }
    },
    
    /**
     * Check if a field is locked by another user
     */
    isFieldLocked(rowId, fieldId) {
      if (!this.collaborationEnabled) return false
      
      return this.$store.getters['database/collaboration/isFieldLocked'](
        this.table.id,
        rowId,
        fieldId
      ) && !this.$store.getters['database/collaboration/hasEditLock'](
        this.table.id,
        rowId,
        fieldId
      )
    },
    
    /**
     * Create a comment on a row
     */
    async createComment(rowId, content, parentId = null) {
      if (!this.collaborationEnabled) return
      
      try {
        await this.$store.dispatch('database/collaboration/createComment', {
          rowId,
          content,
          parentId,
        })
      } catch (error) {
        console.error('Failed to create comment:', error)
        throw error
      }
    },
    
    /**
     * Get comments for a row
     */
    getRowComments(rowId) {
      return this.$store.getters['database/collaboration/commentsForRow'](
        this.table.id,
        rowId
      )
    },
    
    /**
     * Get active users for current context
     */
    getActiveUsers() {
      return this.$store.getters['database/collaboration/activeUsersForContext'](
        this.table.id,
        this.view?.id
      )
    },
  },
}