from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from baserow.api.decorators import validate_body, map_exceptions
from baserow.core.models import Workspace
from baserow.contrib.database.models import Table
from ..models import (
    IntegrationProvider,
    IntegrationConnection,
    IntegrationSync,
    IntegrationWebhook
)
from ..handler import IntegrationHandler
from ..exceptions import (
    IntegrationError,
    AuthenticationError,
    ProviderNotFoundError
)
from .serializers import (
    IntegrationProviderSerializer,
    IntegrationConnectionSerializer,
    IntegrationSyncSerializer,
    IntegrationWebhookSerializer,
    OAuthAuthorizationSerializer,
    OAuthCallbackSerializer,
    SyncConfigurationSerializer
)

E
RROR_INTEGRATION_NOT_FOUND = "ERROR_INTEGRATION_NOT_FOUND"
ERROR_AUTHENTICATION_FAILED = "ERROR_AUTHENTICATION_FAILED"
ERROR_PROVIDER_NOT_FOUND = "ERROR_PROVIDER_NOT_FOUND"


class IntegrationProviderViewSet(ModelViewSet):
    """ViewSet for managing integration providers"""
    
    queryset = IntegrationProvider.objects.filter(is_active=True)
    serializer_class = IntegrationProviderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return IntegrationProvider.objects.filter(is_active=True)


