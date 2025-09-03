<template>
  <div class="kanban-view-mobile">
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
      <!-- Column Navigation -->
      <div class="column-navigation">
        <div class="column-tabs">
          <button
            v-for="(column, index) in columns"
            :key="column.id"
            class="column-tab touch-feedback"
            :class="{ active: activeColumnIndex === index }"
            @click="setActiveColumn(index)"
          >
            <span class="column-name">{{ column.name }}</span>
            <span class="card-count">{{ getColumnCardCount(column) }}</span>
          </button>
        </div>

        <!-- Horizontal scroll indicator -->
        <div class="scroll-indicator">
          <div
            class="scroll-thumb"
            :style="{
              left: `${
                (activeColumnIndex / Math.max(1, columns.length - 1)) * 100
              }%`,
              width: `${100 / Math.max(1, columns.length)}%`,
            }"
          ></div>
        </div>
      </div>

      <!-- Active Column View -->
      <div class="active-column-container">
        <div
          v-if="activeColumn"
          class="mobile-column"
          @touchstart="handleColumnTouchStart"
          @touchmove="handleColumnTouchMove"
          @touchend="handleColumnTouchEnd"
        >
          <!-- Column Header -->
          <div class="column-header">
            <div class="column-info">
              <h2 class="column-title">{{ activeColumn.name }}</h2>
              <span class="column-count"
                >{{ getColumnCardCount(activeColumn) }} cards</span
              >
            </div>
            <button
              class="add-card-btn touch-feedback"
              @click="addCard(activeColumn)"
            >
              <i class="fas fa-plus"></i>
            </button>
          </div>

          <!-- Cards List -->
          <div class="cards-container">
            <div
              v-for="card in getColumnCards(activeColumn)"
              :key="card.id"
              class="kanban-card-mobile touch-feedback"
              :class="{
                dragging: draggingCard === card.id,
                selected: selectedCards.has(card.id),
              }"
              @click="handleCardClick(card)"
              @touchstart="handleCardTouchStart(card, $event)"
              @touchend="handleCardTouchEnd(card, $event)"
            >
              <!-- Card Content -->
              <div class="card-content">
                <div class="card-header">
                  <span class="card-title">{{ getCardTitle(card) }}</span>
                  <button
                    class="card-menu-btn"
                    @click.stop="showCardMenu(card)"
                  >
                    <i class="fas fa-ellipsis-v"></i>
                  </button>
                </div>

                <div class="card-fields">
                  <div
                    v-for="field in getVisibleCardFields()"
                    :key="field.id"
                    class="card-field"
                  >
                    <label class="field-label">{{ field.name }}</label>
                    <div class="field-value">
                      <component
                        :is="getFieldComponent(field.type)"
                        :field="field"
                        :value="card[`field_${field.id}`]"
                        :mobile="true"
                        :compact="true"
                        :readonly="!canEditField(field)"
                        @update="handleFieldUpdate(card, field, $event)"
                      />
                    </div>
                  </div>
                </div>

                <!-- Card Tags/Labels -->
                <div v-if="getCardTags(card).length > 0" class="card-tags">
                  <span
                    v-for="tag in getCardTags(card)"
                    :key="tag.id"
                    class="card-tag"
                    :style="{ backgroundColor: tag.color }"
                  >
                    {{ tag.name }}
                  </span>
                </div>

                <!-- Card Actions -->
                <div class="card-actions">
                  <button
                    v-if="canMoveCard(card)"
                    class="action-btn"
                    @click.stop="showMoveCardModal(card)"
                  >
                    <i class="fas fa-arrows-alt"></i>
                    Move
                  </button>
                  <button class="action-btn" @click.stop="editCard(card)">
                    <i class="fas fa-edit"></i>
                    Edit
                  </button>
                </div>
              </div>

              <!-- Drag Handle -->
              <div
                v-if="canMoveCard(card)"
                class="drag-handle"
                @touchstart="startCardDrag(card, $event)"
              >
                <i class="fas fa-grip-vertical"></i>
              </div>
            </div>

            <!-- Empty State -->
            <div
              v-if="getColumnCards(activeColumn).length === 0"
              class="empty-column"
            >
              <i class="fas fa-inbox"></i>
              <p>No cards in this column</p>
              <button
                class="add-first-card-btn touch-feedback"
                @click="addCard(activeColumn)"
              >
                Add First Card
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Column Navigation Arrows -->
      <div class="column-navigation-arrows">
        <button
          class="nav-arrow left"
          :disabled="activeColumnIndex === 0"
          @click="previousColumn"
        >
          <i class="fas fa-chevron-left"></i>
        </button>
        <button
          class="nav-arrow right"
          :disabled="activeColumnIndex === columns.length - 1"
          @click="nextColumn"
        >
          <i class="fas fa-chevron-right"></i>
        </button>
      </div>

      <!-- Quick Actions -->
      <div class="quick-actions">
        <button
          class="quick-action-btn touch-feedback"
          @click="showColumnManager"
        >
          <i class="fas fa-columns"></i>
          Columns
        </button>
        <button class="quick-action-btn touch-feedback" @click="showFilters">
          <i class="fas fa-filter"></i>
          Filter
        </button>
        <button class="quick-action-btn touch-feedback" @click="showSettings">
          <i class="fas fa-cog"></i>
          Settings
        </button>
      </div>
    </div>

    <!-- Move Card Modal -->
    <div v-if="showMoveModal" class="mobile-modal">
      <div class="modal-header">
        <h3 class="modal-title">Move Card</h3>
        <button class="close-button" @click="showMoveModal = false">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <div class="modal-content">
        <div class="move-options">
          <div
            v-for="column in columns"
            :key="column.id"
            class="move-option touch-feedback"
            @click="moveCardToColumn(selectedCard, column)"
          >
            <span class="column-name">{{ column.name }}</span>
            <span class="card-count"
              >{{ getColumnCardCount(column) }} cards</span
            >
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile Navigation -->
    <div class="mobile-nav">
      <div class="nav-item" :class="{ active: currentTab === 'board' }">
        <i class="icon fas fa-columns"></i>
        <span>Board</span>
      </div>
      <div class="nav-item" :class="{ active: currentTab === 'cards' }">
        <i class="icon fas fa-th-large"></i>
        <span>Cards</span>
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

