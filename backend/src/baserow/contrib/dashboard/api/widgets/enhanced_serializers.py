"""
Enhanced serializers for dashboard widgets.
"""

from rest_framework import serializers
from baserow.contrib.dashboard.widgets.enhanced_widget_models import (
    KPIWidget,
    EnhancedChartWidget,
    DashboardLayout,
    WidgetDataAggregation
)
from baserow.contrib.dashboard.data_sources.models import DashboardDataSource


class KPIWidgetSerializer(serializers.ModelSerializer):
    """
    Serializer for KPI widgets.
    """
    
    class Meta:
        model = KPIWidget
        fields = [
            'id', 'title', 'description', 'order',
            'data_source_id', 'display_format', 'prefix_text', 'suffix_text',
            'comparison_enabled', 'comparison_data_source_id',
            'color_scheme', 'custom_color'
        ]
        read_only_fields = ['id', 'order']


class EnhancedChartWidgetSerializer(serializers.ModelSerializer):
    """
    Serializer for enhanced chart widgets.
    """
    
    data_source_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=DashboardDataSource.objects.all(),
        source='data_sources',
        required=False
    )
    
    class Meta:
        model = EnhancedChartWidget
        fields = [
            'id', 'title', 'description', 'order',
            'chart_type', 'layout_config', 'series_config',
            'color_palette', 'show_legend', 'show_grid', 'show_tooltips',
            'enable_animations', 'animation_duration',
            'auto_refresh', 'refresh_interval', 'data_source_ids'
        ]
        read_only_fields = ['id', 'order']


class DashboardLayoutSerializer(serializers.ModelSerializer):
    """
    Serializer for dashboard layout configuration.
    """
    
    class Meta:
        model = DashboardLayout
        fields = [
            'id', 'dashboard_id', 'grid_columns', 'grid_row_height',
            'layout_data', 'breakpoints', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WidgetLayoutUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating widget layout positions.
    """
    
    layout_data = serializers.ListField(
        child=serializers.DictField(),
        help_text="Array of widget layout configurations"
    )


class WidgetDataAggregationSerializer(serializers.ModelSerializer):
    """
    Serializer for widget data aggregations.
    """
    
    class Meta:
        model = WidgetDataAggregation
        fields = [
            'id', 'widget_id', 'data_source_id', 'aggregation_type',
            'field_name', 'group_by_fields', 'cached_result',
            'cache_expires_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChartDataSerializer(serializers.Serializer):
    """
    Serializer for chart data response.
    """
    
    labels = serializers.ListField(child=serializers.CharField())
    datasets = serializers.ListField(child=serializers.DictField())
    chart_type = serializers.CharField()
    options = serializers.DictField(required=False)


class KPIDataSerializer(serializers.Serializer):
    """
    Serializer for KPI data response.
    """
    
    value = serializers.DecimalField(max_digits=20, decimal_places=2)
    formatted_value = serializers.CharField()
    comparison_value = serializers.DecimalField(
        max_digits=20, decimal_places=2, 
        required=False, allow_null=True
    )
    trend = serializers.CharField(required=False, allow_null=True)
    trend_percentage = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        required=False, allow_null=True
    )