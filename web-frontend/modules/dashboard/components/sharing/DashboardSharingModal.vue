<template>
  <Modal
    ref="modal"
    :title="$t('dashboardSharing.title')"
    :loading="loading"
    @hidden="$emit('hidden')"
  >
    <div class="dashboard-sharing-modal">
      <!-- Current Sharing Settings -->
      <div class="sharing-section">
        <h3>{{ $t('dashboardSharing.currentSettings') }}</h3>
        <div class="sharing-status">
          <div class="status-item">
            <i class="fas fa-lock" :class="{ 'text-success': isPublic }"></i>
            <span>{{ permissionLevelText }}</span>
          </div>
          <div v-if="publicUrl" class="public-url">
            <label>{{ $t('dashboardSharing.publicUrl') }}</label>
            <div class="url-input-group">
              <input
                ref="publicUrlInput"
                :value="publicUrl"
                readonly
                class="form-control"
              />
              <button
                class="btn btn-outline-secondary"
                @click="copyToClipboard(publicUrl)"
              >
                <i class="fas fa-copy"></i>
              </button>
            </div>
          </div>
          <div v-if="embedUrl" class="embed-url">
            <label>{{ $t('dashboardSharing.embedUrl') }}</label>
            <div class="url-input-group">
              <input
                ref="embedUrlInput"
                :value="embedUrl"
                readonly
                class="form-control"
              />
              <button
                class="btn btn-outline-secondary"
                @click="copyToClipboard(embedUrl)"
              >
                <i class="fas fa-copy"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Sharing Actions -->
      <div class="sharing-actions">
        <h3>{{ $t('dashboardSharing.actions') }}</h3>
        
        <div class="action-buttons">
          <button
            v-if="!isPublic"
            class="btn btn-primary"
            :disabled="loading"
            @click="createPublicLink"
          >
            <i class="fas fa-link"></i>
            {{ $t('dashboardSharing.createPublicLink') }}
          </button>
          
          <button
            v-if="!hasEmbedToken"
            class="btn btn-secondary"
            :disabled="loading"
            @click="createEmbedLink"
          >
            <i class="fas fa-code"></i>
            {{ $t('dashboardSharing.createEmbedLink') }}
          </button>
          
          <button
            v-if="isPublic || hasEmbedToken"
            class="btn btn-danger"
            :disabled="loading"
            @click="revokePublicAccess"
          >
            <i class="fas fa-times"></i>
            {{ $t('dashboardSharing.revokeAccess') }}
          </button>
        </div>
      </div>

      <!-- Widget Embedding -->
      <div v-if="dashboard.widgets && dashboard.widgets.length > 0" class="widget-embedding">
        <h3>{{ $t('dashboardSharing.widgetEmbedding') }}</h3>
        <p class="text-muted">{{ $t('dashboardSharing.widgetEmbeddingDescription') }}</p>
        
        <div class="widget-list">
          <div
            v-for="widget in dashboard.widgets"
            :key="widget.id"
            class="widget-item"
          >
            <div class="widget-info">
              <i :class="getWidgetIcon(widget.widget_type)"></i>
              <span>{{ getWidgetName(widget) }}</span>
            </div>
            <button
              class="btn btn-sm btn-outline-primary"
              :disabled="loading"
              @click="createWidgetEmbedLink(widget.id)"
            >
              {{ $t('dashboardSharing.embedWidget') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Permissions Management -->
      <div class="permissions-section">
        <h3>{{ $t('dashboardSharing.permissions') }}</h3>
        
        <div class="add-permission">
          <div class="form-group">
            <label>{{ $t('dashboardSharing.addUser') }}</label>
            <div class="permission-input-group">
              <input
                v-model="newPermission.email"
                type="email"
                class="form-control"
                :placeholder="$t('dashboardSharing.userEmail')"
              />
              <select v-model="newPermission.type" class="form-control">
                <option value="view">{{ $t('dashboardSharing.permissionView') }}</option>
                <option value="edit">{{ $t('dashboardSharing.permissionEdit') }}</option>
                <option value="admin">{{ $t('dashboardSharing.permissionAdmin') }}</option>
              </select>
              <button
                class="btn btn-primary"
                :disabled="!newPermission.email || loading"
                @click="addPermission"
              >
                {{ $t('dashboardSharing.add') }}
              </button>
            </div>
          </div>
        </div>

        <div v-if="permissions.length > 0" class="permissions-list">
          <div
            v-for="permission in permissions"
            :key="permission.user_email"
            class="permission-item"
          >
            <div class="permission-info">
              <span class="user-email">{{ permission.user_email }}</span>
              <span class="permission-type">{{ getPermissionTypeText(permission.permission_type) }}</span>
            </div>
            <button
              class="btn btn-sm btn-outline-danger"
              :disabled="loading"
              @click="removePermission(permission.user_email)"
            >
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <button class="btn btn-secondary" @click="hide">
        {{ $t('action.close') }}
      </button>
    </template>
  </Modal>
</template>

<script>
import Modal from '@baserow/modules/core/components/Modal'
import { notifyIf } from '@baserow/modules/core/utils/error'

export default {
  name: 'DashboardSharingModal',
  components: {
    Modal
  },
  props: {
    dashboard: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      loading: false,
      sharingSettings: null,
      permissions: [],
      newPermission: {
        email: '',
        type: 'view'
      }
    }
  },
  computed: {
    isPublic() {
      return this.sharingSettings?.permission_level === 'public'
    },
    hasEmbedToken() {
      return !!this.sharingSettings?.embed_token
    },
    publicUrl() {
      return this.sharingSettings?.public_url
    },
    embedUrl() {
      return this.sharingSettings?.embed_url
    },
    permissionLevelText() {
      const level = this.sharingSettings?.permission_level || 'private'
      return this.$t(`dashboardSharing.permissionLevel.${level}`)
    }
  },
  async mounted() {
    await this.loadSharingSettings()
    await this.loadPermissions()
  },
  methods: {
    show() {
      this.$refs.modal.show()
    },
    hide() {
      this.$refs.modal.hide()
    },
    async loadSharingSettings() {
      try {
        this.loading = true
        const { data } = await this.$client.get(
          `/dashboard/sharing/dashboards/${this.dashboard.id}/sharing_settings/`
        )
        this.sharingSettings = data
      } catch (error) {
        notifyIf(error, 'dashboard')
      } finally {
        this.loading = false
      }
    },
    async loadPermissions() {
      try {
        const { data } = await this.$client.get(
          `/dashboard/sharing/dashboards/${this.dashboard.id}/permissions/`
        )
        this.permissions = data.permissions
      } catch (error) {
        notifyIf(error, 'dashboard')
      }
    },
    async createPublicLink() {
      try {
        this.loading = true
        const { data } = await this.$client.post(
          `/dashboard/sharing/dashboards/${this.dashboard.id}/create_public_link/`
        )
        
        this.sharingSettings = {
          ...this.sharingSettings,
          permission_level: 'public',
          public_url: data.public_url,
          public_token: data.token
        }
        
        this.$toast.success(this.$t('dashboardSharing.publicLinkCreated'))
      } catch (error) {
        notifyIf(error, 'dashboard')
      } finally {
        this.loading = false
      }
    },
    async createEmbedLink() {
      try {
        this.loading = true
        const { data } = await this.$client.post(
          `/dashboard/sharing/dashboards/${this.dashboard.id}/create_embed_link/`
        )
        
        this.sharingSettings = {
          ...this.sharingSettings,
          embed_url: data.embed_url,
          embed_token: data.token
        }
        
        this.$toast.success(this.$t('dashboardSharing.embedLinkCreated'))
      } catch (error) {
        notifyIf(error, 'dashboard')
      } finally {
        this.loading = false
      }
    },
    async createWidgetEmbedLink(widgetId) {
      try {
        this.loading = true
        const { data } = await this.$client.post(
          `/dashboard/sharing/dashboards/${this.dashboard.id}/create_embed_link/`,
          { widget_ids: [widgetId] }
        )
        
        if (data.widgets && data.widgets.length > 0) {
          const widget = data.widgets[0]
          await this.copyToClipboard(widget.embed_url)
          this.$toast.success(this.$t('dashboardSharing.widgetEmbedLinkCreated'))
        }
      } catch (error) {
        notifyIf(error, 'dashboard')
      } finally {
        this.loading = false
      }
    },
    async revokePublicAccess() {
      try {
        this.loading = true
        await this.$client.post(
          `/dashboard/sharing/dashboards/${this.dashboard.id}/revoke_public_access/`
        )
        
        this.sharingSettings = {
          ...this.sharingSettings,
          permission_level: 'private',
          public_url: null,
          public_token: null,
          embed_url: null,
          embed_token: null
        }
        
        this.$toast.success(this.$t('dashboardSharing.accessRevoked'))
      } catch (error) {
        notifyIf(error, 'dashboard')
      } finally {
        this.loading = false
      }
    },
    async addPermission() {
      try {
        this.loading = true
        await this.$client.post(
          `/dashboard/sharing/dashboards/${this.dashboard.id}/set_permission/`,
          {
            user_email: this.newPermission.email,
            permission_type: this.newPermission.type
          }
        )
        
        this.newPermission = { email: '', type: 'view' }
        await this.loadPermissions()
        this.$toast.success(this.$t('dashboardSharing.permissionAdded'))
      } catch (error) {
        notifyIf(error, 'dashboard')
      } finally {
        this.loading = false
      }
    },
    async removePermission(userEmail) {
      try {
        this.loading = true
        await this.$client.post(
          `/dashboard/sharing/dashboards/${this.dashboard.id}/remove_permission/`,
          { user_email: userEmail }
        )
        
        await this.loadPermissions()
        this.$toast.success(this.$t('dashboardSharing.permissionRemoved'))
      } catch (error) {
        notifyIf(error, 'dashboard')
      } finally {
        this.loading = false
      }
    },
    async copyToClipboard(text) {
      try {
        await navigator.clipboard.writeText(text)
        this.$toast.success(this.$t('dashboardSharing.copiedToClipboard'))
      } catch (error) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea')
        textArea.value = text
        document.body.appendChild(textArea)
        textArea.select()
        document.execCommand('copy')
        document.body.removeChild(textArea)
        this.$toast.success(this.$t('dashboardSharing.copiedToClipboard'))
      }
    },
    getWidgetIcon(widgetType) {
      const icons = {
        chart: 'fas fa-chart-bar',
        kpi: 'fas fa-tachometer-alt',
        table: 'fas fa-table',
        calendar: 'fas fa-calendar'
      }
      return icons[widgetType] || 'fas fa-widget'
    },
    getWidgetName(widget) {
      return widget.configuration?.title || `${widget.widget_type} Widget`
    },
    getPermissionTypeText(type) {
      return this.$t(`dashboardSharing.permissionType.${type}`)
    }
  }
}
</script>

