<template>
  <div class="embedded-widget" :class="{ 'embed-mode': embedMode }">
    <div v-if="loading" class="widget-loading">
      <i class="fas fa-spinner fa-spin"></i>
    </div>

    <div v-else-if="error" class="widget-error">
      <i class="fas fa-exclamation-triangle"></i>
      <p>{{ $t('dashboardEmbed.widgetError') }}</p>
    </div>

    <div v-else class="widget-content">
      <!-- Widget Header -->
      <div v-if="widget.configuration?.title && !embedMode" class="widget-header">
        <h3>{{ widget.configuration.title }}</h3>
        <div class="widget-actions">
          <button
            class="btn btn-sm btn-outline-secondary"
            @click="refreshWidget"
          >
            <i class="fas fa-sync-alt"></i>
          </button>
        </div>
      </div>

      <!-- Widget Body -->
      <div class="widget-body">
        <!-- Chart Widgets -->
        <div v-if="isChartWidget" class="chart-container">
          <canvas :ref="`chart-${widget.id}`"></canvas>
        </div>

        <!-- KPI Widgets -->
        <div v-else-if="widget.widget_type === 'kpi'" class="kpi-container">
          <div class="kpi-value">{{ formatKpiValue(widgetData?.value) }}</div>
          <div class="kpi-label">{{ widget.configuration?.label || 'KPI' }}</div>
          <div v-if="widgetData?.change" class="kpi-change" :class="getChangeClass(widgetData.change)">
            <i :class="getChangeIcon(widgetData.change)"></i>
            {{ formatChange(widgetData.change) }}
          </div>
        </div>

        <!-- Table Widgets -->
        <div v-else-if="widget.widget_type === 'table'" class="table-container">
          <table class="table table-sm">
            <thead>
              <tr>
                <th v-for="column in widgetData?.columns" :key="column.key">
                  {{ column.label }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in widgetData?.rows" :key="index">
                <td v-for="column in widgetData?.columns" :key="column.key">
                  {{ row[column.key] }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Calendar Widgets -->
        <div v-else-if="widget.widget_type === 'calendar'" class="calendar-container">
          <div class="calendar-header">
            <button @click="previousMonth">
              <i class="fas fa-chevron-left"></i>
            </button>
            <span>{{ currentMonthYear }}</span>
            <button @click="nextMonth">
              <i class="fas fa-chevron-right"></i>
            </button>
          </div>
          <div class="calendar-grid">
            <!-- Calendar implementation would go here -->
            <div class="calendar-placeholder">
              {{ $t('dashboardEmbed.calendarPlaceholder') }}
            </div>
          </div>
        </div>

        <!-- Generic Widget Fallback -->
        <div v-else class="generic-widget">
          <div class="widget-icon">
            <i :class="getWidgetIcon(widget.widget_type)"></i>
          </div>
          <div class="widget-info">
            <h4>{{ widget.widget_type }}</h4>
            <p>{{ $t('dashboardEmbed.widgetNotSupported') }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Chart from 'chart.js/auto'

export default {
  name: 'EmbeddedWidget',
  props: {
    widget: {
      type: Object,
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
      widgetData: null,
      chart: null,
      currentDate: new Date()
    }
  },
  computed: {
    isChartWidget() {
      return ['bar', 'line', 'pie', 'doughnut', 'area'].includes(this.widget.widget_type)
    },
    currentMonthYear() {
      return this.currentDate.toLocaleDateString('en-US', { 
        month: 'long', 
        year: 'numeric' 
      })
    }
  },
  async mounted() {
    await this.loadWidgetData()
  },
  beforeDestroy() {
    if (this.chart) {
      this.chart.destroy()
    }
  },
  methods: {
    async loadWidgetData() {
      try {
        this.loading = true
        this.error = null
        
        // Simulate widget data loading
        // In a real implementation, this would fetch data based on widget configuration
        await this.simulateDataLoading()
        
        // Render chart if it's a chart widget
        if (this.isChartWidget) {
          this.$nextTick(() => {
            this.renderChart()
          })
        }
      } catch (error) {
        console.error('Error loading widget data:', error)
        this.error = error.message
        this.handleWidgetError(error)
      } finally {
        this.loading = false
      }
    },
    handleWidgetError(error) {
      this.$emit('error', error)
    },
    async simulateDataLoading() {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // Generate mock data based on widget type
      if (this.isChartWidget) {
        this.widgetData = this.generateChartData()
      } else if (this.widget.widget_type === 'kpi') {
        this.widgetData = this.generateKpiData()
      } else if (this.widget.widget_type === 'table') {
        this.widgetData = this.generateTableData()
      }
    },
    generateChartData() {
      const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
      const data = labels.map(() => Math.floor(Math.random() * 100))
      
      return {
        labels,
        datasets: [{
          label: 'Sample Data',
          data,
          backgroundColor: this.widget.widget_type === 'pie' || this.widget.widget_type === 'doughnut'
            ? ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
            : '#36A2EB',
          borderColor: '#36A2EB',
          borderWidth: 1
        }]
      }
    },
    generateKpiData() {
      return {
        value: Math.floor(Math.random() * 10000),
        change: (Math.random() - 0.5) * 20 // -10% to +10%
      }
    },
    generateTableData() {
      return {
        columns: [
          { key: 'name', label: 'Name' },
          { key: 'value', label: 'Value' },
          { key: 'status', label: 'Status' }
        ],
        rows: [
          { name: 'Item 1', value: 100, status: 'Active' },
          { name: 'Item 2', value: 200, status: 'Inactive' },
          { name: 'Item 3', value: 150, status: 'Active' }
        ]
      }
    },
    renderChart() {
      if (!this.widgetData || !this.isChartWidget) return
      
      const canvas = this.$refs[`chart-${this.widget.id}`]
      if (!canvas) return
      
      const ctx = canvas.getContext('2d')
      
      if (this.chart) {
        this.chart.destroy()
      }
      
      this.chart = new Chart(ctx, {
        type: this.widget.widget_type === 'area' ? 'line' : this.widget.widget_type,
        data: this.widgetData,
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: !this.embedMode || this.widget.widget_type === 'pie' || this.widget.widget_type === 'doughnut'
            }
          },
          scales: this.widget.widget_type === 'pie' || this.widget.widget_type === 'doughnut' ? {} : {
            y: {
              beginAtZero: true
            }
          }
        }
      })
    },
    async refreshWidget() {
      await this.loadWidgetData()
    },
    formatKpiValue(value) {
      if (typeof value === 'number') {
        return value.toLocaleString()
      }
      return value || '0'
    },
    formatChange(change) {
      if (typeof change === 'number') {
        return `${change > 0 ? '+' : ''}${change.toFixed(1)}%`
      }
      return ''
    },
    getChangeClass(change) {
      if (change > 0) return 'positive'
      if (change < 0) return 'negative'
      return 'neutral'
    },
    getChangeIcon(change) {
      if (change > 0) return 'fas fa-arrow-up'
      if (change < 0) return 'fas fa-arrow-down'
      return 'fas fa-minus'
    },
    getWidgetIcon(widgetType) {
      const icons = {
        chart: 'fas fa-chart-bar',
        kpi: 'fas fa-tachometer-alt',
        table: 'fas fa-table',
        calendar: 'fas fa-calendar',
        bar: 'fas fa-chart-bar',
        line: 'fas fa-chart-line',
        pie: 'fas fa-chart-pie',
        doughnut: 'fas fa-chart-pie',
        area: 'fas fa-chart-area'
      }
      return icons[widgetType] || 'fas fa-widget'
    },
    previousMonth() {
      this.currentDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() - 1, 1)
    },
    nextMonth() {
      this.currentDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() + 1, 1)
    }
  }
}
</script>

