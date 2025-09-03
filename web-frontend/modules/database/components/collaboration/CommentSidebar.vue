<template>
  <div class="comment-sidebar" :class="{ 'comment-sidebar--visible': visible }">
    <div class="comment-sidebar__overlay" @click="handleClose"></div>

    <div class="comment-sidebar__panel">
      <div class="comment-sidebar__header">
        <div class="comment-sidebar__title">
          <i class="iconoir-chat-bubble"></i>
          <span>Row Comments</span>
          <div class="comment-sidebar__row-info">Row {{ rowId }}</div>
        </div>
        <button
          class="comment-sidebar__close-btn"
          @click="handleClose"
          title="Close comments"
        >
          <i class="iconoir-xmark"></i>
        </button>
      </div>

      <div class="comment-sidebar__content">
        <CommentThread
          v-if="tableId && rowId"
          :table-id="tableId"
          :row-id="rowId"
          @close="handleClose"
        />
      </div>
    </div>
  </div>
</template>

<script>
import CommentThread from './CommentThread.vue'

export default {
  name: 'CommentSidebar',
  components: {
    CommentThread,
  },
  props: {
    visible: {
      type: Boolean,
      default: false,
    },
    tableId: {
      type: Number,
      default: null,
    },
    rowId: {
      type: Number,
      default: null,
    },
  },
  watch: {
    visible(newValue) {
      if (newValue) {
        // Prevent body scroll when sidebar is open
        document.body.style.overflow = 'hidden'
      } else {
        // Restore body scroll
        document.body.style.overflow = ''
      }
    },
  },
  beforeDestroy() {
    // Ensure body scroll is restored
    document.body.style.overflow = ''
  },
  methods: {
    handleClose() {
      this.$emit('close')
    },
  },
}
</script>

<style lang="scss" scoped>
.comment-sidebar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1050;
  display: flex;
  align-items: stretch;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;

  &--visible {
    opacity: 1;
    visibility: visible;

    .comment-sidebar__panel {
      transform: translateX(0);
    }
  }
}

.comment-sidebar__overlay {
  flex: 1;
  background: rgba(0, 0, 0, 0.5);
  cursor: pointer;
}

.comment-sidebar__panel {
  width: 400px;
  max-width: 90vw;
  background: white;
  display: flex;
  flex-direction: column;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.15);
  transform: translateX(100%);
  transition: transform 0.3s ease;

  @media (max-width: 768px) {
    width: 100vw;
    max-width: none;
  }
}

.comment-sidebar__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #e9ecef;
  background: #f8f9fa;
}

.comment-sidebar__title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #333;

  i {
    font-size: 20px;
    color: #007bff;
  }
}

.comment-sidebar__row-info {
  background: #e9ecef;
  color: #6c757d;
  font-size: 12px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 12px;
  margin-left: 8px;
}

.comment-sidebar__close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #6c757d;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #e9ecef;
    color: #333;
  }

  i {
    font-size: 16px;
  }
}

.comment-sidebar__content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

// Animation for mobile
@media (max-width: 768px) {
  .comment-sidebar__panel {
    transform: translateY(100%);

    .comment-sidebar--visible & {
      transform: translateY(0);
    }
  }
}

// Ensure proper z-index stacking
.comment-sidebar {
  z-index: 1050;
}

// Handle body scroll lock
body.comment-sidebar-open {
  overflow: hidden;
}
</style>
