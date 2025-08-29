"""
Enhanced API views for dashboard widgets.
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from baserow.contrib.dashboard.models import Dashboard
from baserow.contrib.dashboard.widgets.enhanced_widget_models import (
    KPIWidget,
    EnhancedChartWidget,
    DashboardLayout
)
from baserow.contrib.dashboard.widgets.enhanced_widget_types import (
    KPIWidgetType,
    EnhancedChartWidgetType,
    DashboardLayoutHandler
)
from .enhanced_serializers import (
    KPIWidgetSerializer,
    EnhancedChartWidgetSerializer,
    DashboardLayoutSerializer,
    WidgetLayoutUpdateSerializer,
    ChartDataSerializer,
    KPIDataSerializer
)


class KPIWidgetViewSet(ModelViewSet):
    """
    ViewSet for KPI widgets.
    """
    
    queryset = KPIWidget.objects.all()
    serializer_class = KPIWidgetSerializer
    
    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """
        Get aggregated data for the KPI widget.
        """
        widget = self.get_object()
        widget_type = KPIWidgetType()
        
        try:
            kpi_data = widget_type.get_aggregated_data(widget)
            serializer = KPIDataSerializer(kpi_data)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def refresh(self, request, pk=None):
        """
        Force refresh of KPI data.
        """
        widget = self.get_object()
        
        # Clear cached aggregations
        widget.aggregations.all().delete()
        
        # Get fresh data
        widget_type = KPIWidgetType()
        kpi_data = widget_type.get_aggregated_data(widget)
        
        serializer = KPIDataSerializer(kpi_data)
        return Response(serializer.data)


class EnhancedChartWidgetViewSet(ModelViewSet):
    """
    ViewSet for enhanced chart widgets.
    """
    
    queryset = EnhancedChartWidget.objects.all()
    serializer_class = EnhancedChartWidgetSerializer
    
    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """
        Get chart data for the enhanced chart widget.
        """
        widget = self.get_object()
        widget_type = EnhancedChartWidgetType()
        
        try:
            chart_data = widget_type.get_chart_data(widget)
            serializer = ChartDataSerializer(chart_data)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def refresh(self, request, pk=None):
        """
        Force refresh of chart data.
        """
        widget = self.get_object()
        
        # Clear cached aggregations
        widget.aggregations.all().delete()
        
        # Get fresh data
        widget_type = EnhancedChartWidgetType()
        chart_data = widget_type.get_chart_data(widget)
        
        serializer = ChartDataSerializer(chart_data)
        return Response(serializer.data)


class DashboardLayoutViewSet(ModelViewSet):
    """
    ViewSet for dashboard layout management.
    """
    
    queryset = DashboardLayout.objects.all()
    serializer_class = DashboardLayoutSerializer
    
    def get_queryset(self):
        """
        Filter layouts by dashboard if specified.
        """
        queryset = super().get_queryset()
        dashboard_id = self.request.query_params.get('dashboard_id')
        
        if dashboard_id:
            queryset = queryset.filter(dashboard_id=dashboard_id)
        
        return queryset


class DashboardLayoutUpdateView(APIView):
    """
    API view for updating dashboard widget layouts.
    """
    
    def post(self, request, dashboard_id):
        """
        Update the layout configuration for a dashboard.
        """
        dashboard = get_object_or_404(Dashboard, id=dashboard_id)
        serializer = WidgetLayoutUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            layout_data = serializer.validated_data['layout_data']
            
            # Get or create dashboard layout
            dashboard_layout = DashboardLayoutHandler.get_or_create_layout(dashboard)
            
            # Update layout data
            dashboard_layout.layout_data = layout_data
            dashboard_layout.save()
            
            # Return updated layout
            response_serializer = DashboardLayoutSerializer(dashboard_layout)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, dashboard_id):
        """
        Get the current layout configuration for a dashboard.
        """
        dashboard = get_object_or_404(Dashboard, id=dashboard_id)
        dashboard_layout = DashboardLayoutHandler.get_or_create_layout(dashboard)
        
        serializer = DashboardLayoutSerializer(dashboard_layout)
        return Response(serializer.data)


class WidgetDataAggregationView(APIView):
    """
    API view for managing widget data aggregations.
    """
    
    def post(self, request, widget_id):
        """
        Trigger data aggregation for a specific widget.
        """
        # This would integrate with the existing widget system
        # to trigger data aggregation based on widget type
        
        return Response({
            'message': 'Aggregation triggered successfully',
            'widget_id': widget_id
        })
    
    def delete(self, request, widget_id):
        """
        Clear cached aggregations for a widget.
        """
        from baserow.contrib.dashboard.widgets.models import Widget
        
        widget = get_object_or_404(Widget, id=widget_id)
        
        # Clear all cached aggregations for this widget
        deleted_count = widget.aggregations.all().delete()[0]
        
        return Response({
            'message': f'Cleared {deleted_count} cached aggregations',
            'widget_id': widget_id
        })