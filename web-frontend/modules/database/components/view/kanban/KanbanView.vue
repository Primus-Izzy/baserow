<template>
  <div class="kanban-view">
    <div class="kanban-view__loading" v-if="loading">
      <div class="loading"></div>
    </div>
    <div v-else class="kanban-view__container">
      <!-- Kanban columns -->
      <div class="kanban-view__columns" ref="columnsContainer">
        <KanbanColumn
          v-for="column in columns"
          :key="column.id"
          :column="column"
          :fields="cardFields"
          :rows="getRowsForColumn(column)"
          :database="database"
          :table="table"
          :view="view"
          :read-only="readOnly"
          :store-prefix="storePrefix"
          :decorations-by-place="decorationsByPlace"
          @row-updated="updateValue"
          @row-moved="moveRowToColumn"
          @row-clicked="rowClick"
          @add-card="handleAddCard"
        />
        
        <!-- Add new column button (if single-select field allows) -->
        <div v-if="canAddColumns" class="kanban-view__add-column">
          <button 
            class="kanban-view__add-column-btn"
            @click="showAddColumnModal = true"
          >
            <i class="iconoir-plus"></i>
            {{ $t('kanbanView.addColumn') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Row create modal -->
    <RowCreateModal
      v-if="!readOnly && $hasPermission('database.table.create_row', table, database.workspace.id)"
      ref="rowCreateModal"
      :database="database"
      :table="table"
      :view="view"
      :primary-is-sortable="true"
      :visible-fields="cardFields"
      :hidden-fields="hiddenFields"
      :show-hidden-fields="showHiddenFieldsInRowModal"
      :all-fields-in-table="fields"
      @toggle-hidden-fields-visibility="showHiddenFieldsInRowModal = !showHiddenFieldsInRowModal"
      @created="createRow"
      @order-fields="orderFields"
      @toggle-field-visibility="toggleFieldVisibility"
      @field-updated="$emit('refresh', $event)"
      @field-deleted="$emit('refresh')"
    />

    <!-- Row edit modal -->
    <RowEditModal
      ref="rowEditModal"
      enable-navigation
      :database="database"
      :table="table"
      :view="view"
      :all-fields-in-table="fields"
      :primary-is-sortable="true"
      :visible-fields="cardFields"
      :hidden-fields="hiddenFields"
      :rows="allRows"
      :read-only="readOnly || !$hasPermission('database.table.update_row', table, database.workspace.id)"
      :show-hidden-fields="showHiddenFieldsInRowModal"
      @hidden="$emit('selected-row', undefined)"
      @toggle-hidden-fields-visibility="showHiddenFieldsInRowModal = !showHiddenFieldsInRowModal"
      @update="updateValue"
      @order-fields="orderFields"
      @toggle-field-visibility="toggleFieldVisibility"
      @field-updated="$emit('refresh', $event)"
      @field-deleted="$emit('refresh')"
      @field-created="showFieldCreated"
      @field-created-callback-done="afterFieldCreatedUpdateFieldOptions"
      @navigate-previous="$emit('navigate-previous', $event, activeSearchTerm)"
      @navigate-next="$emit('navigate-next', $event, activeSearchTerm)"
      @refresh-row="refreshRow"
    />

    <!-- Floating add button -->
    <ButtonFloating
      v-if="!readOnly && !table.data_sync && $hasPermission('database.table.create_row', table, database.workspace.id)"
      icon="iconoir-plus"
      position="fixed"
      @click="$refs.rowCreateModal.show()"
    />
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { notifyIf } from '@baserow/modules/core/utils/error'
import {
  sortFieldsByOrderAndIdFunction,
  filterVisibleFieldsFunction,
  filterHiddenFieldsFunction,
} from '@baserow/modules/database/utils/view'
import KanbanColumn from '@baserow/modules/database/components/view/kanban/KanbanColumn'
import RowCreateModal from '@baserow/modules/database/components/row/RowCreateModal'
import RowEditModal from '@baserow/modules/database/components/row/RowEditModal'
import viewHelpers from '@baserow/modules/database/mixins/viewHelpers'
import viewDecoration from '@baserow/modules/database/mixins/viewDecoration'
import { populateRow } from '@baserow/modules/database/store/view/grid'
import { clone } from '@baserow/modules/core/utils/object'

export default {
  name: 'KanbanView',
  components: {
    KanbanColumn,
    RowCreateModal,
    RowEditModal,
  },
  mixins: [viewHelpers, viewDecoration],
  props: {
    fields: {
      type: Array,
      required: true,
    },
    view: {
      type: Object,
      required: true,
    },
    table: {
      type: Object,
      required: true,
    },
    database: {
      type: Object,
      required: true,
    },
    readOnly: {
      type: Boolean,
      required: true,
    },
    storePrefix: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      loading: false,
      showHiddenFieldsInRowModal: false,
      showAddColumnModal: false,
    }
  },
  computed: {
    ...mapGetters({
      row: 'rowModalNavigation/getRow',
    }),
    /**
     * Returns the visible field objects in the right order for cards.
     */
    cardFields() {
      const fieldOptions = this.fieldOptions
      return this.fields
        .filter(filterVisibleFieldsFunction(fieldOptions))
        .sort(sortFieldsByOrderAndIdFunction(fieldOptions))
    },
    hiddenFields() {
      const fieldOptions = this.fieldOptions
      return this.fields
        .filter(filterHiddenFieldsFunction(fieldOptions))
        .sort(sortFieldsByOrderAndIdFunction(fieldOptions))
    },
    /**
     * Returns the single-select field that is used for the Kanban columns.
     */
    statusField() {
      const fieldId = this.view.single_select_field
      return this.fields.find((field) => field.id === fieldId) || null
    },
    /**
     * Returns the columns based on the single-select field options.
     */
    columns() {
      if (!this.statusField || !this.statusField.select_options) {
        return []
      }
      
      // Create columns for each select option plus a null column for empty values
      const columns = this.statusField.select_options.map(option => ({
        id: option.id,
        value: option.value,
        color: option.color,
        name: option.value,
        isNull: false,
      }))
      
      // Add a column for rows with null/empty status
      columns.unshift({
        id: 'null',
        value: null,
        color: 'neutral',
        name: this.$t('kanbanView.noStatus'),
        isNull: true,
      })
      
      return columns
    },
    /**
     * Indicates whether new columns can be added (if the status field allows it).
     */
    canAddColumns() {
      return this.statusField && !this.readOnly
    },
    activeSearchTerm() {
      return this.$store.getters[
        `${this.storePrefix}view/kanban/getActiveSearchTerm`
      ]
    },
  },
  watch: {
    row: {
      deep: true,
      handler(row, oldRow) {
        if (this.$refs.rowEditModal) {
          if (
            (oldRow === null && row !== null) ||
            (oldRow && row && oldRow.id !== row.id)
          ) {
            this.populateAndEditRow(row)
          } else if (oldRow !== null && row === null) {
            this.$refs.rowEditModal.hide(false)
          }
        }
      },
    },
  },
  mounted() {
    if (this.row !== null) {
      this.populateAndEditRow(this.row)
    }
  },
  beforeCreate() {
    this.$options.computed = {
      ...(this.$options.computed || {}),
      ...mapGetters({
        allRows: this.$options.propsData.storePrefix + 'view/kanban/getRows',
        fieldOptions:
          this.$options.propsData.storePrefix +
          'view/kanban/getAllFieldOptions',
      }),
    }
  },
  methods: {
    /**
     * Returns the rows that belong to a specific column.
     */
    getRowsForColumn(column) {
      if (!this.statusField) return []
      
      return this.allRows.filter(row => {
        if (!row) return false
        
        const fieldValue = row[`field_${this.statusField.id}`]
        
        if (column.isNull) {
          return fieldValue === null || fieldValue === undefined
        }
        
        return fieldValue === column.value
      })
    },
    /**
     * Creates a new row.
     */
    async createRow({ row, callback }) {
      try {
        await this.$store.dispatch(
          this.storePrefix + 'view/kanban/createNewRow',
          {
            view: this.view,
            table: this.table,
            fields: this.fields,
            values: row,
          }
        )
        callback()
      } catch (error) {
        callback(error)
      }
    },
    /**
     * Updates a field value for a row.
     */
    async updateValue({ field, row, value, oldValue }) {
      try {
        await this.$store.dispatch(
          this.storePrefix + 'view/kanban/updateRowValue',
          {
            table: this.table,
            view: this.view,
            fields: this.fields,
            row,
            field,
            value,
            oldValue,
          }
        )
      } catch (error) {
        notifyIf(error, 'field')
      }
    },
    /**
     * Moves a row to a different column by updating the status field.
     */
    async moveRowToColumn({ row, targetColumn }) {
      if (!this.statusField) return
      
      const newValue = targetColumn.isNull ? null : targetColumn.value
      const oldValue = row[`field_${this.statusField.id}`]
      
      if (newValue === oldValue) return
      
      await this.updateValue({
        field: this.statusField,
        row,
        value: newValue,
        oldValue,
      })
    },
    /**
     * Handles row click to open the edit modal.
     */
    rowClick(row) {
      this.$refs.rowEditModal.show(row.id)
      this.$emit('selected-row', row)
    },
    /**
     * Refreshes a row from the backend.
     */
    refreshRow(row) {
      if (this.refreshingRow) return
      
      this.refreshingRow = true
      
      this.$nextTick(async () => {
        try {
          await this.$store.dispatch(
            this.storePrefix + 'view/kanban/refreshRowFromBackend',
            { table: this.table, row }
          )
        } catch (error) {
          notifyIf(error, 'row')
        } finally {
          this.refreshingRow = false
        }
      })
    },
    /**
     * Shows the field created callback and shows hidden fields.
     */
    showFieldCreated({ fetchNeeded, ...context }) {
      this.fieldCreated({ fetchNeeded, ...context })
      this.showHiddenFieldsInRowModal = true
    },
    /**
     * Populates a new row and opens the row edit modal.
     */
    populateAndEditRow(row) {
      const rowClone = populateRow(clone(row))
      this.$refs.rowEditModal.show(row.id, rowClone)
    },
    /**
     * Handles adding a new card to a specific column.
     */
    handleAddCard({ column, initialValues }) {
      if (this.$refs.rowCreateModal) {
        this.$refs.rowCreateModal.show(initialValues)
      }
    },
  },
}
</script>