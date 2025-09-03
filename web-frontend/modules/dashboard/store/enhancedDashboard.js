export const state = () => ({
  // Enhanced widgets
  kpiWidgets: {},
  enhancedChartWidgets: {},
  
  // Dashboard layout
  dashboardLayouts: {},
  currentLayout: null,
  
  // Widget data cache
  widgetDataCache: {},
  
  // Loading states
  widgetLoadingStates: {},
  layoutLoadingStates: {},
  
  // Real-time subscriptions
  activeSubscriptions: {},
  
  // Performance metrics
  performanceMetrics: {},
})

export const getters = {
  // KPI Widgets
  getKPIWidget: (state) => (widgetId) => {
    return state.kpiWidgets[widgetId]
  },
  
  getKPIWidgetsByDashboard: (state) => (dashboardId) => {
    return Object.values(state.kpiWidgets).filter(
      widget => widget.dashboard === dashboardId
    )
  },
  
  // Enhanced Chart Widgets
  getEnhancedChartWidget: (state) => (widgetId) => {
    return state.enhancedChartWidgets[widgetId]
  },
  
  getEnhancedChartWidgetsByDashboard: (state) => (dashboardId) => {
    return Object.values(state.enhancedChartWidgets).filter(
      widget => widget.dashboard === dashboardId
    )
  },
  
  // Dashboard Layout
  getDashboardLayout: (state) => (dashboardId) => {
    return state.dashboardLayouts[dashboardId]
  },
  
  getCurrentLayout: (state) => {
    return state.currentLayout
  },
  
  // Widget Data
  getWidgetData: (state) => (widgetId) => {
    return state.widgetDataCache[widgetId]
  },
  
  // Loading States
  isWidgetLoading: (state) => (widgetId) => {
    return state.widgetLoadingStates[widgetId] || false
  },
  
  isLayoutLoading: (state) => (dashboardId) => {
    return state.layoutLoadingStates[dashboardId] || false
  },
  
  // Performance
  getWidgetPerformanceMetrics: (state) => (widgetId) => {
    return state.performanceMetrics[widgetId]
  },
  
  // All enhanced widgets for a dashboard
  getAllEnhancedWidgets: (state, getters) => (dashboardId) => {
    const kpiWidgets = getters.getKPIWidgetsByDashboard(dashboardId)
    const chartWidgets = getters.getEnhancedChartWidgetsByDashboard(dashboardId)
    
    return [...kpiWidgets, ...chartWidgets]
  },
}

