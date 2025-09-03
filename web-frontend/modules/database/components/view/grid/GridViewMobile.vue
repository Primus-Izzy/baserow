<template>
  <div class="grid-view-mobile">
    <!-- Mobile Header -->
    <div class="mobile-header">
      <div class="header-actions">
        <button class="action-button" @click="$emit('toggle-sidebar')">
          <i class="fas fa-bars"></i>
        </button>
        <h1 class="header-title">{{ view.name }}</h1>
        <button class="action-button" @click="$emit('show-options')">
          <i class="fas fa-ellipsis-v"></i>
        </button>
      </div>
    </div>

    <!-- Mobile Content -->
    <div class="mobile-content">
      <!-- Quick Actions Bar -->
      <div class="quick-actions-bar">
        <button
          class="quick-action-btn touch-feedback"
          @click="$emit('add-row')"
        >
          <i class="fas fa-plus"></i>
          <span>Add Row</span>
        </button>
        <button
          class="quick-action-btn touch-feedback"
          @click="showFilters = !showFilters"
        >
          <i class="fas fa-filter"></i>
          <span>Filter</span>
        </button>
        <button
          class="quick-action-btn touch-feedback"
          @click="showSort = !showSort"
        >
          <i class="fas fa-sort"></i>
          <span>Sort</span>
        </button>
      </div>

      <!-- Filters Panel (Collapsible) -->
      <div v-if="showFilters" class="mobile-panel">
        <div class="panel-header">
          <h3>Filters</h3>
          <button @click="showFilters = false" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="panel-content">
          <GridViewFilterPresets
            :view="view"
            :mobile="true"
            @apply-filter="handleFilterApply"
          />
        </div>
      </div>

      <!-- Sort Panel (Collapsible) -->
      <div v-if="showSort" class="mobile-panel">
        <div class="panel-header">
          <h3>Sort</h3>
          <button @click="showSort = false" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="panel-content">
          <!-- Sort options would go here -->
        </div>
      </div>

      <!-- Mobile Table View -->
      <div class="mobile-table-container">
        <!-- Horizontal scroll with sticky first column -->
        <div
          class="mobile-table-scroll"
          @touchstart="handleTouchStart"
          @touchend="handleTouchEnd"
          @scroll="handleScroll"
        >
          <table class="mobile-table">
            <thead class="sticky-header">
              <tr>
                <th
                  v-for="field in visibleFields"
                  :key="field.id"
                  class="mobile-th"
                  :class="{ 'sticky-column': field.id === firstFieldId }"
                  @click="handleColumnSort(field)"
                >
                  <div class="th-content">
                    <span class="field-name">{{ field.name }}</span>
                    <i
                      v-if="getSortDirection(field.id)"
                      class="sort-icon"
                      :class="
                        getSortDirection(field.id) === 'ASC'
                          ? 'fas fa-sort-up'
                          : 'fas fa-sort-down'
                      "
                    ></i>
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in rows"
                :key="row.id"
                class="mobile-row touch-feedback"
                @click="handleRowClick(row)"
                @touchstart="handleRowTouchStart(row, $event)"
                @touchend="handleRowTouchEnd(row, $event)"
              >
                <td
                  v-for="field in visibleFields"
                  :key="`${row.id}-${field.id}`"
                  class="mobile-td"
                  :class="{
                    'sticky-column': field.id === firstFieldId,
                    editable: canEditField(field),
                  }"
                  @dblclick="handleCellEdit(row, field)"
                >
                  <div class="cell-content">
                    <component
                      :is="getFieldComponent(field.type)"
                      :field="field"
                      :value="row[`field_${field.id}`]"
                      :mobile="true"
                      :readonly="!canEditField(field)"
                      @update="handleCellUpdate(row, field, $event)"
                    />
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Mobile Card View Toggle -->
      <div class="view-toggle">
        <button
          class="toggle-btn"
          :class="{ active: viewMode === 'table' }"
          @click="viewMode = 'table'"
        >
          <i class="fas fa-table"></i>
          Table
        </button>
        <button
          class="toggle-btn"
          :class="{ active: viewMode === 'cards' }"
          @click="viewMode = 'cards'"
        >
          <i class="fas fa-th-large"></i>
          Cards
        </button>
      </div>

      <!-- Mobile Card View -->
      <div v-if="viewMode === 'cards'" class="mobile-cards">
        <div
          v-for="row in rows"
          :key="row.id"
          class="mobile-card touch-feedback"
          @click="handleRowClick(row)"
          @touchstart="handleCardTouchStart(row, $event)"
        >
          <div class="card-header">
            <span class="card-title">
              {{ getRowTitle(row) }}
            </span>
            <button class="card-menu-btn" @click.stop="showCardMenu(row)">
              <i class="fas fa-ellipsis-v"></i>
            </button>
          </div>
          <div class="card-content">
            <div
              v-for="field in getCardFields()"
              :key="field.id"
              class="card-field"
            >
              <label class="field-label">{{ field.name }}</label>
              <div class="field-value">
                <component
                  :is="getFieldComponent(field.type)"
                  :field="field"
                  :value="row[`field_${field.id}`]"
                  :mobile="true"
                  :compact="true"
                  :readonly="!canEditField(field)"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading indicator -->
      <div v-if="loading" class="mobile-loading">
        <div class="loading-spinner"></div>
        <p>Loading...</p>
      </div>
    </div>

    <!-- Mobile Navigation -->
    <div class="mobile-nav">
      <div class="nav-item" :class="{ active: currentTab === 'data' }">
        <i class="icon fas fa-table"></i>
        <span>Data</span>
      </div>
      <div class="nav-item" :class="{ active: currentTab === 'views' }">
        <i class="icon fas fa-eye"></i>
        <span>Views</span>
      </div>
      <div class="nav-item" :class="{ active: currentTab === 'settings' }">
        <i class="icon fas fa-cog"></i>
        <span>Settings</span>
      </div>
    </div>
  </div>
