<template>
  <div class="comment-button">
    <button
      class="comment-button__btn"
      :class="{
        'comment-button__btn--active': hasComments,
        'comment-button__btn--unresolved': hasUnresolvedComments,
      }"
      @click="handleClick"
      :title="buttonTitle"
    >
      <i class="iconoir-chat-bubble"></i>
      <span v-if="commentCount > 0" class="comment-button__count">
        {{ commentCount }}
      </span>
      <span v-if="unresolvedCount > 0" class="comment-button__unresolved-indicator">
        !
      </span>
    </button>
  </div>
</template>

<script>
export default {
  name: 'CommentButton',
  props: {
    tableId: {
      type: Number,
      required: true,
    },
    rowId: {
      type: Number,
      required: true,
    },
    size: {
      type: String,
      default: 'medium', // 'small', 'medium', 'large'
    },
  },
  computed: {
    comments() {
      return this.$store.getters['database/collaboration/commentsForRow'](
        this.tableId,
        this.rowId
      )
    },
    commentCount() {
      return this.comments.length
    },
    hasComments() {
      return this.commentCount > 0
    },
    unresolvedComments() {
      return this.comments.filter(comment => !comment.is_resolved)
    },
    unresolvedCount() {
      return this.unresolvedComments.length
    },
    hasUnresolvedComments() {
      return this.unresolvedCount > 0
    },
    buttonTitle() {
      if (this.commentCount === 0) {
        return 'Add comment'
      } else if (this.unresolvedCount > 0) {
        return `${this.commentCount} comments (${this.unresolvedCount} unresolved)`
      } else {
        return `${this.commentCount} comments`
      }
    },
  },
  methods: {
    handleClick() {
      this.$emit('click', {
        tableId: this.tableId,
        rowId: this.rowId,
        commentCount: this.commentCount,
        unresolvedCount: this.unresolvedCount,
      })
    },
  },
}
</script>

<style lang="scss" scoped>
.comment-button {
  display: inline-block;
}

.comment-button__btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 6px 8px;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  background: white;
  color: #6c757d;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 32px;
  height: 28px;
  
  &:hover {
    background: #f8f9fa;
    border-color: #adb5bd;
    color: #495057;
  }
  
  &--active {
    background: #e3f2fd;
    border-color: #2196f3;
    color: #1976d2;
    
    &:hover {
      background: #bbdefb;
    }
  }
  
  &--unresolved {
    background: #fff3cd;
    border-color: #ffc107;
    color: #856404;
    
    &:hover {
      background: #ffeaa7;
    }
    
    &.comment-button__btn--active {
      background: #fff3cd;
      border-color: #ffc107;
      color: #856404;
      
      &:hover {
        background: #ffeaa7;
      }
    }
  }
  
  i {
    font-size: 14px;
  }
}

.comment-button__count {
  font-weight: 600;
  font-size: 11px;
  line-height: 1;
}

.comment-button__unresolved-indicator {
  position: absolute;
  top: -2px;
  right: -2px;
  width: 12px;
  height: 12px;
  background: #dc3545;
  color: white;
  border-radius: 50%;
  font-size: 8px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  border: 1px solid white;
}

// Size variations
.comment-button--small {
  .comment-button__btn {
    padding: 4px 6px;
    height: 24px;
    min-width: 28px;
    font-size: 11px;
    
    i {
      font-size: 12px;
    }
  }
  
  .comment-button__count {
    font-size: 10px;
  }
  
  .comment-button__unresolved-indicator {
    width: 10px;
    height: 10px;
    font-size: 7px;
  }
}

.comment-button--large {
  .comment-button__btn {
    padding: 8px 12px;
    height: 36px;
    min-width: 40px;
    font-size: 14px;
    
    i {
      font-size: 16px;
    }
  }
  
  .comment-button__count {
    font-size: 12px;
  }
  
  .comment-button__unresolved-indicator {
    width: 14px;
    height: 14px;
    font-size: 9px;
  }
}
</style>