<template>
  <div class="user-presence-indicator">
    <div class="active-users">
      <div
        v-for="user in activeUsers"
        :key="user.user_id"
        class="user-avatar"
        :title="`${user.user_name} (${user.user_email})`"
        :style="{ backgroundColor: getUserColor(user.user_id) }"
      >
        {{ getUserInitials(user.user_name) }}
      </div>
      <div v-if="activeUsers.length > maxVisible" class="user-count">
        +{{ activeUsers.length - maxVisible }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserPresenceIndicator',
  props: {
    tableId: {
      type: Number,
      required: true,
    },
    viewId: {
      type: Number,
      default: null,
    },
    maxVisible: {
      type: Number,
      default: 5,
    },
  },
  computed: {
    activeUsers() {
      return this.$store.getters[
        'database/collaboration/activeUsersForContext'
      ](this.tableId, this.viewId).slice(0, this.maxVisible)
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
      // Generate consistent color based on user ID
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
  },
}
</script>

<style lang="scss" scoped>
.user-presence-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}

.active-users {
  display: flex;
  align-items: center;
  gap: 4px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  font-weight: 600;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s ease;

  &:hover {
    transform: scale(1.1);
  }
}

.user-count {
  background: #6c757d;
  color: white;
  font-size: 11px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 12px;
  min-width: 24px;
  text-align: center;
}
</style>
