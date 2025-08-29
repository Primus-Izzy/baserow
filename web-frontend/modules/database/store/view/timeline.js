import bufferedRows from '@baserow/modules/database/store/view/bufferedRows'
import TimelineService from '@baserow/modules/database/services/view/timeline'
import { getRowMetadata } from '@baserow/modules/database/utils/row'

export function populateRow(row, metadata = {}) {
  row._ = {
    metadata: getRowMetadata(row, metadata),
    dragging: false,
  }
  return row
}

const timelineBufferedRows = bufferedRows({
  service: TimelineService,
  customPopulateRow: populateRow,
})

export const state = () => ({
  ...timelineBufferedRows.state(),
  dependencies: [],
  milestones: [],
  criticalPath: [],
  loading: false,
})

export const mutations = {
  ...timelineBufferedRows.mutations,
  SET_DEPENDENCIES(state, dependencies) {
    state.dependencies = dependencies
  },
  ADD_DEPENDENCY(state, dependency) {
    state.dependencies.push(dependency)
  },
  REMOVE_DEPENDENCY(state, dependencyId) {
    const index = state.dependencies.findIndex(dep => dep.id === dependencyId)
    if (index !== -1) {
      state.dependencies.splice(index, 1)
    }
  },
  SET_MILESTONES(state, milestones) {
    state.milestones = milestones
  },
  ADD_MILESTONE(state, milestone) {
    state.milestones.push(milestone)
  },
  REMOVE_MILESTONE(state, milestoneId) {
    const index = state.milestones.findIndex(milestone => milestone.id === milestoneId)
    if (index !== -1) {
      state.milestones.splice(index, 1)
    }
  },
  UPDATE_MILESTONE(state, { milestoneId, values }) {
    const milestone = state.milestones.find(m => m.id === milestoneId)
    if (milestone) {
      Object.assign(milestone, values)
    }
  },
  SET_CRITICAL_PATH(state, criticalPath) {
    state.criticalPath = criticalPath
  },
  SET_LOADING(state, loading) {
    state.loading = loading
  },
}

export const actions = {
  ...timelineBufferedRows.actions,
  async fetchInitial(
    { dispatch },
    { viewId, fields, adhocFiltering, adhocSorting }
  ) {
    const data = await dispatch('fetchInitialRows', {
      viewId,
      fields,
      initialRowArguments: { includeFieldOptions: true },
      adhocFiltering,
      adhocSorting,
    })
    await dispatch('forceUpdateAllFieldOptions', data.field_options)
    
    // Fetch timeline-specific data
    await dispatch('fetchDependencies', viewId)
    await dispatch('fetchMilestones', viewId)
  },

  async fetchDependencies({ commit }, viewId) {
    try {
      const { data } = await TimelineService.getDependencies(viewId)
      commit('SET_DEPENDENCIES', data)
    } catch (error) {
      console.error('Failed to fetch dependencies:', error)
    }
  },

  async fetchMilestones({ commit }, viewId) {
    try {
      const { data } = await TimelineService.getMilestones(viewId)
      commit('SET_MILESTONES', data)
    } catch (error) {
      console.error('Failed to fetch milestones:', error)
    }
  },

  async createDependency({ commit }, { viewId, predecessorRowId, successorRowId, dependencyType, lagDays = 0 }) {
    try {
      const { data } = await TimelineService.createDependency(viewId, {
        predecessor_row_id: predecessorRowId,
        successor_row_id: successorRowId,
        dependency_type: dependencyType,
        lag_days: lagDays,
      })
      commit('ADD_DEPENDENCY', data)
      return data
    } catch (error) {
      throw error
    }
  },

  async deleteDependency({ commit }, { viewId, dependencyId }) {
    try {
      await TimelineService.deleteDependency(viewId, dependencyId)
      commit('REMOVE_DEPENDENCY', dependencyId)
    } catch (error) {
      throw error
    }
  },

  async createMilestone({ commit }, { viewId, name, dateFieldId, rowId, color, icon, description }) {
    try {
      const { data } = await TimelineService.createMilestone(viewId, {
        name,
        date_field: dateFieldId,
        row_id: rowId,
        color,
        icon,
        description,
      })
      commit('ADD_MILESTONE', data)
      return data
    } catch (error) {
      throw error
    }
  },

  async deleteMilestone({ commit }, { viewId, milestoneId }) {
    try {
      await TimelineService.deleteMilestone(viewId, milestoneId)
      commit('REMOVE_MILESTONE', milestoneId)
    } catch (error) {
      throw error
    }
  },

  async updateMilestone({ commit }, { viewId, milestoneId, values }) {
    try {
      const { data } = await TimelineService.updateMilestone(viewId, milestoneId, values)
      commit('UPDATE_MILESTONE', { milestoneId, values: data })
      return data
    } catch (error) {
      throw error
    }
  },

  async recalculateSchedule({ commit }, { viewId, rowId, newStartDate, newEndDate }) {
    try {
      commit('SET_LOADING', true)
      const { data } = await TimelineService.recalculateSchedule(viewId, {
        row_id: rowId,
        new_start_date: newStartDate,
        new_end_date: newEndDate,
      })
      
      // The backend returns the list of updated row IDs
      // We might need to refresh the affected rows
      return data.updated_rows
    } catch (error) {
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchCriticalPath({ commit }, viewId) {
    try {
      const { data } = await TimelineService.getCriticalPath(viewId)
      commit('SET_CRITICAL_PATH', data)
      return data
    } catch (error) {
      console.error('Failed to fetch critical path:', error)
      return []
    }
  },
}

export const getters = {
  ...timelineBufferedRows.getters,
  getDependencies: (state) => state.dependencies,
  getMilestones: (state) => state.milestones,
  getCriticalPath: (state) => state.criticalPath,
  getLoading: (state) => state.loading,
  getDependenciesForRow: (state) => (rowId) => {
    return state.dependencies.filter(
      dep => dep.predecessor_row_id === rowId || dep.successor_row_id === rowId
    )
  },
  getMilestonesForRow: (state) => (rowId) => {
    return state.milestones.filter(milestone => milestone.row_id === rowId)
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}