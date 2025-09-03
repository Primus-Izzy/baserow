<template>
  <div
    class="dashboard-kpi-widget"
    :class="{
      'dashboard-kpi-widget--with-header-description': widget.description,
      [`dashboard-kpi-widget--${widget.color_scheme}`]: widget.color_scheme,
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

      <div class="dashboard-kpi-widget__content widget__content">
        <!-- Number Display -->
        <div
          v-if="widget.display_format === 'number'"
          class="kpi-widget__main-value"
        >
          <span v-if="widget.prefix_text" class="kpi-widget__prefix">
            {{ widget.prefix_text }}
          </span>
          <span class="kpi-widget__value" :style="{ color: getValueColor() }">
            {{ kpiData.formatted_value || '0' }}
          </span>
          <span v-if="widget.suffix_text" class="kpi-widget__suffix">
            {{ widget.suffix_text }}
          </span>
        </div>

        <!-- Gauge Display -->
        <GaugeChart
          v-else-if="widget.display_format === 'gauge'"
          :value="kpiData.value || 0"
          :min-value="widget.gauge_min || 0"
          :max-value="widget.gauge_max || 100"
          :unit="widget.suffix_text"
          :color-ranges="widget.gauge_color_ranges || defaultGaugeRanges"
          :loading="loading"
        />

        <!-- Progress Bar Display -->
        <div
          v-else-if="widget.display_format === 'progress'"
          class="kpi-widget__progress"
        >
          <div class="kpi-widget__progress-header">
            <span class="kpi-widget__progress-label">{{ widget.title }}</span>
            <span class="kpi-widget__progress-value">
              {{ kpiData.formatted_value || '0' }}
            </span>
          </div>
          <div class="kpi-widget__progress-bar">
            <div
              class="kpi-widget__progress-fill"
              :style="{
                width: `${getProgressPercentage()}%`,
                backgroundColor: getValueColor(),
              }"
            ></div>
          </div>
        </div>

        <!-- Sparkline Display -->
        <div
          v-else-if="widget.display_format === 'sparkline'"
          class="kpi-widget__sparkline"
        >
          <div class="kpi-widget__sparkline-value">
            <span class="kpi-widget__value" :style="{ color: getValueColor() }">
              {{ kpiData.formatted_value || '0' }}
            </span>
          </div>
          <canvas
            ref="sparklineCanvas"
            class="kpi-widget__sparkline-chart"
            width="200"
            height="60"
          ></canvas>
        </div>

        <!-- Comparison/Trend Information -->
        <div
          v-if="widget.comparison_enabled && kpiData.comparison_value !== null"
          class="kpi-widget__comparison"
        >
          <div class="kpi-widget__trend">
            <i :class="getTrendIcon()" class="kpi-widget__trend-icon"></i>
            <span class="kpi-widget__trend-text">
              {{ getTrendText() }}
            </span>
          </div>
        </div>
      </div>
    </template>
    <div v-else class="dashboard-kpi-widget__loading loading-spinner"></div>
  </div>
</template>

<script>
import WidgetContextMenu from '@baserow/modules/dashboard/components/widget/WidgetContextMenu'
import GaugeChart from '@baserow/modules/dashboard/components/widget/GaugeChart'