export default {
  name: 'KanbanViewMobile',
  mixins: [mobileResponsive],
  props: {
    view: {
      type: Object,
      required: true,
    },
    columns: {
      type: Array,
      default: () => [],
    },
    cards: {
      type: Array,
      default: () => [],
    },
    fields: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      activeColumnIndex: 0,
      currentTab: 'board',
      selectedCards: new Set(),
      draggingCard: null,
      showMoveModal: false,
      selectedCard: null,
      longPressTimer: null,
      touchStartX: 0,
      touchStartY: 0,
    }
  },
  computed: {
    activeColumn() {
      return this.columns[this.activeColumnIndex] || null
    },
  },
  methods: {
    setActiveColumn(index) {
      this.activeColumnIndex = index
    },

    previousColumn() {
      if (this.activeColumnIndex > 0) {
        this.activeColumnIndex--
      }
    },

    nextColumn() {
      if (this.activeColumnIndex < this.columns.length - 1) {
        this.activeColumnIndex++
      }
    },

    getColumnCardCount(column) {
      return this.getColumnCards(column).length
    },

    getColumnCards(column) {
      return this.cards.filter(
        (card) => card[`field_${this.view.kanban_field_id}`] === column.value
      )
    },

    getCardTitle(card) {
      const titleField = this.fields.find((f) => f.primary)
      return titleField ? card[`field_${titleField.id}`] : `Card ${card.id}`
    },

    getVisibleCardFields() {
      return this.fields
        .filter(
          (field) =>
            field.id !== this.view.kanban_field_id &&
            !field.hidden &&
            field.type !== 'file'
        )
        .slice(0, 3) // Show max 3 fields on mobile
    },

    getCardTags(card) {
      // Implementation would depend on your tag system
      return []
    },

    getFieldComponent(fieldType) {
      return `KanbanField${fieldType}`
    },

    canEditField(field) {
      return !field.readonly
    },

    canMoveCard(card) {
      return true // Implementation would depend on permissions
    },

    handleCardClick(card) {
      if (!this.selectedCards.has(card.id)) {
        this.$emit('card-click', card)
      }
    },

    handleCardTouchStart(card, event) {
      this.handleTouchStart(event)
      this.touchStartX = event.touches[0].clientX
      this.touchStartY = event.touches[0].clientY

      // Start long press timer for selection
      this.longPressTimer = setTimeout(() => {
        this.toggleCardSelection(card)
        if (navigator.vibrate) {
          navigator.vibrate(50)
        }
      }, 500)
    },

    handleCardTouchEnd(card, event) {
      this.handleTouchEnd(event)
      if (this.longPressTimer) {
        clearTimeout(this.longPressTimer)
        this.longPressTimer = null
      }
    },

    handleColumnTouchStart(event) {
      this.handleTouchStart(event)
    },

    handleColumnTouchMove(event) {
      // Handle swipe between columns
      const touchX = event.touches[0].clientX
      const deltaX = touchX - this.touchStartX

      if (Math.abs(deltaX) > 50) {
        if (deltaX > 0 && this.activeColumnIndex > 0) {
          this.previousColumn()
        } else if (
          deltaX < 0 &&
          this.activeColumnIndex < this.columns.length - 1
        ) {
          this.nextColumn()
        }
        this.touchStartX = touchX
      }
    },

    handleColumnTouchEnd(event) {
      this.handleTouchEnd(event)
    },

    toggleCardSelection(card) {
      if (this.selectedCards.has(card.id)) {
        this.selectedCards.delete(card.id)
      } else {
        this.selectedCards.add(card.id)
      }
      this.$emit('selection-change', Array.from(this.selectedCards))
    },

    startCardDrag(card, event) {
      this.draggingCard = card.id
      // Implementation for drag and drop would go here
    },

    addCard(column) {
      this.$emit('add-card', column)
    },

    editCard(card) {
      this.$emit('edit-card', card)
    },

    showCardMenu(card) {
      this.$emit('show-card-menu', card)
    },

    showMoveCardModal(card) {
      this.selectedCard = card
      this.showMoveModal = true
    },

    moveCardToColumn(card, column) {
      this.$emit('move-card', { card, column })
      this.showMoveModal = false
    },

    handleFieldUpdate(card, field, value) {
      this.$emit('field-update', { card, field, value })
    },

    showColumnManager() {
      this.$emit('show-column-manager')
    },

    showFilters() {
      this.$emit('show-filters')
    },

    showSettings() {
      this.$emit('show-settings')
    },
  },

  // Handle swipe gestures for column navigation
  mounted() {
    this.$on('swipe-left', () => {
      this.nextColumn()
    })

    this.$on('swipe-right', () => {
      this.previousColumn()
    })
  },
}
</script>

