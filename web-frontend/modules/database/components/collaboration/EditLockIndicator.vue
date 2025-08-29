<template>
  <div v-if="isLocked" class="edit-lock-indicator">
    <div class="lock-icon">
      <i class="fas fa-lock"></i>
    </div>
    <div class="lock-message">
      <span v-if="isMyLock" class="my-lock">
        You are editing this field
      </span>
      <span v-else class="other-lock">
        {{ lockOwnerName }} is editing this field
      </span>
    </div>
    <button
      v-if="isMyLock"
      class="release-lock-btn"
      @click="releaseLock"
      title="Release lock"
    >
      <i class="fas fa-times"></i>
    </button>
  </div>
</template>

<script>
export default {
  name: 'EditLockIndicator',
  props: {
    tableId: {
      type: Number,
      required: true,
    },
    rowId: {
      type: Number,
      required: true,
    },
    fieldId: {
      type: Number,
      required: true,
    },
  },
  computed: {
    isLocked() {
      return this.$store.getters['database/collaboration/isFieldLocked'](
        this.tableId,
        this.rowId,
        this.fieldId
      )
    },
    lockOwnerId() {
      return this.$store.getters['database/collaboration/fieldLockOwner'](
        this.tableId,
        this.rowId,
        this.fieldId
      )
    },
    isMyLock() {
      return this.$store.getters['database/collaboration/hasEditLock'](
        this.tableId,
        this.rowId,
        this.fieldId
      )
    },
    lockOwnerName() {
      if (!this.lockOwnerId) return 'Unknown User'
      const presence = this.$store.getters['database/collaboration/userPresence'](this.lockOwnerId)
      return presence?.userName || 'Unknown User'
    },
  },
  methods: {
    async releaseLock() {
      try {
        await this.$store.dispatch('database/collaboration/releaseEditLock', {
          rowId: this.rowId,
          fieldId: this.fieldId,
        })
      } catch (error) {
        console.error('Failed to release edit lock:', error)
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.edit-lock-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: rgba(255, 193, 7, 0.1);
  border: 1px solid rgba(255, 193, 7, 0.3);
  border-radius: 6px;
  font-size: 12px;
  margin-bottom: 8px;
}

.lock-icon {
  color: #ffc107;
  font-size: 14px;
}

.lock-message {
  flex: 1;
  
  .my-lock {
    color: #28a745;
    font-weight: 500;
  }
  
  .other-lock {
    color: #ffc107;
    font-weight: 500;
  }
}

.release-lock-btn {
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  padding: 2px;
  border-radius: 2px;
  transition: color 0.2s ease;
  
  &:hover {
    color: #dc3545;
  }
}
</style>