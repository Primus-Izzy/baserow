"""
URL configuration for mobile API endpoints
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PushSubscriptionViewSet, PushNotificationViewSet, OfflineOperationViewSet,
    MobileSettingsViewSet, CameraUploadViewSet
)

router = DefaultRouter()
router.register('push-subscriptions', PushSubscriptionViewSet, basename='push-subscriptions')
router.register('push-notifications', PushNotificationViewSet, basename='push-notifications')
router.register('offline-operations', OfflineOperationViewSet, basename='offline-operations')
router.register('mobile-settings', MobileSettingsViewSet, basename='mobile-settings')
router.register('camera-uploads', CameraUploadViewSet, basename='camera-uploads')

app_name = 'baserow.contrib.mobile.api'

urlpatterns = [
    path('', include(router.urls)),
]