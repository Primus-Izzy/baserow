<template>
  <div ref="cell" class="grid-view__cell grid-field-people__cell active">
    <div ref="dropdownLink" class="grid-field-people__list">
      <div
        v-for="item in displayValue"
        :key="item.id"
        class="field-people__item"
      >
        <template v-if="item.id && item.name">
          <div
            v-if="field.show_avatar"
            class="field-people__avatar"
            :title="getPersonDisplayName(item)"
          >
            <Avatar
              :initials="getPersonInitials(item)"
              :name="item.name"
              size="small"
            />
          </div>
          <div
            class="field-people__name background-color--light-gray"
            :class="{ 'field-people__name--no-avatar': !field.show_avatar }"
          >
            <span class="field-people__name-text">{{
              getPersonDisplayName(item)
            }}</span>
            <a
              v-if="!readOnly && (!field.multiple_people || displayValue.length > 1)"
              class="field-people__remove"
              @click.prevent="removeValue($event, value, item.id)"
            >
              <i class="iconoir-cancel"></i>
            </a>
          </div>
        </template>
      </div>
      <a
        v-if="!readOnly && (!field.multiple_people || canAddMore)"
        class="grid-field-people__item grid-field-people__item--link"
        @click.prevent="toggleDropdown()"
      >
        <i class="iconoir-plus"></i>
      </a>
    </div>
    <FieldCollaboratorDropdown
      v-if="!readOnly"
      ref="dropdown"
      :collaborators="availableCollaborators"
      :show-input="false"
      :show-empty-value="false"
      class="dropdown--floating"
      @show="editing = true"
      @hide="editing = false"
      @input="updateValue($event, value)"
    />
  </div>
</template>

<script>
import gridField from '@baserow/modules/database/mixins/gridField'
import peopleField from '@baserow/modules/database/mixins/peopleField'
import FieldCollaboratorDropdown from '@baserow/modules/database/components/field/FieldCollaboratorDropdown'
import Avatar from '@baserow/modules/core/components/Avatar'

export default {
  name: 'GridViewFieldPeople',
  components: { FieldCollaboratorDropdown, Avatar },
  mixins: [gridField, peopleField],
  data() {
    return {
      editing: false,
    }
  },
  computed: {
    displayValue() {
      if (!this.value) {
        return []
      }
      return this.field.multiple_people 
        ? (Array.isArray(this.value) ? this.value : [])
        : (this.value.id ? [this.value] : [])
    },
    canAddMore() {
      if (!this.field.multiple_people) {
        return !this.value || !this.value.id
      }
      return true
    }
  }
}
</script>

<style lang="scss" scoped>
.grid-field-people__cell {
  padding: 0;
}

.grid-field-people__list {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
  padding: 4px;
  min-height: 32px;
}

.field-people__item {
  display: flex;
  align-items: center;
  gap: 4px;
  max-width: 100%;
}

.field-people__avatar {
  flex-shrink: 0;
}

.field-people__name {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  max-width: 120px;
  
  &--no-avatar {
    padding-left: 8px;
  }
}

.field-people__name-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.field-people__remove {
  color: #666;
  font-size: 10px;
  cursor: pointer;
  flex-shrink: 0;
  
  &:hover {
    color: #333;
  }
}

.grid-field-people__item--link {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  background-color: #f3f4f6;
  color: #666;
  cursor: pointer;
  flex-shrink: 0;
  
  &:hover {
    background-color: #e5e7eb;
    color: #333;
  }
  
  i {
    font-size: 12px;
  }
}
</style>