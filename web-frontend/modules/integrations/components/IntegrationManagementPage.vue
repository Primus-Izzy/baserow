<template>
  <div class="integration-management-page">
    <div class="integration-management-page__header">
      <h1>Integrations</h1>
      <p>Connect Baserow with your favorite tools and services</p>
    </div>

    <div class="integration-management-page__content">
      <!-- Available Providers -->
      <div class="integration-section">
        <h2>Available Integrations</h2>
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <span>Loading integrations...</span>
        </div>
        <div v-else class="provider-grid">
          <IntegrationProviderCard
            v-for="provider in providers"
            :key="provider.id"
            :provider="provider"
            :connection="getConnectionForProvider(provider)"
            :workspace-id="workspaceId"
            @connection-revoked="refreshConnections"
          />
        </div>
      </div>

      <!-- Active Syncs -->
      <div v-if="connections.length > 0" class="integration-section">
        <div class="section-header">
          <h2>Active Syncs</h2>
          <Button
            type="primary"
            icon="fas fa-plus"
            @click="showCreateSyncModal = true"
          >
            Create Sync
          </Button>
        </div>

        <div v-if="syncs.length === 0" class="empty-state">
          <i class="fas fa-sync-alt"></i>
          <h3>No syncs configured</h3>
          <p>Create your first sync to start connecting your data</p>
          <Button type="primary" @click="showCreateSyncModal = true">
            Create Sync
          </Button>
        </div>

        <div v-else class="syncs-table">
          <table>
            <thead>
              <tr>
                <th>Sync Type</th>
                <th>Provider</th>
                <th>Table</th>
                <th>External Resource</th>
                <th>Direction</th>
                <th>Status</th>
                <th>Last Sync</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="sync in syncs" :key="sync.id">
                <td>
                  <div class="sync-type">
                    <i :class="getSyncTypeIcon(sync.sync_type)"></i>
                    {{ getSyncTypeLabel(sync.sync_type) }}
                  </div>
                </td>
                <td>
                  <div class="provider-info">
                    <img
                      v-if="sync.connection.provider.icon_url"
                      :src="sync.connection.provider.icon_url"
                      :alt="sync.connection.provider.display_name"
                      class="provider-icon"
                    />
                    {{ sync.connection.provider.display_name }}
                  </div>
                </td>
                <td>{{ sync.table.name }}</td>
                <td>
                  {{ sync.external_resource_name || sync.external_resource_id }}
                </td>
                <td>
                  <Badge :color="getSyncDirectionColor(sync.sync_direction)">
                    {{ getSyncDirectionLabel(sync.sync_direction) }}
                  </Badge>
                </td>
                <td>
                  <div class="sync-status">
                    <Badge :color="getSyncStatusColor(sync.last_sync_status)">
                      {{ sync.last_sync_status }}
                    </Badge>
                    <SwitchInput
                      :value="sync.is_active"
                      size="small"
                      @input="toggleSyncActive(sync)"
                    />
                  </div>
                </td>
                <td>
                  <span v-if="sync.last_sync_at" class="last-sync-time">
                    {{ formatDate(sync.last_sync_at) }}
                  </span>
                  <span v-else class="text-muted">Never</span>
                </td>
                <td>
                  <div class="sync-actions">
                    <Button
                      size="small"
                      icon="fas fa-sync"
                      :loading="sync.syncing"
                      @click="triggerSync(sync)"
                      title="Trigger sync now"
                    />
                    <Button
                      size="small"
                      icon="fas fa-edit"
                      @click="editSync(sync)"
                      title="Edit sync"
                    />
                    <Button
                      size="small"
                      type="danger"
                      icon="fas fa-trash"
                      @click="deleteSync(sync)"
                      title="Delete sync"
                    />
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Integration Logs -->
      <div v-if="connections.length > 0" class="integration-section">
        <h2>Recent Activity</h2>
        <div class="activity-log">
          <div v-if="logs.length === 0" class="empty-logs">
            <p>No recent activity</p>
          </div>
          <div v-else class="log-entries">
            <div
              v-for="log in logs"
              :key="log.id"
              class="log-entry"
              :class="`log-entry--${log.level}`"
            >
              <div class="log-icon">
                <i :class="getLogIcon(log.level)"></i>
              </div>
              <div class="log-content">
                <div class="log-message">{{ log.message }}</div>
                <div class="log-meta">
                  {{ log.connection.provider.display_name }} •
                  {{ formatDate(log.created_at) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Sync Modal -->
    <IntegrationSyncModal
      v-if="showCreateSyncModal || editingSync"
      :value="showCreateSyncModal || !!editingSync"
      :connection="selectedConnection"
      :table="selectedTable"
      :editing-sync="editingSync"
      @input="closeSyncModal"
      @sync-saved="handleSyncSaved"
    />

    <!-- Connection Selection Modal -->
    <Modal
      :value="showConnectionModal"
      @input="showConnectionModal = false"
      title="Select Connection"
    >
      <div class="connection-selection">
        <p>Choose which integration to create a sync for:</p>
        <div class="connection-list">
          <div
            v-for="connection in connections"
            :key="connection.id"
            class="connection-option"
            @click="selectConnection(connection)"
          >
            <img
              v-if="connection.provider.icon_url"
              :src="connection.provider.icon_url"
              :alt="connection.provider.display_name"
              class="provider-icon"
            />
            <div class="connection-info">
              <h4>{{ connection.provider.display_name }}</h4>
              <p>
                {{
                  connection.external_user_name ||
                  connection.external_user_email
                }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </Modal>

    <!-- Table Selection Modal -->
    <Modal
      :value="showTableModal"
      @input="showTableModal = false"
      title="Select Table"
    >
      <div class="table-selection">
        <p>Choose which table to sync:</p>
        <div class="table-list">
          <div
            v-for="table in tables"
            :key="table.id"
            class="table-option"
            @click="selectTable(table)"
          >
            <i class="fas fa-table"></i>
            <div class="table-info">
              <h4>{{ table.name }}</h4>
              <p>{{ table.fields.length }} fields</p>
            </div>
          </div>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import IntegrationProviderCard from './IntegrationProviderCard'
import IntegrationSyncModal from './IntegrationSyncModal'

export default {
  name: 'IntegrationManagementPage',
  components: {
    IntegrationProviderCard,
    IntegrationSyncModal,
  },
  props: {
    workspaceId: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      loading: false,
      showCreateSyncModal: false,
      showConnectionModal: false,
      showTableModal: false,
      editingSync: null,
      selectedConnection: null,
      selectedTable: null,
      syncs: [],
      logs: [],
      tables: [],
    }
  },
  computed: {
    ...mapState('integrations', ['providers', 'connections']),
  },
  async mounted() {
    await this.loadData()
  },
  methods: {
    ...mapActions('integrations', [
      'fetchProviders',
      'fetchConnections',
      'triggerSync',
      'toggleSyncActive',
    ]),

    async loadData() {
      this.loading = true
      try {
        await Promise.all([
          this.fetchProviders(),
          this.fetchConnections(this.workspaceId),
          this.loadSyncs(),
          this.loadTables(),
        ])
      } catch (error) {
        this.$toast.error('Failed to load integration data')
      } finally {
        this.loading = false
      }
    },

    async loadSyncs() {
      // Load syncs for all connections
      const syncPromises = this.connections.map((connection) =>
        this.$services.integration.getSyncs(connection.id)
      )

      const syncResponses = await Promise.all(syncPromises)
      this.syncs = syncResponses.flatMap((response) => response.data.results)
    },

    async loadTables() {
      const response = await this.$services.table.getAll(this.workspaceId)
      this.tables = response.data.results
    },

    async refreshConnections() {
      await this.fetchConnections(this.workspaceId)
      await this.loadSyncs()
    },

    getConnectionForProvider(provider) {
      return this.connections.find((c) => c.provider.id === provider.id)
    },

    getSyncTypeIcon(syncType) {
      const icons = {
        calendar: 'fas fa-calendar-alt',
        file_storage: 'fas fa-cloud',
        notifications: 'fas fa-bell',
        data_import: 'fas fa-download',
        data_export: 'fas fa-upload',
      }
      return icons[syncType] || 'fas fa-sync'
    },

    getSyncTypeLabel(syncType) {
      const labels = {
        calendar: 'Calendar',
        file_storage: 'File Storage',
        notifications: 'Notifications',
        data_import: 'Data Import',
        data_export: 'Data Export',
      }
      return labels[syncType] || syncType
    },

    getSyncDirectionColor(direction) {
      const colors = {
        bidirectional: 'primary',
        import_only: 'success',
        export_only: 'warning',
      }
      return colors[direction] || 'secondary'
    },

    getSyncDirectionLabel(direction) {
      const labels = {
        bidirectional: 'Both ways',
        import_only: 'Import',
        export_only: 'Export',
      }
      return labels[direction] || direction
    },

    getSyncStatusColor(status) {
      const colors = {
        success: 'success',
        pending: 'warning',
        failed: 'danger',
        running: 'primary',
      }
      return colors[status] || 'secondary'
    },

    getLogIcon(level) {
      const icons = {
        info: 'fas fa-info-circle',
        warning: 'fas fa-exclamation-triangle',
        error: 'fas fa-times-circle',
      }
      return icons[level] || 'fas fa-info-circle'
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleString()
    },

    async triggerSync(sync) {
      sync.syncing = true
      try {
        await this.triggerSync(sync.id)
        this.$toast.success('Sync triggered successfully')
        await this.loadSyncs()
      } catch (error) {
        this.$toast.error('Failed to trigger sync')
      } finally {
        sync.syncing = false
      }
    },

    async toggleSyncActive(sync) {
      try {
        await this.toggleSyncActive(sync.id)
        sync.is_active = !sync.is_active
        this.$toast.success(`Sync ${sync.is_active ? 'enabled' : 'disabled'}`)
      } catch (error) {
        this.$toast.error('Failed to toggle sync status')
      }
    },

    editSync(sync) {
      this.editingSync = sync
      this.selectedConnection = sync.connection
      this.selectedTable = sync.table
    },

    async deleteSync(sync) {
      if (!confirm('Are you sure you want to delete this sync?')) {
        return
      }

      try {
        await this.$services.integration.deleteSync(sync.id)
        this.$toast.success('Sync deleted successfully')
        await this.loadSyncs()
      } catch (error) {
        this.$toast.error('Failed to delete sync')
      }
    },

    createSync() {
      if (this.connections.length === 0) {
        this.$toast.warning('Please connect to an integration first')
        return
      }

      if (this.connections.length === 1) {
        this.selectedConnection = this.connections[0]
        this.showTableModal = true
      } else {
        this.showConnectionModal = true
      }
    },

    selectConnection(connection) {
      this.selectedConnection = connection
      this.showConnectionModal = false
      this.showTableModal = true
    },

    selectTable(table) {
      this.selectedTable = table
      this.showTableModal = false
      this.showCreateSyncModal = true
    },

    closeSyncModal() {
      this.showCreateSyncModal = false
      this.editingSync = null
      this.selectedConnection = null
      this.selectedTable = null
    },

    async handleSyncSaved() {
      await this.loadSyncs()
    },
  },
}
</script>

<style lang="scss" scoped>
.integration-management-page {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;

  &__header {
    margin-bottom: 32px;

    h1 {
      margin: 0 0 8px 0;
      font-size: 32px;
      font-weight: 700;
      color: var(--color-neutral-900);
    }

    p {
      margin: 0;
      font-size: 16px;
      color: var(--color-neutral-600);
    }
  }
}

.integration-section {
  margin-bottom: 48px;

  h2 {
    margin: 0 0 24px 0;
    font-size: 24px;
    font-weight: 600;
    color: var(--color-neutral-900);
  }
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;

  h2 {
    margin: 0;
  }
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  gap: 12px;

  .loading-spinner {
    width: 20px;
    height: 20px;
    border: 2px solid var(--color-neutral-200);
    border-top: 2px solid var(--color-primary-500);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
}

.provider-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;

  i {
    font-size: 48px;
    color: var(--color-neutral-400);
    margin-bottom: 16px;
  }

  h3 {
    margin: 0 0 8px 0;
    font-size: 20px;
    color: var(--color-neutral-700);
  }

  p {
    margin: 0 0 24px 0;
    color: var(--color-neutral-600);
  }
}

.syncs-table {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);

  table {
    width: 100%;
    border-collapse: collapse;

    th {
      background: var(--color-neutral-100);
      padding: 12px 16px;
      text-align: left;
      font-weight: 600;
      color: var(--color-neutral-700);
      border-bottom: 1px solid var(--color-neutral-200);
    }

    td {
      padding: 12px 16px;
      border-bottom: 1px solid var(--color-neutral-100);
      vertical-align: middle;
    }

    tr:hover {
      background: var(--color-neutral-50);
    }
  }
}

.sync-type {
  display: flex;
  align-items: center;
  gap: 8px;

  i {
    color: var(--color-primary-500);
  }
}

.provider-info {
  display: flex;
  align-items: center;
  gap: 8px;

  .provider-icon {
    width: 20px;
    height: 20px;
    object-fit: contain;
  }
}

.sync-status {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sync-actions {
  display: flex;
  gap: 4px;
}

.last-sync-time {
  font-size: 14px;
  color: var(--color-neutral-600);
}

.activity-log {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.empty-logs {
  text-align: center;
  padding: 20px;
  color: var(--color-neutral-600);
}

.log-entries {
  max-height: 400px;
  overflow-y: auto;
}

.log-entry {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid var(--color-neutral-100);

  &:last-child {
    border-bottom: none;
  }

  &--error .log-icon i {
    color: var(--color-error-500);
  }

  &--warning .log-icon i {
    color: var(--color-warning-500);
  }

  &--info .log-icon i {
    color: var(--color-primary-500);
  }
}

.log-content {
  flex: 1;

  .log-message {
    font-weight: 500;
    margin-bottom: 4px;
  }

  .log-meta {
    font-size: 12px;
    color: var(--color-neutral-600);
  }
}

.connection-selection,
.table-selection {
  padding: 20px;
}

.connection-list,
.table-list {
  display: grid;
  gap: 12px;
  margin-top: 16px;
}

.connection-option,
.table-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border: 1px solid var(--color-neutral-200);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: var(--color-primary-300);
    background: var(--color-primary-50);
  }

  .provider-icon {
    width: 32px;
    height: 32px;
    object-fit: contain;
  }

  i {
    font-size: 24px;
    color: var(--color-primary-500);
  }

  h4 {
    margin: 0 0 4px 0;
    font-size: 16px;
    font-weight: 600;
  }

  p {
    margin: 0;
    font-size: 14px;
    color: var(--color-neutral-600);
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
