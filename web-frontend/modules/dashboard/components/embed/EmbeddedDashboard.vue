<template>
  <div class="embedded-dashboard" :class="{ 'embed-mode': embedMode }">
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner">
        <i class="fas fa-spinner fa-spin"></i>
        <p>{{ $t('dashboardEmbed.loading') }}</p>
      </div>
    </div>

    <div v-else-if="error" class="error-container">
      <div class="error-message">
        <i class="fas fa-exclamation-triangle"></i>
        <h3>{{ $t('dashboardEmbed.error') }}</h3>
        <p>{{ error }}</p>
      </div>
    </div>

    <div v-else-if="dashboard" class="dashboard-content">
      <!-- Dashboard Header (hidden in embed mode) -->
      <div v-if="!embedMode" class="dashboard-header">
        <h1>{{ dashboard.name }}</h1>
        <div class="dashboard-actions">
          <button
            class="btn btn-outline-primary"
            @click="refreshDashboard"
          >
            <i class="fas fa-sync-alt"></i>
            {{ $t('dashboardEmbed.refresh') }}
          </button>
        </div>
      </div>

      <!-- Dashboard Grid -->
      <div class="dashboard-grid" :style="gridStyle">
        <div
          v-for="widget in dashboard.widgets"
          :key="widget.id"
          class="widget-container"
          :style="getWidgetStyle(widget)"
        >
          <EmbeddedWidget
            :widget="widget"
            :embed-mode="embedMode"
            @error="handleWidgetError"
          />
        </div>
      </div>

      <!-- Powered by Baserow (for public embeds) -->
      <div v-if="embedMode" class="powered-by">
        <a href="https://baserow.io" target="_blank" rel="noopener">
          <i class="fas fa-external-link-alt"></i>
          {{ $t('dashboardEmbed.poweredBy') }}
        </a>
      </div>
    </div>
  </div>
</template>

<script>
import EmbeddedWidget from './EmbeddedWidget.vue'

export default {
  name: 'EmbeddedDashboard',
  components: {
    EmbeddedWidget
  },
  props: {
    token: {
      type: String,
      required: true
    },
    embedMode: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      loading: true,
      error: null,
      dashboard: null,
      refreshInterval: null
    }
  },
  computed: {
    gridStyle() {
      if (!this.dashboard?.layout) return {}
      
      return {
        gridTemplateColumns: `repeat(${this.dashboard.layout.columns || 12}, 1fr)`,
        gridTemplateRows: `repeat(${this.dashboard.layout.rows || 8}, 1fr)`,
        gap: this.embedMode ? '8px' : '16px'
      }
    }
  },
  async mounted() {
    await this.loadDashboard()
    
    // Set up auto-refresh for embedded dashboards
    if (this.embedMode) {
      this.refreshInterval = setInterval(() => {
        this.refreshDashboard()
      }, 30000) // Refresh every 30 seconds
    }
  },
  beforeDestroy() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval)
    }
  },
  methods: {
    async loadDashboard() {
      try {
        this.loading = true
        this.error = null
        
        const endpoint = this.embedMode 
          ? `/dashboard/sharing/embed/${this.token}/`
          : `/dashboard/sharing/public/${this.token}/`
        
        const { data } = await this.$client.get(endpoint)
        this.dashboard = data
      } catch (error) {
        console.error('Error loading dashboard:', error)
        this.error = error.response?.data?.error || this.$t('dashboardEmbed.loadError')
      } finally {
        this.loading = false
      }
    },
    async refreshDashboard() {
      // Refresh without showing loading state
      try {
        const endpoint = this.embedMode 
          ? `/dashboard/sharing/embed/${this.token}/`
          : `/dashboard/sharing/public/${this.token}/`
        
        const { data } = await this.$client.get(endpoint)
        this.dashboard = data
      } catch (error) {
        console.error('Error refreshing dashboard:', error)
      }
    },
    getWidgetStyle(widget) {
      const position = widget.position || {}
      
      return {
        gridColumn: `${position.x || 1} / span ${position.width || 4}`,
        gridRow: `${position.y || 1} / span ${position.height || 3}`,
        minHeight: this.embedMode ? '200px' : '250px'
      }
    },
    handleWidgetError(error) {
      console.error('Widget error:', error)
      // Could show a toast or handle widget-specific errors
    }
  }
}
</script>

<style lang="scss" scoped>
.embedded-dashboard {
  width: 100%;
  height: 100%;
  
  &.embed-mode {
    padding: 8px;
    background: #f8f9fa;
  }
  
  .loading-container,
  .error-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    min-height: 400px;
  }
  
  .loading-spinner {
    text-align: center;
    
    i {
      font-size: 2rem;
      color: #007bff;
      margin-bottom: 1rem;
    }
    
    p {
      color: #6c757d;
    }
  }
  
  .error-message {
    text-align: center;
    
    i {
      font-size: 3rem;
      color: #dc3545;
      margin-bottom: 1rem;
    }
    
    h3 {
      color: #dc3545;
      margin-bottom: 0.5rem;
    }
    
    p {
      color: #6c757d;
    }
  }
  
  .dashboard-content {
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  
  .dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 0;
    border-bottom: 1px solid #e9ecef;
    margin-bottom: 1rem;
    
    h1 {
      margin: 0;
      font-size: 1.5rem;
    }
  }
  
  .dashboard-grid {
    display: grid;
    flex: 1;
    width: 100%;
    height: 100%;
    
    .widget-container {
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      overflow: hidden;
      
      .embed-mode & {
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      }
    }
  }
  
  .powered-by {
    text-align: center;
    padding: 1rem;
    margin-top: 1rem;
    
    a {
      color: #6c757d;
      text-decoration: none;
      font-size: 0.875rem;
      
      &:hover {
        color: #007bff;
      }
      
      i {
        margin-left: 0.25rem;
      }
    }
  }
}

// Responsive design for embedded dashboards
@media (max-width: 768px) {
  .embedded-dashboard {
    &.embed-mode {
      .dashboard-grid {
        grid-template-columns: 1fr !important;
        
        .widget-container {
          grid-column: 1 !important;
          min-height: 300px !important;
        }
      }
    }
  }
}
</style>