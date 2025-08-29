export default (client) => {
  return {
    /**
     * Get sharing settings for a dashboard
     */
    getSharingSettings(dashboardId) {
      return client.get(`/dashboard/sharing/dashboards/${dashboardId}/sharing_settings/`)
    },

    /**
     * Create a public sharing link for a dashboard
     */
    createPublicLink(dashboardId) {
      return client.post(`/dashboard/sharing/dashboards/${dashboardId}/create_public_link/`)
    },

    /**
     * Create an embed link for a dashboard or specific widgets
     */
    createEmbedLink(dashboardId, widgetIds = null) {
      const payload = widgetIds ? { widget_ids: widgetIds } : {}
      return client.post(`/dashboard/sharing/dashboards/${dashboardId}/create_embed_link/`, payload)
    },

    /**
     * Revoke public access to a dashboard
     */
    revokePublicAccess(dashboardId) {
      return client.post(`/dashboard/sharing/dashboards/${dashboardId}/revoke_public_access/`)
    },

    /**
     * Get all permissions for a dashboard
     */
    getPermissions(dashboardId) {
      return client.get(`/dashboard/sharing/dashboards/${dashboardId}/permissions/`)
    },

    /**
     * Set specific permissions for a user on a dashboard
     */
    setPermission(dashboardId, userEmail, permissionType) {
      return client.post(`/dashboard/sharing/dashboards/${dashboardId}/set_permission/`, {
        user_email: userEmail,
        permission_type: permissionType
      })
    },

    /**
     * Remove specific permissions for a user on a dashboard
     */
    removePermission(dashboardId, userEmail) {
      return client.post(`/dashboard/sharing/dashboards/${dashboardId}/remove_permission/`, {
        user_email: userEmail
      })
    },

    /**
     * Get public dashboard data by token
     */
    getPublicDashboard(token) {
      return client.get(`/dashboard/sharing/public/${token}/`)
    },

    /**
     * Get embeddable dashboard data by token
     */
    getEmbedDashboard(token) {
      return client.get(`/dashboard/sharing/embed/${token}/`)
    },

    /**
     * Get embeddable widget data by token
     */
    getEmbedWidget(token) {
      return client.get(`/dashboard/sharing/embed/widget/${token}/`)
    }
  }
}