</template>

<script>
import mobileResponsive from '@baserow/modules/core/mixins/mobileResponsive'
import GridViewFilterPresets from './GridViewFilterPresets'

export default {
  name: 'GridViewMobile',
  components: {
    GridViewFilterPresets,
  },
  mixins: [mobileResponsive],
  props: {
    view: {
      type: Object,
      required: true,
    },
    rows: {
      type: Array,
      default: () => [],
    },
    fields: {
      type: Array,
      default: () => [],
    },
    loading: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      showFilters: false,
      showSort: false,
      viewMode: 'table', // 'table' or 'cards'
      currentTab: 'data',
      longPressTimer: null,
      selectedRows: new Set(),
    }
  },
  computed: {
    visibleFields() {
      return this.fields.filter((field) => !field.hidden)
    },
    firstFieldId() {
      return this.visibleFields.length > 0 ? this.visibleFields[0].id : null
    },
  },
  methods: {
    handleFilterApply(filter) {
      this.$emit('apply-filter', filter)
      this.showFilters = false
    },

    handleColumnSort(field) {
      this.$emit('sort-column', field)
    },

    getSortDirection(fieldId) {
      // Implementation would depend on your sort state
      return null
    },

    handleRowClick(row) {
      if (!this.selectedRows.has(row.id)) {
        this.$emit('row-click', row)
      }
    },

    handleRowTouchStart(row, event) {
      this.handleTouchStart(event)
      // Start long press timer for multi-select
      this.longPressTimer = setTimeout(() => {
        this.toggleRowSelection(row)
        // Haptic feedback if available
        if (navigator.vibrate) {
          navigator.vibrate(50)
        }
      }, 500)
    },

    handleRowTouchEnd(row, event) {
      this.handleTouchEnd(event)
      if (this.longPressTimer) {
        clearTimeout(this.longPressTimer)
        this.longPressTimer = null
      }
    },

    handleCardTouchStart(row, event) {
      this.handleLongPress(event, () => {
        this.showCardMenu(row)
      })
    },

    toggleRowSelection(row) {
      if (this.selectedRows.has(row.id)) {
        this.selectedRows.delete(row.id)
      } else {
        this.selectedRows.add(row.id)
      }
      this.$emit('selection-change', Array.from(this.selectedRows))
    },

    handleCellEdit(row, field) {
      if (this.canEditField(field)) {
        this.$emit('cell-edit', { row, field })
      }
    },

    handleCellUpdate(row, field, value) {
      this.$emit('cell-update', { row, field, value })
    },

    canEditField(field) {
      // Implementation would depend on your permission system
      return !field.readonly
    },

    getFieldComponent(fieldType) {
      // Return appropriate mobile field component
      return `GridViewField${fieldType}`
    },

    getRowTitle(row) {
      const firstField = this.visibleFields[0]
      return firstField ? row[`field_${firstField.id}`] : `Row ${row.id}`
    },

    getCardFields() {
      // Return first 4-5 most important fields for card view
      return this.visibleFields.slice(0, 5)
    },

    showCardMenu(row) {
      this.$emit('show-card-menu', row)
    },

    handleScroll(event) {
      // Handle horizontal scroll with sticky column
      const scrollLeft = event.target.scrollLeft
      const stickyColumns = document.querySelectorAll('.sticky-column')
      stickyColumns.forEach((col) => {
        col.style.transform = `translateX(${scrollLeft}px)`
      })
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@baserow/modules/core/assets/scss/components/mobile/responsive.scss';

.grid-view-mobile {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-neutral-50);
}

.quick-actions-bar {
  display: flex;
  padding: $mobile-spacing-sm $mobile-spacing-md;
  gap: $mobile-spacing-sm;
  background: var(--color-neutral-100);
  border-bottom: 1px solid var(--color-neutral-200);

  .quick-action-btn {
    @include touch-friendly;
    display: flex;
    flex-direction: column;
    align-items: center;
    background: var(--color-neutral-50);
    border: 1px solid var(--color-neutral-300);
    border-radius: 8px;
    padding: $mobile-spacing-sm;
    flex: 1;

    .fas {
      margin-bottom: 4px;
      font-size: 16px;
    }

    span {
      font-size: $mobile-font-size-xs;
    }
  }
}

.mobile-panel {
  background: var(--color-neutral-50);
  border-bottom: 1px solid var(--color-neutral-200);

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: $mobile-spacing-md;
    border-bottom: 1px solid var(--color-neutral-200);

    h3 {
      margin: 0;
      font-size: $mobile-font-size-md;
    }

    .close-btn {
      @include touch-friendly;
      background: none;
      border: none;
      color: var(--color-neutral-600);
    }
  }

  .panel-content {
    padding: $mobile-spacing-md;
  }
}

