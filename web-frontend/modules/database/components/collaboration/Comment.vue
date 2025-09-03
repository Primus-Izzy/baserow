<template>
  <div class="comment" :class="{ 'comment--resolved': comment.is_resolved }">
    <div class="comment__avatar">
      <div
        class="comment__avatar-circle"
        :style="{ backgroundColor: getUserColor(comment.user) }"
        :title="`${comment.user_name} (${comment.user_email})`"
      >
        {{ getUserInitials(comment.user_name) }}
      </div>
    </div>

    <div class="comment__content">
      <div class="comment__header">
        <div class="comment__author">
          <span class="comment__author-name">{{ comment.user_name }}</span>
          <span
            class="comment__timestamp"
            :title="formatFullDate(comment.created_at)"
          >
            {{ formatRelativeTime(comment.created_at) }}
          </span>
          <span
            v-if="comment.updated_at !== comment.created_at"
            class="comment__edited"
          >
            (edited {{ formatRelativeTime(comment.updated_at) }})
          </span>
        </div>
        <div class="comment__actions">
          <button
            v-if="canResolve"
            class="comment__action-btn"
            :class="{ active: comment.is_resolved }"
            @click="toggleResolution"
            :title="
              comment.is_resolved ? 'Mark as unresolved' : 'Mark as resolved'
            "
          >
            <i
              :class="
                comment.is_resolved ? 'iconoir-check-circle' : 'iconoir-circle'
              "
            ></i>
          </button>
          <button
            class="comment__action-btn"
            @click="startReply"
            title="Reply to comment"
          >
            <i class="iconoir-reply"></i>
          </button>
          <button
            v-if="canEdit"
            class="comment__action-btn"
            @click="startEdit"
            title="Edit comment"
          >
            <i class="iconoir-edit-pencil"></i>
          </button>
          <button
            v-if="canDelete"
            class="comment__action-btn comment__action-btn--danger"
            @click="deleteComment"
            title="Delete comment"
          >
            <i class="iconoir-trash"></i>
          </button>
        </div>
      </div>

      <div v-if="!isEditing" class="comment__body">
        <div class="comment__text" v-html="formattedContent"></div>
        <div
          v-if="comment.mentions && comment.mentions.length > 0"
          class="comment__mentions"
        >
          <span class="comment__mentions-label">Mentioned:</span>
          <span
            v-for="mention in comment.mentions"
            :key="mention.id"
            class="comment__mention-tag"
          >
            @{{ mention.first_name }}
          </span>
        </div>
      </div>

      <CommentForm
        v-else
        :initial-content="comment.content"
        :table-id="tableId"
        :row-id="rowId"
        :is-editing="true"
        @submit="handleEdit"
        @cancel="cancelEdit"
        class="comment__edit-form"
      />

      <div
        v-if="comment.replies && comment.replies.length > 0"
        class="comment__replies"
      >
        <Comment
          v-for="reply in comment.replies"
          :key="reply.id"
          :comment="reply"
          :table-id="tableId"
          :row-id="rowId"
          :is-reply="true"
          @update="$emit('update', $event)"
          @delete="$emit('delete', $event)"
          @resolve="$emit('resolve', $event)"
        />
      </div>
    </div>
  </div>
</template>

<script>
import CommentForm from './CommentForm.vue'

