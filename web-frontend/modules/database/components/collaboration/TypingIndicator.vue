<template>
  <div v-if="typingUsers.length > 0" class="typing-indicator">
    <div class="typing-dots">
      <div class="dot"></div>
      <div class="dot"></div>
      <div class="dot"></div>
    </div>
    <span class="typing-text">
      {{ typingText }}
    </span>
  </div>
</template>

<script>
export default {
  name: 'TypingIndicator',
  props: {
    fieldId: {
      type: Number,
      required: true,
    },
    rowId: {
      type: Number,
      required: true,
    },
  },
  computed: {
    typingUsers() {
      const indicators = this.$store.getters[
        'database/collaboration/typingIndicatorsForField'
      ](this.fieldId, this.rowId)
      const now = Date.now()

      // Filter out stale indicators (older than 5 seconds)
      return indicators.filter((indicator) => {
        return now - indicator.timestamp < 5000
      })
    },
    typingText() {
      const userNames = this.typingUsers.map((indicator) => {
        const presence = this.$store.getters[
          'database/collaboration/userPresence'
        ](indicator.userId)
        return presence?.userName || 'Someone'
      })

      if (userNames.length === 1) {
        return `${userNames[0]} is typing...`
      } else if (userNames.length === 2) {
        return `${userNames[0]} and ${userNames[1]} are typing...`
      } else if (userNames.length > 2) {
        return `${userNames[0]} and ${
          userNames.length - 1
        } others are typing...`
      }

      return ''
    },
  },
}
</script>

<style lang="scss" scoped>
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 12px;
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

.typing-dots {
  display: flex;
  gap: 2px;
}

.dot {
  width: 4px;
  height: 4px;
  background: #666;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;

  &:nth-child(1) {
    animation-delay: -0.32s;
  }

  &:nth-child(2) {
    animation-delay: -0.16s;
  }
}

@keyframes typing {
  0%,
  80%,
  100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.typing-text {
  font-style: italic;
}
</style>
