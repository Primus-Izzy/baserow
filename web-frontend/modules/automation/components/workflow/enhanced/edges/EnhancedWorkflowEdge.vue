<template>
  <g class="enhanced-workflow-edge">
    <!-- Main edge path -->
    <path
      :d="edgePath"
      :class="[
        'edge-path',
        { conditional: isConditional, animated: isAnimated },
      ]"
      :stroke="edgeColor"
      :stroke-width="strokeWidth"
      fill="none"
      :marker-end="markerEnd"
    />

    <!-- Condition label for conditional edges -->
    <g v-if="isConditional && conditionLabel" class="condition-label">
      <rect
        :x="labelPosition.x - labelWidth / 2"
        :y="labelPosition.y - 12"
        :width="labelWidth"
        height="24"
        rx="12"
        fill="white"
        stroke="#007bff"
        stroke-width="2"
      />
      <text
        :x="labelPosition.x"
        :y="labelPosition.y + 4"
        text-anchor="middle"
        class="condition-text"
        font-size="12"
        font-weight="600"
        fill="#007bff"
      >
        {{ conditionLabel }}
      </text>
    </g>

    <!-- Animation dots for active execution -->
    <circle v-if="isAnimated" class="animation-dot" r="4" fill="#007bff">
      <animateMotion
        :dur="animationDuration"
        repeatCount="indefinite"
        :path="edgePath"
      />
    </circle>
  </g>
</template>

<script>
export default {
  name: 'EnhancedWorkflowEdge',
  props: {
    id: {
      type: String,
      required: true,
    },
    sourceX: {
      type: Number,
      required: true,
    },
    sourceY: {
      type: Number,
      required: true,
    },
    targetX: {
      type: Number,
      required: true,
    },
    targetY: {
      type: Number,
      required: true,
    },
    data: {
      type: Object,
      default: () => ({}),
    },
  },
  computed: {
    isConditional() {
      return this.data.condition !== null && this.data.condition !== undefined
    },

    isAnimated() {
      return this.data.animated || false
    },

    conditionLabel() {
      if (!this.isConditional) return null

      const condition = this.data.condition
      if (typeof condition === 'boolean') {
        return condition ? 'TRUE' : 'FALSE'
      }

      if (typeof condition === 'string') {
        return condition.toUpperCase()
      }

      return 'IF'
    },

    edgeColor() {
      if (this.isConditional) {
        const condition = this.data.condition
        if (condition === true) return '#51cf66'
        if (condition === false) return '#ff6b6b'
        return '#007bff'
      }

      return '#6c757d'
    },

    strokeWidth() {
      return this.isConditional ? 3 : 2
    },

    markerEnd() {
      return 'url(#arrowhead)'
    },

    animationDuration() {
      return '2s'
    },

    edgePath() {
      const { sourceX, sourceY, targetX, targetY } = this

      // Calculate control points for a smooth curve
      const deltaX = targetX - sourceX
      const deltaY = targetY - sourceY

      // Create a smooth S-curve
      const controlPoint1X = sourceX + deltaX * 0.5
      const controlPoint1Y = sourceY + Math.min(deltaY * 0.3, 50)
      const controlPoint2X = targetX - deltaX * 0.5
      const controlPoint2Y = targetY - Math.min(deltaY * 0.3, 50)

      return `M ${sourceX} ${sourceY} C ${controlPoint1X} ${controlPoint1Y}, ${controlPoint2X} ${controlPoint2Y}, ${targetX} ${targetY}`
    },

    labelPosition() {
      // Position the label at the midpoint of the edge
      const midX = (this.sourceX + this.targetX) / 2
      const midY = (this.sourceY + this.targetY) / 2

      return { x: midX, y: midY }
    },

    labelWidth() {
      if (!this.conditionLabel) return 0

      // Estimate width based on text length
      return Math.max(this.conditionLabel.length * 8 + 16, 60)
    },
  },
}
</script>

<style lang="scss" scoped>
.enhanced-workflow-edge {
  .edge-path {
    transition: all 0.3s ease;

    &:hover {
      stroke-width: 4;
    }

    &.conditional {
      stroke-dasharray: none;
    }

    &.animated {
      stroke-dasharray: 8 4;
      animation: dash 1s linear infinite;
    }
  }

  .condition-label {
    pointer-events: none;

    rect {
      filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
    }
  }

  .condition-text {
    user-select: none;
  }

  .animation-dot {
    filter: drop-shadow(0 0 4px rgba(0, 123, 255, 0.6));
  }
}

@keyframes dash {
  to {
    stroke-dashoffset: -12;
  }
}
</style>
