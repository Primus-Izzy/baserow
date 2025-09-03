<template>
  <div class="grid-view-rich-text-editor">
    <div
      ref="editor"
      class="grid-view-rich-text-editor__content"
      :class="{ 'grid-view-rich-text-editor__content--focused': isFocused }"
      contenteditable
      @input="onInput"
      @focus="onFocus"
      @blur="onBlur"
      @keydown="onKeyDown"
      v-html="formattedValue"
    ></div>

    <div
      v-if="isFocused && !readOnly"
      class="grid-view-rich-text-editor__toolbar"
    >
      <div class="grid-view-rich-text-editor__toolbar-group">
        <button
          type="button"
          class="grid-view-rich-text-editor__toolbar-button"
          :class="{
            'grid-view-rich-text-editor__toolbar-button--active':
              isFormatActive('bold'),
          }"
          @click="toggleFormat('bold')"
          title="Bold"
        >
          <i class="iconoir-bold"></i>
        </button>
        <button
          type="button"
          class="grid-view-rich-text-editor__toolbar-button"
          :class="{
            'grid-view-rich-text-editor__toolbar-button--active':
              isFormatActive('italic'),
          }"
          @click="toggleFormat('italic')"
          title="Italic"
        >
          <i class="iconoir-italic"></i>
        </button>
        <button
          type="button"
          class="grid-view-rich-text-editor__toolbar-button"
          :class="{
            'grid-view-rich-text-editor__toolbar-button--active':
              isFormatActive('underline'),
          }"
          @click="toggleFormat('underline')"
          title="Underline"
        >
          <i class="iconoir-underline"></i>
        </button>
      </div>

      <div class="grid-view-rich-text-editor__toolbar-group">
        <button
          type="button"
          class="grid-view-rich-text-editor__toolbar-button"
          @click="insertLink"
          title="Insert Link"
        >
          <i class="iconoir-link"></i>
        </button>
        <button
          type="button"
          class="grid-view-rich-text-editor__toolbar-button"
          @click="clearFormatting"
          title="Clear Formatting"
        >
          <i class="iconoir-text"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GridViewRichTextEditor',
  props: {
    value: {
      type: String,
      default: '',
    },
    readOnly: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      isFocused: false,
      currentValue: this.value,
    }
  },
  computed: {
    formattedValue() {
      return this.currentValue || ''
    },
  },
  watch: {
    value(newValue) {
      if (newValue !== this.currentValue) {
        this.currentValue = newValue
        this.updateEditorContent()
      }
    },
  },
  mounted() {
    this.updateEditorContent()
  },
  methods: {
    updateEditorContent() {
      if (
        this.$refs.editor &&
        this.$refs.editor.innerHTML !== this.formattedValue
      ) {
        this.$refs.editor.innerHTML = this.formattedValue
      }
    },
    onInput(event) {
      this.currentValue = event.target.innerHTML
      this.$emit('input', this.currentValue)
    },
    onFocus() {
      this.isFocused = true
      this.$emit('focus')
    },
    onBlur() {
      this.isFocused = false
      this.$emit('blur')
    },
    onKeyDown(event) {
      // Handle Enter key
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault()
        this.onBlur()
        this.$emit('save')
        return
      }

      // Handle Escape key
      if (event.key === 'Escape') {
        event.preventDefault()
        this.currentValue = this.value
        this.updateEditorContent()
        this.onBlur()
        this.$emit('cancel')
        return
      }

      // Handle keyboard shortcuts
      if (event.ctrlKey || event.metaKey) {
        switch (event.key) {
          case 'b':
            event.preventDefault()
            this.toggleFormat('bold')
            break
          case 'i':
            event.preventDefault()
            this.toggleFormat('italic')
            break
          case 'u':
            event.preventDefault()
            this.toggleFormat('underline')
            break
        }
      }
    },
    toggleFormat(command) {
      document.execCommand(command, false, null)
      this.$refs.editor.focus()
      this.onInput({ target: this.$refs.editor })
    },
    isFormatActive(command) {
      return document.queryCommandState(command)
    },
    insertLink() {
      const url = prompt('Enter URL:')
      if (url) {
        document.execCommand('createLink', false, url)
        this.$refs.editor.focus()
        this.onInput({ target: this.$refs.editor })
      }
    },
    clearFormatting() {
      document.execCommand('removeFormat', false, null)
      this.$refs.editor.focus()
      this.onInput({ target: this.$refs.editor })
    },
    focus() {
      this.$refs.editor.focus()
    },
  },
}
</script>

<style lang="scss" scoped>
.grid-view-rich-text-editor {
  position: relative;

  &__content {
    min-height: 20px;
    padding: 4px 8px;
    border: 1px solid transparent;
    border-radius: 4px;
    outline: none;
    line-height: 1.4;

    &--focused {
      border-color: #4285f4;
      background: #fff;
      box-shadow: 0 0 0 2px rgba(66, 133, 244, 0.1);
    }

    &:empty::before {
      content: attr(placeholder);
      color: #999;
      pointer-events: none;
    }
  }

  &__toolbar {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: #fff;
    border: 1px solid #e1e5e9;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    padding: 4px;
    display: flex;
    gap: 4px;
    z-index: 1000;
    margin-top: 2px;
  }

  &__toolbar-group {
    display: flex;
    gap: 2px;

    &:not(:last-child) {
      border-right: 1px solid #e1e5e9;
      padding-right: 4px;
      margin-right: 4px;
    }
  }

  &__toolbar-button {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border: none;
    background: transparent;
    border-radius: 3px;
    cursor: pointer;
    color: #666;
    transition: all 0.2s;

    &:hover {
      background: #f5f5f5;
      color: #333;
    }

    &--active {
      background: #4285f4;
      color: #fff;

      &:hover {
        background: #3367d6;
      }
    }

    i {
      font-size: 14px;
    }
  }
}

// Global styles for rich text content
:deep(.grid-view-rich-text-editor__content) {
  strong,
  b {
    font-weight: bold;
  }

  em,
  i {
    font-style: italic;
  }

  u {
    text-decoration: underline;
  }

  a {
    color: #4285f4;
    text-decoration: underline;

    &:hover {
      color: #3367d6;
    }
  }
}
</style>
