export default (client) => {
  return {
    // KPI Widget services
    createKPIWidget(dashboardId, values) {
      return client.post(`/dashboard/enhanced/kpi-widgets/`, {
        dashboard: dashboardId,
        ...values,
      })
    },

    updateKPIWidget(widgetId, values) {
      return client.patch(`/dashboard/enhanced/kpi-widgets/${widgetId}/`, values)
    },

    deleteKPIWidget(widgetId) {
      return client.delete(`/dashboard/enhanced/kpi-widgets/${widgetId}/`)
    },

    getKPIWidgetData(widgetId) {
      return client.get(`/dashboard/enhanced/kpi-widgets/${widgetId}/data/`)
    },

    refreshKPIWidget(widgetId) {
      return client.post(`/dashboard/enhanced/kpi-widgets/${widgetId}/refresh/`)
    },

    // Enhanced Chart Widget services
    createEnhancedChartWidget(dashboardId, values) {
      return client.post(`/dashboard/enhanced/enhanced-chart-widgets/`, {
        dashboard: dashboardId,
        ...values,
      })
    },

    updateEnhancedChartWidget(widgetId, values) {
      return client.patch(`/dashboard/enhanced/enhanced-chart-widgets/${widgetId}/`, values)
    },

    deleteEnhancedChartWidget(widgetId) {
      return client.delete(`/dashboard/enhanced/enhanced-chart-widgets/${widgetId}/`)
    },

    getEnhancedChartWidgetData(widgetId) {
      return client.get(`/dashboard/enhanced/enhanced-chart-widgets/${widgetId}/data/`)
    },

    refreshEnhancedChartWidget(widgetId) {
      return client.post(`/dashboard/enhanced/enhanced-chart-widgets/${widgetId}/refresh/`)
    },

    // Dashboard Layout services
    getDashboardLayout(dashboardId) {
      return client.get(`/dashboard/enhanced/dashboard/${dashboardId}/layout/`)
    },

    updateDashboardLayout(dashboardId, layoutData) {
      return client.post(`/dashboard/enhanced/dashboard/${dashboardId}/layout/`, {
        layout_data: layoutData,
      })
    },

    getDashboardLayouts(params = {}) {
      return client.get('/dashboard/enhanced/dashboard-layouts/', { params })
    },

    createDashboardLayout(values) {
      return client.post('/dashboard/enhanced/dashboard-layouts/', values)
    },

    updateDashboardLayoutConfig(layoutId, values) {
      return client.patch(`/dashboard/enhanced/dashboard-layouts/${layoutId}/`, values)
    },

    deleteDashboardLayout(layoutId) {
      return client.delete(`/dashboard/enhanced/dashboard-layouts/${layoutId}/`)
    },

    // Widget Data Aggregation services
    triggerWidgetAggregation(widgetId) {
      return client.post(`/dashboard/enhanced/widget/${widgetId}/aggregation/`)
    },

    clearWidgetAggregation(widgetId) {
      return client.delete(`/dashboard/enhanced/widget/${widgetId}/aggregation/`)
    },

    // Batch operations
    batchUpdateWidgets(updates) {
      return client.post('/dashboard/enhanced/widgets/batch-update/', {
        updates,
      })
    },

    batchRefreshWidgets(widgetIds) {
      return client.post('/dashboard/enhanced/widgets/batch-refresh/', {
        widget_ids: widgetIds,
      })
    },

    // Multi-data source operations
    getMultiDataSourceData(dataSourceIds) {
      return client.post('/dashboard/enhanced/data-sources/multi-fetch/', {
        data_source_ids: dataSourceIds,
      })
    },

    // Real-time data subscriptions
    subscribeToWidgetUpdates(widgetId, callback) {
      // This would integrate with WebSocket connections
      // For now, return a placeholder subscription object
      return {
        unsubscribe: () => {
          // Cleanup subscription
        },
      }
    },

    // Export and sharing
    exportDashboard(dashboardId, format = 'pdf') {
      return client.get(`/dashboard/enhanced/dashboard/${dashboardId}/export/`, {
        params: { format },
        responseType: 'blob',
      })
    },

    generatePublicDashboardLink(dashboardId, options = {}) {
      return client.post(`/dashboard/enhanced/dashboard/${dashboardId}/public-link/`, options)
    },

    getPublicDashboardData(publicToken) {
      return client.get(`/dashboard/enhanced/public/${publicToken}/`)
    },

    // Widget templates
    getWidgetTemplates(widgetType = null) {
      const params = widgetType ? { widget_type: widgetType } : {}
      return client.get('/dashboard/enhanced/widget-templates/', { params })
    },

    createWidgetFromTemplate(templateId, dashboardId, customizations = {}) {
      return client.post('/dashboard/enhanced/widget-templates/create/', {
        template_id: templateId,
        dashboard_id: dashboardId,
        customizations,
      })
    },

    // Performance and analytics
    getWidgetPerformanceMetrics(widgetId, timeRange = '24h') {
      return client.get(`/dashboard/enhanced/widget/${widgetId}/metrics/`, {
        params: { time_range: timeRange },
      })
    },

    getDashboardAnalytics(dashboardId, timeRange = '7d') {
      return client.get(`/dashboard/enhanced/dashboard/${dashboardId}/analytics/`, {
        params: { time_range: timeRange },
      })
    },
  }
}