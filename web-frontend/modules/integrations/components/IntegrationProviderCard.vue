<template>
  <div class="integration-provider-card">
    <div class="integration-provider-card__header">
      <div class="integration-provider-card__icon">
        <img v-if="provider.icon_url" :src="provider.icon_url" :alt="provider.display_name" />
        <i v-else class="fas fa-plug"></i>
      </div>
      <div class="integration-provider-card__info">
        <h3 class="integration-provider-card__title">{{ provider.display_name }}</h3>
        <p class="integration-provider-card__description">{{ provider.description }}</p>
      </div>
    </div>
    
    <div class="integration-provider-card__status">
      <div v-if="connection" class="integration-provider-card__connected">
        <i class="fas fa-check-circle text-success"></i>
        <span>Connected as {{ connection.external_user_name || connection.external_user_email }}</span>
        <Badge v-if="connection.status !== 'active'" :color="getStatusColor(connection.status)">
          {{ connection.status }}
        </Badge>
      </div>
      <div v-else class="integration-provider-card__disconnected">
        <i class="fas fa-times-circle text-muted"></i>
        <span>Not connected</span>
      </div>
    </div>
    
    <div class="integration-provider-card__actions">
      <Button
        v-if="!connection"
        type="primary"
        size="small"
        :loading="connecting"
        @click="connect"
      >
        Connect
      </Button>
      <template v-else>
        <Button
          v-if="connection.status === 'expired'"
          type="secondary"
          size="small"
          :loading="refreshing"
          @click="refreshToken"
        >
          Refresh
        </Button>
        <Button
          type="danger"
          size="small"
          :loading="disconnecting"
          @click="disconnect"
        >
          Disconnect
        </Button>
      </template>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'IntegrationProviderCard',
  props: {
    provider: {
      type: Object,
      required: true,
    },
    connection: {
      type: Object,
      default: null,
    },
    workspaceId: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      connecting: false,
      disconnecting: false,
      refreshing: false,
    }
  },
  methods: {
    ...mapActions('integrations', ['startOAuthFlow', 'revokeConnection']),
    
    async connect() {
      this.connecting = true
      try {
        await this.startOAuthFlow({
          provider: this.provider.name,
          workspaceId: this.workspaceId,
        })
      } catch (error) {
        this.$toast.error('Failed to start connection process')
      } finally {
        this.connecting = false
      }
    },
    
    async disconnect() {
      this.disconnecting = true
      try {
        await this.revokeConnection(this.connection.id)
        this.$toast.success('Integration disconnected successfully')
        this.$emit('connection-revoked')
      } catch (error) {
        this.$toast.error('Failed to disconnect integration')
      } finally {
        this.disconnecting = false
      }
    },
    
    async refreshToken() {
      this.refreshing = true
      try {
        await this.$store.dispatch('integrations/refreshToken', this.connection.id)
        this.$toast.success('Connection refreshed successfully')
      } catch (error) {
        this.$toast.error('Failed to refresh connection')
      } finally {
        this.refreshing = false
      }
    },
    
    getStatusColor(status) {
      const colors = {
        active: 'success',
        expired: 'warning',
        error: 'danger',
        revoked: 'secondary',
      }
      return colors[status] || 'secondary'
    },
  },
}
</script>

<style lang="scss" scoped>
.integration-provider-card {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 20px;
  background: var(--color-neutral-50);
  
  &__header {
    display: flex;
    align-items: flex-start;
    margin-bottom: 16px;
  }
  
  &__icon {
    width: 48px;
    height: 48px;
    margin-right: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    
    img {
      width: 100%;
      height: 100%;
      object-fit: contain;
    }
    
    i {
      font-size: 24px;
      color: var(--color-neutral-600);
    }
  }
  
  &__info {
    flex: 1;
  }
  
  &__title {
    margin: 0 0 8px 0;
    font-size: 18px;
    font-weight: 600;
    color: var(--color-neutral-900);
  }
  
  &__description {
    margin: 0;
    color: var(--color-neutral-600);
    font-size: 14px;
    line-height: 1.4;
  }
  
  &__status {
    margin-bottom: 16px;
    
    &__connected,
    &__disconnected {
      display: flex;
      align-items: center;
      font-size: 14px;
      
      i {
        margin-right: 8px;
      }
      
      span {
        margin-right: 8px;
      }
    }
  }
  
  &__actions {
    display: flex;
    gap: 8px;
  }
}
</style>