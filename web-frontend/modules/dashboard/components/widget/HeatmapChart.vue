<template>
  <div class="heatmap-chart-container">
    <canvas
      ref="heatmapCanvas"
      class="heatmap-chart"
      :width="canvasWidth"
      :height="canvasHeight"
    ></canvas>

    <div v-if="loading" class="heatmap-chart__loading">
      <div class="loading-spinner"></div>
    </div>

    <div
      v-if="!loading && (!chartData || chartData.length === 0)"
      class="heatmap-chart__no-data"
    >
      <div class="heatmap-chart__no-data-content">
        <i class="fas fa-th heatmap-chart__no-data-icon"></i>
        <p class="heatmap-chart__no-data-text">
          {{ $t('heatmapChart.noData') }}
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HeatmapChart',
  props: {
    chartData: {
      type: Array,
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
  },
  data() {
    return {
      canvasWidth: 400,
      canvasHeight: 300,
      ctx: null,
    }
  },
  computed: {
    colorScale() {
      return this.chartOptions.colorScale || ['#f7fbff', '#08519c']
    },
    cellSize() {
      return this.chartOptions.cellSize || 20
    },
    maxValue() {
      if (!this.chartData || this.chartData.length === 0) return 0
      return Math.max(...this.chartData.map((d) => d.value))
    },
    minValue() {
      if (!this.chartData || this.chartData.length === 0) return 0
      return Math.min(...this.chartData.map((d) => d.value))
    },
  },
  mounted() {
    this.initCanvas()
    this.drawHeatmap()
    window.addEventListener('resize', this.handleResize)
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize)
  },
  watch: {
    chartData: {
      handler() {
        this.drawHeatmap()
      },
      deep: true,
    },
  },
  methods: {
    initCanvas() {
      const canvas = this.$refs.heatmapCanvas
      if (!canvas) return

      this.ctx = canvas.getContext('2d')
      this.updateCanvasSize()
    },
    updateCanvasSize() {
      const container = this.$el
      if (!container) return

      this.canvasWidth = container.clientWidth
      this.canvasHeight = container.clientHeight

      const canvas = this.$refs.heatmapCanvas
      if (canvas) {
        canvas.width = this.canvasWidth
        canvas.height = this.canvasHeight
      }
    },
    drawHeatmap() {
      if (!this.ctx || !this.chartData || this.chartData.length === 0) return

      // Clear canvas
      this.ctx.clearRect(0, 0, this.canvasWidth, this.canvasHeight)

      // Calculate grid dimensions
      const uniqueX = [...new Set(this.chartData.map((d) => d.x))]
      const uniqueY = [...new Set(this.chartData.map((d) => d.y))]

      const cellWidth = this.canvasWidth / uniqueX.length
      const cellHeight = this.canvasHeight / uniqueY.length

      // Draw cells
      this.chartData.forEach((dataPoint) => {
        const x = uniqueX.indexOf(dataPoint.x) * cellWidth
        const y = uniqueY.indexOf(dataPoint.y) * cellHeight
        const color = this.getColorForValue(dataPoint.value)

        this.ctx.fillStyle = color
        this.ctx.fillRect(x, y, cellWidth, cellHeight)

        // Draw border
        this.ctx.strokeStyle = '#fff'
        this.ctx.lineWidth = 1
        this.ctx.strokeRect(x, y, cellWidth, cellHeight)

        // Draw value text if cell is large enough
        if (cellWidth > 30 && cellHeight > 20) {
          this.ctx.fillStyle = this.getTextColor(color)
          this.ctx.font = '12px Arial'
          this.ctx.textAlign = 'center'
          this.ctx.textBaseline = 'middle'
          this.ctx.fillText(
            dataPoint.value.toString(),
            x + cellWidth / 2,
            y + cellHeight / 2
          )
        }
      })
    },
    getColorForValue(value) {
      const ratio = (value - this.minValue) / (this.maxValue - this.minValue)
      return this.interpolateColor(
        this.colorScale[0],
        this.colorScale[1],
        ratio
      )
    },
    interpolateColor(color1, color2, ratio) {
      const hex1 = color1.replace('#', '')
      const hex2 = color2.replace('#', '')

      const r1 = parseInt(hex1.substr(0, 2), 16)
      const g1 = parseInt(hex1.substr(2, 2), 16)
      const b1 = parseInt(hex1.substr(4, 2), 16)

      const r2 = parseInt(hex2.substr(0, 2), 16)
      const g2 = parseInt(hex2.substr(2, 2), 16)
      const b2 = parseInt(hex2.substr(4, 2), 16)

      const r = Math.round(r1 + (r2 - r1) * ratio)
      const g = Math.round(g1 + (g2 - g1) * ratio)
      const b = Math.round(b1 + (b2 - b1) * ratio)

      return `rgb(${r}, ${g}, ${b})`
    },
    getTextColor(backgroundColor) {
      // Simple contrast calculation
      const rgb = backgroundColor.match(/\d+/g)
      if (!rgb) return '#000'

      const brightness =
        (parseInt(rgb[0]) * 299 +
          parseInt(rgb[1]) * 587 +
          parseInt(rgb[2]) * 114) /
        1000
      return brightness > 128 ? '#000' : '#fff'
    },
    handleResize() {
      this.updateCanvasSize()
      this.drawHeatmap()
    },
  },
}
</script>

<style lang="scss" scoped>
.heatmap-chart-container {
  position: relative;
  height: 100%;
  width: 100%;
  min-height: 200px;
}

.heatmap-chart {
  width: 100%;
  height: 100%;
}

.heatmap-chart__loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.8);
}

.heatmap-chart__no-data {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(
    135deg,
    rgba(81, 144, 239, 0.05) 0%,
    rgba(81, 144, 239, 0.02) 100%
  );
  border: 2px dashed rgba(81, 144, 239, 0.2);
  border-radius: 8px;
}

.heatmap-chart__no-data-content {
  text-align: center;
  color: #666;
}

.heatmap-chart__no-data-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.heatmap-chart__no-data-text {
  font-size: 16px;
  margin: 0;
  opacity: 0.7;
}

@media (max-width: 768px) {
  .heatmap-chart-container {
    min-height: 150px;
  }

  .heatmap-chart__no-data-icon {
    font-size: 36px;
    margin-bottom: 12px;
  }

  .heatmap-chart__no-data-text {
    font-size: 14px;
  }
}
</style>
