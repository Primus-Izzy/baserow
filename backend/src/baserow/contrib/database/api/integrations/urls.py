"""
URL patterns for third-party integration APIs.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ZapierIntegrationViewSet,
    MakeIntegrationViewSet,
    IntegrationStatsView
)

app_name = "baserow.contrib.database.api.integrations"

router = DefaultRouter()
router.register(r'zapier', ZapierIntegrationViewSet, basename='zapier_integration')
router.register(r'make', MakeIntegrationViewSet, basename='make_integration')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'groups/<int:group_id>/stats/',
        IntegrationStatsView.as_view(),
        name='integration_stats'
    ),
]