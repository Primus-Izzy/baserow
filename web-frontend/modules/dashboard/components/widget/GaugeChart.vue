<template>
  <div class="gauge-chart-container">
    <canvas
      ref="gaugeCanvas"
      class="gauge-chart"
      :width="canvasSize"
      :height="canvasSize"
    ></canvas>

    <div class="gauge-chart__value">
      <span class="gauge-chart__value-number">{{ displayValue }}</span>
      <span v-if="unit" class="gauge-chart__value-unit">{{ unit }}</span>
    </div>

    <div v-if="loading" class="gauge-chart__loading">
      <div class="loading-spinner"></div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GaugeChart',
  props: {
    value: {
      type: Number,
      required: true,
    },
    minValue: {
      type: Number,
      default: 0,
    },
    maxValue: {
      type: Number,
      default: 100,
    },
    unit: {
      type: String,
      default: '',
    },
    colorRanges: {
      type: Array,
      default: () => [
        { min: 0, max: 30, color: '#dc3545' },
        { min: 30, max: 70, color: '#ffc107' },
        { min: 70, max: 100, color: '#28a745' },
      ],
    },
    showLabels: {
      type: Boolean,
      default: true,
    },
    loading: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      canvasSize: 200,
      ctx: null,
      animationFrame: null,
      currentValue: 0,
    }
  },
  computed: {
    displayValue() {
      return Math.round(this.currentValue * 10) / 10
    },
    normalizedValue() {
      return Math.max(
        0,
        Math.min(
          100,
          ((this.value - this.minValue) / (this.maxValue - this.minValue)) * 100
        )
      )
    },
    valueColor() {
      const range = this.colorRanges.find(
        (r) => this.normalizedValue >= r.min && this.normalizedValue <= r.max
      )
      return range ? range.color : '#6c757d'
    },
  },
  mounted() {
    this.initCanvas()
    this.animateToValue()
    window.addEventListener('resize', this.handleResize)
  },
  beforeDestroy() {
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame)
    }
    window.removeEventListener('resize', this.handleResize)
  },
  watch: {
    value() {
      this.animateToValue()
    },
  },
  methods: {
    initCanvas() {
      const canvas = this.$refs.gaugeCanvas
      if (!canvas) return

      this.ctx = canvas.getContext('2d')
      this.updateCanvasSize()
      this.drawGauge()
    },
    updateCanvasSize() {
      const container = this.$el
      if (!container) return

      const size = Math.min(container.clientWidth, container.clientHeight, 300)
      this.canvasSize = size

      const canvas = this.$refs.gaugeCanvas
      if (canvas) {
        canvas.width = size
        canvas.height = size
      }
    },
    animateToValue() {
      const startValue = this.currentValue
      const endValue = this.value
      const duration = 1000 // 1 second
      const startTime = Date.now()

      const animate = () => {
        const elapsed = Date.now() - startTime
        const progress = Math.min(elapsed / duration, 1)

        // Easing function
        const easeOutCubic = 1 - Math.pow(1 - progress, 3)

        this.currentValue = startValue + (endValue - startValue) * easeOutCubic
        this.drawGauge()

        if (progress < 1) {
          this.animationFrame = requestAnimationFrame(animate)
        }
      }

      animate()
    },
    drawGauge() {
      if (!this.ctx) return

      const size = this.canvasSize
      const centerX = size / 2
      const centerY = size / 2
      const radius = size * 0.35

      // Clear canvas
      this.ctx.clearRect(0, 0, size, size)

      // Draw background arc
      this.drawArc(centerX, centerY, radius, -Math.PI, 0, '#e9ecef', 8)

      // Draw color ranges
      this.colorRanges.forEach((range) => {
        const startAngle = -Math.PI + (range.min / 100) * Math.PI
        const endAngle = -Math.PI + (range.max / 100) * Math.PI
        this.drawArc(
          centerX,
          centerY,
          radius,
          startAngle,
          endAngle,
          range.color,
          8
        )
      })

      // Draw value arc
      const valueAngle = -Math.PI + (this.normalizedValue / 100) * Math.PI
      this.drawArc(
        centerX,
        centerY,
        radius - 15,
        -Math.PI,
        valueAngle,
        this.valueColor,
        12
      )

      // Draw needle
      this.drawNeedle(centerX, centerY, radius - 30, valueAngle)

      // Draw center circle
      this.ctx.beginPath()
      this.ctx.arc(centerX, centerY, 8, 0, 2 * Math.PI)
      this.ctx.fillStyle = '#495057'
      this.ctx.fill()

      // Draw labels
      if (this.showLabels) {
        this.drawLabels(centerX, centerY, radius)
      }
    },
    drawArc(x, y, radius, startAngle, endAngle, color, lineWidth) {
      this.ctx.beginPath()
      this.ctx.arc(x, y, radius, startAngle, endAngle)
      this.ctx.strokeStyle = color
      this.ctx.lineWidth = lineWidth
      this.ctx.lineCap = 'round'
      this.ctx.stroke()
    },
    drawNeedle(x, y, length, angle) {
      this.ctx.save()
      this.ctx.translate(x, y)
      this.ctx.rotate(angle)

      this.ctx.beginPath()
      this.ctx.moveTo(0, -3)
      this.ctx.lineTo(length, 0)
      this.ctx.lineTo(0, 3)
      this.ctx.closePath()

      this.ctx.fillStyle = '#495057'
      this.ctx.fill()

      this.ctx.restore()
    },
    drawLabels(centerX, centerY, radius) {
      this.ctx.fillStyle = '#6c757d'
      this.ctx.font = '12px Arial'
      this.ctx.textAlign = 'center'
      this.ctx.textBaseline = 'middle'

      // Draw min value
      const minX = centerX - radius * 0.8
      const minY = centerY + 10
      this.ctx.fillText(this.minValue.toString(), minX, minY)

      // Draw max value
      const maxX = centerX + radius * 0.8
      const maxY = centerY + 10
      this.ctx.fillText(this.maxValue.toString(), maxX, maxY)
    },
    handleResize() {
      this.updateCanvasSize()
      this.drawGauge()
    },
  },
}
</script>

<style lang="scss" scoped>
.gauge-chart-container {
  position: relative;
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.gauge-chart {
  max-width: 100%;
  max-height: 70%;
}

.gauge-chart__value {
  margin-top: 10px;
  text-align: center;
}

.gauge-chart__value-number {
  font-size: 24px;
  font-weight: bold;
  color: #495057;
}

.gauge-chart__value-unit {
  font-size: 14px;
  color: #6c757d;
  margin-left: 4px;
}

.gauge-chart__loading {
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

@media (max-width: 768px) {
  .gauge-chart__value-number {
    font-size: 20px;
  }

  .gauge-chart__value-unit {
    font-size: 12px;
  }
}
</style>
