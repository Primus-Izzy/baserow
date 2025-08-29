<template>
  <div class="comment-form">
    <div class="comment-form__input-container">
      <div class="comment-form__avatar">
        <div
          class="comment-form__avatar-circle"
          :style="{ backgroundColor: currentUserColor }"
        >
          {{ currentUserInitials }}
        </div>
      </div>
      
      <div class="comment-form__input-wrapper">
        <RichTextEditor
          ref="editor"
          v-model="content"
          :placeholder="placeholder"
          :mentions="availableMentions"
          @mention="handleMention"
          @keydown="handleKeydown"
          @focus="handleFocus"
          @blur="handleBlur"
          class="comment-form__editor"
        />
        
        <div v-if="showMentionSuggestions" class="comment-form__mentions">
          <div
            v-for="(user, index) in filteredMentions"
            :key="user.id"
            class="comment-form__mention-item"
            :class="{ active: selectedMentionIndex === index }"
            @click="selectMention(user)"
          >
            <div
              class="comment-form__mention-avatar"
              :style="{ backgroundColor: getUserColor(user.id) }"
            >
              {{ getUserInitials(user.first_name) }}
            </div>
            <div class="comment-form__mention-info">
              <div class="comment-form__mention-name">{{ user.first_name }}</div>
              <div class="comment-form__mention-email">{{ user.email }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="content.trim() || isEditing" class="comment-form__actions">
      <button
        type="button"
        class="comment-form__btn comment-form__btn--secondary"
        @click="handleCancel"
      >
        Cancel
      </button>
      <button
        type="button"
        class="comment-form__btn comment-form__btn--primary"
        :disabled="!content.trim() || submitting"
        @click="handleSubmit"
      >
        <i v-if="submitting" class="iconoir-refresh spinning"></i>
        {{ isEditing ? 'Update' : 'Comment' }}
      </button>
    </div>
  </div>
</template>

<script>
import RichTextEditor from './RichTextEditor.vue'

export default {
  name: 'CommentForm',
  components: {
    RichTextEditor,
  },
  props: {
    tableId: {
      type: Number,
      required: true,
    },
    rowId: {
      type: Number,
      required: true,
    },
    parentId: {
      type: Number,
      default: null,
    },
    initialContent: {
      type: String,
      default: '',
    },
    placeholder: {
      type: String,
      default: 'Write a comment...',
    },
    isEditing: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      content: this.initialContent,
      submitting: false,
      showMentionSuggestions: false,
      mentionQuery: '',
      selectedMentionIndex: 0,
      mentionStartPos: 0,
    }
  },
  computed: {
    currentUserInitials() {
      const name = this.$auth.user.first_name || this.$auth.user.email
      return name
        .split(' ')
        .map(part => part.charAt(0).toUpperCase())
        .join('')
        .substring(0, 2)
    },
    currentUserColor() {
      return this.getUserColor(this.$auth.user.id)
    },
    availableMentions() {
      // Get active users from the collaboration store
      const activeUsers = this.$store.getters['database/collaboration/activeUsersForContext'](
        this.tableId,
        null
      )
      
      // Filter out current user
      return activeUsers.filter(user => user.user_id !== this.$auth.user.id)
    },
    filteredMentions() {
      if (!this.mentionQuery) {
        return this.availableMentions.slice(0, 5)
      }
      
      const query = this.mentionQuery.toLowerCase()
      return this.availableMentions
        .filter(user => 
          user.user_name.toLowerCase().includes(query) ||
          user.user_email.toLowerCase().includes(query)
        )
        .slice(0, 5)
    },
  },
  watch: {
    initialContent(newValue) {
      this.content = newValue
    },
  },
  methods: {
    getUserInitials(name) {
      if (!name) return '?'
      return name
        .split(' ')
        .map(part => part.charAt(0).toUpperCase())
        .join('')
        .substring(0, 2)
    },
    getUserColor(userId) {
      const colors = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
        '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
      ]
      return colors[userId % colors.length]
    },
    handleMention(query, startPos) {
      this.mentionQuery = query
      this.mentionStartPos = startPos
      this.showMentionSuggestions = true
      this.selectedMentionIndex = 0
    },
    selectMention(user) {
      const beforeMention = this.content.substring(0, this.mentionStartPos)
      const afterMention = this.content.substring(this.mentionStartPos + this.mentionQuery.length + 1)
      
      this.content = `${beforeMention}@${user.user_id} ${afterMention}`
      this.showMentionSuggestions = false
      this.mentionQuery = ''
      
      // Focus back to editor
      this.$nextTick(() => {
        this.$refs.editor.focus()
      })
    },
    handleKeydown(event) {
      if (this.showMentionSuggestions) {
        if (event.key === 'ArrowDown') {
          event.preventDefault()
          this.selectedMentionIndex = Math.min(
            this.selectedMentionIndex + 1,
            this.filteredMentions.length - 1
          )
        } else if (event.key === 'ArrowUp') {
          event.preventDefault()
          this.selectedMentionIndex = Math.max(this.selectedMentionIndex - 1, 0)
        } else if (event.key === 'Enter') {
          event.preventDefault()
          if (this.filteredMentions[this.selectedMentionIndex]) {
            this.selectMention(this.filteredMentions[this.selectedMentionIndex])
          }
        } else if (event.key === 'Escape') {
          this.showMentionSuggestions = false
        }
      } else if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
        event.preventDefault()
        this.handleSubmit()
      }
    },
    handleFocus() {
      // Focus handling if needed
    },
    handleBlur() {
      // Delay hiding suggestions to allow clicking
      setTimeout(() => {
        this.showMentionSuggestions = false
      }, 200)
    },
    async handleSubmit() {
      if (!this.content.trim() || this.submitting) return
      
      this.submitting = true
      
      try {
        this.$emit('submit', {
          content: this.content.trim(),
          parentId: this.parentId,
        })
        
        if (!this.isEditing) {
          this.content = ''
        }
      } catch (error) {
        console.error('Failed to submit comment:', error)
      } finally {
        this.submitting = false
      }
    },
    handleCancel() {
      if (this.isEditing) {
        this.$emit('cancel')
      } else {
        this.content = ''
        this.$emit('cancel')
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.comment-form {
  position: relative;
}

.comment-form__input-container {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.comment-form__avatar {
  flex-shrink: 0;
  margin-top: 8px;
}

.comment-form__avatar-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  font-weight: 600;
}

.comment-form__input-wrapper {
  flex: 1;
  position: relative;
}

.comment-form__editor {
  width: 100%;
  min-height: 80px;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 12px;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.5;
  resize: vertical;
  transition: border-color 0.2s ease;
  
  &:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
  }
  
  &::placeholder {
    color: #6c757d;
  }
}

.comment-form__mentions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
}

.comment-form__mention-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  
  &:hover,
  &.active {
    background: #f8f9fa;
  }
}

.comment-form__mention-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 10px;
  font-weight: 600;
  flex-shrink: 0;
}

.comment-form__mention-info {
  flex: 1;
  min-width: 0;
}

.comment-form__mention-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.comment-form__mention-email {
  font-size: 12px;
  color: #6c757d;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.comment-form__actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 12px;
  padding-left: 44px; // Account for avatar width
}

.comment-form__btn {
  padding: 8px 16px;
  border: 1px solid transparent;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 4px;
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  &--primary {
    background: #007bff;
    color: white;
    
    &:hover:not(:disabled) {
      background: #0056b3;
    }
  }
  
  &--secondary {
    background: transparent;
    color: #6c757d;
    border-color: #dee2e6;
    
    &:hover {
      background: #f8f9fa;
      color: #333;
    }
  }
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>