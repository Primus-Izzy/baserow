<template>
  <div class="enhanced-chart-container">
    <component
      v-if="chartData.datasets.length > 0 && !loading"
      :is="chartComponent"
      :data="processedChartData"
      :options="processedChartOptions"
      class="enhanced-chart"
      @chart:render="onChartRender"
    />
    
    <div v-else-if="loading" class="enhanced-chart__loading">
      <div class="loading-spinner"></div>
    </div>

    <div v-else class="enhanced-chart__no-data">
      <div class="enhanced-chart__no-data-content">
        <i class="fas fa-chart-bar enhanced-chart__no-data-icon"></i>
        <p class="enhanced-chart__no-data-text">
          {{ $t('enhancedChart.noData') }}
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import {
  Chart as ChartJS,
  ArcElement,
  LineElement,
  BarElement,
  PointElement,
  BarController,
  BubbleController,
  DoughnutController,
  LineController,
  PieController,
  PolarAreaController,
  RadarController,
  ScatterController,
  CategoryScale,
  LinearScale,
  LogarithmicScale,
  RadialLinearScale,
  TimeScale,
  TimeSeriesScale,
  Decimation,
  Filler,
  Legend,
  Title,
  Tooltip,
  SubTitle,
  Colors,
} from 'chart.js'

import {
  Bar,
  Line,
  Pie,
  Doughnut,
  PolarArea,
  Radar,
  Scatter,
  Bubble,
} from 'vue-chartjs'

// Register Chart.js components
ChartJS.register(
  ArcElement,
  LineElement,
  BarElement,
  PointElement,
  BarController,
  BubbleController,
  DoughnutController,
  LineController,
  PieController,
  PolarAreaController,
  RadarController,
  ScatterController,
  CategoryScale,
  LinearScale,
  LogarithmicScale,
  RadialLinearScale,
  TimeScale,
  TimeSeriesScale,
  Decimation,
  Filler,
  Legend,
  Title,
  Tooltip,
  SubTitle,
  Colors
)

