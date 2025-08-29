"""
URL configuration for enhanced automation trigger API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    DateBasedTriggerNodeViewSet,
    LinkedRecordChangeTriggerNodeViewSet,
    WebhookTriggerNodeViewSet,
    ConditionalTriggerNodeViewSet,
    TriggerTemplateViewSet,
    WebhookEndpointView,
    TriggerValidationView,
    TriggerUsageStatsView,
)

app_name = "baserow.contrib.automation.api.enhanced_triggers"

router = DefaultRouter()
router.register(
    "date-triggers", 
    DateBasedTriggerNodeViewSet, 
    basename="date_trigger"
)
router.register(
    "link-triggers", 
    LinkedRecordChangeTriggerNodeViewSet, 
    basename="link_trigger"
)
router.register(
    "webhook-triggers", 
    WebhookTriggerNodeViewSet, 
    basename="webhook_trigger"
)
router.register(
    "conditional-triggers", 
    ConditionalTriggerNodeViewSet, 
    basename="conditional_trigger"
)
router.register(
    "templates", 
    TriggerTemplateViewSet, 
    basename="trigger_template"
)

urlpatterns = [
    path("", include(router.urls)),
    
    # Public webhook endpoint
    path(
        "webhooks/<str:webhook_path>/",
        WebhookEndpointView.as_view(),
        name="webhook_endpoint"
    ),
    
    # Validation and statistics endpoints
    path(
        "validate/",
        TriggerValidationView.as_view(),
        name="trigger_validation"
    ),
    path(
        "usage-stats/",
        TriggerUsageStatsView.as_view(),
        name="trigger_usage_stats"
    ),
]