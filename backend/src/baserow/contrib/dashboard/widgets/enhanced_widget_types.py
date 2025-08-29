"""
Enhanced widget types for the dashboard system expansion.
"""

from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta

from baserow.contrib.dashboard.data_sources.handler import DashboardDataSourceHandler
from baserow.contrib.dashboard.data_sources.models import DashboardDataSource
from baserow.contrib.dashboard.types import WidgetDict
from baserow.contrib.dashboard.widgets.models import Widget
from baserow.contrib.integrations.local_baserow.service_types import (
    LocalBaserowAggregateRowsUserServiceType,
)
from baserow.core.services.registries import service_type_registry

from .enhanced_widget_models import (
    KPIWidget, 
    EnhancedChartWidget, 
    DashboardLayout,
    WidgetDataAggregation
)
from .registries import WidgetType


class KPIWidgetType(WidgetType):
    """
    KPI Widget Type for displaying key performance indicators.
    """
    type = "kpi"
    model_class = KPIWidget
    serializer_field_names = [
        "data_source_id", 
        "display_format", 
        "prefix_text", 
        "suffix_text",
        "comparison_enabled",
        "comparison_data_source_id",
        "color_scheme",
        "custom_color"
    ]
    serializer_field_overrides = {
        "data_source_id": serializers.PrimaryKeyRelatedField(
            queryset=DashboardDataSource.objects.all(),
            required=False,
            default=None,
            help_text="References a data source field for the KPI value.",
        ),
        "comparison_data_source_id": serializers.PrimaryKeyRelatedField(
            queryset=DashboardDataSource.objects.all(),
            required=False,
            default=None,
            allow_null=True,
            help_text="References a data source for comparison value.",
        ),
        "display_format": serializers.ChoiceField(
            choices=[
                ('number', 'Number'),
                ('percentage', 'Percentage'),
                ('currency', 'Currency'),
                ('duration', 'Duration'),
            ],
            default='number'
        ),
        "color_scheme": serializers.ChoiceField(
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
    }

    class SerializedDict(WidgetDict):
        data_source_id: int
        display_format: str
        prefix_text: str
        suffix_text: str
        comparison_enabled: bool
        comparison_data_source_id: int
        color_scheme: str
        custom_color: str

    def prepare_value_for_db(self, values: dict, instance: Widget | None = None):
        if instance is None:
            # Auto-create data source for new KPI widgets
            available_name = DashboardDataSourceHandler().find_unused_data_source_name(
                values["dashboard"], "KPIDataSource"
            )
            data_source = DashboardDataSourceHandler().create_data_source(
                dashboard=values["dashboard"],
                name=available_name,
                service_type=service_type_registry.get(
                    LocalBaserowAggregateRowsUserServiceType.type
                ),
            )
            values["data_source"] = data_source
        return values

    def get_aggregated_data(self, widget: KPIWidget):
        """
        Get or compute aggregated data for the KPI widget.
        """
        # Check for cached aggregation
        aggregation = WidgetDataAggregation.objects.filter(
            widget=widget,
            data_source=widget.data_source,
            cache_expires_at__gt=timezone.now()
        ).first()
        
        if aggregation:
            return aggregation.cached_result
        
        # Compute new aggregation
        # This would integrate with the existing data source system
        # For now, return a placeholder structure
        result = {
            'value': 0,
            'formatted_value': '0',
            'comparison_value': None,
            'trend': None
        }
        
        # Cache the result
        WidgetDataAggregation.objects.update_or_create(
            widget=widget,
            data_source=widget.data_source,
            aggregation_type='sum',  # This would be configurable
            field_name='default',
            defaults={
                'cached_result': result,
                'cache_expires_at': timezone.now() + timedelta(minutes=15)
            }
        )
        
        return result


class EnhancedChartWidgetType(WidgetType):
    """
    Enhanced Chart Widget Type supporting multiple chart types and data sources.
    """
    type = "enhanced_chart"
    model_class = EnhancedChartWidget
    serializer_field_names = [
        "chart_type",
        "layout_config", 
        "series_config",
        "color_palette",
        "show_legend",
        "show_grid", 
        "show_tooltips",
        "enable_animations",
        "animation_duration",
        "auto_refresh",
        "refresh_interval"
    ]
    serializer_field_overrides = {
        "chart_type": serializers.ChoiceField(
            choices=[
                ('bar', 'Bar Chart'),
                ('line', 'Line Chart'),
                ('area', 'Area Chart'),
                ('pie', 'Pie Chart'),
                ('donut', 'Donut Chart'),
                ('mixed', 'Mixed Chart'),
            ],
            default='bar'
        ),
        "layout_config": serializers.JSONField(default=dict),
        "series_config": serializers.JSONField(default=list),
        "color_palette": serializers.ListField(
            child=serializers.CharField(max_length=7),
            default=list
        ),
    }

    class SerializedDict(WidgetDict):
        chart_type: str
        layout_config: dict
        series_config: list
        color_palette: list
        show_legend: bool
        show_grid: bool
        show_tooltips: bool
        enable_animations: bool
        animation_duration: int
        auto_refresh: bool
        refresh_interval: int

    def prepare_value_for_db(self, values: dict, instance: Widget | None = None):
        # Set default layout configuration
        if 'layout_config' not in values:
            values['layout_config'] = {
                'x': 0,
                'y': 0,
                'w': 6,
                'h': 4,
                'minW': 3,
                'minH': 2
            }
        
        # Set default color palette if not provided
        if 'color_palette' not in values or not values['color_palette']:
            values['color_palette'] = [
                '#5190ef', '#2BC3F1', '#FFC744', 
                '#E26AB0', '#3E4ACB', '#FF6B6B'
            ]
        
        return values

    def get_chart_data(self, widget: EnhancedChartWidget):
        """
        Get aggregated chart data from multiple data sources.
        """
        chart_data = {
            'labels': [],
            'datasets': [],
            'type': widget.chart_type
        }
        
        # Process each data source
        for i, data_source in enumerate(widget.data_sources.all()):
            # Get cached or compute aggregation
            aggregation = self._get_or_compute_aggregation(widget, data_source)
            
            if aggregation:
                dataset = {
                    'label': data_source.name,
                    'data': aggregation.get('data', []),
                    'backgroundColor': widget.color_palette[i % len(widget.color_palette)] if widget.color_palette else '#5190ef',
                    'borderColor': widget.color_palette[i % len(widget.color_palette)] if widget.color_palette else '#5190ef',
                }
                chart_data['datasets'].append(dataset)
                
                # Use labels from first data source
                if i == 0:
                    chart_data['labels'] = aggregation.get('labels', [])
        
        return chart_data

    def _get_or_compute_aggregation(self, widget: EnhancedChartWidget, data_source):
        """
        Get or compute aggregation for a specific data source.
        """
        # Check for cached aggregation
        aggregation = WidgetDataAggregation.objects.filter(
            widget=widget,
            data_source=data_source,
            cache_expires_at__gt=timezone.now()
        ).first()
        
        if aggregation:
            return aggregation.cached_result
        
        # Compute new aggregation
        # This would integrate with the existing data source system
        result = {
            'data': [10, 20, 30, 40, 50],  # Placeholder data
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May']
        }
        
        # Cache the result
        WidgetDataAggregation.objects.update_or_create(
            widget=widget,
            data_source=data_source,
            aggregation_type='sum',
            field_name='default',
            defaults={
                'cached_result': result,
                'cache_expires_at': timezone.now() + timedelta(minutes=15)
            }
        )
        
        return result


class DashboardLayoutHandler:
    """
    Handler for managing dashboard layout operations.
    """
    
    @staticmethod
    def get_or_create_layout(dashboard):
        """
        Get or create layout configuration for a dashboard.
        """
        layout, created = DashboardLayout.objects.get_or_create(
            dashboard=dashboard,
            defaults={
                'grid_columns': 12,
                'grid_row_height': 60,
                'layout_data': [],
                'breakpoints': {
                    'lg': 1200,
                    'md': 996,
                    'sm': 768,
                    'xs': 480,
                    'xxs': 0
                }
            }
        )
        return layout
    
    @staticmethod
    def update_widget_layout(widget: Widget, layout_config: dict):
        """
        Update layout configuration for a specific widget.
        """
        dashboard_layout = DashboardLayoutHandler.get_or_create_layout(widget.dashboard)
        
        # Find and update widget in layout data
        layout_data = dashboard_layout.layout_data
        widget_layout = None
        
        for item in layout_data:
            if item.get('i') == str(widget.id):
                widget_layout = item
                break
        
        if not widget_layout:
            # Add new widget to layout
            widget_layout = {
                'i': str(widget.id),
                'x': layout_config.get('x', 0),
                'y': layout_config.get('y', 0),
                'w': layout_config.get('w', 6),
                'h': layout_config.get('h', 4),
                'minW': layout_config.get('minW', 3),
                'minH': layout_config.get('minH', 2)
            }
            layout_data.append(widget_layout)
        else:
            # Update existing widget layout
            widget_layout.update(layout_config)
        
        dashboard_layout.layout_data = layout_data
        dashboard_layout.save()
        
        return dashboard_layout
    
    @staticmethod
    def remove_widget_from_layout(widget: Widget):
        """
        Remove widget from dashboard layout.
        """
        try:
            dashboard_layout = DashboardLayout.objects.get(dashboard=widget.dashboard)
            layout_data = dashboard_layout.layout_data
            
            # Remove widget from layout data
            dashboard_layout.layout_data = [
                item for item in layout_data 
                if item.get('i') != str(widget.id)
            ]
            dashboard_layout.save()
        except DashboardLayout.DoesNotExist:
            pass  # No layout to update