<style lang="scss" scoped>
.embedded-widget {
  height: 100%;
  display: flex;
  flex-direction: column;
  
  .widget-loading,
  .widget-error {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    color: #6c757d;
    
    i {
      margin-right: 0.5rem;
    }
  }
  
  .widget-content {
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  
  .widget-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border-bottom: 1px solid #e9ecef;
    
    h3 {
      margin: 0;
      font-size: 1rem;
      font-weight: 600;
    }
  }
  
  .widget-body {
    flex: 1;
    padding: 1rem;
    overflow: hidden;
  }
  
  .chart-container {
    height: 100%;
    position: relative;
    
    canvas {
      max-height: 100%;
    }
  }
  
  .kpi-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100%;
    text-align: center;
    
    .kpi-value {
      font-size: 2.5rem;
      font-weight: bold;
      color: #007bff;
      margin-bottom: 0.5rem;
    }
    
    .kpi-label {
      font-size: 1rem;
      color: #6c757d;
      margin-bottom: 1rem;
    }
    
    .kpi-change {
      font-size: 0.875rem;
      font-weight: 500;
      
      &.positive {
        color: #28a745;
      }
      
      &.negative {
        color: #dc3545;
      }
      
      &.neutral {
        color: #6c757d;
      }
      
      i {
        margin-right: 0.25rem;
      }
    }
  }
  
  .table-container {
    height: 100%;
    overflow: auto;
    
    .table {
      margin: 0;
      
      th {
        background-color: #f8f9fa;
        border-top: none;
        font-weight: 600;
        font-size: 0.875rem;
      }
      
      td {
        font-size: 0.875rem;
      }
    }
  }
  
  .calendar-container {
    height: 100%;
    
    .calendar-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
      
      button {
        background: none;
        border: none;
        padding: 0.5rem;
        cursor: pointer;
        
        &:hover {
          background-color: #f8f9fa;
          border-radius: 0.25rem;
        }
      }
      
      span {
        font-weight: 600;
      }
    }
    
    .calendar-grid {
      height: calc(100% - 3rem);
      
      .calendar-placeholder {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
        color: #6c757d;
        font-style: italic;
      }
    }
  }
  
  .generic-widget {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100%;
    text-align: center;
    color: #6c757d;
    
    .widget-icon {
      font-size: 3rem;
      margin-bottom: 1rem;
    }
    
    .widget-info {
      h4 {
        margin-bottom: 0.5rem;
        text-transform: capitalize;
      }
      
      p {
        font-size: 0.875rem;
        margin: 0;
      }
    }
  }
}

// Embed mode adjustments
.embedded-widget.embed-mode {
  .widget-header {
    padding: 0.5rem;
    
    h3 {
      font-size: 0.875rem;
    }
  }
  
  .widget-body {
    padding: 0.5rem;
  }
  
  .kpi-container {
    .kpi-value {
      font-size: 2rem;
    }
  }
}
</style>