import { WidgetType } from '@baserow/modules/dashboard/widgetTypes'
import KPIWidget from '@baserow/modules/dashboard/components/widget/KPIWidget'
import EnhancedChartWidget from '@baserow/modules/dashboard/components/widget/EnhancedChartWidget'
import KPIWidgetSvg from '@baserow/modules/dashboard/assets/images/widgets/kpi_widget.svg'
import BarChartWidgetSvg from '@baserow/modules/dashboard/assets/images/widgets/bar_chart_widget.svg'
import LineChartWidgetSvg from '@baserow/modules/dashboard/assets/images/widgets/line_chart_widget.svg'
import PieChartWidgetSvg from '@baserow/modules/dashboard/assets/images/widgets/pie_chart_widget.svg'
import AreaChartWidgetSvg from '@baserow/modules/dashboard/assets/images/widgets/area_chart_widget.svg'

export class KPIWidgetType extends WidgetType {
  static getType() {
    return 'kpi'
  }

  get name() {
    return this.app.i18n.t('kpiWidget.name')
  }

  get createWidgetImage() {
    return KPIWidgetSvg
  }

  get component() {
    return KPIWidget
  }

  get settingsComponent() {
    // This would be implemented separately
    return null
  }

  get variations() {
    return [
      {
        name: this.app.i18n.t('kpiWidget.number'),
        createWidgetImage: KPIWidgetSvg,
        type: this,
        params: {
          display_format: 'number',
          color_scheme: 'blue',
        },
      },
      {
        name: this.app.i18n.t('kpiWidget.gauge'),
        createWidgetImage: KPIWidgetSvg,
        type: this,
        params: {
          display_format: 'gauge',
          color_scheme: 'blue',
          gauge_min: 0,
          gauge_max: 100,
        },
      },
      {
        name: this.app.i18n.t('kpiWidget.progress'),
        createWidgetImage: KPIWidgetSvg,
        type: this,
        params: {
          display_format: 'progress',
          color_scheme: 'green',
          progress_min: 0,
          progress_max: 100,
        },
      },
      {
        name: this.app.i18n.t('kpiWidget.sparkline'),
        createWidgetImage: KPIWidgetSvg,
        type: this,
        params: {
          display_format: 'sparkline',
          color_scheme: 'purple',
        },
      },
      {
        name: this.app.i18n.t('kpiWidget.percentage'),
        createWidgetImage: KPIWidgetSvg,
        type: this,
        params: {
          display_format: 'number',
          value_format: 'percentage',
          color_scheme: 'green',
        },
      },
      {
        name: this.app.i18n.t('kpiWidget.currency'),
        createWidgetImage: KPIWidgetSvg,
        type: this,
        params: {
          display_format: 'number',
          value_format: 'currency',
          color_scheme: 'orange',
        },
      },
    ]
  }

  isLoading(widget, data) {
    const dataSourceId = widget.data_source_id
    if (data[dataSourceId] && Object.keys(data[dataSourceId]).length !== 0) {
      return false
    }
    return true
  }

  getOrder() {
    return 10
  }
}

export class EnhancedChartWidgetType extends WidgetType {
  static getType() {
    return 'enhanced_chart'
  }

  get name() {
    return this.app.i18n.t('enhancedChartWidget.name')
  }

  get createWidgetImage() {
    return BarChartWidgetSvg
  }

  get component() {
    return EnhancedChartWidget
  }

  get settingsComponent() {
    // This would be implemented separately
    return null
  }

  get variations() {
    return [
      {
        name: this.app.i18n.t('enhancedChartWidget.bar'),
        createWidgetImage: BarChartWidgetSvg,
        type: this,
        params: {
          chart_type: 'bar',
          show_legend: true,
          show_grid: true,
        },
      },
      {
        name: this.app.i18n.t('enhancedChartWidget.stackedBar'),
        createWidgetImage: BarChartWidgetSvg,
        type: this,
        params: {
          chart_type: 'stacked-bar',
          show_legend: true,
          show_grid: true,
        },
      },
      {
        name: this.app.i18n.t('enhancedChartWidget.horizontalBar'),
        createWidgetImage: BarChartWidgetSvg,
        type: this,
        params: {
          chart_type: 'horizontal-bar',
          show_legend: true,
          show_grid: true,
        },
      },
      {
        name: this.app.i18n.t('enhancedChartWidget.line'),
        createWidgetImage: LineChartWidgetSvg,
        type: this,
        params: {
          chart_type: 'line',
          show_legend: true,
          show_grid: true,
        },
      },
      {
        name: this.app.i18n.t('enhancedChartWidget.area'),
        createWidgetImage: AreaChartWidgetSvg,
        type: this,
        params: {
          chart_type: 'area',
          show_legend: true,
          show_grid: true,
        },
      },
      {
        name: this.app.i18n.t('enhancedChartWidget.pie'),
        createWidgetImage: PieChartWidgetSvg,
        type: this,
        params: {
          chart_type: 'pie',
          show_legend: true,
          show_grid: false,
        },
      },
      {
        name: this.app.i18n.t('enhancedChartWidget.donut'),
        createWidgetImage: PieChartWidgetSvg,
        type: this,
        params: {
          chart_type: 'donut',
          show_legend: true,
          show_grid: false,
        },
      },
      {
        name: this.app.i18n.t('enhancedChartWidget.polar'),
        createWidgetImage: PieChartWidgetSvg,
        type: this,
        params: {
          chart_type: 'polar',
          show_legend: true,
          show_grid: false,
        },
      },
      {
        name: this.app.i18n.t('enhancedChartWidget.radar'),
        createWidgetImage: LineChartWidgetSvg,
        type: this,
        params: {
          chart_type: 'radar',
          show_legend: true,
          show_grid: true,
        },
      },
      {
        name: this.app.i18n.t('enhancedChartWidget.scatter'),
        createWidgetImage: LineChartWidgetSvg,
        type: this,
        params: {
          chart_type: 'scatter',
          show_legend: true,
          show_grid: true,
        },
      },
      {
        name: this.app.i18n.t('enhancedChartWidget.bubble'),
        createWidgetImage: LineChartWidgetSvg,
        type: this,
        params: {
          chart_type: 'bubble',
          show_legend: true,
          show_grid: true,
        },
      },
      {
        name: this.app.i18n.t('enhancedChartWidget.combo'),
        createWidgetImage: BarChartWidgetSvg,
        type: this,
        params: {
          chart_type: 'combo',
          show_legend: true,
          show_grid: true,
        },
      },
    ]
  }