.mobile-table-container {
  flex: 1;
  overflow: hidden;

  .mobile-table-scroll {
    height: 100%;
    overflow: auto;
    @include mobile-only {
      -webkit-overflow-scrolling: touch;
    }
  }

  .mobile-table {
    width: 100%;
    border-collapse: collapse;

    .sticky-header {
      position: sticky;
      top: 0;
      background: var(--color-neutral-100);
      z-index: 10;
    }

    .mobile-th {
      @include touch-friendly;
      border: 1px solid var(--color-neutral-200);
      background: var(--color-neutral-100);
      font-weight: 600;
      text-align: left;

      &.sticky-column {
        position: sticky;
        left: 0;
        z-index: 11;
        background: var(--color-neutral-200);
      }

      .th-content {
        display: flex;
        justify-content: space-between;
        align-items: center;

        .field-name {
          font-size: $mobile-font-size-sm;
        }

        .sort-icon {
          color: var(--color-primary);
        }
      }
    }

    .mobile-row {
      &:nth-child(even) {
        background: var(--color-neutral-25);
      }

      &:hover,
      &:active {
        background: var(--color-primary-100);
      }
    }

    .mobile-td {
      border: 1px solid var(--color-neutral-200);
      padding: $mobile-spacing-sm;
      min-width: 120px;

      &.sticky-column {
        position: sticky;
        left: 0;
        background: inherit;
        z-index: 5;
      }

      &.editable {
        cursor: pointer;

        &:hover {
          background: var(--color-primary-50);
        }
      }

      .cell-content {
        font-size: $mobile-font-size-sm;
        line-height: 1.4;
      }
    }
  }
}

.view-toggle {
  display: flex;
  padding: $mobile-spacing-sm $mobile-spacing-md;
  background: var(--color-neutral-100);
  border-top: 1px solid var(--color-neutral-200);

  .toggle-btn {
    @include touch-friendly;
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    background: none;
    border: none;
    color: var(--color-neutral-600);

    &.active {
      color: var(--color-primary);
    }

    .fas {
      margin-bottom: 4px;
    }
  }
}

.mobile-cards {
  padding: $mobile-spacing-md;
  display: grid;
  gap: $mobile-spacing-md;

  .mobile-card {
    background: var(--color-neutral-50);
    border: 1px solid var(--color-neutral-200);
    border-radius: 8px;
    padding: $mobile-spacing-md;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: $mobile-spacing-sm;

      .card-title {
        font-weight: 600;
        font-size: $mobile-font-size-md;
      }

      .card-menu-btn {
        @include touch-friendly;
        background: none;
        border: none;
        color: var(--color-neutral-600);
      }
    }

    .card-content {
      .card-field {
        margin-bottom: $mobile-spacing-sm;

        .field-label {
          display: block;
          font-size: $mobile-font-size-xs;
          color: var(--color-neutral-600);
          margin-bottom: 2px;
        }

        .field-value {
          font-size: $mobile-font-size-sm;
        }
      }
    }
  }
}

.mobile-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: $mobile-spacing-xl;

  .loading-spinner {
    width: 32px;
    height: 32px;
    border: 3px solid var(--color-neutral-200);
    border-top: 3px solid var(--color-primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: $mobile-spacing-md;
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