<style lang="scss" scoped>
@import '@baserow/modules/core/assets/scss/components/mobile/responsive.scss';

.kanban-view-mobile {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-neutral-50);
}

.column-navigation {
  background: var(--color-neutral-100);
  border-bottom: 1px solid var(--color-neutral-200);

  .column-tabs {
    display: flex;
    overflow-x: auto;
    padding: $mobile-spacing-sm $mobile-spacing-md;
    gap: $mobile-spacing-sm;
    -webkit-overflow-scrolling: touch;

    .column-tab {
      @include touch-friendly;
      display: flex;
      flex-direction: column;
      align-items: center;
      background: var(--color-neutral-50);
      border: 1px solid var(--color-neutral-300);
      border-radius: 8px;
      padding: $mobile-spacing-sm $mobile-spacing-md;
      min-width: 100px;
      white-space: nowrap;

      &.active {
        background: var(--color-primary);
        color: white;
        border-color: var(--color-primary);
      }

      .column-name {
        font-size: $mobile-font-size-sm;
        font-weight: 600;
      }

      .card-count {
        font-size: $mobile-font-size-xs;
        opacity: 0.8;
        margin-top: 2px;
      }
    }
  }

  .scroll-indicator {
    height: 3px;
    background: var(--color-neutral-200);
    position: relative;

    .scroll-thumb {
      position: absolute;
      height: 100%;
      background: var(--color-primary);
      transition: left 0.3s ease;
    }
  }
}

.active-column-container {
  flex: 1;
  overflow: hidden;

  .mobile-column {
    height: 100%;
    display: flex;
    flex-direction: column;
  }
}

