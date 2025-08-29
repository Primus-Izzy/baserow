"""
URL configuration for enhanced automation actions API.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from baserow.contrib.automation.api.enhanced_actions.views import (
    NotificationActionNodeViewSet,
    WebhookActionNodeViewSet,
    StatusChangeActionNodeViewSet,
    ConditionalBranchNodeViewSet,
    DelayActionNodeViewSet,
    WorkflowExecutionLogViewSet,
    ActionTemplateViewSet,
)

router = DefaultRouter()
router.register('notification-actions', NotificationActionNodeViewSet)
router.register('webhook-actions', WebhookActionNodeViewSet)
router.register('status-change-actions', StatusChangeActionNodeViewSet)
router.register('conditional-branches', ConditionalBranchNodeViewSet)
router.register('delay-actions', DelayActionNodeViewSet)
router.register('execution-logs', WorkflowExecutionLogViewSet)
router.register('action-templates', ActionTemplateViewSet)

urlpatterns = [
    path('', include(router.urls)),
]