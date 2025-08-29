<template>
  <div class="grid-view-formula-syntax-highlighter">
    <div
      ref="editor"
      class="grid-view-formula-syntax-highlighter__editor"
      :class="{ 
        'grid-view-formula-syntax-highlighter__editor--focused': isFocused,
        'grid-view-formula-syntax-highlighter__editor--error': hasError
      }"
      contenteditable
      @input="onInput"
      @focus="onFocus"
      @blur="onBlur"
      @keydown="onKeyDown"
      v-html="highlightedFormula"
    ></div>
    
    <div
      v-if="validationError"
      class="grid-view-formula-syntax-highlighter__error"
    >
      <i class="iconoir-warning-triangle"></i>
      {{ validationError }}
    </div>
    
    <div
      v-if="isFocused && suggestions.length > 0"
      class="grid-view-formula-syntax-highlighter__suggestions"
    >
      <div
        v-for="(suggestion, index) in suggestions"
        :key="suggestion.value"
        class="grid-view-formula-syntax-highlighter__suggestion"
        :class="{ 'grid-view-formula-syntax-highlighter__suggestion--highlighted': index === highlightedSuggestion }"
        @click="applySuggestion(suggestion)"
        @mouseenter="highlightedSuggestion = index"
      >
        <div class="grid-view-formula-syntax-highlighter__suggestion-icon">
          <i :class="getSuggestionIcon(suggestion.type)"></i>
        </div>
        <div class="grid-view-formula-syntax-highlighter__suggestion-content">
          <div class="grid-view-formula-syntax-highlighter__suggestion-name">
            {{ suggestion.name }}
          </div>
          <div class="grid-view-formula-syntax-highlighter__suggestion-description">
            {{ suggestion.description }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { debounce } from 'lodash'

export default {
  name: 'GridViewFormulaSyntaxHighlighter',
  props: {
    value: {
      type: String,
      default: '',
    },
    fields: {
      type: Array,
      default: () => [],
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
      validationError: null,
      suggestions: [],
      highlightedSuggestion: -1,
      cursorPosition: 0,
    }
  },
  computed: {
    hasError() {
      return !!this.validationError
    },
    highlightedFormula() {
      return this.highlightSyntax(this.currentValue)
    },
    formulaFunctions() {
      return [
        { name: 'SUM', type: 'function', description: 'Sum of values' },
        { name: 'AVERAGE', type: 'function', description: 'Average of values' },
        { name: 'COUNT', type: 'function', description: 'Count of values' },
        { name: 'MAX', type: 'function', description: 'Maximum value' },
        { name: 'MIN', type: 'function', description: 'Minimum value' },
        { name: 'IF', type: 'function', description: 'Conditional logic' },
        { name: 'CONCAT', type: 'function', description: 'Concatenate text' },
        { name: 'UPPER', type: 'function', description: 'Convert to uppercase' },
        { name: 'LOWER', type: 'function', description: 'Convert to lowercase' },
        { name: 'LENGTH', type: 'function', description: 'Text length' },
        { name: 'ROUND', type: 'function', description: 'Round number' },
        { name: 'ABS', type: 'function', description: 'Absolute value' },
        { name: 'NOW', type: 'function', description: 'Current date and time' },
        { name: 'TODAY', type: 'function', description: 'Current date' },
      ]
    },
    fieldSuggestions() {
      return this.fields.map(field => ({
        name: field.name,
        value: `field("${field.name}")`,
        type: 'field',
        description: `${field.type} field`,
      }))
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
  created() {
    this.debouncedValidate = debounce(this.validateFormula, 300)
  },
  mounted() {
    this.updateEditorContent()
  },
  methods: {
    updateEditorContent() {
      if (this.$refs.editor && this.$refs.editor.innerHTML !== this.highlightedFormula) {
        this.$refs.editor.innerHTML = this.highlightedFormula
      }
    },
    onInput(event) {
      this.currentValue = this.getPlainText(event.target.innerHTML)
      this.cursorPosition = this.getCursorPosition()
      this.$emit('input', this.currentValue)
      this.debouncedValidate()
      this.updateSuggestions()
    },
    onFocus() {
      this.isFocused = true
      this.$emit('focus')
      this.updateSuggestions()
    },
    onBlur() {
      // Delay blur to allow suggestion clicks
      setTimeout(() => {
        this.isFocused = false
        this.suggestions = []
        this.highlightedSuggestion = -1
        this.$emit('blur')
      }, 150)
    },
    onKeyDown(event) {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault()
        this.onBlur()
        this.$emit('save')
        return
      }
      
      if (event.key === 'Escape') {
        event.preventDefault()
        this.currentValue = this.value
        this.updateEditorContent()
        this.onBlur()
        this.$emit('cancel')
        return
      }
      
      // Handle suggestion navigation
      if (this.suggestions.length > 0) {
        switch (event.key) {
          case 'ArrowDown':
            event.preventDefault()
            this.highlightedSuggestion = Math.min(
              this.highlightedSuggestion + 1,
              this.suggestions.length - 1
            )
            break
          case 'ArrowUp':
            event.preventDefault()
            this.highlightedSuggestion = Math.max(this.highlightedSuggestion - 1, 0)
            break
          case 'Tab':
          case 'Enter':
            if (this.highlightedSuggestion >= 0) {
              event.preventDefault()
              this.applySuggestion(this.suggestions[this.highlightedSuggestion])
            }
            break
        }
      }
    },
    highlightSyntax(formula) {
      if (!formula) return ''
      
      let highlighted = formula
      
      // Highlight functions
      highlighted = highlighted.replace(
        /\b([A-Z_]+)\s*\(/g,
        '<span class="formula-function">$1</span>('
      )
      
      // Highlight field references
      highlighted = highlighted.replace(
        /field\s*\(\s*["']([^"']+)["']\s*\)/g,
        'field(<span class="formula-field">"$1"</span>)'
      )
      
      // Highlight strings
      highlighted = highlighted.replace(
        /(["'])([^"']*)\1/g,
        '<span class="formula-string">$1$2$1</span>'
      )
      
      // Highlight numbers
      highlighted = highlighted.replace(
        /\b(\d+(?:\.\d+)?)\b/g,
        '<span class="formula-number">$1</span>'
      )
      
      // Highlight operators
      highlighted = highlighted.replace(
        /([+\-*/=<>!&|])/g,
        '<span class="formula-operator">$1</span>'
      )
      
      return highlighted
    },
    getPlainText(html) {
      const div = document.createElement('div')
      div.innerHTML = html
      return div.textContent || div.innerText || ''
    },
    getCursorPosition() {
      const selection = window.getSelection()
      if (selection.rangeCount > 0) {
        const range = selection.getRangeAt(0)
        return range.startOffset
      }
      return 0
    },
    updateSuggestions() {
      const text = this.currentValue
      const cursorPos = this.cursorPosition
      
      // Get the word at cursor position
      const beforeCursor = text.substring(0, cursorPos)
      const wordMatch = beforeCursor.match(/(\w+)$/)
      
      if (!wordMatch) {
        this.suggestions = []
        return
      }
      
      const currentWord = wordMatch[1].toLowerCase()
      
      // Filter functions and fields
      const functionSuggestions = this.formulaFunctions.filter(func =>
        func.name.toLowerCase().startsWith(currentWord)
      )
      
      const fieldSuggestions = this.fieldSuggestions.filter(field =>
        field.name.toLowerCase().includes(currentWord)
      )
      
      this.suggestions = [...functionSuggestions, ...fieldSuggestions].slice(0, 8)
      this.highlightedSuggestion = this.suggestions.length > 0 ? 0 : -1
    },
    applySuggestion(suggestion) {
      const text = this.currentValue
      const cursorPos = this.cursorPosition
      
      // Find the word to replace
      const beforeCursor = text.substring(0, cursorPos)
      const afterCursor = text.substring(cursorPos)
      const wordMatch = beforeCursor.match(/(\w+)$/)
      
      if (wordMatch) {
        const wordStart = beforeCursor.length - wordMatch[1].length
        const newText = text.substring(0, wordStart) + 
                       (suggestion.value || suggestion.name) + 
                       afterCursor
        
        this.currentValue = newText
        this.$emit('input', this.currentValue)
        this.updateEditorContent()
      }
      
      this.suggestions = []
      this.highlightedSuggestion = -1
      this.$refs.editor.focus()
    },
    getSuggestionIcon(type) {
      switch (type) {
        case 'function':
          return 'iconoir-code'
        case 'field':
          return 'iconoir-db-table'
        default:
          return 'iconoir-text'
      }
    },
    async validateFormula() {
      if (!this.currentValue.trim()) {
        this.validationError = null
        return
      }
      
      try {
        // This would typically call a backend validation service
        // For now, we'll do basic syntax checking
        this.basicSyntaxValidation(this.currentValue)
        this.validationError = null
      } catch (error) {
        this.validationError = error.message
      }
    },
    basicSyntaxValidation(formula) {
      // Check for balanced parentheses
      let parenCount = 0
      for (const char of formula) {
        if (char === '(') parenCount++
        if (char === ')') parenCount--
        if (parenCount < 0) {
          throw new Error('Unmatched closing parenthesis')
        }
      }
      if (parenCount > 0) {
        throw new Error('Unmatched opening parenthesis')
      }
      
      // Check for valid field references
      const fieldRefs = formula.match(/field\s*\(\s*["']([^"']+)["']\s*\)/g)
      if (fieldRefs) {
        for (const ref of fieldRefs) {
          const fieldName = ref.match(/["']([^"']+)["']/)[1]
          if (!this.fields.some(field => field.name === fieldName)) {
            throw new Error(`Field "${fieldName}" does not exist`)
          }
        }
      }
    },
    focus() {
      this.$refs.editor.focus()
    },
  },
}
</script>

<style lang="scss" scoped>
.grid-view-formula-syntax-highlighter {
  position: relative;
  
  &__editor {
    min-height: 20px;
    padding: 8px 12px;
    border: 1px solid #e1e5e9;
    border-radius: 4px;
    outline: none;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 13px;
    line-height: 1.4;
    background: #fafafa;
    transition: all 0.2s;
    
    &--focused {
      border-color: #4285f4;
      background: #fff;
      box-shadow: 0 0 0 2px rgba(66, 133, 244, 0.1);
    }
    
    &--error {
      border-color: #f44336;
      background: #fff5f5;
    }
    
    &:empty::before {
      content: 'Enter formula...';
      color: #999;
      pointer-events: none;
    }
  }
  
  &__error {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 4px;
    padding: 4px 8px;
    background: #ffebee;
    border: 1px solid #ffcdd2;
    border-radius: 4px;
    color: #c62828;
    font-size: 12px;
    
    i {
      font-size: 14px;
    }
  }
  
  &__suggestions {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: #fff;
    border: 1px solid #e1e5e9;
    border-radius: 6px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    max-height: 200px;
    overflow-y: auto;
    z-index: 1000;
    margin-top: 2px;
  }
  
  &__suggestion {
    display: flex;
    align-items: center;
    padding: 8px 12px;
    cursor: pointer;
    transition: background-color 0.2s;
    
    &:hover,
    &--highlighted {
      background: #f8f9fa;
    }
  }
  
  &__suggestion-icon {
    margin-right: 8px;
    color: #666;
    
    i {
      font-size: 16px;
    }
  }
  
  &__suggestion-content {
    flex: 1;
  }
  
  &__suggestion-name {
    font-weight: 600;
    font-size: 13px;
    margin-bottom: 2px;
  }
  
  &__suggestion-description {
    font-size: 11px;
    color: #666;
  }
}

// Global styles for syntax highlighting
:deep(.grid-view-formula-syntax-highlighter__editor) {
  .formula-function {
    color: #1976d2;
    font-weight: 600;
  }
  
  .formula-field {
    color: #388e3c;
  }
  
  .formula-operator {
    color: #f57c00;
  }
  
  .formula-string {
    color: #d32f2f;
  }
  
  .formula-number {
    color: #7b1fa2;
  }
}
</style>