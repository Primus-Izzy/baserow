"""
URL Configuration for Notification API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    NotificationViewSet,
    NotificationTypeViewSet,
    NotificationPreferenceViewSet,
    NotificationTemplateViewSet,
    AdminNotificationViewSet
)

app_name = 'baserow.contrib.database.api.notifications'

router = DefaultRouter()
router.register('notifications', NotificationViewSet, basename='notification')
router.register('notification-types', NotificationTypeViewSet, basename='notification-type')
router.register('preferences', NotificationPreferenceViewSet, basename='notification-preference')
router.register('templates', NotificationTemplateViewSet, basename='notification-template')
router.register('admin', AdminNotificationViewSet, basename='admin-notification')

urlpatterns = [
    path('', include(router.urls)),
]