.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $mobile-spacing-md;
  background: var(--color-neutral-100);
  border-bottom: 1px solid var(--color-neutral-200);

  .column-info {
    .column-title {
      margin: 0;
      font-size: $mobile-font-size-lg;
      font-weight: 600;
    }

    .column-count {
      font-size: $mobile-font-size-sm;
      color: var(--color-neutral-600);
    }
  }

  .add-card-btn {
    @include touch-friendly;
    background: var(--color-primary);
    color: white;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.cards-container {
  flex: 1;
  overflow-y: auto;
  padding: $mobile-spacing-md;
  -webkit-overflow-scrolling: touch;

  .kanban-card-mobile {
    background: var(--color-neutral-50);
    border: 1px solid var(--color-neutral-200);
    border-radius: 8px;
    margin-bottom: $mobile-spacing-md;
    position: relative;

    &.selected {
      border-color: var(--color-primary);
      box-shadow: 0 0 0 2px var(--color-primary-100);
    }

    &.dragging {
      opacity: 0.7;
      transform: scale(1.05);
    }

    .card-content {
      padding: $mobile-spacing-md;

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: $mobile-spacing-sm;

        .card-title {
          font-weight: 600;
          font-size: $mobile-font-size-md;
          line-height: 1.4;
          flex: 1;
        }

        .card-menu-btn {
          @include touch-friendly;
          background: none;
          border: none;
          color: var(--color-neutral-600);
          padding: 4px;
        }
      }

      .card-fields {
        margin-bottom: $mobile-spacing-sm;

        .card-field {
          margin-bottom: $mobile-spacing-sm;

          .field-label {
            display: block;
            font-size: $mobile-font-size-xs;
            color: var(--color-neutral-600);
            margin-bottom: 2px;
            font-weight: 500;
          }

          .field-value {
            font-size: $mobile-font-size-sm;
          }
        }
      }

      .card-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        margin-bottom: $mobile-spacing-sm;

        .card-tag {
          font-size: $mobile-font-size-xs;
          padding: 2px 6px;
          border-radius: 12px;
          color: white;
          font-weight: 500;
        }
      }

      .card-actions {
        display: flex;
        gap: $mobile-spacing-sm;

        .action-btn {
          @include touch-friendly;
          background: var(--color-neutral-100);
          border: 1px solid var(--color-neutral-300);
          border-radius: 6px;
          padding: 4px 8px;
          font-size: $mobile-font-size-xs;
          color: var(--color-neutral-700);

          .fas {
            margin-right: 4px;
          }
        }
      }
    }

    .drag-handle {
      position: absolute;
      right: 8px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--color-neutral-400);
      cursor: grab;
      padding: 4px;

      &:active {
        cursor: grabbing;
      }
    }
  }

  .empty-column {
    text-align: center;
    padding: $mobile-spacing-xl;
    color: var(--color-neutral-600);

    .fas {
      font-size: 48px;
      margin-bottom: $mobile-spacing-md;
      opacity: 0.5;
    }

    p {
      margin-bottom: $mobile-spacing-md;
      font-size: $mobile-font-size-md;
    }

    .add-first-card-btn {
      @include touch-friendly;
      background: var(--color-primary);
      color: white;
      border: none;
      border-radius: 8px;
      padding: $mobile-spacing-sm $mobile-spacing-md;
    }
  }
}

.column-navigation-arrows {
  position: fixed;
  top: 50%;
  left: 0;
  right: 0;
  transform: translateY(-50%);
  display: flex;
  justify-content: space-between;
  pointer-events: none;
  z-index: 10;

  .nav-arrow {
    @include touch-friendly;
    background: var(--color-neutral-50);
    border: 1px solid var(--color-neutral-300);
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    pointer-events: auto;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

    &:disabled {
      opacity: 0.3;
      pointer-events: none;
    }

    &.left {
      margin-left: $mobile-spacing-md;
    }

    &.right {
      margin-right: $mobile-spacing-md;
    }
  }
}

.quick-actions {
  display: flex;
  padding: $mobile-spacing-sm $mobile-spacing-md;
  gap: $mobile-spacing-sm;
  background: var(--color-neutral-100);
  border-top: 1px solid var(--color-neutral-200);

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

.mobile-modal {
  .move-options {
    .move-option {
      @include touch-friendly;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: $mobile-spacing-md;
      border-bottom: 1px solid var(--color-neutral-200);

      &:last-child {
        border-bottom: none;
      }

      .column-name {
        font-weight: 600;
      }

      .card-count {
        font-size: $mobile-font-size-sm;
        color: var(--color-neutral-600);
      }
    }
  }
}
</style>
