"""
Enhanced widget models for the dashboard system expansion.
Includes new widget types: KPI, Pie Chart, Line Chart, Area Chart.
"""

from django.db import models
from django.contrib.postgres.fields import ArrayField
from .models import Widget


class KPIWidget(Widget):
    """
    KPI (Key Performance Indicator) widget that displays a single metric
    with customizable formatting and comparison values.
    """
    
    data_source = models.ForeignKey(
        "dashboard.DashboardDataSource",
        on_delete=models.PROTECT,
        help_text="Data source for fetching the KPI value.",
    )
    
    # KPI Configuration
    display_format = models.CharField(
        max_length=50,
        choices=[
            ('number', 'Number'),
            ('percentage', 'Percentage'),
            ('currency', 'Currency'),
            ('duration', 'Duration'),
        ],
        default='number',
        help_text="Format for displaying the KPI value"
    )
    
    prefix_text = models.CharField(
        max_length=50,
        blank=True,
        help_text="Text to display before the value"
    )
    
    suffix_text = models.CharField(
        max_length=50,
        blank=True,
        help_text="Text to display after the value"
    )
    
    # Comparison and trend
    comparison_enabled = models.BooleanField(
        default=False,
        help_text="Whether to show comparison with previous period"
    )
    
    comparison_data_source = models.ForeignKey(
        "dashboard.DashboardDataSource",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='kpi_comparison_widgets',
        help_text="Data source for comparison value"
    )
    
    # Visual styling
    color_scheme = models.CharField(
        max_length=20,
        choices=[
            ('blue', 'Blue'),
            ('green', 'Green'),
            ('red', 'Red'),
            ('orange', 'Orange'),
            ('purple', 'Purple'),
            ('custom', 'Custom'),
        ],
        default='blue'
    )
    
    custom_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Custom hex color code (e.g., #FF5733)"
    )


class EnhancedChartWidget(Widget):
    """
    Enhanced chart widget supporting multiple chart types with advanced configuration.
    """
    
    data_sources = models.ManyToManyField(
        "dashboard.DashboardDataSource",
        help_text="Multiple data sources for the chart"
    )
    
    # Chart configuration
    chart_type = models.CharField(
        max_length=20,
        choices=[
            ('bar', 'Bar Chart'),
            ('line', 'Line Chart'),
            ('area', 'Area Chart'),
            ('pie', 'Pie Chart'),
            ('donut', 'Donut Chart'),
            ('mixed', 'Mixed Chart'),
        ],
        default='bar'
    )
    
    # Layout and positioning
    layout_config = models.JSONField(
        default=dict,
        help_text="Layout configuration for drag-and-drop positioning"
    )
    
    # Series configuration for multiple data sources
    series_config = models.JSONField(
        default=list,
        help_text="Configuration for each data series"
    )
    
    # Chart styling
    color_palette = ArrayField(
        models.CharField(max_length=7),
        default=list,
        blank=True,
        help_text="Custom color palette for chart series"
    )
    
    # Advanced options
    show_legend = models.BooleanField(default=True)
    show_grid = models.BooleanField(default=True)
    show_tooltips = models.BooleanField(default=True)
    
    # Animation settings
    enable_animations = models.BooleanField(default=True)
    animation_duration = models.IntegerField(
        default=1000,
        help_text="Animation duration in milliseconds"
    )
    
    # Real-time updates
    auto_refresh = models.BooleanField(
        default=False,
        help_text="Enable automatic data refresh"
    )
    
    refresh_interval = models.IntegerField(
        default=60,
        help_text="Refresh interval in seconds"
    )


class DashboardLayout(models.Model):
    """
    Model to store dashboard layout configuration for drag-and-drop functionality.
    """
    
    dashboard = models.OneToOneField(
        "dashboard.Dashboard",
        on_delete=models.CASCADE,
        related_name='layout_config'
    )
    
    # Grid layout configuration
    grid_columns = models.IntegerField(
        default=12,
        help_text="Number of columns in the grid system"
    )
    
    grid_row_height = models.IntegerField(
        default=60,
        help_text="Height of each grid row in pixels"
    )
    
    # Layout data
    layout_data = models.JSONField(
        default=list,
        help_text="Array of widget layout configurations"
    )
    
    # Responsive breakpoints
    breakpoints = models.JSONField(
        default=dict,
        help_text="Responsive breakpoint configurations"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class WidgetDataAggregation(models.Model):
    """
    Model for storing pre-computed aggregations for efficient data processing.
    """
    
    widget = models.ForeignKey(
        Widget,
        on_delete=models.CASCADE,
        related_name='aggregations'
    )
    
    data_source = models.ForeignKey(
        "dashboard.DashboardDataSource",
        on_delete=models.CASCADE
    )
    
    # Aggregation configuration
    aggregation_type = models.CharField(
        max_length=20,
        choices=[
            ('sum', 'Sum'),
            ('avg', 'Average'),
            ('count', 'Count'),
            ('min', 'Minimum'),
            ('max', 'Maximum'),
            ('median', 'Median'),
            ('std_dev', 'Standard Deviation'),
        ]
    )
    
    field_name = models.CharField(max_length=255)
    group_by_fields = ArrayField(
        models.CharField(max_length=255),
        default=list,
        blank=True
    )
    
    # Cached results
    cached_result = models.JSONField(
        default=dict,
        help_text="Cached aggregation result"
    )
    
    cache_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the cached result expires"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['widget', 'data_source', 'aggregation_type', 'field_name']