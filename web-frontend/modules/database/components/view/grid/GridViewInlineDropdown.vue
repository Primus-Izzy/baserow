<template>
  <div class="grid-view-inline-dropdown" :class="{ 'grid-view-inline-dropdown--open': isOpen }">
    <div
      ref="trigger"
      class="grid-view-inline-dropdown__trigger"
      @click="toggle"
      @keydown="onKeyDown"
      tabindex="0"
    >
      <span class="grid-view-inline-dropdown__value">
        {{ displayValue || placeholder }}
      </span>
      <i class="grid-view-inline-dropdown__arrow iconoir-nav-arrow-down"></i>
    </div>
    
    <div
      v-if="isOpen"
      ref="dropdown"
      class="grid-view-inline-dropdown__dropdown"
      :style="dropdownStyle"
    >
      <div
        v-if="searchable"
        class="grid-view-inline-dropdown__search"
      >
        <input
          ref="searchInput"
          v-model="searchQuery"
          type="text"
          class="grid-view-inline-dropdown__search-input"
          :placeholder="$t('gridView.inlineDropdown.search')"
          @keydown="onSearchKeyDown"
        />
      </div>
      
      <div class="grid-view-inline-dropdown__options">
        <div
          v-for="(option, index) in filteredOptions"
          :key="option.value"
          class="grid-view-inline-dropdown__option"
          :class="{
            'grid-view-inline-dropdown__option--selected': option.value === value,
            'grid-view-inline-dropdown__option--highlighted': index === highlightedIndex,
          }"
          @click="selectOption(option)"
          @mouseenter="highlightedIndex = index"
        >
          <div
            v-if="option.color"
            class="grid-view-inline-dropdown__option-color"
            :style="{ backgroundColor: option.color }"
          ></div>
          <span class="grid-view-inline-dropdown__option-text">
            {{ option.label }}
          </span>
          <i
            v-if="option.value === value"
            class="grid-view-inline-dropdown__option-check iconoir-check"
          ></i>
        </div>
        
        <div
          v-if="filteredOptions.length === 0"
          class="grid-view-inline-dropdown__no-options"
        >
          {{ $t('gridView.inlineDropdown.noOptions') }}
        </div>
        
        <div
          v-if="allowCreate && searchQuery && !exactMatch"
          class="grid-view-inline-dropdown__create-option"
          @click="createOption"
        >
          <i class="iconoir-plus"></i>
          {{ $t('gridView.inlineDropdown.createOption', { value: searchQuery }) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GridViewInlineDropdown',
  props: {
    value: {
      type: [String, Number, null],
      default: null,
    },
    options: {
      type: Array,
      required: true,
    },
    placeholder: {
      type: String,
      default: 'Select an option',
    },
    searchable: {
      type: Boolean,
      default: true,
    },
    allowCreate: {
      type: Boolean,
      default: false,
    },
    readOnly: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      isOpen: false,
      searchQuery: '',
      highlightedIndex: -1,
      dropdownStyle: {},
    }
  },
  computed: {
    displayValue() {
      const option = this.options.find(opt => opt.value === this.value)
      return option ? option.label : ''
    },
    filteredOptions() {
      if (!this.searchQuery) {
        return this.options
      }
      return this.options.filter(option =>
        option.label.toLowerCase().includes(this.searchQuery.toLowerCase())
      )
    },
    exactMatch() {
      return this.options.some(option =>
        option.label.toLowerCase() === this.searchQuery.toLowerCase()
      )
    },
  },
  mounted() {
    document.addEventListener('click', this.handleClickOutside)
    window.addEventListener('resize', this.updateDropdownPosition)
  },
  beforeDestroy() {
    document.removeEventListener('click', this.handleClickOutside)
    window.removeEventListener('resize', this.updateDropdownPosition)
  },
  methods: {
    toggle() {
      if (this.readOnly) return
      
      if (this.isOpen) {
        this.close()
      } else {
        this.open()
      }
    },
    open() {
      this.isOpen = true
      this.searchQuery = ''
      this.highlightedIndex = this.findSelectedIndex()
      this.$nextTick(() => {
        this.updateDropdownPosition()
        if (this.searchable && this.$refs.searchInput) {
          this.$refs.searchInput.focus()
        }
      })
    },
    close() {
      this.isOpen = false
      this.searchQuery = ''
      this.highlightedIndex = -1
    },
    selectOption(option) {
      this.$emit('input', option.value)
      this.$emit('change', option)
      this.close()
    },
    createOption() {
      const newOption = {
        value: this.searchQuery,
        label: this.searchQuery,
      }
      this.$emit('create-option', newOption)
      this.selectOption(newOption)
    },
    findSelectedIndex() {
      return this.filteredOptions.findIndex(option => option.value === this.value)
    },
    onKeyDown(event) {
      if (this.readOnly) return
      
      switch (event.key) {
        case 'Enter':
        case ' ':
          event.preventDefault()
          if (!this.isOpen) {
            this.open()
          } else if (this.highlightedIndex >= 0) {
            this.selectOption(this.filteredOptions[this.highlightedIndex])
          }
          break
        case 'Escape':
          event.preventDefault()
          this.close()
          break
        case 'ArrowDown':
          event.preventDefault()
          if (!this.isOpen) {
            this.open()
          } else {
            this.highlightedIndex = Math.min(
              this.highlightedIndex + 1,
              this.filteredOptions.length - 1
            )
          }
          break
        case 'ArrowUp':
          event.preventDefault()
          if (this.isOpen) {
            this.highlightedIndex = Math.max(this.highlightedIndex - 1, 0)
          }
          break
      }
    },
    onSearchKeyDown(event) {
      switch (event.key) {
        case 'Enter':
          event.preventDefault()
          if (this.highlightedIndex >= 0) {
            this.selectOption(this.filteredOptions[this.highlightedIndex])
          } else if (this.allowCreate && this.searchQuery && !this.exactMatch) {
            this.createOption()
          }
          break
        case 'Escape':
          event.preventDefault()
          this.close()
          break
        case 'ArrowDown':
          event.preventDefault()
          this.highlightedIndex = Math.min(
            this.highlightedIndex + 1,
            this.filteredOptions.length - 1
          )
          break
        case 'ArrowUp':
          event.preventDefault()
          this.highlightedIndex = Math.max(this.highlightedIndex - 1, 0)
          break
      }
    },
    handleClickOutside(event) {
      if (!this.$el.contains(event.target)) {
        this.close()
      }
    },
    updateDropdownPosition() {
      if (!this.isOpen || !this.$refs.dropdown) return
      
      const trigger = this.$refs.trigger
      const dropdown = this.$refs.dropdown
      const triggerRect = trigger.getBoundingClientRect()
      const dropdownRect = dropdown.getBoundingClientRect()
      const viewportHeight = window.innerHeight
      
      let top = triggerRect.bottom + 2
      let left = triggerRect.left
      
      // Check if dropdown would go below viewport
      if (top + dropdownRect.height > viewportHeight) {
        top = triggerRect.top - dropdownRect.height - 2
      }
      
      // Check if dropdown would go outside right edge
      if (left + dropdownRect.width > window.innerWidth) {
        left = window.innerWidth - dropdownRect.width - 10
      }
      
      this.dropdownStyle = {
        position: 'fixed',
        top: `${top}px`,
        left: `${left}px`,
        minWidth: `${triggerRect.width}px`,
        zIndex: 1000,
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.grid-view-inline-dropdown {
  position: relative;
  
  &__trigger {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 8px;
    border: 1px solid transparent;
    border-radius: 4px;
    cursor: pointer;
    outline: none;
    transition: all 0.2s;
    
    &:hover {
      border-color: #e1e5e9;
      background: #f8f9fa;
    }
    
    &:focus {
      border-color: #4285f4;
      box-shadow: 0 0 0 2px rgba(66, 133, 244, 0.1);
    }
  }
  
  &--open &__trigger {
    border-color: #4285f4;
    box-shadow: 0 0 0 2px rgba(66, 133, 244, 0.1);
  }
  
  &__value {
    flex: 1;
    text-align: left;
    color: #333;
    
    &:empty {
      color: #999;
    }
  }
  
  &__arrow {
    margin-left: 8px;
    color: #666;
    font-size: 12px;
    transition: transform 0.2s;
  }
  
  &--open &__arrow {
    transform: rotate(180deg);
  }
  
  &__dropdown {
    background: #fff;
    border: 1px solid #e1e5e9;
    border-radius: 6px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    max-height: 200px;
    overflow: hidden;
  }
  
  &__search {
    padding: 8px;
    border-bottom: 1px solid #e1e5e9;
  }
  
  &__search-input {
    width: 100%;
    padding: 6px 8px;
    border: 1px solid #e1e5e9;
    border-radius: 4px;
    outline: none;
    font-size: 14px;
    
    &:focus {
      border-color: #4285f4;
    }
  }
  
  &__options {
    max-height: 160px;
    overflow-y: auto;
  }
  
  &__option {
    display: flex;
    align-items: center;
    padding: 8px 12px;
    cursor: pointer;
    transition: background-color 0.2s;
    
    &:hover,
    &--highlighted {
      background: #f8f9fa;
    }
    
    &--selected {
      background: #e3f2fd;
      color: #1976d2;
    }
  }
  
  &__option-color {
    width: 12px;
    height: 12px;
    border-radius: 2px;
    margin-right: 8px;
    flex-shrink: 0;
  }
  
  &__option-text {
    flex: 1;
  }
  
  &__option-check {
    margin-left: 8px;
    color: #4285f4;
    font-size: 14px;
  }
  
  &__no-options {
    padding: 12px;
    text-align: center;
    color: #666;
    font-style: italic;
  }
  
  &__create-option {
    display: flex;
    align-items: center;
    padding: 8px 12px;
    cursor: pointer;
    color: #4285f4;
    border-top: 1px solid #e1e5e9;
    transition: background-color 0.2s;
    
    &:hover {
      background: #f8f9fa;
    }
    
    i {
      margin-right: 8px;
      font-size: 14px;
    }
  }
}
</style>