export default {
  name: 'EnhancedChart',
  components: {
    Bar,
    Line,
    Pie,
    Doughnut,
    PolarArea,
    Radar,
    Scatter,
    Bubble,
  },
  props: {
    chartType: {
      type: String,
      required: true,
      validator: (value) => {
        return [
          'bar', 'line', 'area', 'pie', 'donut', 'mixed',
          'polar', 'radar', 'scatter', 'bubble', 'stacked-bar',
          'horizontal-bar', 'combo'
        ].includes(value)
      }
    },
    chartData: {
      type: Object,
      required: true,
    },
    chartOptions: {
      type: Object,
      default: () => ({}),
    },
    loading: {
      type: Boolean,
      default: false,
    },
    realTimeEnabled: {
      type: Boolean,
      default: false,
    },
    refreshInterval: {
      type: Number,
      default: 30000, // 30 seconds
    },
  },
  data() {
    return {
      chartInstance: null,
      realTimeInterval: null,
    }
  },
  computed: {
    chartComponent() {
      const componentMap = {
        bar: 'Bar',
        'stacked-bar': 'Bar',
        'horizontal-bar': 'Bar',
        line: 'Line',
        area: 'Line',
        pie: 'Pie',
        donut: 'Doughnut',
        polar: 'PolarArea',
        radar: 'Radar',
        scatter: 'Scatter',
        bubble: 'Bubble',
        mixed: 'Bar',
        combo: 'Bar',
      }
      
      return componentMap[this.chartType] || 'Bar'
    },
    processedChartData() {
      const data = { ...this.chartData }
      
      // Process area charts
      if (this.chartType === 'area') {
        data.datasets = data.datasets.map(dataset => ({
          ...dataset,
          fill: true,
          backgroundColor: this.addAlpha(dataset.backgroundColor || dataset.borderColor, 0.2),
        }))
      }
      
      // Process stacked bar charts
      if (this.chartType === 'stacked-bar') {
        data.datasets = data.datasets.map(dataset => ({
          ...dataset,
          stack: dataset.stack || 'Stack 0',
        }))
      }
      
      // Process mixed/combo charts
      if (this.chartType === 'mixed' || this.chartType === 'combo') {
        data.datasets = data.datasets.map(dataset => ({
          ...dataset,
          type: dataset.type || 'bar',
        }))
      }
      
      return data
    },
    processedChartOptions() {
      const options = { ...this.chartOptions }
      
      // Add responsive design options
      options.responsive = true
      options.maintainAspectRatio = false
      
      // Configure for horizontal bar charts
      if (this.chartType === 'horizontal-bar') {
        options.indexAxis = 'y'
      }
      
      // Configure for stacked charts
      if (this.chartType === 'stacked-bar') {
        options.scales = {
          ...options.scales,
          x: {
            ...options.scales?.x,
            stacked: true,
          },
          y: {
            ...options.scales?.y,
            stacked: true,
          },
        }
      }
      
      // Mobile optimizations
      if (this.isMobile) {
        options.plugins = {
          ...options.plugins,
          legend: {
            ...options.plugins?.legend,
            position: 'bottom',
            labels: {
              ...options.plugins?.legend?.labels,
              boxWidth: 12,
              padding: 15,
              font: {
                size: 11,
              },
            },
          },
          tooltip: {
            ...options.plugins?.tooltip,
            titleFont: {
              size: 11,
            },
            bodyFont: {
              size: 10,
            },
          },
        }
      }
      
      return options
    },
    isMobile() {
      return window.innerWidth <= 768
    },
  },
  mounted() {
    this.setupRealTimeUpdates()
    window.addEventListener('resize', this.handleResize)
  },
  beforeDestroy() {
    this.clearRealTimeUpdates()
    window.removeEventListener('resize', this.handleResize)
  },
  methods: {
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
      
      // If already rgba, modify alpha
      if (color.startsWith('rgba')) {
        return color.replace(/[\d\.]+\)$/g, `${alpha})`)
      }
      
      // If rgb, convert to rgba
      if (color.startsWith('rgb')) {
        return color.replace('rgb', 'rgba').replace(')', `, ${alpha})`)
      }
      
      return color
    },
    onChartRender(chart) {
      this.chartInstance = chart
      this.$emit('chart-ready', chart)
    },
    setupRealTimeUpdates() {
      if (this.realTimeEnabled && this.refreshInterval > 0) {
        this.realTimeInterval = setInterval(() => {
          this.$emit('refresh-data')
        }, this.refreshInterval)
      }
    },
    clearRealTimeUpdates() {
      if (this.realTimeInterval) {
        clearInterval(this.realTimeInterval)
        this.realTimeInterval = null
      }
    },
    handleResize() {
      if (this.chartInstance) {
        this.chartInstance.resize()
      }
    },
    updateChartData(newData) {
      if (this.chartInstance) {
        // Smooth data updates for real-time charts
        this.chartInstance.data = newData
        this.chartInstance.update('none') // No animation for real-time updates
      }
    },
    exportChart(format = 'png') {
      if (this.chartInstance) {
        const canvas = this.chartInstance.canvas
        const url = canvas.toDataURL(`image/${format}`)
        
        // Create download link
        const link = document.createElement('a')
        link.download = `chart.${format}`
        link.href = url
        link.click()
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.enhanced-chart-container {
  position: relative;
  height: 100%;
  width: 100%;
  min-height: 200px;
}

.enhanced-chart {
  height: 100% !important;
  width: 100% !important;
}

.enhanced-chart__loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 200px;
}

.enhanced-chart__no-data {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 200px;
  background: linear-gradient(
    135deg,
    rgba(81, 144, 239, 0.05) 0%,
    rgba(81, 144, 239, 0.02) 100%
  );
  border: 2px dashed rgba(81, 144, 239, 0.2);
  border-radius: 8px;
}

.enhanced-chart__no-data-content {
  text-align: center;
  color: #666;
}

.enhanced-chart__no-data-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.enhanced-chart__no-data-text {
  font-size: 16px;
  margin: 0;
  opacity: 0.7;
}

@media (max-width: 768px) {
  .enhanced-chart-container {
    min-height: 150px;
  }
  
  .enhanced-chart__no-data-icon {
    font-size: 36px;
    margin-bottom: 12px;
  }
  
  .enhanced-chart__no-data-text {
    font-size: 14px;
  }
}
</style>