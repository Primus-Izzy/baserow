<template>
  <ViewHeader
    :view="view"
    :fields="fields"
    :table="table"
    :database="database"
    :read-only="readOnly"
    :store-prefix="storePrefix"
  >
    <template #title>
      {{ view.name }}
    </template>

    <template #menus>
      <!-- Calendar configuration dropdown -->
      <Dropdown
        v-if="!readOnly"
        ref="calendarConfigDropdown"
        :show-search="false"
        class="header__filter"
      >
        <template #header>
          <div class="header__filter-name">
            <i class="iconoir-calendar header__filter-icon"></i>
            {{ $t('calendarViewHeader.settings') }}
          </div>
        </template>
        <template #body>
          <div class="calendar-config">
            <!-- Date field selection -->
            <div class="calendar-config__section">
              <label class="calendar-config__label">
                {{ $t('calendarViewHeader.dateField') }}
              </label>
              <Dropdown
                :value="view.date_field"
                :show-search="false"
                @input="updateDateField"
              >
                <template #value>
                  <div v-if="dateField">
                    <i :class="'iconoir-' + dateField._.type.iconClass"></i>
                    {{ dateField.name }}
                  </div>
                  <div v-else class="calendar-config__placeholder">
                    {{ $t('calendarViewHeader.selectDateField') }}
                  </div>
                </template>
                <DropdownItem
                  v-for="field in dateFields"
                  :key="field.id"
                  :name="field.name"
                  :value="field.id"
                  :icon="field._.type.iconClass"
                />
              </Dropdown>
            </div>

            <!-- Event title field selection -->
            <div class="calendar-config__section">
              <label class="calendar-config__label">
                {{ $t('calendarViewHeader.titleField') }}
              </label>
              <Dropdown
                :value="view.event_title_field"
                :show-search="false"
                @input="updateTitleField"
              >
                <template #value>
                  <div v-if="titleField">
                    <i :class="'iconoir-' + titleField._.type.iconClass"></i>
                    {{ titleField.name }}
                  </div>
                  <div v-else class="calendar-config__placeholder">
                    {{ $t('calendarViewHeader.selectTitleField') }}
                  </div>
                </template>
                <DropdownItem
                  v-for="field in textFields"
                  :key="field.id"
                  :name="field.name"
                  :value="field.id"
                  :icon="field._.type.iconClass"
                />
              </Dropdown>
            </div>

            <!-- Event color field selection -->
            <div class="calendar-config__section">
              <label class="calendar-config__label">
                {{ $t('calendarViewHeader.colorField') }}
              </label>
              <Dropdown
                :value="view.event_color_field"
                :show-search="false"
                @input="updateColorField"
              >
                <template #value>
                  <div v-if="colorField">
                    <i :class="'iconoir-' + colorField._.type.iconClass"></i>
                    {{ colorField.name }}
                  </div>
                  <div v-else class="calendar-config__placeholder">
                    {{ $t('calendarViewHeader.selectColorField') }}
                  </div>
                </template>
                <DropdownItem
                  :name="$t('calendarViewHeader.noColorField')"
                  :value="null"
                  icon="iconoir-cancel"
                />
                <DropdownItem
                  v-for="field in colorFields"
                  :key="field.id"
                  :name="field.name"
                  :value="field.id"
                  :icon="field._.type.iconClass"
                />
              </Dropdown>
            </div>

            <!-- Recurring events toggle -->
            <div class="calendar-config__section">
              <SwitchInput
                :value="view.enable_recurring_events"
                @input="updateRecurringEvents"
              >
                {{ $t('calendarViewHeader.enableRecurring') }}
              </SwitchInput>
            </div>

            <!-- External sync configuration -->
            <div class="calendar-config__section">
              <div class="calendar-config__subsection-title">
                {{ $t('calendarViewHeader.externalSync') }}
              </div>
              <SwitchInput
                :value="view.enable_external_sync"
                @input="updateExternalSync"
              >
                {{ $t('calendarViewHeader.enableExternalSync') }}
              </SwitchInput>
              
              <div v-if="view.enable_external_sync" class="calendar-config__external-options">
                <button
                  class="button button--small"
                  @click="showExternalSyncModal = true"
                >
                  {{ $t('calendarViewHeader.configureSync') }}
                </button>
              </div>
            </div>
          </div>
        </template>
      </Dropdown>

      <!-- Field options dropdown -->
      <ViewFieldsContext
        ref="fieldsContext"
        :database="database"
        :view="view"
        :fields="fields"
        :allow-cover-image-field="false"
        :store-prefix="storePrefix"
        :disable-sort="false"
        @refresh="$emit('refresh', $event)"
      >
        <template #header>
          <div class="header__filter-name">
            <i class="iconoir-eye-alt header__filter-icon"></i>
            {{ $t('calendarViewHeader.fieldOptions') }}
          </div>
        </template>
      </ViewFieldsContext>
    </template>

    <!-- External sync modal -->
    <CalendarExternalSyncModal
      v-if="showExternalSyncModal"
      :view="view"
      @close="showExternalSyncModal = false"
      @updated="handleExternalSyncUpdate"
    />
  </ViewHeader>
