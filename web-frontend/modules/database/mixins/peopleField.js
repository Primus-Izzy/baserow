import selectDropdown from '@baserow/modules/database/mixins/selectDropdown'
import availableCollaborators from '@baserow/modules/database/mixins/availableCollaborators'

export default {
  mixins: [selectDropdown, availableCollaborators],
  methods: {
    /**
     * Removes the provided ID from the current values list and emits an update
     * event with the new values list.
     */
    removeValue(event, currentValues, itemIdToRemove) {
      if (this.field.multiple_people) {
        const vals = currentValues.filter((item) => item.id !== itemIdToRemove)
        this.$emit('update', vals, currentValues)
      } else {
        // For single people field, clear the value
        this.$emit('update', null, currentValues)
      }
    },
    
    /**
     * Checks if the new value is valid for the field and if
     * so will add it to a new values list. If this new list of values is unequal
     * to the old list of values an update event will be emitted which will result
     * in an API call in order to persist the new value to the field.
     */
    updateValue(newId, oldValue) {
      const workspaceUser =
        this.workspaceCollaborators.find(
          (workspaceUser) => workspaceUser.id === newId
        ) || null

      let newOption = null
      if (workspaceUser) {
        newOption = {
          id: workspaceUser.id,
          name: workspaceUser.name,
        }
      }

      let newValue
      if (this.field.multiple_people) {
        if (!oldValue) {
          oldValue = []
        }
        newValue = [...oldValue]
        if (newOption && !newValue.find(item => item.id === newOption.id)) {
          newValue.push(newOption)
        }
      } else {
        // For single people field, replace the value
        newValue = newOption
      }

      if (JSON.stringify(newValue) !== JSON.stringify(oldValue)) {
        this.$emit('update', newValue, oldValue)
      }
    },
    
    /**
     * Get display name for a person based on field configuration
     */
    getPersonDisplayName(person) {
      if (!person || !person.name) return ''
      
      if (this.field.show_email && person.email) {
        return `${person.name} (${person.email})`
      }
      return person.name
    },
    
    /**
     * Get initials for a person's avatar
     */
    getPersonInitials(person) {
      if (!person || !person.name) return '?'
      
      return person.name
        .split(' ')
        .map(word => word.charAt(0))
        .join('')
        .toUpperCase()
        .substring(0, 2)
    }
  },
}