export default {
  name: 'Comment',
  components: {
    CommentForm,
  },
  props: {
    comment: {
      type: Object,
      required: true,
    },
    tableId: {
      type: Number,
      required: true,
    },
    rowId: {
      type: Number,
      required: true,
    },
    isReply: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      isEditing: false,
    }
  },
  computed: {
    canEdit() {
      return this.comment.user === this.$auth.user.id
    },
    canDelete() {
      return this.comment.user === this.$auth.user.id
    },
    canResolve() {
      // Allow any user to resolve/unresolve comments
      return true
    },
    formattedContent() {
      let content = this.escapeHtml(this.comment.content)

      // Convert @mentions to clickable links
      content = content.replace(/@(\d+)/g, (match, userId) => {
        const mention = this.comment.mentions?.find(
          (m) => m.id === parseInt(userId)
        )
        if (mention) {
          return `<span class="mention">@${mention.first_name}</span>`
        }
        return match
      })

      // Convert line breaks to <br>
      content = content.replace(/\n/g, '<br>')

      return content
    },
  },
  methods: {
    getUserInitials(name) {
      if (!name) return '?'
      return name
        .split(' ')
        .map((part) => part.charAt(0).toUpperCase())
        .join('')
        .substring(0, 2)
    },
    getUserColor(userId) {
      const colors = [
        '#FF6B6B',
        '#4ECDC4',
        '#45B7D1',
        '#96CEB4',
        '#FFEAA7',
        '#DDA0DD',
        '#98D8C8',
        '#F7DC6F',
        '#BB8FCE',
        '#85C1E9',
      ]
      return colors[userId % colors.length]
    },
    formatRelativeTime(dateString) {
      const date = new Date(dateString)
      const now = new Date()
      const diffInSeconds = Math.floor((now - date) / 1000)

      if (diffInSeconds < 60) {
        return 'just now'
      } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60)
        return `${minutes}m ago`
      } else if (diffInSeconds < 86400) {
        const hours = Math.floor(diffInSeconds / 3600)
        return `${hours}h ago`
      } else if (diffInSeconds < 604800) {
        const days = Math.floor(diffInSeconds / 86400)
        return `${days}d ago`
      } else {
        return date.toLocaleDateString()
      }
    },
    formatFullDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleString()
    },
    escapeHtml(text) {
      const div = document.createElement('div')
      div.textContent = text
      return div.innerHTML
    },
    startReply() {
      this.$emit('reply', this.comment.id)
    },
    startEdit() {
      this.isEditing = true
    },
    cancelEdit() {
      this.isEditing = false
    },
    async handleEdit(commentData) {
      this.$emit('update', {
        id: this.comment.id,
        content: commentData.content,
      })
      this.isEditing = false
    },
    deleteComment() {
      this.$emit('delete', this.comment.id)
    },
    toggleResolution() {
      this.$emit('resolve', this.comment.id)
    },
  },
}
</script>

<style lang="scss" scoped>
.comment {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;

  &--resolved {
    opacity: 0.7;

    .comment__content {
      background: #f8f9fa;
      border-left: 3px solid #28a745;
    }
  }
}

.comment__avatar {
  flex-shrink: 0;
}

.comment__avatar-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.comment__content {
  flex: 1;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 12px 16px;
  transition: all 0.2s ease;

  &:hover {
    border-color: #dee2e6;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }
}

.comment__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.comment__author {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.comment__author-name {
  font-weight: 600;
  color: #333;
}

.comment__timestamp {
  color: #6c757d;
}

.comment__edited {
  color: #6c757d;
  font-style: italic;
}

.comment__actions {
  display: flex;
  align-items: center;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s ease;

  .comment:hover & {
    opacity: 1;
  }
}

.comment__action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: #6c757d;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #f8f9fa;
    color: #333;
  }

  &.active {
    color: #28a745;
  }

  &--danger {
    &:hover {
      background: #dc3545;
      color: white;
    }
  }

  i {
    font-size: 14px;
  }
}

.comment__body {
  margin-bottom: 8px;
}

.comment__text {
  color: #333;
  line-height: 1.5;
  word-wrap: break-word;

  :deep(.mention) {
    background: #e3f2fd;
    color: #1976d2;
    padding: 2px 4px;
    border-radius: 3px;
    font-weight: 500;
  }
}

.comment__mentions {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #e9ecef;
  font-size: 12px;
}

.comment__mentions-label {
  color: #6c757d;
  margin-right: 8px;
}

.comment__mention-tag {
  display: inline-block;
  background: #e3f2fd;
  color: #1976d2;
  padding: 2px 6px;
  border-radius: 12px;
  margin-right: 4px;
  font-size: 11px;
  font-weight: 500;
}

.comment__edit-form {
  margin-top: 8px;
}

.comment__replies {
  margin-top: 12px;
  padding-left: 16px;
  border-left: 2px solid #e9ecef;
}
</style>
