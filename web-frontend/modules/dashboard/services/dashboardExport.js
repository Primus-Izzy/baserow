export default (client) => {
  return {
    /**
     * Create a new export job for a dashboard
     */
    createExport(dashboardId, config) {
      return client.post(`/dashboard/exports/dashboards/${dashboardId}/create_export/`, config)
    },

    /**
     * Get all export jobs for a dashboard
     */
    getDashboardExports(dashboardId) {
      return client.get(`/dashboard/exports/dashboards/${dashboardId}/exports/`)
    },

    /**
     * Get all export jobs for the current user
     */
    getUserExports() {
      return client.get('/dashboard/exports/dashboards/my_exports/')
    },

    /**
     * Get status of a specific export job
     */
    getExportStatus(exportId) {
      return client.get(`/dashboard/exports/dashboards/status/?export_id=${exportId}`)
    },

    /**
     * Cancel a pending export job
     */
    cancelExport(exportId) {
      return client.post('/dashboard/exports/dashboards/cancel/', {
        export_id: exportId
      })
    },

    /**
     * Delete an export file
     */
    deleteExport(exportId) {
      return client.delete(`/dashboard/exports/dashboards/delete_export/?export_id=${exportId}`)
    },

    /**
     * Download an export file
     */
    downloadExport(exportId) {
      return client.get(`/dashboard/exports/dashboards/download/?export_id=${exportId}`, {
        responseType: 'blob'
      })
    },

    /**
     * Schedule recurring exports for a dashboard
     */
    scheduleExport(dashboardId, config) {
      return client.post(`/dashboard/exports/dashboards/${dashboardId}/schedule_export/`, config)
    },

    /**
     * Get download URL for an export
     */
    getDownloadUrl(exportId) {
      return `/api/dashboard/exports/dashboards/download/?export_id=${exportId}`
    }
  }
}