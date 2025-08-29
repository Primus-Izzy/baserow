import CalendarService from '@baserow/modules/database/services/view/calendar'
import { clone } from '@baserow/modules/core/utils/object'

export const state = () => ({
  viewId: null,
  events: [],
  loading: false,
  fieldOptions: {},
  lastFetchedRange: {
    startDate: null,
    endDate: null,
  },
})

export const mutations = {
  SET_VIEW_ID(state, viewId) {
    state.viewId = viewId
  },
  
  SET_EVENTS(state, events) {
    state.events = events
  },
  
  ADD_EVENT(state, event) {
    const existingIndex = state.events.findIndex(e => e.id === event.id)
    if (existingIndex !== -1) {
      state.events.splice(existingIndex, 1, event)
    } else {
      state.events.push(event)
    }
  },
  
  UPDATE_EVENT(state, event) {
    const index = state.events.findIndex(e => e.id === event.id)
    if (index !== -1) {
      state.events.splice(index, 1, event)
    }
  },
  
  REMOVE_EVENT(state, eventId) {
    const index = state.events.findIndex(e => e.id === eventId)
    if (index !== -1) {
      state.events.splice(index, 1)
    }
  },
  
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  
  SET_FIELD_OPTIONS(state, fieldOptions) {
    state.fieldOptions = fieldOptions
  },
  
  UPDATE_FIELD_OPTIONS(state, { fieldId, options }) {
    state.fieldOptions = {
      ...state.fieldOptions,
      [fieldId]: options,
    }
  },
  
  SET_LAST_FETCHED_RANGE(state, { startDate, endDate }) {
    state.lastFetchedRange = { startDate, endDate }
  },
  
  CLEAR_EVENTS(state) {
    state.events = []
  },
}

