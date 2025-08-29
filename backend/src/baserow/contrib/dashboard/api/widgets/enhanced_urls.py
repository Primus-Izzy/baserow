"""
Enhanced URL patterns for dashboard widget APIs.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .enhanced_views import (
    KPIWidgetViewSet,
    EnhancedChartWidgetViewSet,
    DashboardLayoutViewSet,
    DashboardLayoutUpdateView,
    WidgetDataAggregationView
)

router = DefaultRouter()
router.register(r'kpi-widgets', KPIWidgetViewSet, basename='kpi-widget')
router.register(r'enhanced-chart-widgets', EnhancedChartWidgetViewSet, basename='enhanced-chart-widget')
router.register(r'dashboard-layouts', DashboardLayoutViewSet, basename='dashboard-layout')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'dashboard/<int:dashboard_id>/layout/',
        DashboardLayoutUpdateView.as_view(),
        name='dashboard-layout-update'
    ),
    path(
        'widget/<int:widget_id>/aggregation/',
        WidgetDataAggregationView.as_view(),
        name='widget-data-aggregation'
    ),
]