export const mutations = {
  // KPI Widgets
  SET_KPI_WIDGET(state, widget) {
    state.kpiWidgets = {
      ...state.kpiWidgets,
      [widget.id]: widget,
    }
  },
  
  UPDATE_KPI_WIDGET(state, { widgetId, updates }) {
    if (state.kpiWidgets[widgetId]) {
      state.kpiWidgets[widgetId] = {
        ...state.kpiWidgets[widgetId],
        ...updates,
      }
    }
  },
  
  DELETE_KPI_WIDGET(state, widgetId) {
    const { [widgetId]: deleted, ...rest } = state.kpiWidgets
    state.kpiWidgets = rest
  },
  
  // Enhanced Chart Widgets
  SET_ENHANCED_CHART_WIDGET(state, widget) {
    state.enhancedChartWidgets = {
      ...state.enhancedChartWidgets,
      [widget.id]: widget,
    }
  },
  
  UPDATE_ENHANCED_CHART_WIDGET(state, { widgetId, updates }) {
    if (state.enhancedChartWidgets[widgetId]) {
      state.enhancedChartWidgets[widgetId] = {
        ...state.enhancedChartWidgets[widgetId],
        ...updates,
      }
    }
  },
  
  DELETE_ENHANCED_CHART_WIDGET(state, widgetId) {
    const { [widgetId]: deleted, ...rest } = state.enhancedChartWidgets
    state.enhancedChartWidgets = rest
  },
  
  // Dashboard Layout
  SET_DASHBOARD_LAYOUT(state, { dashboardId, layout }) {
    state.dashboardLayouts = {
      ...state.dashboardLayouts,
      [dashboardId]: layout,
    }
  },
  
  SET_CURRENT_LAYOUT(state, layout) {
    state.currentLayout = layout
  },
  
  UPDATE_DASHBOARD_LAYOUT(state, { dashboardId, updates }) {
    if (state.dashboardLayouts[dashboardId]) {
      state.dashboardLayouts[dashboardId] = {
        ...state.dashboardLayouts[dashboardId],
        ...updates,
      }
    }
  },
  
  // Widget Data Cache
  SET_WIDGET_DATA(state, { widgetId, data }) {
    state.widgetDataCache = {
      ...state.widgetDataCache,
      [widgetId]: data,
    }
  },
  
  CLEAR_WIDGET_DATA(state, widgetId) {
    const { [widgetId]: deleted, ...rest } = state.widgetDataCache
    state.widgetDataCache = rest
  },
  
  // Loading States
  SET_WIDGET_LOADING(state, { widgetId, loading }) {
    state.widgetLoadingStates = {
      ...state.widgetLoadingStates,
      [widgetId]: loading,
    }
  },
  
  SET_LAYOUT_LOADING(state, { dashboardId, loading }) {
    state.layoutLoadingStates = {
      ...state.layoutLoadingStates,
      [dashboardId]: loading,
    }
  },
  
  // Subscriptions
  SET_SUBSCRIPTION(state, { widgetId, subscription }) {
    state.activeSubscriptions = {
      ...state.activeSubscriptions,
      [widgetId]: subscription,
    }
  },
  
  REMOVE_SUBSCRIPTION(state, widgetId) {
    const { [widgetId]: deleted, ...rest } = state.activeSubscriptions
    state.activeSubscriptions = rest
  },
  
  // Performance Metrics
  SET_PERFORMANCE_METRICS(state, { widgetId, metrics }) {
    state.performanceMetrics = {
      ...state.performanceMetrics,
      [widgetId]: metrics,
    }
  },
}

