<template>
  <div class="control__elements">
    <ul v-if="field.multiple_people" class="field-people__items">
      <li
        v-for="item in value"
        :key="item.id"
        class="field-people__item field-people__item--row-edit"
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
              size="medium"
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
              v-if="!readOnly"
              class="field-people__remove"
              @click.prevent="removeValue($event, value, item.id)"
            >
              <i class="iconoir-cancel"></i>
            </a>
          </div>
        </template>
      </li>
    </ul>

    <div v-else-if="value && value.id" class="field-people__single-item">
      <div
        v-if="field.show_avatar"
        class="field-people__avatar"
        :title="getPersonDisplayName(value)"
      >
        <Avatar
          :initials="getPersonInitials(value)"
          :name="value.name"
          size="medium"
        />
      </div>
      <div
        class="field-people__name background-color--light-gray"
        :class="{ 'field-people__name--no-avatar': !field.show_avatar }"
      >
        <span class="field-people__name-text">{{
          getPersonDisplayName(value)
        }}</span>
        <a
          v-if="!readOnly"
          class="field-people__remove"
          @click.prevent="clearSingleValue"
        >
          <i class="iconoir-cancel"></i>
        </a>
      </div>
    </div>

    <span v-if="!readOnly" ref="dropdownLink">
      <ButtonText icon="iconoir-plus" @click.prevent="toggleDropdown()">
        {{
          field.multiple_people
            ? $t('rowEditFieldPeople.addPerson')
            : value && value.id
            ? $t('rowEditFieldPeople.changePerson')
            : $t('rowEditFieldPeople.selectPerson')
        }}
      </ButtonText>
    </span>

    <FieldCollaboratorDropdown
      v-if="!readOnly"
      ref="dropdown"
      :collaborators="availableCollaborators"
      :disabled="readOnly"
      :show-input="false"
      :show-empty-value="!field.multiple_people"
      :error="touched && !valid"
      @input="updateValue($event, value)"
      @hide="touch()"
    />

    <div v-show="touched && !valid" class="error">
      {{ error }}
    </div>
  </div>
</template>

<script>
import rowEditField from '@baserow/modules/database/mixins/rowEditField'
import peopleField from '@baserow/modules/database/mixins/peopleField'
import FieldCollaboratorDropdown from '@baserow/modules/database/components/field/FieldCollaboratorDropdown'
import Avatar from '@baserow/modules/core/components/Avatar'

export default {
  name: 'RowEditFieldPeople',
  components: { FieldCollaboratorDropdown, Avatar },
  mixins: [rowEditField, peopleField],
  methods: {
    clearSingleValue() {
      this.$emit('update', null, this.value)
    },
  },
}
</script>

<style lang="scss" scoped>
.field-people__items {
  list-style: none;
  padding: 0;
  margin: 0 0 8px 0;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.field-people__item,
.field-people__single-item {
  display: flex;
  align-items: center;
  gap: 8px;

  &--row-edit {
    margin-bottom: 0;
  }
}

.field-people__avatar {
  flex-shrink: 0;
}

.field-people__name {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 14px;

  &--no-avatar {
    padding-left: 12px;
  }
}

.field-people__name-text {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.field-people__remove {
  color: #666;
  font-size: 12px;
  cursor: pointer;
  flex-shrink: 0;

  &:hover {
    color: #333;
  }
}
</style>
