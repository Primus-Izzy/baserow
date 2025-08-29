export default (client) => {
  return {
    getProviders() {
      return client.get('/integrations/providers/')
    },
    
    getConnections(workspaceId) {
      return client.get(`/integrations/workspaces/${workspaceId}/connections/`)
    },
    
    startOAuth(provider, workspaceId, state = null) {
      return client.post('/integrations/connections/authorize/', {
        provider,
        workspace_id: workspaceId,
        state,
      })
    },
    
    revokeConnection(connectionId) {
      return client.post(`/integrations/connections/${connectionId}/revoke/`)
    },
    
    refreshToken(connectionId) {
      return client.post(`/integrations/connections/${connectionId}/refresh_token/`)
    },
    
    getSyncs(connectionId) {
      return client.get(`/integrations/connections/${connectionId}/syncs/`)
    },
    
    createSync(connectionId, syncConfig) {
      return client.post(`/integrations/connections/${connectionId}/syncs/`, syncConfig)
    },
    
    updateSync(syncId, syncConfig) {
      return client.patch(`/integrations/syncs/${syncId}/`, syncConfig)
    },
    
    deleteSync(syncId) {
      return client.delete(`/integrations/syncs/${syncId}/`)
    },
    
    triggerSync(syncId) {
      return client.post(`/integrations/syncs/${syncId}/trigger_sync/`)
    },
    
    toggleSyncActive(syncId) {
      return client.post(`/integrations/syncs/${syncId}/toggle_active/`)
    },
    
    // Google-specific methods
    getGoogleCalendars(connectionId) {
      return client.get(`/integrations/connections/${connectionId}/google/calendars/`)
    },
    
    getGoogleDriveFiles(connectionId, folderId = null) {
      const params = folderId ? { folder_id: folderId } : {}
      return client.get(`/integrations/connections/${connectionId}/google/drive/files/`, { params })
    },
    
    // Microsoft-specific methods
    getOutlookCalendars(connectionId) {
      return client.get(`/integrations/connections/${connectionId}/microsoft/calendars/`)
    },
    
    getOneDriveFiles(connectionId, folderId = null) {
      const params = folderId ? { folder_id: folderId } : {}
      return client.get(`/integrations/connections/${connectionId}/microsoft/onedrive/files/`, { params })
    },
    
    // Slack-specific methods
    getSlackChannels(connectionId) {
      return client.get(`/integrations/connections/${connectionId}/slack/channels/`)
    },
    
    sendSlackMessage(connectionId, channel, message) {
      return client.post(`/integrations/connections/${connectionId}/slack/send_message/`, {
        channel,
        message,
      })
    },
    
    // Dropbox-specific methods
    getDropboxFiles(connectionId, folderPath = '') {
      return client.get(`/integrations/connections/${connectionId}/dropbox/files/`, {
        params: { folder_path: folderPath },
      })
    },
    
    // Microsoft Teams-specific methods
    getMicrosoftTeams(connectionId) {
      return client.get(`/integrations/microsoft/${connectionId}/teams/`)
    },
    
    getTeamsChannels(connectionId, teamId) {
      return client.get(`/integrations/microsoft/${connectionId}/teams/${teamId}/channels/`)
    },
    
    sendTeamsMessage(connectionId, teamId, channelId, message) {
      return client.post(`/integrations/microsoft/${connectionId}/teams/${teamId}/channels/${channelId}/message/`, {
        message,
      })
    },
    
    // Email-specific methods
    sendEmail(connectionId, emailData) {
      return client.post(`/integrations/connections/${connectionId}/send_email/`, emailData)
    },
    
    validateEmailConnection(connectionId) {
      return client.post(`/integrations/connections/${connectionId}/validate_email/`)
    },
  }
}