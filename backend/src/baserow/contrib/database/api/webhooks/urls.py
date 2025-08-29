"""
URL patterns for webhook API endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import WebhookViewSet, WebhookStatsView

app_name = "baserow.contrib.database.api.webhooks"

router = DefaultRouter()
router.register(r'webhooks', WebhookViewSet, basename='webhook')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'groups/<int:group_id>/webhook-stats/',
        WebhookStatsView.as_view(),
        name='webhook_stats'
    ),
]