export const actions = {
  /**
   * Sets the view ID for the calendar store.
   */
  setViewId({ commit }, { viewId }) {
    commit('SET_VIEW_ID', viewId)
  },

  /**
   * Fetches events for the calendar view within a date range.
   */
  async fetchEvents(
    { commit, state, rootGetters },
    { viewId, startDate, endDate, includeRecurring = true }
  ) {
    commit('SET_LOADING', true)
    
    try {
      const isPublic = rootGetters['view/public/getIsPublic']
      const publicAuthToken = isPublic ? rootGetters['view/public/getAuthToken'] : null
      
      const response = await CalendarService.fetchEvents(
        viewId,
        startDate,
        endDate,
        includeRecurring,
        null,
        publicAuthToken
      )
      
      commit('SET_EVENTS', response.events || [])
      commit('SET_LAST_FETCHED_RANGE', { startDate, endDate })
      
      if (response.field_options) {
        commit('SET_FIELD_OPTIONS', response.field_options)
      }
    } catch (error) {
      commit('SET_EVENTS', [])
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  /**
   * Moves an event to a new date.
   */
  async moveEvent(
    { commit, rootGetters },
    { viewId, rowId, newDate, updateEndDate = false }
  ) {
    try {
      const isPublic = rootGetters['view/public/getIsPublic']
      const publicAuthToken = isPublic ? rootGetters['view/public/getAuthToken'] : null
      
      await CalendarService.moveEvent(
        viewId,
        rowId,
        newDate,
        updateEndDate,
        null,
        publicAuthToken
      )
      
      // Update the event in the store
      const event = state.events.find(e => e.id === rowId)
      if (event) {
        const updatedEvent = { ...event, date: newDate }
        commit('UPDATE_EVENT', updatedEvent)
      }
    } catch (error) {
      throw error
    }
  },

  /**
   * Creates a recurring pattern for an event.
   */
  async createRecurringPattern(
    { rootGetters },
    { viewId, patternData }
  ) {
    try {
      const isPublic = rootGetters['view/public/getIsPublic']
      const publicAuthToken = isPublic ? rootGetters['view/public/getAuthToken'] : null
      
      const response = await CalendarService.createRecurringPattern(
        viewId,
        patternData,
        null,
        publicAuthToken
      )
      
      return response
    } catch (error) {
      throw error
    }
  },

  /**
   * Updates a recurring pattern.
   */
  async updateRecurringPattern(
    { rootGetters },
    { viewId, patternId, patternData }
  ) {
    try {
      const isPublic = rootGetters['view/public/getIsPublic']
      const publicAuthToken = isPublic ? rootGetters['view/public/getAuthToken'] : null
      
      const response = await CalendarService.updateRecurringPattern(
        viewId,
        patternId,
        patternData,
        null,
        publicAuthToken
      )
      
      return response
    } catch (error) {
      throw error
    }
  },

  /**
   * Deletes a recurring pattern.
   */
  async deleteRecurringPattern(
    { rootGetters },
    { viewId, patternId }
  ) {
    try {
      const isPublic = rootGetters['view/public/getIsPublic']
      const publicAuthToken = isPublic ? rootGetters['view/public/getAuthToken'] : null
      
      await CalendarService.deleteRecurringPattern(
        viewId,
        patternId,
        null,
        publicAuthToken
      )
    } catch (error) {
      throw error
    }
  },

  /**
   * Updates field options for the calendar view.
   */
  async updateFieldOptions(
    { commit, rootGetters },
    { fieldId, values }
  ) {
    try {
      commit('UPDATE_FIELD_OPTIONS', { fieldId, options: values })
    } catch (error) {
      throw error
    }
  },

  /**
   * Forces update of all field options.
   */
  forceUpdateAllFieldOptions({ commit }, fieldOptions) {
    commit('SET_FIELD_OPTIONS', fieldOptions)
  },

  /**
   * Adds a field to the calendar view.
   */
  addField({ commit, state }, { field, value }) {
    // Add default field options
    const defaultOptions = {
      hidden: false,
      show_in_event: false,
      event_display_style: 'text',
    }
    
    commit('UPDATE_FIELD_OPTIONS', { 
      fieldId: field.id, 
      options: defaultOptions 
    })
  },

  /**
   * Removes field options when a field is deleted.
   */
  forceDeleteFieldOptions({ commit, state }, fieldId) {
    const newFieldOptions = { ...state.fieldOptions }
    delete newFieldOptions[fieldId]
    commit('SET_FIELD_OPTIONS', newFieldOptions)
  },

  /**
   * Handles when a new row is created.
   */
  afterNewRowCreated({ commit, state }, { view, fields, values }) {
    // If the new row has a date that falls within our current range, add it
    const dateField = fields.find(f => f.id === view.date_field)
    if (dateField && values[`field_${dateField.id}`]) {
      const eventDate = new Date(values[`field_${dateField.id}`])
      const { startDate, endDate } = state.lastFetchedRange
      
      if (startDate && endDate) {
        const rangeStart = new Date(startDate)
        const rangeEnd = new Date(endDate)
        
        if (eventDate >= rangeStart && eventDate <= rangeEnd) {
          const event = {
            id: values.id,
            date: values[`field_${dateField.id}`],
            ...values,
          }
          commit('ADD_EVENT', event)
        }
      }
    }
  },

  /**
   * Handles when an existing row is updated.
   */
  afterExistingRowUpdated({ commit, state }, { view, fields, row, values }) {
    const event = state.events.find(e => e.id === row.id)
    if (event) {
      const updatedEvent = { ...event, ...values }
      commit('UPDATE_EVENT', updatedEvent)
    }
  },

  /**
   * Handles when an existing row is deleted.
   */
  afterExistingRowDeleted({ commit }, { view, fields, row }) {
    commit('REMOVE_EVENT', row.id)
  },

  /**
   * Clears all events from the store.
   */
  clearEvents({ commit }) {
    commit('CLEAR_EVENTS')
  },
}

export const getters = {
  getViewId(state) {
    return state.viewId
  },
  
  getEvents(state) {
    return state.events
  },
  
  getLoading(state) {
    return state.loading
  },
  
  getFieldOptions: (state) => (field) => {
    return state.fieldOptions[field.id] || {
      hidden: false,
      show_in_event: false,
      event_display_style: 'text',
    }
  },
  
  getAllFieldOptions(state) {
    return state.fieldOptions
  },
  
  getLastFetchedRange(state) {
    return state.lastFetchedRange
  },
  
  getEventsForDate: (state) => (date) => {
    const dateStr = date.toISOString().split('T')[0]
    return state.events.filter(event => {
      if (!event.date) return false
      const eventDate = new Date(event.date).toISOString().split('T')[0]
      return eventDate === dateStr
    })
  },
  
  getEventsInRange: (state) => (startDate, endDate) => {
    return state.events.filter(event => {
      if (!event.date) return false
      const eventDate = new Date(event.date)
      return eventDate >= startDate && eventDate <= endDate
    })
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}