<template>
  <div class="grid-view-column-groups">
    <div class="grid-view-column-groups__header">
      <h3>{{ $t('gridView.columnGroups.title') }}</h3>
      <Button
        v-if="!readOnly"
        type="primary"
        size="small"
        @click="showCreateModal = true"
      >
        <i class="iconoir-plus"></i>
        {{ $t('gridView.columnGroups.createGroup') }}
      </Button>
    </div>

    <div class="grid-view-column-groups__list">
      <div
        v-for="group in columnGroups"
        :key="group.id"
        class="grid-view-column-groups__group"
      >
        <div class="grid-view-column-groups__group-header">
          <div 
            class="grid-view-column-groups__group-color"
            :style="{ backgroundColor: group.color || '#e1e5e9' }"
          ></div>
          <div class="grid-view-column-groups__group-info">
            <div class="grid-view-column-groups__group-name">
              {{ group.name }}
            </div>
            <div class="grid-view-column-groups__group-details">
              {{ getGroupDescription(group) }}
            </div>
          </div>
          <div class="grid-view-column-groups__group-actions">
            <Button
              type="ghost"
              size="small"
              @click="toggleGroupCollapsed(group)"
            >
              <i :class="group.is_collapsed ? 'iconoir-nav-arrow-right' : 'iconoir-nav-arrow-down'"></i>
            </Button>
            <Button
              v-if="!readOnly"
              type="ghost"
              size="small"
              @click="editGroup(group)"
            >
              <i class="iconoir-edit-pencil"></i>
            </Button>
            <Button
              v-if="!readOnly"
              type="ghost"
              size="small"
              @click="deleteGroup(group)"
            >
              <i class="iconoir-bin"></i>
            </Button>
          </div>
        </div>

        <div
          v-if="!group.is_collapsed"
          class="grid-view-column-groups__group-fields"
        >
          <div
            v-for="fieldId in group.fields"
            :key="fieldId"
            class="grid-view-column-groups__field-item"
          >
            <i class="iconoir-db-table"></i>
            {{ getFieldName(fieldId) }}
          </div>
        </div>
      </div>

      <div
        v-if="columnGroups.length === 0"
        class="grid-view-column-groups__empty"
      >
        <i class="iconoir-group"></i>
        <p>{{ $t('gridView.columnGroups.noGroups') }}</p>
        <p class="grid-view-column-groups__empty-hint">
          {{ $t('gridView.columnGroups.createHint') }}
        </p>
      </div>
    </div>

    <!-- Create/Edit Group Modal -->
    <Modal
      v-if="showCreateModal || editingGroup"
      @hidden="closeModal"
    >
      <h2 slot="title">
        {{ editingGroup ? $t('gridView.columnGroups.editGroup') : $t('gridView.columnGroups.createGroup') }}
      </h2>
      
      <form @submit.prevent="saveGroup">
        <FormGroup
          :label="$t('gridView.columnGroups.groupName')"
          required
        >
          <FormInput
            v-model="groupForm.name"
            :placeholder="$t('gridView.columnGroups.groupNamePlaceholder')"
            required
          />
        </FormGroup>

        <FormGroup :label="$t('gridView.columnGroups.groupColor')">
          <ColorPicker v-model="groupForm.color" />
        </FormGroup>

        <FormGroup
          :label="$t('gridView.columnGroups.fields')"
          required
        >
          <div class="grid-view-column-groups__field-selection">
            <div
              v-for="field in availableFields"
              :key="field.id"
              class="grid-view-column-groups__field-option"
            >
              <Checkbox
                :model-value="groupForm.fields.includes(field.id)"
                @update:model-value="toggleFieldInGroup(field.id, $event)"
              >
                {{ field.name }}
              </Checkbox>
            </div>
          </div>
        </FormGroup>

        <FormGroup>
          <Checkbox v-model="groupForm.is_collapsed">
            {{ $t('gridView.columnGroups.startCollapsed') }}
          </Checkbox>
        </FormGroup>

        <div class="modal__actions">
          <Button type="secondary" @click="closeModal">
            {{ $t('action.cancel') }}
          </Button>
          <Button type="primary" :loading="saving" @click="saveGroup">
            {{ editingGroup ? $t('action.save') : $t('action.create') }}
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
  name: 'GridViewColumnGroups',
  props: {
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
      default: false,
    },
  },
  data() {
    return {
      columnGroups: [],
      showCreateModal: false,
      editingGroup: null,
      saving: false,
      groupForm: {
        name: '',
        color: '#4285f4',
        fields: [],
        is_collapsed: false,
      },
    }
  },
  computed: {
    availableFields() {
      return this.fields.filter(field => !field.primary)
    },
  },
  async mounted() {
    await this.loadColumnGroups()
  },
  methods: {
    async loadColumnGroups() {
      try {
        const { data } = await GridViewService(this.$client).getColumnGroups(this.view.id)
        this.columnGroups = data
      } catch (error) {
        notifyIf(error, 'view')
      }
    },
    getFieldName(fieldId) {
      const field = this.fields.find(f => f.id === fieldId)
      return field ? field.name : `Field ${fieldId}`
    },
    getGroupDescription(group) {
      const fieldCount = group.fields.length
      if (fieldCount === 0) {
        return this.$t('gridView.columnGroups.noFields')
      } else if (fieldCount === 1) {
        return this.$t('gridView.columnGroups.oneField')
      } else {
        return this.$t('gridView.columnGroups.multipleFields', { count: fieldCount })
      }
    },
    async toggleGroupCollapsed(group) {
      try {
        await GridViewService(this.$client).updateColumnGroup(
          this.view.id,
          group.id,
          { is_collapsed: !group.is_collapsed }
        )
        group.is_collapsed = !group.is_collapsed
        this.$emit('groups-updated', this.columnGroups)
      } catch (error) {
        notifyIf(error, 'view')
      }
    },
    editGroup(group) {
      this.editingGroup = group
      this.groupForm = {
        name: group.name,
        color: group.color || '#4285f4',
        fields: [...group.fields],
        is_collapsed: group.is_collapsed,
      }
    },
    async deleteGroup(group) {
      if (confirm(this.$t('gridView.columnGroups.confirmDelete', { name: group.name }))) {
        try {
          await GridViewService(this.$client).deleteColumnGroup(this.view.id, group.id)
          this.columnGroups = this.columnGroups.filter(g => g.id !== group.id)
          this.$emit('groups-updated', this.columnGroups)
          this.$store.dispatch('toast/success', {
            title: this.$t('gridView.columnGroups.deleted'),
            message: this.$t('gridView.columnGroups.deletedMessage', { name: group.name }),
          })
        } catch (error) {
          notifyIf(error, 'view')
        }
      }
    },
    toggleFieldInGroup(fieldId, isSelected) {
      if (isSelected) {
        if (!this.groupForm.fields.includes(fieldId)) {
          this.groupForm.fields.push(fieldId)
        }
      } else {
        this.groupForm.fields = this.groupForm.fields.filter(id => id !== fieldId)
      }
    },
    async saveGroup() {
      if (this.groupForm.fields.length === 0) {
        this.$store.dispatch('toast/error', {
          title: this.$t('error.generic.title'),
          message: this.$t('gridView.columnGroups.selectFields'),
        })
        return
      }

      this.saving = true
      try {
        if (this.editingGroup) {
          const { data } = await GridViewService(this.$client).updateColumnGroup(
            this.view.id,
            this.editingGroup.id,
            this.groupForm
          )
          const index = this.columnGroups.findIndex(g => g.id === this.editingGroup.id)
          this.columnGroups.splice(index, 1, data)
        } else {
          const { data } = await GridViewService(this.$client).createColumnGroup(
            this.view.id,
            this.groupForm
          )
          this.columnGroups.push(data)
        }
        
        this.$emit('groups-updated', this.columnGroups)
        this.closeModal()
        
        this.$store.dispatch('toast/success', {
          title: this.editingGroup ? $t('gridView.columnGroups.updated') : $t('gridView.columnGroups.created'),
          message: this.editingGroup 
            ? $t('gridView.columnGroups.updatedMessage', { name: this.groupForm.name })
            : $t('gridView.columnGroups.createdMessage', { name: this.groupForm.name }),
        })
      } catch (error) {
        notifyIf(error, 'view')
      } finally {
        this.saving = false
      }
    },
    closeModal() {
      this.showCreateModal = false
      this.editingGroup = null
      this.groupForm = {
        name: '',
        color: '#4285f4',
        fields: [],
        is_collapsed: false,
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.grid-view-column-groups {
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

  &__group {
    border: 1px solid #e1e5e9;
    border-radius: 6px;
    background: #fff;
    overflow: hidden;
  }

  &__group-header {
    display: flex;
    align-items: center;
    padding: 12px;
  }

  &__group-color {
    width: 16px;
    height: 16px;
    border-radius: 3px;
    margin-right: 12px;
    flex-shrink: 0;
  }

  &__group-info {
    flex: 1;
  }

  &__group-name {
    font-weight: 600;
    margin-bottom: 2px;
  }

  &__group-details {
    font-size: 12px;
    color: #666;
  }

  &__group-actions {
    display: flex;
    gap: 4px;
  }

  &__group-fields {
    padding: 0 12px 12px 40px;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  &__field-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: #666;
    
    i {
      font-size: 14px;
    }
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

  &__field-selection {
    max-height: 200px;
    overflow-y: auto;
    border: 1px solid #e1e5e9;
    border-radius: 4px;
    padding: 8px;
  }

  &__field-option {
    padding: 4px 0;
  }
}
</style>