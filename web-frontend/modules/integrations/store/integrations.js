import IntegrationService from '@baserow/modules/integrations/services/integration'

export const state = () => ({
  providers: [],
  connections: [],
  syncs: [],
  loading: false,
  error: null,
})

export const mutations = {
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  SET_ERROR(state, error) {
    state.error = error
  },
  SET_PROVIDERS(state, providers) {
    state.providers = providers
  },
  SET_CONNECTIONS(state, connections) {
    state.connections = connections
  },
  SET_SYNCS(state, syncs) {
    state.syncs = syncs
  },
  ADD_CONNECTION(state, connection) {
    state.connections.push(connection)
  },
  UPDATE_CONNECTION(state, updatedConnection) {
    const index = state.connections.findIndex(c => c.id === updatedConnection.id)
    if (index !== -1) {
      state.connections.splice(index, 1, updatedConnection)
    }
  },
  REMOVE_CONNECTION(state, connectionId) {
    const index = state.connections.findIndex(c => c.id === connectionId)
    if (index !== -1) {
      state.connections.splice(index, 1)
    }
  },
  ADD_SYNC(state, sync) {
    state.syncs.push(sync)
  },
  UPDATE_SYNC(state, updatedSync) {
    const index = state.syncs.findIndex(s => s.id === updatedSync.id)
    if (index !== -1) {
      state.syncs.splice(index, 1, updatedSync)
    }
  },
  REMOVE_SYNC(state, syncId) {
    const index = state.syncs.findIndex(s => s.id === syncId)
    if (index !== -1) {
      state.syncs.splice(index, 1)
    }
  },
}

export const actions = {
  async fetchProviders({ commit }) {
    commit('SET_LOADING', true)
    try {
      const { data } = await IntegrationService(this.$client).getProviders()
      commit('SET_PROVIDERS', data.results)
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Failed to fetch providers')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchConnections({ commit }, workspaceId) {
    commit('SET_LOADING', true)
    try {
      const { data } = await IntegrationService(this.$client).getConnections(workspaceId)
      commit('SET_CONNECTIONS', data.results)
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Failed to fetch connections')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async startOAuthFlow({ commit }, { provider, workspaceId }) {
    try {
      const { data } = await IntegrationService(this.$client).startOAuth(provider, workspaceId)
      // Redirect to authorization URL
      window.location.href = data.authorization_url
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Failed to start OAuth flow')
      throw error
    }
  },

  async revokeConnection({ commit }, connectionId) {
    try {
      await IntegrationService(this.$client).revokeConnection(connectionId)
      commit('REMOVE_CONNECTION', connectionId)
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Failed to revoke connection')
      throw error
    }
  },

  async createSync({ commit }, { connectionId, syncConfig }) {
    try {
      const { data } = await IntegrationService(this.$client).createSync(connectionId, syncConfig)
      commit('ADD_SYNC', data)
      return data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Failed to create sync')
      throw error
    }
  },

  async triggerSync({ commit }, syncId) {
    try {
      await IntegrationService(this.$client).triggerSync(syncId)
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Failed to trigger sync')
      throw error
    }
  },

  updateConnectionStatus({ commit }, { connection_id, status }) {
    const connection = this.state.integrations.connections.find(c => c.id === connection_id)
    if (connection) {
      commit('UPDATE_CONNECTION', { ...connection, status })
    }
  },

  updateSyncStatus({ commit }, { sync_id, status, error_message }) {
    const sync = this.state.integrations.syncs.find(s => s.id === sync_id)
    if (sync) {
      commit('UPDATE_SYNC', { ...sync, last_sync_status: status, sync_error_message: error_message })
    }
  },
}

export const getters = {
  getProviderByName: (state) => (name) => {
    return state.providers.find(p => p.name === name)
  },
  getConnectionsByProvider: (state) => (providerName) => {
    return state.connections.filter(c => c.provider.name === providerName)
  },
  getSyncsByConnection: (state) => (connectionId) => {
    return state.syncs.filter(s => s.connection.id === connectionId)
  },
}