<style lang="scss" scoped>
.dashboard-sharing-modal {
  .sharing-section,
  .sharing-actions,
  .widget-embedding,
  .permissions-section {
    margin-bottom: 2rem;
    
    h3 {
      margin-bottom: 1rem;
      font-size: 1.1rem;
      font-weight: 600;
    }
  }

  .sharing-status {
    .status-item {
      display: flex;
      align-items: center;
      margin-bottom: 1rem;
      
      i {
        margin-right: 0.5rem;
        width: 1rem;
      }
    }
    
    .public-url,
    .embed-url {
      margin-bottom: 1rem;
      
      label {
        display: block;
        margin-bottom: 0.25rem;
        font-weight: 500;
      }
    }
  }

  .url-input-group {
    display: flex;
    
    input {
      flex: 1;
      border-top-right-radius: 0;
      border-bottom-right-radius: 0;
    }
    
    button {
      border-top-left-radius: 0;
      border-bottom-left-radius: 0;
      border-left: 0;
    }
  }

  .action-buttons {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .widget-list {
    .widget-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.75rem;
      border: 1px solid #e9ecef;
      border-radius: 0.25rem;
      margin-bottom: 0.5rem;
      
      .widget-info {
        display: flex;
        align-items: center;
        
        i {
          margin-right: 0.5rem;
          width: 1rem;
        }
      }
    }
  }

  .add-permission {
    margin-bottom: 1.5rem;
    
    .permission-input-group {
      display: flex;
      gap: 0.5rem;
      
      input {
        flex: 2;
      }
      
      select {
        flex: 1;
      }
      
      button {
        flex-shrink: 0;
      }
    }
  }

  .permissions-list {
    .permission-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.75rem;
      border: 1px solid #e9ecef;
      border-radius: 0.25rem;
      margin-bottom: 0.5rem;
      
      .permission-info {
        .user-email {
          font-weight: 500;
          margin-right: 1rem;
        }
        
        .permission-type {
          color: #6c757d;
          font-size: 0.875rem;
        }
      }
    }
  }
}
</style>