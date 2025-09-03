<template>
  <ViewHeader
    :view="view"
    :fields="fields"
    :table="table"
    :database="database"
    :read-only="readOnly"
    :store-prefix="storePrefix"
  >
    <!-- Kanban-specific controls -->
    <template #controls>
      <!-- Status field selector -->
      <div class="kanban-header__control">
        <label class="kanban-header__label">
          {{ $t('kanbanView.statusField') }}
        </label>
        <Dropdown
          v-model="statusFieldId"
          :disabled="readOnly"
          class="kanban-header__dropdown"
        >
          <DropdownItem
            v-for="field in singleSelectFields"
            :key="field.id"
            :name="field.name"
            :value="field.id"
          >
            <i class="iconoir-list"></i>
            {{ field.name }}
          </DropdownItem>
        </Dropdown>
      </div>

      <!-- Card color field selector -->
      <div class="kanban-header__control">
        <label class="kanban-header__label">
          {{ $t('kanbanView.cardColorField') }}
        </label>
        <Dropdown
          v-model="cardColorFieldId"
          :disabled="readOnly"
          class="kanban-header__dropdown"
        >
          <DropdownItem :name="$t('kanbanView.noColorField')" :value="null">
            <i class="iconoir-color-picker"></i>
            {{ $t('kanbanView.noColorField') }}
          </DropdownItem>
          <DropdownItem
            v-for="field in singleSelectFields"
            :key="field.id"
            :name="field.name"
            :value="field.id"
          >
            <i class="iconoir-color-picker"></i>
            {{ field.name }}
          </DropdownItem>
        </Dropdown>
      </div>

      <!-- Card fields selector -->
      <div class="kanban-header__control">
        <button
          class="kanban-header__button"
          @click="showFieldsModal = true"
          :disabled="readOnly"
        >
          <i class="iconoir-settings"></i>
          {{ $t('kanbanView.configureFields') }}
        </button>
      </div>
    </template>

    <!-- Fields configuration modal -->
    <Modal v-if="showFieldsModal" @hidden="showFieldsModal = false">
      <h2 class="box__title">{{ $t('kanbanView.configureFields') }}</h2>

      <div class="kanban-fields-config">
        <p class="kanban-fields-config__description">
          {{ $t('kanbanView.configureFieldsDescription') }}
        </p>

        <div class="kanban-fields-config__list">
          <div
            v-for="field in configurableFields"
            :key="field.id"
            class="kanban-fields-config__item"
          >
            <Checkbox
              :checked="isFieldVisible(field)"
              @input="toggleFieldVisibility(field, $event)"
            >
              {{ field.name }}
            </Checkbox>

            <div class="kanban-fields-config__field-type">
              {{ getFieldTypeName(field) }}
            </div>
          </div>
        </div>
      </div>

      <div class="actions">
        <button class="button button--large" @click="showFieldsModal = false">
          {{ $t('action.done') }}
        </button>
      </div>
    </Modal>
  </ViewHeader>
</template>

<script>
import ViewHeader from '@baserow/modules/database/components/view/ViewHeader'
import { notifyIf } from '@baserow/modules/core/utils/error'

export default {
  name: 'KanbanViewHeader',
  components: {
    ViewHeader,
  },
  props: {
    view: {
      type: Object,
      required: true,
    },
    fields: {
      type: Array,
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
      showFieldsModal: false,
    }
  },
  computed: {
    /**
     * Returns all single-select fields that can be used for Kanban columns.
     */
    singleSelectFields() {
      return this.fields.filter((field) => field.type === 'single_select')
    },
    /**
     * Returns fields that can be configured for display on cards.
     */
    configurableFields() {
      return this.fields.filter(
        (field) => !field.primary && field.id !== this.view.single_select_field
      )
    },
    /**
     * Gets/sets the status field ID.
     */
    statusFieldId: {
      get() {
        return this.view.single_select_field
      },
      async set(value) {
        if (value === this.view.single_select_field) return

        try {
          await this.$store.dispatch('view/update', {
            view: this.view,
            values: { single_select_field: value },
          })
          this.$emit('refresh')
        } catch (error) {
          notifyIf(error, 'view')
        }
      },
    },
    /**
     * Gets/sets the card color field ID.
     */
    cardColorFieldId: {
      get() {
        return this.view.card_cover_image_field
      },
      async set(value) {
        if (value === this.view.card_cover_image_field) return

        try {
          await this.$store.dispatch('view/update', {
            view: this.view,
            values: { card_cover_image_field: value },
          })
        } catch (error) {
          notifyIf(error, 'view')
        }
      },
    },
  },
  methods: {
    /**
     * Checks if a field is visible on cards.
     */
    isFieldVisible(field) {
      const fieldOptions =
        this.$store.getters[`${this.storePrefix}view/kanban/getAllFieldOptions`]
      const options = fieldOptions[field.id]
      return options ? !options.hidden : true
    },
    /**
     * Toggles field visibility on cards.
     */
    async toggleFieldVisibility(field, visible) {
      try {
        await this.$store.dispatch(
          `${this.storePrefix}view/kanban/updateFieldOptionsOfField`,
          {
            field,
            values: { hidden: !visible },
          }
        )
      } catch (error) {
        notifyIf(error, 'field')
      }
    },
    /**
     * Returns a human-readable field type name.
     */
    getFieldTypeName(field) {
      const fieldType = this.$registry.get('field', field.type)
      return fieldType.getName()
    },
  },
}
</script>
