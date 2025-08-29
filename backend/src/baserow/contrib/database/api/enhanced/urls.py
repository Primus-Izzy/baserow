"""
URL patterns for enhanced API endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    EnhancedUserViewSet,
    EnhancedGroupViewSet,
    EnhancedViewViewSet,
    EnhancedTableViewSet,
    EnhancedDatabaseViewSet,
    APIStatsView,
    APIKeyManagementView
)

app_name = "baserow.contrib.database.api.enhanced"

router = DefaultRouter()
router.register(r'users', EnhancedUserViewSet, basename='enhanced_user')
router.register(r'groups', EnhancedGroupViewSet, basename='enhanced_group')
router.register(r'views', EnhancedViewViewSet, basename='enhanced_view')
router.register(r'tables', EnhancedTableViewSet, basename='enhanced_table')
router.register(r'databases', EnhancedDatabaseViewSet, basename='enhanced_database')

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', APIStatsView.as_view(), name='api_stats'),
    path('api-keys/', APIKeyManagementView.as_view(), name='api_keys'),
]