class IntegrationConnectionViewSet(ModelViewSet):
    """ViewSet for managing integration connections"""
    
    serializer_class = IntegrationConnectionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        workspace_id = self.kwargs.get('workspace_id')
        if workspace_id:
            return IntegrationConnection.objects.filter(
                user=self.request.user,
                workspace_id=workspace_id
            )
        return IntegrationConnection.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    @validate_body(OAuthAuthorizationSerializer)
    @map_exceptions({
        ProviderNotFoundError: ERROR_PROVIDER_NOT_FOUND,
        IntegrationError: ERROR_INTEGRATION_NOT_FOUND
    })
    def authorize(self, request, **kwargs):
        """Start OAuth authorization flow"""
        provider_name = request.data['provider']
        workspace_id = request.data['workspace_id']
        state = request.data.get('state')
        
        workspace = get_object_or_404(Workspace, id=workspace_id)
        
        handler = IntegrationHandler()
        auth_url = handler.get_authorization_url(
            provider_name, request.user, workspace, state
        )
        
        return Response({'authorization_url': auth_url})
    
    @action(detail=False, methods=['post'], url_path='callback/(?P<provider_name>[^/.]+)')
    @validate_body(OAuthCallbackSerializer)
    @map_exceptions({
        AuthenticationError: ERROR_AUTHENTICATION_FAILED,
        ProviderNotFoundError: ERROR_PROVIDER_NOT_FOUND
    })
    def oauth_callback(self, request, provider_name, **kwargs):
        """Handle OAuth callback"""
        if 'error' in request.data:
            return Response(
                {'error': request.data['error']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        code = request.data['code']
        workspace_id = request.session.get('integration_workspace_id')
        
        if not workspace_id:
            return Response(
                {'error': 'Invalid session'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        workspace = get_object_or_404(Workspace, id=workspace_id)
        
        handler = IntegrationHandler()
        connection = handler.exchange_code_for_tokens(
            provider_name, code, request.user, workspace
        )
        
        serializer = IntegrationConnectionSerializer(connection)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None, **kwargs):
        """Revoke integration connection"""
        connection = self.get_object()
        
        handler = IntegrationHandler()
        handler.revoke_connection(connection)
        
        return Response({'message': 'Connection revoked successfully'})
    
    @action(detail=True, methods=['post'])
    def refresh_token(self, request, pk=None, **kwargs):
        """Refresh access token"""
        connection = self.get_object()
        
        handler = IntegrationHandler()
        try:
            updated_connection = handler.refresh_access_token(connection)
            serializer = IntegrationConnectionSerializer(updated_connection)
            return Response(serializer.data)
        except AuthenticationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class IntegrationSyncViewSet(ModelViewSet):
    """ViewSet for managing integration syncs"""
    
    serializer_class = IntegrationSyncSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        connection_id = self.kwargs.get('connection_id')
        if connection_id:
            return IntegrationSync.objects.filter(
                connection_id=connection_id,
                connection__user=self.request.user
            )
        return IntegrationSync.objects.filter(connection__user=self.request.user)
    
    @validate_body(SyncConfigurationSerializer)
    def create(self, request, **kwargs):
        """Create new sync configuration"""
        connection_id = self.kwargs.get('connection_id')
        table_id = request.data.get('table_id')
        
        connection = get_object_or_404(
            IntegrationConnection,
            id=connection_id,
            user=request.user
        )
        table = get_object_or_404(Table, id=table_id)
        
        handler = IntegrationHandler()
        sync = handler.create_sync(connection, table, request.data)
        
        serializer = IntegrationSyncSerializer(sync)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def trigger_sync(self, request, pk=None, **kwargs):
        """Manually trigger sync"""
        sync = self.get_object()
        
        # This would trigger the sync task
        from ..tasks import run_integration_sync
        run_integration_sync.delay(sync.id)
        
        return Response({'message': 'Sync triggered successfully'})
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None, **kwargs):
        """Toggle sync active status"""
        sync = self.get_object()
        sync.is_active = not sync.is_active
        sync.save()
        
        serializer = IntegrationSyncSerializer(sync)
        return Response(serializer.data)


class GoogleIntegrationViewSet(ModelViewSet):
    """ViewSet for Google-specific integration actions"""
    
    permission_classes = [IsAuthenticated]
    
    def get_connection(self, connection_id):
        """Get Google connection for current user"""
        return get_object_or_404(
            IntegrationConnection,
            id=connection_id,
            user=self.request.user,
            provider__provider_type='google'
        )
    
    @action(detail=False, methods=['get'], url_path='(?P<connection_id>[^/.]+)/calendars')
    def list_calendars(self, request, connection_id, **kwargs):
        """List Google Calendars"""
        connection = self.get_connection(connection_id)
        
        from ..handler import GoogleIntegrationHandler
        handler = GoogleIntegrationHandler(connection)
        
        try:
            calendars = handler.list_calendars()
            return Response({'calendars': calendars})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], url_path='(?P<connection_id>[^/.]+)/drive/files')
    def list_drive_files(self, request, connection_id, **kwargs):
        """List Google Drive files"""
        connection = self.get_connection(connection_id)
        folder_id = request.query_params.get('folder_id')
        
        from ..handler import GoogleIntegrationHandler
        handler = GoogleIntegrationHandler(connection)
        
        try:
            files = handler.list_drive_files(folder_id)
            return Response({'files': files})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class MicrosoftIntegrationViewSet(ModelViewSet):
    """ViewSet for Microsoft-specific integration actions"""
    
    permission_classes = [IsAuthenticated]
    
    def get_connection(self, connection_id):
        """Get Microsoft connection for current user"""
        return get_object_or_404(
            IntegrationConnection,
            id=connection_id,
            user=self.request.user,
            provider__provider_type='microsoft'
        )
    
    @action(detail=False, methods=['get'], url_path='(?P<connection_id>[^/.]+)/calendars')
    def list_calendars(self, request, connection_id, **kwargs):
        """List Outlook calendars"""
        connection = self.get_connection(connection_id)
        
        from ..handler import MicrosoftIntegrationHandler
        handler = MicrosoftIntegrationHandler(connection)
        
        try:
            calendars = handler.list_calendars()
            return Response({'calendars': calendars})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], url_path='(?P<connection_id>[^/.]+)/teams')
    def list_teams(self, request, connection_id, **kwargs):
        """List Microsoft Teams"""
        connection = self.get_connection(connection_id)
        
        from ..handler import MicrosoftIntegrationHandler
        handler = MicrosoftIntegrationHandler(connection)
        
        try:
            teams = handler.list_teams()
            return Response({'teams': teams})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], url_path='(?P<connection_id>[^/.]+)/teams/(?P<team_id>[^/.]+)/channels')
    def list_team_channels(self, request, connection_id, team_id, **kwargs):
        """List channels in a Microsoft Team"""
        connection = self.get_connection(connection_id)
        
        from ..handler import MicrosoftIntegrationHandler
        handler = MicrosoftIntegrationHandler(connection)
        
        try:
            channels = handler.list_team_channels(team_id)
            return Response({'channels': channels})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'], url_path='(?P<connection_id>[^/.]+)/teams/(?P<team_id>[^/.]+)/channels/(?P<channel_id>[^/.]+)/message')
    def send_teams_message(self, request, connection_id, team_id, channel_id, **kwargs):
        """Send message to Microsoft Teams channel"""
        connection = self.get_connection(connection_id)
        message = request.data.get('message', '')
        
        if not message:
            return Response(
                {'error': 'Message is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from ..handler import MicrosoftIntegrationHandler
        handler = MicrosoftIntegrationHandler(connection)
        
        try:
            result = handler.send_teams_message(team_id, channel_id, message)
            return Response({'result': result})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class SlackIntegrationViewSet(ModelViewSet):
    """ViewSet for Slack-specific integration actions"""
    
    permission_classes = [IsAuthenticated]
    
    def get_connection(self, connection_id):
        """Get Slack connection for current user"""
        return get_object_or_404(
            IntegrationConnection,
            id=connection_id,
            user=self.request.user,
            provider__provider_type='slack'
        )
    
    @action(detail=False, methods=['get'], url_path='(?P<connection_id>[^/.]+)/channels')
    def list_channels(self, request, connection_id, **kwargs):
        """List Slack channels"""
        connection = self.get_connection(connection_id)
        
        from ..handler import SlackIntegrationHandler
        handler = SlackIntegrationHandler(connection)
        
        try:
            channels = handler.list_channels()
            return Response({'channels': channels})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'], url_path='(?P<connection_id>[^/.]+)/send_message')
    def send_message(self, request, connection_id, **kwargs):
        """Send message to Slack channel"""
        connection = self.get_connection(connection_id)
        channel = request.data.get('channel', '')
        message = request.data.get('message', '')
        
        if not channel or not message:
            return Response(
                {'error': 'Channel and message are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from ..handler import SlackIntegrationHandler
        handler = SlackIntegrationHandler(connection)
        
        try:
            result = handler.send_message(channel, message)
            return Response({'result': result})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )