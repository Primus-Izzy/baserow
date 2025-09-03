<template>
  <div class="chart-configuration">
    <div class="chart-configuration__section">
      <h3 class="chart-configuration__section-title">Chart Type</h3>
      <div class="chart-configuration__chart-types">
        <div
          v-for="type in availableChartTypes"
          :key="type.value"
          class="chart-configuration__chart-type"
          :class="{
            'chart-configuration__chart-type--active':
              configuration.chart_type === type.value,
          }"
          @click="updateConfiguration('chart_type', type.value)"
        >
          <i
            :class="type.icon"
            class="chart-configuration__chart-type-icon"
          ></i>
          <span class="chart-configuration__chart-type-label">{{
            type.label
          }}</span>
        </div>
      </div>
    </div>

    <div class="chart-configuration__section">
      <h3 class="chart-configuration__section-title">Display Options</h3>
      <div class="chart-configuration__options">
        <label class="chart-configuration__option">
          <input
            v-model="configuration.show_legend"
            type="checkbox"
            @change="updateConfiguration('show_legend', $event.target.checked)"
          />
          <span>Show Legend</span>
        </label>

        <label class="chart-configuration__option">
          <input
            v-model="configuration.show_grid"
            type="checkbox"
            @change="updateConfiguration('show_grid', $event.target.checked)"
          />
          <span>Show Grid</span>
        </label>

        <label class="chart-configuration__option">
          <input
            v-model="configuration.show_tooltips"
            type="checkbox"
            @change="
              updateConfiguration('show_tooltips', $event.target.checked)
            "
          />
          <span>Show Tooltips</span>
        </label>

        <label class="chart-configuration__option">
          <input
            v-model="configuration.enable_animations"
            type="checkbox"
            @change="
              updateConfiguration('enable_animations', $event.target.checked)
            "
          />
          <span>Enable Animations</span>
        </label>
      </div>
    </div>

    <div
      v-if="configuration.enable_animations"
      class="chart-configuration__section"
    >
      <h3 class="chart-configuration__section-title">Animation Settings</h3>
      <div class="chart-configuration__field">
        <label>Animation Duration (ms)</label>
        <input
          v-model.number="configuration.animation_duration"
          type="number"
          min="0"
          max="5000"
          step="100"
          @input="
            updateConfiguration('animation_duration', $event.target.value)
          "
        />
      </div>
    </div>

    <div class="chart-configuration__section">
      <h3 class="chart-configuration__section-title">Real-time Updates</h3>
      <div class="chart-configuration__options">
        <label class="chart-configuration__option">
          <input
            v-model="configuration.real_time_enabled"
            type="checkbox"
            @change="
              updateConfiguration('real_time_enabled', $event.target.checked)
            "
          />
          <span>Enable Real-time Updates</span>
        </label>

        <label
          v-if="configuration.real_time_enabled"
          class="chart-configuration__option"
        >
          <input
            v-model="configuration.use_websocket"
            type="checkbox"
            @change="
              updateConfiguration('use_websocket', $event.target.checked)
            "
          />
          <span>Use WebSocket (faster updates)</span>
        </label>
      </div>

      <div
        v-if="configuration.real_time_enabled"
        class="chart-configuration__field"
      >
        <label>Refresh Interval (seconds)</label>
        <select
          v-model="configuration.refresh_interval"
          @change="updateConfiguration('refresh_interval', $event.target.value)"
        >
          <option value="5">5 seconds</option>
          <option value="10">10 seconds</option>
          <option value="30">30 seconds</option>
          <option value="60">1 minute</option>
          <option value="300">5 minutes</option>
          <option value="900">15 minutes</option>
        </select>
      </div>
    </div>

    <div class="chart-configuration__section">
      <h3 class="chart-configuration__section-title">Color Scheme</h3>
      <div class="chart-configuration__color-schemes">
        <div
          v-for="scheme in colorSchemes"
          :key="scheme.name"
          class="chart-configuration__color-scheme"
          :class="{
            'chart-configuration__color-scheme--active':
              configuration.color_scheme === scheme.name,
          }"
          @click="updateConfiguration('color_scheme', scheme.name)"
        >
          <div class="chart-configuration__color-preview">
            <div
              v-for="color in scheme.colors.slice(0, 4)"
              :key="color"
              class="chart-configuration__color-swatch"
              :style="{ backgroundColor: color }"
            ></div>
          </div>
          <span class="chart-configuration__color-scheme-name">{{
            scheme.label
          }}</span>
        </div>
      </div>
    </div>

    <div v-if="isStackedChart" class="chart-configuration__section">
      <h3 class="chart-configuration__section-title">Stacking Options</h3>
      <div class="chart-configuration__field">
        <label>Stack Mode</label>
        <select
          v-model="configuration.stack_mode"
          @change="updateConfiguration('stack_mode', $event.target.value)"
        >
          <option value="normal">Normal</option>
          <option value="percent">Percentage</option>
        </select>
      </div>
    </div>

    <div v-if="hasAxes" class="chart-configuration__section">
      <h3 class="chart-configuration__section-title">Axis Configuration</h3>
      <div class="chart-configuration__axes">
        <div class="chart-configuration__axis">
          <h4>X-Axis</h4>
          <label class="chart-configuration__option">
            <input
              v-model="configuration.x_axis_display"
              type="checkbox"
              @change="
                updateConfiguration('x_axis_display', $event.target.checked)
              "
            />
            <span>Show X-Axis</span>
          </label>
          <div
            v-if="configuration.x_axis_display"
            class="chart-configuration__field"
          >
            <label>X-Axis Label</label>
            <input
              v-model="configuration.x_axis_label"
              type="text"
              placeholder="Enter X-axis label"
              @input="updateConfiguration('x_axis_label', $event.target.value)"
            />
          </div>
        </div>

        <div class="chart-configuration__axis">
          <h4>Y-Axis</h4>
          <label class="chart-configuration__option">
            <input
              v-model="configuration.y_axis_display"
              type="checkbox"
              @change="
                updateConfiguration('y_axis_display', $event.target.checked)
              "
            />
            <span>Show Y-Axis</span>
          </label>
          <div
            v-if="configuration.y_axis_display"
            class="chart-configuration__field"
          >
            <label>Y-Axis Label</label>
            <input
              v-model="configuration.y_axis_label"
              type="text"
              placeholder="Enter Y-axis label"
              @input="updateConfiguration('y_axis_label', $event.target.value)"
            />
          </div>
        </div>
      </div>
    </div>

    <div class="chart-configuration__section">
      <h3 class="chart-configuration__section-title">Export Options</h3>
      <div class="chart-configuration__export-buttons">
        <button
          class="chart-configuration__export-button"
          @click="exportChart('png')"
        >
          Export as PNG
        </button>
        <button
          class="chart-configuration__export-button"
          @click="exportChart('pdf')"
        >
          Export as PDF
        </button>
        <button
          class="chart-configuration__export-button"
          @click="exportChart('svg')"
        >
          Export as SVG
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ChartConfiguration',
  props: {
    configuration: {
      type: Object,
      required: true,
    },
    chartInstance: {
      type: Object,
      default: null,
    },
  },
  data() {
    return {
      availableChartTypes: [
        { value: 'bar', label: 'Bar Chart', icon: 'fas fa-chart-bar' },
        {
          value: 'stacked-bar',
          label: 'Stacked Bar',
          icon: 'fas fa-chart-bar',
        },
        {
          value: 'horizontal-bar',
          label: 'Horizontal Bar',
          icon: 'fas fa-chart-bar',
        },
        { value: 'line', label: 'Line Chart', icon: 'fas fa-chart-line' },
        { value: 'area', label: 'Area Chart', icon: 'fas fa-chart-area' },
        { value: 'pie', label: 'Pie Chart', icon: 'fas fa-chart-pie' },
        { value: 'donut', label: 'Donut Chart', icon: 'fas fa-chart-pie' },
        { value: 'polar', label: 'Polar Area', icon: 'fas fa-chart-pie' },
        { value: 'radar', label: 'Radar Chart', icon: 'fas fa-chart-line' },
        { value: 'scatter', label: 'Scatter Plot', icon: 'fas fa-braille' },
        { value: 'bubble', label: 'Bubble Chart', icon: 'fas fa-circle' },
        { value: 'combo', label: 'Combo Chart', icon: 'fas fa-chart-bar' },
      ],
      colorSchemes: [
        {
          name: 'default',
          label: 'Default',
          colors: ['#5190ef', '#28a745', '#ffc107', '#dc3545', '#6f42c1'],
        },
        {
          name: 'blue',
          label: 'Blue Tones',
          colors: ['#0d6efd', '#6610f2', '#6f42c1', '#d63384', '#dc3545'],
        },
        {
          name: 'green',
          label: 'Green Tones',
          colors: ['#198754', '#20c997', '#0dcaf0', '#6610f2', '#6f42c1'],
        },
        {
          name: 'warm',
          label: 'Warm Colors',
          colors: ['#fd7e14', '#ffc107', '#dc3545', '#d63384', '#6f42c1'],
        },
        {
          name: 'cool',
          label: 'Cool Colors',
          colors: ['#0dcaf0', '#20c997', '#198754', '#6610f2', '#6f42c1'],
        },
        {
          name: 'monochrome',
          label: 'Monochrome',
          colors: ['#212529', '#495057', '#6c757d', '#adb5bd', '#dee2e6'],
        },
      ],
    }
  },
  computed: {
    isStackedChart() {
      return this.configuration.chart_type === 'stacked-bar'
    },
    hasAxes() {
      return !['pie', 'donut', 'polar'].includes(this.configuration.chart_type)
    },
  },
  methods: {
    updateConfiguration(key, value) {
      this.$emit('update-configuration', { [key]: value })
    },
    exportChart(format) {
      if (this.chartInstance) {
        this.$emit('export-chart', format)
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.chart-configuration {
  padding: 20px;
  max-height: 600px;
  overflow-y: auto;

  &__section {
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid #e9ecef;

    &:last-child {
      border-bottom: none;
    }
  }

  &__section-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 12px;
    color: #333;
  }

  &__chart-types {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 8px;
  }

  &__chart-type {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 12px 8px;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;

    &:hover {
      border-color: #5190ef;
      background-color: #f8f9fa;
    }

    &--active {
      border-color: #5190ef;
      background-color: #e7f3ff;
    }
  }

  &__chart-type-icon {
    font-size: 20px;
    margin-bottom: 4px;
    color: #666;
  }

  &__chart-type-label {
    font-size: 12px;
    text-align: center;
    color: #666;
  }

  &__options {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  &__option {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;

    input[type='checkbox'] {
      margin: 0;
    }
  }

  &__field {
    margin-bottom: 12px;

    label {
      display: block;
      font-size: 14px;
      font-weight: 500;
      margin-bottom: 4px;
      color: #333;
    }

    input,
    select {
      width: 100%;
      padding: 8px 12px;
      border: 1px solid #ddd;
      border-radius: 4px;
      font-size: 14px;

      &:focus {
        outline: none;
        border-color: #5190ef;
        box-shadow: 0 0 0 2px rgba(81, 144, 239, 0.2);
      }
    }
  }

  &__color-schemes {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 12px;
  }

  &__color-scheme {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 8px;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;

    &:hover {
      border-color: #5190ef;
    }

    &--active {
      border-color: #5190ef;
      background-color: #e7f3ff;
    }
  }

  &__color-preview {
    display: flex;
    gap: 2px;
    margin-bottom: 4px;
  }

  &__color-swatch {
    width: 16px;
    height: 16px;
    border-radius: 2px;
  }

  &__color-scheme-name {
    font-size: 12px;
    color: #666;
  }

  &__axes {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }

  &__axis {
    h4 {
      font-size: 14px;
      font-weight: 600;
      margin-bottom: 8px;
      color: #333;
    }
  }

  &__export-buttons {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }

  &__export-button {
    padding: 8px 16px;
    background-color: #5190ef;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    transition: background-color 0.2s ease;

    &:hover {
      background-color: #4080df;
    }
  }
}

@media (max-width: 768px) {
  .chart-configuration {
    padding: 16px;

    &__chart-types {
      grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    }

    &__color-schemes {
      grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
    }

    &__axes {
      grid-template-columns: 1fr;
    }

    &__export-buttons {
      flex-direction: column;
    }
  }
}
</style>