  isLoading(widget, data) {
    // Check if any of the data sources are loading
    if (!widget.data_source_ids || widget.data_source_ids.length === 0) {
      return true
    }

    return widget.data_source_ids.some(dataSourceId => {
      const sourceData = data[dataSourceId]
      return !sourceData || Object.keys(sourceData).length === 0
    })
  }

  getOrder() {
    return 20
  }
}

// Enhanced chart sub-types for better organization
export class BarChartWidgetType extends EnhancedChartWidgetType {
  static getType() {
    return 'bar_chart'
  }

  get name() {
    return this.app.i18n.t('enhancedChartWidget.bar')
  }

  get variations() {
    return [
      {
        name: this.app.i18n.t('enhancedChartWidget.bar'),
        createWidgetImage: BarChartWidgetSvg,
        type: this,
        params: {
          chart_type: 'bar',
          show_legend: true,
          show_grid: true,
        },
      },
    ]
  }
}

export class LineChartWidgetType extends EnhancedChartWidgetType {
  static getType() {
    return 'line_chart'
  }

  get name() {
    return this.app.i18n.t('enhancedChartWidget.line')
  }

  get createWidgetImage() {
    return LineChartWidgetSvg
  }

  get variations() {
    return [
      {
        name: this.app.i18n.t('enhancedChartWidget.line'),
        createWidgetImage: LineChartWidgetSvg,
        type: this,
        params: {
          chart_type: 'line',
          show_legend: true,
          show_grid: true,
        },
      },
    ]
  }
}

export class AreaChartWidgetType extends EnhancedChartWidgetType {
  static getType() {
    return 'area_chart'
  }

  get name() {
    return this.app.i18n.t('enhancedChartWidget.area')
  }

  get createWidgetImage() {
    return AreaChartWidgetSvg
  }

  get variations() {
    return [
      {
        name: this.app.i18n.t('enhancedChartWidget.area'),
        createWidgetImage: AreaChartWidgetSvg,
        type: this,
        params: {
          chart_type: 'area',
          show_legend: true,
          show_grid: true,
        },
      },
    ]
  }
}

export class PieChartWidgetType extends EnhancedChartWidgetType {
  static getType() {
    return 'pie_chart'
  }

  get name() {
    return this.app.i18n.t('enhancedChartWidget.pie')
  }

  get createWidgetImage() {
    return PieChartWidgetSvg
  }

  get variations() {
    return [
      {
        name: this.app.i18n.t('enhancedChartWidget.pie'),
        createWidgetImage: PieChartWidgetSvg,
        type: this,
        params: {
          chart_type: 'pie',
          show_legend: true,
          show_grid: false,
        },
      },
      {
        name: this.app.i18n.t('enhancedChartWidget.donut'),
        createWidgetImage: PieChartWidgetSvg,
        type: this,
        params: {
          chart_type: 'donut',
          show_legend: true,
          show_grid: false,
        },
      },
    ]
  }
}

// Advanced chart types
export class HeatmapWidgetType extends WidgetType {
  static getType() {
    return 'heatmap'
  }

  get name() {
    return this.app.i18n.t('heatmapWidget.name')
  }

  get createWidgetImage() {
    return PieChartWidgetSvg // Use a placeholder for now
  }

  get component() {
    return () => import('@baserow/modules/dashboard/components/widget/HeatmapChart')
  }

  get variations() {
    return [
      {
        name: this.app.i18n.t('heatmapWidget.standard'),
        createWidgetImage: PieChartWidgetSvg,
        type: this,
        params: {
          color_scale: ['#f7fbff', '#08519c'],
          cell_size: 20,
        },
      },
    ]
  }

  getOrder() {
    return 30
  }
}

export class GaugeWidgetType extends WidgetType {
  static getType() {
    return 'gauge'
  }

  get name() {
    return this.app.i18n.t('gaugeWidget.name')
  }

  get createWidgetImage() {
    return KPIWidgetSvg
  }

  get component() {
    return () => import('@baserow/modules/dashboard/components/widget/GaugeChart')
  }

  get variations() {
    return [
      {
        name: this.app.i18n.t('gaugeWidget.standard'),
        createWidgetImage: KPIWidgetSvg,
        type: this,
        params: {
          min_value: 0,
          max_value: 100,
          show_labels: true,
        },
      },
    ]
  }

  getOrder() {
    return 25
  }
}