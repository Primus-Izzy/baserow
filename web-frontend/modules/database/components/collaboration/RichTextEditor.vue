<template>
  <div class="rich-text-editor">
    <textarea
      ref="textarea"
      v-model="localValue"
      :placeholder="placeholder"
      class="rich-text-editor__textarea"
      @input="handleInput"
      @keydown="handleKeydown"
      @focus="handleFocus"
      @blur="handleBlur"
      @click="handleClick"
    ></textarea>
  </div>
</template>

<script>
export default {
  name: 'RichTextEditor',
  props: {
    value: {
      type: String,
      default: '',
    },
    placeholder: {
      type: String,
      default: '',
    },
    mentions: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      localValue: this.value,
      cursorPosition: 0,
    }
  },
  watch: {
    value(newValue) {
      if (newValue !== this.localValue) {
        this.localValue = newValue
      }
    },
    localValue(newValue) {
      this.$emit('input', newValue)
    },
  },
  methods: {
    handleInput(event) {
      this.localValue = event.target.value
      this.checkForMentions()
    },
    handleKeydown(event) {
      this.$emit('keydown', event)
    },
    handleFocus(event) {
      this.$emit('focus', event)
    },
    handleBlur(event) {
      this.$emit('blur', event)
    },
    handleClick(event) {
      this.cursorPosition = event.target.selectionStart
    },
    checkForMentions() {
      const textarea = this.$refs.textarea
      const cursorPos = textarea.selectionStart
      const textBeforeCursor = this.localValue.substring(0, cursorPos)
      
      // Look for @ symbol followed by text
      const mentionMatch = textBeforeCursor.match(/@(\w*)$/)
      
      if (mentionMatch) {
        const query = mentionMatch[1]
        const startPos = cursorPos - mentionMatch[0].length
        this.$emit('mention', query, startPos)
      }
    },
    focus() {
      this.$refs.textarea.focus()
    },
    blur() {
      this.$refs.textarea.blur()
    },
    setCursorPosition(position) {
      this.$nextTick(() => {
        const textarea = this.$refs.textarea
        textarea.setSelectionRange(position, position)
        textarea.focus()
      })
    },
  },
}
</script>

<style lang="scss" scoped>
.rich-text-editor {
  position: relative;
}

.rich-text-editor__textarea {
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
</style>