export default {
  name: 'KPIWidget',
  components: { WidgetContextMenu, GaugeChart },
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
      kpiData: {
        value: 0,
        formatted_value: '0',
        comparison_value: null,
        trend: null,
        trend_percentage: null,
        sparkline_data: [],
      },
      defaultGaugeRanges: [
        { min: 0, max: 30, color: '#dc3545' },
        { min: 30, max: 70, color: '#ffc107' },
        { min: 70, max: 100, color: '#28a745' },
      ],
    }
  },
  computed: {
    dataSource() {
      return this.$store.getters[
        `${this.storePrefix}dashboardApplication/getDataSourceById`
      ](this.widget.data_source_id)
    },
    isEditMode() {
      return this.$store.getters[
        `${this.storePrefix}dashboardApplication/isEditMode`
      ]
    },
    dataSourceMisconfigured() {
      const data = this.dataForDataSource
      if (data) {
        return !!data._error
      }
      return false
    },
    dataForDataSource() {
      return this.$store.getters[
        `${this.storePrefix}dashboardApplication/getDataForDataSource`
      ](this.dataSource?.id)
    },
  },
  async mounted() {
    await this.fetchKPIData()
    this.drawSparkline()
  },
  updated() {
    if (this.widget.display_format === 'sparkline') {
      this.$nextTick(() => {
        this.drawSparkline()
      })
    }
  },
  methods: {
    async fetchKPIData() {
      try {
        const { data } = await this.$axios.get(
          `/api/dashboard/enhanced/kpi-widgets/${this.widget.id}/data/`
        )
        this.kpiData = data
      } catch (error) {
        console.error('Error fetching KPI data:', error)
      }
    },
    getValueColor() {
      if (this.widget.color_scheme === 'custom' && this.widget.custom_color) {
        return this.widget.custom_color
      }

      const colorMap = {
        blue: '#5190ef',
        green: '#28a745',
        red: '#dc3545',
        orange: '#fd7e14',
        purple: '#6f42c1',
      }

      return colorMap[this.widget.color_scheme] || '#5190ef'
    },
    getTrendIcon() {
      if (!this.kpiData.trend) return ''

      return (
        {
          up: 'fas fa-arrow-up',
          down: 'fas fa-arrow-down',
          neutral: 'fas fa-minus',
        }[this.kpiData.trend] || ''
      )
    },
    getTrendText() {
      if (!this.kpiData.trend_percentage) return ''

      const percentage = Math.abs(this.kpiData.trend_percentage)
      const direction = this.kpiData.trend === 'up' ? 'increase' : 'decrease'

      return `${percentage}% ${direction}`
    },
    async refreshData() {
      try {
        const { data } = await this.$axios.post(
          `/api/dashboard/enhanced/kpi-widgets/${this.widget.id}/refresh/`
        )
        this.kpiData = data
        this.drawSparkline()
      } catch (error) {
        console.error('Error refreshing KPI data:', error)
      }
    },
    getProgressPercentage() {
      const min = this.widget.progress_min || 0
      const max = this.widget.progress_max || 100
      const value = this.kpiData.value || 0
      return Math.max(0, Math.min(100, ((value - min) / (max - min)) * 100))
    },
    drawSparkline() {
      if (
        this.widget.display_format !== 'sparkline' ||
        !this.$refs.sparklineCanvas
      )
        return

      const canvas = this.$refs.sparklineCanvas
      const ctx = canvas.getContext('2d')
      const data = this.kpiData.sparkline_data || []

      if (data.length === 0) return

      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // Calculate dimensions
      const padding = 10
      const width = canvas.width - padding * 2
      const height = canvas.height - padding * 2

      const minValue = Math.min(...data)
      const maxValue = Math.max(...data)
      const range = maxValue - minValue || 1

      // Draw line
      ctx.beginPath()
      ctx.strokeStyle = this.getValueColor()
      ctx.lineWidth = 2

      data.forEach((value, index) => {
        const x = padding + (index / (data.length - 1)) * width
        const y = padding + height - ((value - minValue) / range) * height

        if (index === 0) {
          ctx.moveTo(x, y)
        } else {
          ctx.lineTo(x, y)
        }
      })

      ctx.stroke()

      // Draw area fill
      ctx.lineTo(padding + width, padding + height)
      ctx.lineTo(padding, padding + height)
      ctx.closePath()
      ctx.fillStyle = this.addAlpha(this.getValueColor(), 0.2)
      ctx.fill()
    },
    addAlpha(color, alpha) {
      if (!color) return color

      // Convert hex to rgba
      if (color.startsWith('#')) {
        const hex = color.slice(1)
        const r = parseInt(hex.slice(0, 2), 16)
        const g = parseInt(hex.slice(2, 4), 16)
        const b = parseInt(hex.slice(4, 6), 16)
        return `rgba(${r}, ${g}, ${b}, ${alpha})`
      }

      return color
    },
  },
}
</script>

<style lang="scss" scoped>
.dashboard-kpi-widget {
  height: 100%;
  display: flex;
  flex-direction: column;

  &__content {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 20px;
  }

  &__loading {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.kpi-widget {
  &__main-value {
    display: flex;
    align-items: baseline;
    justify-content: center;
    margin-bottom: 16px;
  }

  &__prefix,
  &__suffix {
    font-size: 14px;
    color: #666;
    margin: 0 4px;
  }

  &__value {
    font-size: 48px;
    font-weight: bold;
    line-height: 1;
  }

  &__comparison {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  &__trend {
    display: flex;
    align-items: center;
    font-size: 14px;
    color: #666;
  }

  &__trend-icon {
    margin-right: 4px;

    &.fa-arrow-up {
      color: #28a745;
    }

    &.fa-arrow-down {
      color: #dc3545;
    }

    &.fa-minus {
      color: #6c757d;
    }
  }

  &__trend-text {
    font-weight: 500;
  }

  &__progress {
    width: 100%;
    padding: 0 20px;
  }

  &__progress-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }

  &__progress-label {
    font-size: 14px;
    color: #666;
    font-weight: 500;
  }

  &__progress-value {
    font-size: 18px;
    font-weight: bold;
    color: #333;
  }

  &__progress-bar {
    width: 100%;
    height: 12px;
    background-color: #e9ecef;
    border-radius: 6px;
    overflow: hidden;
  }

  &__progress-fill {
    height: 100%;
    border-radius: 6px;
    transition: width 0.3s ease;
  }

  &__sparkline {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  &__sparkline-value {
    margin-bottom: 12px;
  }

  &__sparkline-chart {
    max-width: 100%;
    height: auto;
  }
}

// Color scheme variations
.dashboard-kpi-widget {
  &--blue .kpi-widget__value {
    color: #5190ef;
  }

  &--green .kpi-widget__value {
    color: #28a745;
  }

  &--red .kpi-widget__value {
    color: #dc3545;
  }

  &--orange .kpi-widget__value {
    color: #fd7e14;
  }

  &--purple .kpi-widget__value {
    color: #6f42c1;
  }
}

@media (max-width: 768px) {
  .kpi-widget__value {
    font-size: 36px;
  }

  .dashboard-kpi-widget__content {
    padding: 16px;
  }
}
</style>
