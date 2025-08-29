from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from baserow.contrib.dashboard.models import Dashboard
from baserow.contrib.dashboard.sharing.handler import dashboard_sharing_handler
from baserow.contrib.dashboard.api.sharing.serializers import (
    PublicLinkSerializer,
    EmbedLinkSerializer,
    DashboardPermissionSerializer,
    SetPermissionSerializer,
    RemovePermissionSerializer,
    DashboardSharingSettingsSerializer
)
from baserow.api.decorators import validate_body
from baserow.core.exceptions import UserNotInWorkspace
from django.core.exceptions import PermissionDenied, ValidationError
import logging

logger = logging.getLogger(__name__)


class DashboardSharingViewSet(ViewSet):
    """ViewSet for dashboard sharing functionality."""
    
    permission_classes = [IsAuthenticated]
    
    def get_dashboard(self, dashboard_id):
        """Get dashboard and check basic access."""
        dashboard = get_object_or_404(Dashboard, id=dashboard_id)
        
        if not dashboard_sharing_handler.user_can_view_dashboard(dashboard, self.request.user):
            raise PermissionDenied("You don't have permission to access this dashboard")
        
        return dashboard
    
    @action(detail=True, methods=['post'])
    @validate_body(PublicLinkSerializer, return_validated=True)
    def create_public_link(self, request, pk=None, validated_data=None):
        """Create a public sharing link for a dashboard."""
        dashboard = self.get_dashboard(pk)
        
        try:
            result = dashboard_sharing_handler.create_public_link(dashboard, request.user)
            serializer = PublicLinkSerializer(result)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Error creating public link: {str(e)}")
            return Response({'error': 'Failed to create public link'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    @validate_body(EmbedLinkSerializer, return_validated=True)
    def create_embed_link(self, request, pk=None, validated_data=None):
        """Create an embed link for dashboard or specific widgets."""
        dashboard = self.get_dashboard(pk)
        
        try:
            widget_ids = validated_data.get('widget_ids')
            result = dashboard_sharing_handler.create_embed_link(dashboard, request.user, widget_ids)
            serializer = EmbedLinkSerializer(result)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Error creating embed link: {str(e)}")
            return Response({'error': 'Failed to create embed link'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def revoke_public_access(self, request, pk=None):
        """Revoke public access to a dashboard."""
        dashboard = self.get_dashboard(pk)
        
        try:
            dashboard_sharing_handler.revoke_public_access(dashboard, request.user)
            return Response({'message': 'Public access revoked successfully'}, status=status.HTTP_200_OK)
        except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Error revoking public access: {str(e)}")
            return Response({'error': 'Failed to revoke public access'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def permissions(self, request, pk=None):
        """Get all permissions for a dashboard."""
        dashboard = self.get_dashboard(pk)
        
        try:
            permissions = dashboard_sharing_handler.get_dashboard_permissions(dashboard, request.user)
            return Response({'permissions': permissions}, status=status.HTTP_200_OK)
        except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Error getting permissions: {str(e)}")
            return Response({'error': 'Failed to get permissions'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    @validate_body(SetPermissionSerializer, return_validated=True)
    def set_permission(self, request, pk=None, validated_data=None):
        """Set specific permissions for a user on a dashboard."""
        dashboard = self.get_dashboard(pk)
        
        try:
            target_user = validated_data['user_email']
            permission_type = validated_data['permission_type']
            
            permission = dashboard_sharing_handler.set_dashboard_permission(
                dashboard, target_user, permission_type, request.user
            )
            
            serializer = DashboardPermissionSerializer(permission)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except (PermissionDenied, UserNotInWorkspace) as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Error setting permission: {str(e)}")
            return Response({'error': 'Failed to set permission'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    @validate_body(RemovePermissionSerializer, return_validated=True)
    def remove_permission(self, request, pk=None, validated_data=None):
        """Remove specific permissions for a user on a dashboard."""
        dashboard = self.get_dashboard(pk)
        
        try:
            target_user = validated_data['user_email']
            
            dashboard_sharing_handler.remove_dashboard_permission(
                dashboard, target_user, request.user
            )
            
            return Response({'message': 'Permission removed successfully'}, status=status.HTTP_200_OK)
        except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Error removing permission: {str(e)}")
            return Response({'error': 'Failed to remove permission'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def sharing_settings(self, request, pk=None):
        """Get current sharing settings for a dashboard."""
        dashboard = self.get_dashboard(pk)
        
        try:
            serializer = DashboardSharingSettingsSerializer(dashboard)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting sharing settings: {str(e)}")
            return Response({'error': 'Failed to get sharing settings'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def public_dashboard_view(request, token):
    """Public view for accessing shared dashboards."""
    dashboard = dashboard_sharing_handler.get_public_dashboard_by_token(token)
    
    if not dashboard:
        return JsonResponse({'error': 'Dashboard not found or not public'}, status=404)
    
    # Return dashboard data for public viewing
    return JsonResponse({
        'id': str(dashboard.id),
        'name': dashboard.name,
        'layout': dashboard.layout,
        'widgets': [
            {
                'id': str(widget.id),
                'type': widget.widget_type,
                'configuration': widget.configuration,
                'position': widget.position
            }
            for widget in dashboard.widgets.all()
        ]
    })


def embed_dashboard_view(request, token):
    """Embed view for dashboards."""
    dashboard = dashboard_sharing_handler.get_embeddable_dashboard_by_token(token)
    
    if not dashboard:
        return JsonResponse({'error': 'Dashboard not found or not embeddable'}, status=404)
    
    # Return minimal dashboard data for embedding
    return JsonResponse({
        'id': str(dashboard.id),
        'name': dashboard.name,
        'layout': dashboard.layout,
        'widgets': [
            {
                'id': str(widget.id),
                'type': widget.widget_type,
                'configuration': widget.configuration,
                'position': widget.position
            }
            for widget in dashboard.widgets.all()
        ],
        'embed_mode': True
    })


def embed_widget_view(request, token):
    """Embed view for individual widgets."""
    widget = dashboard_sharing_handler.get_embeddable_widget_by_token(token)
    
    if not widget:
        return JsonResponse({'error': 'Widget not found or not embeddable'}, status=404)
    
    # Return widget data for embedding
    return JsonResponse({
        'id': str(widget.id),
        'type': widget.widget_type,
        'configuration': widget.configuration,
        'position': widget.position,
        'embed_mode': True
    })