<template>
  <div
    class="dashboard-enhanced-chart-widget"
    :class="{
      'dashboard-enhanced-chart-widget--with-header-description':
        widget.description,
    }"
  >
    <template v-if="!loading">
      <div
        class="widget__header"
        :class="{
          'widget__header--edit-mode': editMode,
        }"
      >
        <div class="widget__header-main">
          <div class="widget__header-title-wrapper">
            <div class="widget__header-title">{{ widget.title }}</div>

            <Badge
              v-if="dataSourceMisconfigured"
              color="red"
              size="small"
              indicator
              rounded
              >{{ $t('widget.fixConfiguration') }}</Badge
            >
          </div>
          <div v-if="widget.description" class="widget__header-description">
            {{ widget.description }}
          </div>
        </div>
        <WidgetContextMenu
          v-if="isEditMode"
          :widget="widget"
          :dashboard="dashboard"
          @delete-widget="$emit('delete-widget', $event)"
        ></WidgetContextMenu>
      </div>

      <div class="dashboard-enhanced-chart-widget__content widget__content">
        <EnhancedChart
          ref="enhancedChart"
          :chart-type="widget.chart_type"
          :chart-data="chartData"
          :chart-options="chartOptions"
          :loading="chartLoading"
          :real-time-enabled="widget.real_time_enabled"
          :refresh-interval="widget.refresh_interval * 1000"
          @refresh-data="fetchChartData"
          @chart-ready="onChartReady"
        />
      </div>
    </template>
    <div
      v-else
      class="dashboard-enhanced-chart-widget__loading loading-spinner"
    ></div>
  </div>
</template>

<script>
import WidgetContextMenu from '@baserow/modules/dashboard/components/widget/WidgetContextMenu'
import EnhancedChart from '@baserow/modules/dashboard/components/widget/EnhancedChart'
import { realTimeUpdatesService } from '@baserow/modules/dashboard/services/realTimeUpdates'

export default {
  name: 'EnhancedChartWidget',
  components: { WidgetContextMenu, EnhancedChart },
  props: {
    dashboard: {
      type: Object,
      required: true,
    },
    widget: {
      type: Object,
      required: true,
    },
    storePrefix: {
      type: String,
      required: false,
      default: '',
    },
    loading: {
      type: Boolean,
      required: false,
      default: false,
    },
    editMode: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  data() {
    return {
      chartData: {
        labels: [],
        datasets: [],
        type: 'bar',
      },
      chartLoading: false,
      refreshInterval: null,
      realTimeSubscription: null,
    }
  },
  computed: {
    isEditMode() {
      return this.$store.getters[
        `${this.storePrefix}dashboardApplication/isEditMode`
      ]
    },
    dataSourceMisconfigured() {
      // Check if any data sources have errors
      return (
        this.widget.data_source_ids?.some((id) => {
          const data =
            this.$store.getters[
              `${this.storePrefix}dashboardApplication/getDataForDataSource`
            ](id)
          return data && data._error
        }) || false
      )
    },
    chartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: this.widget.show_legend,
            align: 'start',
            position: 'bottom',
            labels: {
              usePointStyle: true,
              boxWidth: 14,
              pointStyle: 'circle',
              padding: 20,
            },
          },
          tooltip: {
            enabled: this.widget.show_tooltips,
            backgroundColor: '#202128',
            padding: 10,
            bodyFont: {
              size: 12,
            },
            titleFont: {
              size: 12,
            },
          },
        },
        scales: this.getScalesConfig(),
        animation: {
          duration: this.widget.enable_animations
            ? this.widget.animation_duration
            : 0,
        },
        elements: this.getElementsConfig(),
      }
    },
  },
  async mounted() {
    await this.fetchChartData()
    this.setupRealTimeUpdates()
  },
  beforeDestroy() {
    this.clearRealTimeUpdates()
  },
  methods: {
    async fetchChartData() {
      this.chartLoading = true
      try {
        const { data } = await this.$axios.get(
          `/api/dashboard/enhanced/enhanced-chart-widgets/${this.widget.id}/data/`
        )
        this.chartData = data
      } catch (error) {
        console.error('Error fetching chart data:', error)
        this.chartData = {
          labels: [],
          datasets: [],
          type: this.widget.chart_type,
        }
      } finally {
        this.chartLoading = false
      }
    },
    async refreshData() {
      try {
        const { data } = await this.$axios.post(
          `/api/dashboard/enhanced/enhanced-chart-widgets/${this.widget.id}/refresh/`
        )
        this.chartData = data
      } catch (error) {
        console.error('Error refreshing chart data:', error)
      }
    },
    setupRealTimeUpdates() {
      if (this.widget.real_time_enabled) {
        this.realTimeSubscription = realTimeUpdatesService.subscribe(
          this.widget.id,
          (data) => {
            if (data.error) {
              console.error('Real-time update error:', data.error)
              return
            }

            // Update chart data with smooth animation
            this.chartData = data
            this.$refs.enhancedChart?.updateChartData(data)
          },
          {
            interval: this.widget.refresh_interval * 1000 || 30000,
            widgetType: 'enhanced_chart',
            useWebSocket: this.widget.use_websocket || false,
          }
        )
      } else if (this.widget.auto_refresh && this.widget.refresh_interval > 0) {
        // Fallback to traditional polling
        this.refreshInterval = setInterval(() => {
          this.fetchChartData()
        }, this.widget.refresh_interval * 1000)
      }
    },
    clearRealTimeUpdates() {
      if (this.realTimeSubscription) {
        this.realTimeSubscription.unsubscribe()
        this.realTimeSubscription = null
      }

      if (this.refreshInterval) {
        clearInterval(this.refreshInterval)
        this.refreshInterval = null
      }
    },
    getScalesConfig() {
      const config = {}

      if (
        this.widget.chart_type !== 'pie' &&
        this.widget.chart_type !== 'donut'
      ) {
        config.y = {
          grid: {
            display: this.widget.show_grid,
          },
        }
        config.x = {
          grid: {
            display: this.widget.show_grid,
          },
        }
      }

      return config
    },
    getElementsConfig() {
      const config = {}

      if (this.widget.chart_type === 'bar') {
        config.bar = {
          borderRadius: {
            topLeft: 4,
            topRight: 4,
            bottomLeft: 0,
            bottomRight: 0,
          },
          borderWidth: 1,
        }
      }

      if (
        this.widget.chart_type === 'line' ||
        this.widget.chart_type === 'area'
      ) {
        config.line = {
          tension: 0.4,
        }
        config.point = {
          radius: 4,
          hoverRadius: 6,
        }
      }

      return config
    },
    onChartReady(chartInstance) {
      this.chartInstance = chartInstance
      this.$emit('chart-ready', chartInstance)
    },
  },
}
</script>

<style lang="scss" scoped>
.dashboard-enhanced-chart-widget {
  height: 100%;
  display: flex;
  flex-direction: column;

  &__content {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 16px;
    min-height: 0; // Important for chart responsiveness
  }

  &__loading {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .dashboard-enhanced-chart-widget__content {
    padding: 12px;
  }
}
</style>
