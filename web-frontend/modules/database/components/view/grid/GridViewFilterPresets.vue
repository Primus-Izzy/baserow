<template>
  <div class="grid-view-filter-presets">
    <div class="grid-view-filter-presets__header">
      <h3>{{ $t('gridView.filterPresets.title') }}</h3>
      <Button
        v-if="!readOnly && hasActiveFilters"
        type="primary"
        size="small"
        @click="showSaveModal = true"
      >
        <i class="iconoir-bookmark"></i>
        {{ $t('gridView.filterPresets.saveCurrentFilters') }}
      </Button>
    </div>

    <div class="grid-view-filter-presets__list">
      <div
        v-for="preset in filterPresets"
        :key="preset.id"
        class="grid-view-filter-presets__preset"
        :class="{
          'grid-view-filter-presets__preset--default': preset.is_default,
        }"
      >
        <div class="grid-view-filter-presets__preset-info">
          <div class="grid-view-filter-presets__preset-name">
            {{ preset.name }}
            <span
              v-if="preset.is_default"
              class="grid-view-filter-presets__default-badge"
            >
              {{ $t('gridView.filterPresets.default') }}
            </span>
          </div>
          <div class="grid-view-filter-presets__preset-details">
            {{ getPresetDescription(preset) }}
          </div>
        </div>

        <div class="grid-view-filter-presets__preset-actions">
          <Button type="ghost" size="small" @click="applyPreset(preset)">
            <i class="iconoir-filter"></i>
            {{ $t('gridView.filterPresets.apply') }}
          </Button>
          <Button
            v-if="!readOnly"
            type="ghost"
            size="small"
            @click="setAsDefault(preset)"
            :disabled="preset.is_default"
          >
            <i class="iconoir-star"></i>
          </Button>
          <Button
            v-if="!readOnly"
            type="ghost"
            size="small"
            @click="deletePreset(preset)"
          >
            <i class="iconoir-bin"></i>
          </Button>
        </div>
      </div>

      <div
        v-if="filterPresets.length === 0"
        class="grid-view-filter-presets__empty"
      >
        <i class="iconoir-filter"></i>
        <p>{{ $t('gridView.filterPresets.noPresets') }}</p>
        <p class="grid-view-filter-presets__empty-hint">
          {{ $t('gridView.filterPresets.createHint') }}
        </p>
      </div>
    </div>

    <!-- Save Preset Modal -->
    <Modal v-if="showSaveModal" @hidden="closeSaveModal">
      <h2 slot="title">
        {{ $t('gridView.filterPresets.savePreset') }}
      </h2>

      <form @submit.prevent="savePreset">
        <FormGroup :label="$t('gridView.filterPresets.presetName')" required>
          <FormInput
            v-model="presetForm.name"
            :placeholder="$t('gridView.filterPresets.presetNamePlaceholder')"
            required
          />
        </FormGroup>

        <FormGroup>
          <Checkbox v-model="presetForm.is_default">
            {{ $t('gridView.filterPresets.setAsDefault') }}
          </Checkbox>
        </FormGroup>

        <div class="grid-view-filter-presets__current-filters">
          <h4>{{ $t('gridView.filterPresets.currentFilters') }}</h4>
          <div
            v-for="(filter, index) in currentFilters"
            :key="index"
            class="grid-view-filter-presets__filter-item"
          >
            {{ getFilterDescription(filter) }}
          </div>
        </div>

        <div class="modal__actions">
          <Button type="secondary" @click="closeSaveModal">
            {{ $t('action.cancel') }}
          </Button>
          <Button type="primary" :loading="saving" @click="savePreset">
            {{ $t('action.save') }}
          </Button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<script>
import { notifyIf } from '@baserow/modules/core/utils/error'
import GridViewService from '@baserow/modules/database/services/view/grid'

