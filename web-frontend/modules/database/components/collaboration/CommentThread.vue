<template>
  <div class="comment-thread">
    <div class="comment-thread__header">
      <h4 class="comment-thread__title">Comments ({{ totalComments }})</h4>
      <div class="comment-thread__actions">
        <button
          v-if="hasUnresolvedComments"
          class="comment-thread__filter-btn"
          :class="{ active: !showResolved }"
          @click="toggleResolvedFilter"
        >
          <i class="iconoir-eye-off"></i>
          Hide resolved
        </button>
        <button
          class="comment-thread__refresh-btn"
          @click="refreshComments"
          :disabled="loading"
        >
          <i class="iconoir-refresh" :class="{ spinning: loading }"></i>
        </button>
      </div>
    </div>

    <div class="comment-thread__content">
      <div
        v-if="loading && comments.length === 0"
        class="comment-thread__loading"
      >
        <div class="comment-skeleton" v-for="i in 3" :key="i">
          <div class="comment-skeleton__avatar"></div>
          <div class="comment-skeleton__content">
            <div class="comment-skeleton__header"></div>
            <div class="comment-skeleton__text"></div>
          </div>
        </div>
      </div>

      <div v-else-if="comments.length === 0" class="comment-thread__empty">
        <i class="iconoir-chat-bubble-empty"></i>
        <p>No comments yet. Be the first to comment!</p>
      </div>

      <div v-else class="comment-thread__list">
        <Comment
          v-for="comment in filteredComments"
          :key="comment.id"
          :comment="comment"
          :table-id="tableId"
          :row-id="rowId"
          @reply="handleReply"
          @update="handleCommentUpdate"
          @delete="handleCommentDelete"
          @resolve="handleCommentResolve"
        />
      </div>

      <CommentForm
        :table-id="tableId"
        :row-id="rowId"
        :parent-id="replyToComment"
        :placeholder="
          replyToComment ? 'Write a reply...' : 'Write a comment...'
        "
        @submit="handleCommentSubmit"
        @cancel="cancelReply"
        class="comment-thread__form"
      />
    </div>
  </div>
</template>

<script>
import Comment from './Comment.vue'
import CommentForm from './CommentForm.vue'

export default {
  name: 'CommentThread',
  components: {
    Comment,
    CommentForm,
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
  },
  data() {
    return {
      loading: false,
      showResolved: true,
      replyToComment: null,
    }
  },
  computed: {
    comments() {
      return this.$store.getters['database/collaboration/commentsForRow'](
        this.tableId,
        this.rowId
      )
    },
    filteredComments() {
      if (this.showResolved) {
        return this.comments
      }
      return this.comments.filter((comment) => !comment.is_resolved)
    },
    totalComments() {
      return this.comments.length
    },
    hasUnresolvedComments() {
      return this.comments.some((comment) => !comment.is_resolved)
    },
  },
  async mounted() {
    await this.loadComments()
  },
  methods: {
    async loadComments() {
      this.loading = true
      try {
        await this.$store.dispatch('database/collaboration/loadComments', {
          tableId: this.tableId,
          rowId: this.rowId,
          includeResolved: this.showResolved,
        })
      } catch (error) {
        this.$toast.error('Failed to load comments')
        console.error('Failed to load comments:', error)
      } finally {
        this.loading = false
      }
    },
    async refreshComments() {
      await this.loadComments()
    },
    toggleResolvedFilter() {
      this.showResolved = !this.showResolved
      this.loadComments()
    },
    handleReply(commentId) {
      this.replyToComment = commentId
      this.$nextTick(() => {
        // Focus the comment form
        const form = this.$el.querySelector('.comment-thread__form textarea')
        if (form) {
          form.focus()
        }
      })
    },
    cancelReply() {
      this.replyToComment = null
    },
    async handleCommentSubmit(commentData) {
      try {
        await this.$store.dispatch('database/collaboration/createComment', {
          tableId: this.tableId,
          rowId: this.rowId,
          content: commentData.content,
          parentId: commentData.parentId,
        })
        this.replyToComment = null
        this.$toast.success('Comment added successfully')
      } catch (error) {
        this.$toast.error('Failed to add comment')
        console.error('Failed to create comment:', error)
      }
    },
    async handleCommentUpdate(comment) {
      try {
        await this.$store.dispatch('database/collaboration/updateComment', {
          commentId: comment.id,
          content: comment.content,
        })
        this.$toast.success('Comment updated successfully')
      } catch (error) {
        this.$toast.error('Failed to update comment')
        console.error('Failed to update comment:', error)
      }
    },
    async handleCommentDelete(commentId) {
      if (!confirm('Are you sure you want to delete this comment?')) {
        return
      }

      try {
        await this.$store.dispatch('database/collaboration/deleteComment', {
          commentId,
        })
        this.$toast.success('Comment deleted successfully')
      } catch (error) {
        this.$toast.error('Failed to delete comment')
        console.error('Failed to delete comment:', error)
      }
    },
    async handleCommentResolve(commentId) {
      try {
        await this.$store.dispatch(
          'database/collaboration/toggleCommentResolution',
          {
            commentId,
          }
        )
      } catch (error) {
        this.$toast.error('Failed to update comment status')
        console.error('Failed to toggle comment resolution:', error)
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.comment-thread {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.comment-thread__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #e9ecef;
}

.comment-thread__title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.comment-thread__actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.comment-thread__filter-btn,
.comment-thread__refresh-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  background: white;
  color: #6c757d;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #f8f9fa;
    border-color: #adb5bd;
  }

  &.active {
    background: #007bff;
    border-color: #007bff;
    color: white;
  }

  i {
    font-size: 14px;
  }
}

.comment-thread__refresh-btn {
  padding: 8px;

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .spinning {
    animation: spin 1s linear infinite;
  }
}

.comment-thread__content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.comment-thread__loading {
  padding: 20px;
}

.comment-skeleton {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;

  &__avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #e9ecef;
    animation: pulse 1.5s ease-in-out infinite;
  }

  &__content {
    flex: 1;
  }

  &__header {
    width: 120px;
    height: 12px;
    background: #e9ecef;
    border-radius: 4px;
    margin-bottom: 8px;
    animation: pulse 1.5s ease-in-out infinite;
  }

  &__text {
    width: 100%;
    height: 40px;
    background: #e9ecef;
    border-radius: 4px;
    animation: pulse 1.5s ease-in-out infinite;
  }
}

.comment-thread__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #6c757d;
  text-align: center;

  i {
    font-size: 48px;
    margin-bottom: 16px;
    opacity: 0.5;
  }

  p {
    margin: 0;
    font-size: 14px;
  }
}

.comment-thread__list {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}

.comment-thread__form {
  border-top: 1px solid #e9ecef;
  padding: 16px 20px;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
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
