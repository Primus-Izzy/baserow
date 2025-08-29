from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    IntegrationProviderViewSet,
    IntegrationConnectionViewSet,
    IntegrationSyncViewSet,
    GoogleIntegrationViewSet,
    MicrosoftIntegrationViewSet,
    SlackIntegrationViewSet
)

router = DefaultRouter()
router.register('providers', IntegrationProviderViewSet, basename='integration-provider')
router.register('connections', IntegrationConnectionViewSet, basename='integration-connection')
router.register('syncs', IntegrationSyncViewSet, basename='integration-sync')
router.register('google', GoogleIntegrationViewSet, basename='google-integration')
router.register('microsoft', MicrosoftIntegrationViewSet, basename='microsoft-integration')
router.register('slack', SlackIntegrationViewSet, basename='slack-integration')

app_name = "baserow.contrib.integrations.api"

urlpatterns = [
    path('', include(router.urls)),
    path('workspaces/<int:workspace_id>/connections/', 
         IntegrationConnectionViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='workspace-connections'),
    path('connections/<uuid:connection_id>/syncs/',
         IntegrationSyncViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='connection-syncs'),
]