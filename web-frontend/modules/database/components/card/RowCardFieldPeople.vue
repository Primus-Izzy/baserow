<template>
  <div class="row-card-field-people">
    <div v-for="item in displayValue" :key="item.id" class="field-people__item">
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
          class="field-people__name"
          :class="{ 'field-people__name--no-avatar': !field.show_avatar }"
        >
          <span class="field-people__name-text">{{
            getPersonDisplayName(item)
          }}</span>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import Avatar from '@baserow/modules/core/components/Avatar'

export default {
  name: 'RowCardFieldPeople',
  functional: true,
  components: { Avatar },
  props: ['field', 'value'],
  render(h, { props }) {
    const { field, value } = props

    const getPersonDisplayName = (person) => {
      if (!person || !person.name) return ''

      if (field.show_email && person.email) {
        return `${person.name} (${person.email})`
      }
      return person.name
    }

    const getPersonInitials = (person) => {
      if (!person || !person.name) return '?'

      return person.name
        .split(' ')
        .map((word) => word.charAt(0))
        .join('')
        .toUpperCase()
        .substring(0, 2)
    }

    const displayValue = (() => {
      if (!value) return []
      return field.multiple_people
        ? Array.isArray(value)
          ? value
          : []
        : value.id
        ? [value]
        : []
    })()

    if (displayValue.length === 0) {
      return h('div', { class: 'row-card-field-people' })
    }

    return h(
      'div',
      {
        class: 'row-card-field-people',
      },
      displayValue
        .map((item) => {
          if (!item.id || !item.name) return null

          const children = []

          if (field.show_avatar) {
            children.push(
              h(
                'div',
                {
                  class: 'field-people__avatar',
                  attrs: { title: getPersonDisplayName(item) },
                },
                [
                  h(Avatar, {
                    props: {
                      initials: getPersonInitials(item),
                      name: item.name,
                      size: 'small',
                    },
                  }),
                ]
              )
            )
          }

          children.push(
            h(
              'div',
              {
                class: {
                  'field-people__name': true,
                  'field-people__name--no-avatar': !field.show_avatar,
                },
              },
              [
                h(
                  'span',
                  {
                    class: 'field-people__name-text',
                  },
                  getPersonDisplayName(item)
                ),
              ]
            )
          )

          return h(
            'div',
            {
              key: item.id,
              class: 'field-people__item',
            },
            children
          )
        })
        .filter(Boolean)
    )
  },
}
</script>

<style lang="scss" scoped>
.row-card-field-people {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
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
  padding: 2px 6px;
  background-color: #f3f4f6;
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
</style>