</template>

<script>
import ViewHeader from '@baserow/modules/database/components/view/ViewHeader'
import ViewFieldsContext from '@baserow/modules/database/components/view/ViewFieldsContext'
import CalendarExternalSyncModal from './CalendarExternalSyncModal'
import { notifyIf } from '@baserow/modules/core/utils/error'

export default {
  name: 'CalendarViewHeader',
  components: {
    ViewHeader,
    ViewFieldsContext,
    CalendarExternalSyncModal,
  },
  props: {
    database: {
      type: Object,
      required: true,
    },
    table: {
      type: Object,
      required: true,
    },
    view: {
      type: Object,
      required: true,
    },
    fields: {
      type: Array,
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
      showExternalSyncModal: false,
    }
  },
  computed: {
    dateField() {
      return this.fields.find(field => field.id === this.view.date_field)
    },
    
    titleField() {
      return this.fields.find(field => field.id === this.view.event_title_field)
    },
    
    colorField() {
      return this.fields.find(field => field.id === this.view.event_color_field)
    },
    
    dateFields() {
      return this.fields.filter(field => 
        field.type === 'date' || field.type === 'datetime'
      )
    },
    
    textFields() {
      return this.fields.filter(field => 
        field.type === 'text' || 
        field.type === 'long_text' ||
        field.type === 'rich_text'
      )
    },
    
    colorFields() {
      return this.fields.filter(field => 
        field.type === 'single_select' || 
        field.type === 'multiple_select' ||
        field.type === 'color'
      )
    },
  },
  methods: {
    async updateDateField(fieldId) {
      try {
        await this.$store.dispatch('view/update', {
          view: this.view,
          values: { date_field: fieldId },
        })
        this.$emit('refresh')
      } catch (error) {
        notifyIf(error, 'view')
      }
    },
    
    async updateTitleField(fieldId) {
      try {
        await this.$store.dispatch('view/update', {
          view: this.view,
          values: { event_title_field: fieldId },
        })
        this.$emit('refresh')
      } catch (error) {
        notifyIf(error, 'view')
      }
    },
    
    async updateColorField(fieldId) {
      try {
        await this.$store.dispatch('view/update', {
          view: this.view,
          values: { event_color_field: fieldId },
        })
        this.$emit('refresh')
      } catch (error) {
        notifyIf(error, 'view')
      }
    },
    
    async updateRecurringEvents(enabled) {
      try {
        await this.$store.dispatch('view/update', {
          view: this.view,
          values: { enable_recurring_events: enabled },
        })
        this.$emit('refresh')
      } catch (error) {
        notifyIf(error, 'view')
      }
    },
    
    async updateExternalSync(enabled) {
      try {
        await this.$store.dispatch('view/update', {
          view: this.view,
          values: { enable_external_sync: enabled },
        })
        this.$emit('refresh')
      } catch (error) {
        notifyIf(error, 'view')
      }
    },
    
    handleExternalSyncUpdate() {
      this.showExternalSyncModal = false
      this.$emit('refresh')
    },
  },
}
</script>

<style lang="scss" scoped>
.calendar-config {
  padding: 12px;
  min-width: 280px;

  &__section {
    margin-bottom: 16px;

    &:last-child {
      margin-bottom: 0;
    }
  }

  &__label {
    display: block;
    font-size: 12px;
    font-weight: 600;
    color: $color-neutral-600;
    margin-bottom: 6px;
    text-transform: uppercase;
  }

  &__placeholder {
    color: $color-neutral-400;
    font-style: italic;
  }

  &__subsection-title {
    font-size: 13px;
    font-weight: 600;
    color: $color-neutral-700;
    margin-bottom: 8px;
  }

  &__external-options {
    margin-top: 8px;
  }
}
</style>