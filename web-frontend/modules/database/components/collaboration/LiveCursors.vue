<template>
  <div class="live-cursors">
    <div
      v-for="(cursor, userId) in liveCursors"
      :key="userId"
      class="live-cursor"
      :style="{
        left: cursor.x + 'px',
        top: cursor.y + 'px',
        '--cursor-color': getUserColor(userId),
      }"
    >
      <div class="cursor-pointer"></div>
      <div class="cursor-label">
        {{ getUserName(userId) }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LiveCursors',
  computed: {
    liveCursors() {
      const cursors = this.$store.getters['database/collaboration/liveCursors']
      const now = Date.now()

      // Filter out stale cursors (older than 10 seconds)
      return Object.fromEntries(
        Object.entries(cursors).filter(([, cursor]) => {
          return now - cursor.timestamp < 10000
        })
      )
    },
  },
  methods: {
    getUserName(userId) {
      const presence =
        this.$store.getters['database/collaboration/userPresence'](userId)
      return presence?.userName || 'Unknown User'
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
.live-cursors {
  position: fixed;
  top: 0;
  left: 0;
  pointer-events: none;
  z-index: 9999;
}

.live-cursor {
  position: absolute;
  pointer-events: none;
  transition: all 0.1s ease-out;
}

.cursor-pointer {
  width: 0;
  height: 0;
  border-left: 8px solid var(--cursor-color);
  border-right: 8px solid transparent;
  border-bottom: 12px solid var(--cursor-color);
  border-top: 4px solid transparent;
  transform: rotate(-45deg);
}

.cursor-label {
  position: absolute;
  top: 16px;
  left: 8px;
  background: var(--cursor-color);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  white-space: nowrap;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);

  &::before {
    content: '';
    position: absolute;
    top: -4px;
    left: 4px;
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 4px solid var(--cursor-color);
  }
}
</style>