export const actions = {
  // KPI Widget Actions
  async createKPIWidget({ commit }, { dashboardId, values }) {
    try {
      const { data } = await this.$axios.post('/api/dashboard/enhanced/kpi-widgets/', {
        dashboard: dashboardId,
        ...values,
      })
      
      commit('SET_KPI_WIDGET', data)
      return data
    } catch (error) {
      throw error
    }
  },
  
  async updateKPIWidget({ commit }, { widgetId, values }) {
    try {
      const { data } = await this.$axios.patch(
        `/api/dashboard/enhanced/kpi-widgets/${widgetId}/`,
        values
      )
      
      commit('UPDATE_KPI_WIDGET', { widgetId, updates: data })
      return data
    } catch (error) {
      throw error
    }
  },
  
  async deleteKPIWidget({ commit }, widgetId) {
    try {
      await this.$axios.delete(`/api/dashboard/enhanced/kpi-widgets/${widgetId}/`)
      commit('DELETE_KPI_WIDGET', widgetId)
      commit('CLEAR_WIDGET_DATA', widgetId)
    } catch (error) {
      throw error
    }
  },
  
  async fetchKPIWidgetData({ commit }, widgetId) {
    commit('SET_WIDGET_LOADING', { widgetId, loading: true })
    
    try {
      const { data } = await this.$axios.get(
        `/api/dashboard/enhanced/kpi-widgets/${widgetId}/data/`
      )
      
      commit('SET_WIDGET_DATA', { widgetId, data })
      return data
    } catch (error) {
      throw error
    } finally {
      commit('SET_WIDGET_LOADING', { widgetId, loading: false })
    }
  },
  
  // Enhanced Chart Widget Actions
  async createEnhancedChartWidget({ commit }, { dashboardId, values }) {
    try {
      const { data } = await this.$axios.post('/api/dashboard/enhanced/enhanced-chart-widgets/', {
        dashboard: dashboardId,
        ...values,
      })
      
      commit('SET_ENHANCED_CHART_WIDGET', data)
      return data
    } catch (error) {
      throw error
    }
  },
  
  async updateEnhancedChartWidget({ commit }, { widgetId, values }) {
    try {
      const { data } = await this.$axios.patch(
        `/api/dashboard/enhanced/enhanced-chart-widgets/${widgetId}/`,
        values
      )
      
      commit('UPDATE_ENHANCED_CHART_WIDGET', { widgetId, updates: data })
      return data
    } catch (error) {
      throw error
    }
  },
  
  async deleteEnhancedChartWidget({ commit }, widgetId) {
    try {
      await this.$axios.delete(`/api/dashboard/enhanced/enhanced-chart-widgets/${widgetId}/`)
      commit('DELETE_ENHANCED_CHART_WIDGET', widgetId)
      commit('CLEAR_WIDGET_DATA', widgetId)
    } catch (error) {
      throw error
    }
  },
  
  async fetchEnhancedChartWidgetData({ commit }, widgetId) {
    commit('SET_WIDGET_LOADING', { widgetId, loading: true })
    
    try {
      const { data } = await this.$axios.get(
        `/api/dashboard/enhanced/enhanced-chart-widgets/${widgetId}/data/`
      )
      
      commit('SET_WIDGET_DATA', { widgetId, data })
      return data
    } catch (error) {
      throw error
    } finally {
      commit('SET_WIDGET_LOADING', { widgetId, loading: false })
    }
  },
  
  // Dashboard Layout Actions
  async fetchDashboardLayout({ commit }, dashboardId) {
    commit('SET_LAYOUT_LOADING', { dashboardId, loading: true })
    
    try {
      const { data } = await this.$axios.get(
        `/api/dashboard/enhanced/dashboard/${dashboardId}/layout/`
      )
      
      commit('SET_DASHBOARD_LAYOUT', { dashboardId, layout: data })
      commit('SET_CURRENT_LAYOUT', data)
      return data
    } catch (error) {
      throw error
    } finally {
      commit('SET_LAYOUT_LOADING', { dashboardId, loading: false })
    }
  },
  
  async updateDashboardLayout({ commit }, { dashboardId, layoutData }) {
    try {
      const { data } = await this.$axios.post(
        `/api/dashboard/enhanced/dashboard/${dashboardId}/layout/`,
        { layout_data: layoutData }
      )
      
      commit('UPDATE_DASHBOARD_LAYOUT', { dashboardId, updates: data })
      return data
    } catch (error) {
      throw error
    }
  },
  
  // Batch Operations
  async batchRefreshWidgets({ dispatch }, widgetIds) {
    const promises = widgetIds.map(widgetId => {
      // Determine widget type and call appropriate refresh action
      return dispatch('refreshWidget', widgetId)
    })
    
    return Promise.all(promises)
  },
  
  async refreshWidget({ state, dispatch }, widgetId) {
    // Determine widget type and call appropriate refresh method
    if (state.kpiWidgets[widgetId]) {
      return dispatch('fetchKPIWidgetData', widgetId)
    } else if (state.enhancedChartWidgets[widgetId]) {
      return dispatch('fetchEnhancedChartWidgetData', widgetId)
    }
  },
  
  // Real-time Subscriptions
  subscribeToWidgetUpdates({ commit }, { widgetId, callback }) {
    // This would integrate with WebSocket connections
    const subscription = {
      unsubscribe: () => {
        commit('REMOVE_SUBSCRIPTION', widgetId)
      },
    }
    
    commit('SET_SUBSCRIPTION', { widgetId, subscription })
    return subscription
  },
  
  unsubscribeFromWidgetUpdates({ commit, state }, widgetId) {
    const subscription = state.activeSubscriptions[widgetId]
    if (subscription) {
      subscription.unsubscribe()
      commit('REMOVE_SUBSCRIPTION', widgetId)
    }
  },
  
  // Performance Metrics
  async fetchWidgetPerformanceMetrics({ commit }, { widgetId, timeRange = '24h' }) {
    try {
      const { data } = await this.$axios.get(
        `/api/dashboard/enhanced/widget/${widgetId}/metrics/`,
        { params: { time_range: timeRange } }
      )
      
      commit('SET_PERFORMANCE_METRICS', { widgetId, metrics: data })
      return data
    } catch (error) {
      throw error
    }
  },
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions,
}