export default {
  name: 'GridViewFilterPresets',
  props: {
    view: {
      type: Object,
      required: true,
    },
    fields: {
      type: Array,
      required: true,
    },
    currentFilters: {
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
      filterPresets: [],
      showSaveModal: false,
      saving: false,
      presetForm: {
        name: '',
        is_default: false,
      },
    }
  },
  computed: {
    hasActiveFilters() {
      return this.currentFilters && this.currentFilters.length > 0
    },
  },
  async mounted() {
    await this.loadFilterPresets()
  },
  methods: {
    async loadFilterPresets() {
      try {
        const { data } = await GridViewService(this.$client).getFilterPresets(
          this.view.id
        )
        this.filterPresets = data
      } catch (error) {
        notifyIf(error, 'view')
      }
    },
    getPresetDescription(preset) {
      const filterCount = preset.filters.length
      if (filterCount === 0) {
        return this.$t('gridView.filterPresets.noFilters')
      } else if (filterCount === 1) {
        return this.$t('gridView.filterPresets.oneFilter')
      } else {
        return this.$t('gridView.filterPresets.multipleFilters', {
          count: filterCount,
        })
      }
    },
    getFilterDescription(filter) {
      const field = this.fields.find((f) => f.id === filter.field)
      const fieldName = field ? field.name : `Field ${filter.field}`
      return `${fieldName} ${filter.type} ${filter.value}`
    },
    async applyPreset(preset) {
      try {
        this.$emit('apply-preset', preset.filters)
        this.$store.dispatch('toast/info', {
          title: this.$t('gridView.filterPresets.applied'),
          message: this.$t('gridView.filterPresets.appliedMessage', {
            name: preset.name,
          }),
        })
      } catch (error) {
        notifyIf(error, 'view')
      }
    },
    async setAsDefault(preset) {
      try {
        await GridViewService(this.$client).updateFilterPreset(
          this.view.id,
          preset.id,
          { is_default: true }
        )
        // Update local state
        this.filterPresets.forEach((p) => {
          p.is_default = p.id === preset.id
        })
        this.$store.dispatch('toast/success', {
          title: this.$t('gridView.filterPresets.defaultSet'),
          message: this.$t('gridView.filterPresets.defaultSetMessage', {
            name: preset.name,
          }),
        })
      } catch (error) {
        notifyIf(error, 'view')
      }
    },
    async deletePreset(preset) {
      if (
        confirm(
          this.$t('gridView.filterPresets.confirmDelete', { name: preset.name })
        )
      ) {
        try {
          await GridViewService(this.$client).deleteFilterPreset(
            this.view.id,
            preset.id
          )
          this.filterPresets = this.filterPresets.filter(
            (p) => p.id !== preset.id
          )
          this.$store.dispatch('toast/success', {
            title: this.$t('gridView.filterPresets.deleted'),
            message: this.$t('gridView.filterPresets.deletedMessage', {
              name: preset.name,
            }),
          })
        } catch (error) {
          notifyIf(error, 'view')
        }
      }
    },
    async savePreset() {
      this.saving = true
      try {
        const { data } = await GridViewService(this.$client).createFilterPreset(
          this.view.id,
          {
            name: this.presetForm.name,
            filters: this.currentFilters,
            is_default: this.presetForm.is_default,
          }
        )

        if (this.presetForm.is_default) {
          // Update other presets to not be default
          this.filterPresets.forEach((p) => {
            p.is_default = false
          })
        }

        this.filterPresets.push(data)
        this.closeSaveModal()

        this.$store.dispatch('toast/success', {
          title: this.$t('gridView.filterPresets.saved'),
          message: this.$t('gridView.filterPresets.savedMessage', {
            name: data.name,
          }),
        })
      } catch (error) {
        notifyIf(error, 'view')
      } finally {
        this.saving = false
      }
    },
    closeSaveModal() {
      this.showSaveModal = false
      this.presetForm = {
        name: '',
        is_default: false,
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.grid-view-filter-presets {
  &__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
    }
  }

  &__list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  &__preset {
    display: flex;
    align-items: center;
    padding: 12px;
    border: 1px solid #e1e5e9;
    border-radius: 6px;
    background: #fff;

    &--default {
      border-color: #4285f4;
      background: #f8f9ff;
    }
  }

  &__preset-info {
    flex: 1;
  }

  &__preset-name {
    font-weight: 600;
    margin-bottom: 2px;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  &__default-badge {
    background: #4285f4;
    color: white;
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 10px;
    text-transform: uppercase;
    font-weight: 500;
  }

  &__preset-details {
    font-size: 12px;
    color: #666;
  }

  &__preset-actions {
    display: flex;
    gap: 4px;
  }

  &__empty {
    text-align: center;
    padding: 40px 20px;
    color: #666;

    i {
      font-size: 48px;
      margin-bottom: 16px;
      opacity: 0.5;
    }

    p {
      margin: 0 0 8px 0;
      font-size: 14px;
    }

    &-hint {
      font-size: 12px;
      opacity: 0.8;
    }
  }

  &__current-filters {
    margin: 16px 0;

    h4 {
      margin: 0 0 8px 0;
      font-size: 14px;
      font-weight: 600;
    }
  }

  &__filter-item {
    padding: 6px 12px;
    background: #f5f5f5;
    border-radius: 4px;
    font-size: 12px;
    margin-bottom: 4px;
  }
}
</style>
