<template>
  <div class="grid-view__cell grid-field-people__cell">
    <div class="grid-field-people__list">
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
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import Avatar from '@baserow/modules/core/components/Avatar'

export default {
  name: 'FunctionalGridViewFieldPeople',
  functional: true,
  components: { Avatar },
  props: ['field', 'value'],
  render(h, { props, injections }) {
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
        .map(word => word.charAt(0))
        .join('')
        .toUpperCase()
        .substring(0, 2)
    }
    
    const displayValue = (() => {
      if (!value) return []
      return field.multiple_people 
        ? (Array.isArray(value) ? value : [])
        : (value.id ? [value] : [])
    })()

    return h('div', {
      class: 'grid-view__cell grid-field-people__cell'
    }, [
      h('div', {
        class: 'grid-field-people__list'
      }, displayValue.map(item => {
        if (!item.id || !item.name) return null
        
        const children = []
        
        if (field.show_avatar) {
          children.push(h('div', {
            class: 'field-people__avatar',
            attrs: { title: getPersonDisplayName(item) }
          }, [
            h(Avatar, {
              props: {
                initials: getPersonInitials(item),
                name: item.name,
                size: 'small'
              }
            })
          ]))
        }
        
        children.push(h('div', {
          class: {
            'field-people__name': true,
            'background-color--light-gray': true,
            'field-people__name--no-avatar': !field.show_avatar
          }
        }, [
          h('span', {
            class: 'field-people__name-text'
          }, getPersonDisplayName(item))
        ]))
        
        return h('div', {
          key: item.id,
          class: 'field-people__item'
        }, children)
      }).filter(Boolean))
    ])
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
</style>