from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
from django.core.files.storage import default_storage
from baserow.contrib.dashboard.models import Dashboard, DashboardExport
from baserow.contrib.dashboard.export.handler import dashboard_export_handler
from baserow.contrib.dashboard.sharing.handler import dashboard_sharing_handler
from baserow.contrib.dashboard.api.export.serializers import (
    CreateExportSerializer,
    ExportStatusSerializer,
    ExportListSerializer,
    ScheduleExportSerializer
)
from baserow.api.decorators import validate_body
from django.core.exceptions import PermissionDenied, ValidationError
import logging
import mimetypes

logger = logging.getLogger(__name__)


class DashboardExportViewSet(ViewSet):
    """ViewSet for dashboard export functionality."""
    
    permission_classes = [IsAuthenticated]
    
    def get_dashboard(self, dashboard_id):
        """Get dashboard and check basic access."""
        dashboard = get_object_or_404(Dashboard, id=dashboard_id)
        
        if not dashboard_sharing_handler.user_can_view_dashboard(dashboard, self.request.user):
            raise PermissionDenied("You don't have permission to access this dashboard")
        
        return dashboard
    
    @action(detail=True, methods=['post'])
    @validate_body(CreateExportSerializer, return_validated=True)
    def create_export(self, request, pk=None, validated_data=None):
        """Create a new export job for a dashboard."""
        dashboard = self.get_dashboard(pk)
        
        try:
            export_job = dashboard_export_handler.create_export_job(
                dashboard=dashboard,
                user=request.user,
                export_format=validated_data['export_format'],
                configuration=validated_data.get('configuration'),
                delivery_email=validated_data.get('delivery_email'),
                schedule_config=validated_data.get('schedule_config')
            )
            
            serializer = ExportStatusSerializer(export_job)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except (PermissionDenied, ValidationError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating export: {str(e)}")
            return Response({'error': 'Failed to create export'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def exports(self, request, pk=None):
        """Get all export jobs for a dashboard."""
        dashboard = self.get_dashboard(pk)
        
        try:
            exports = dashboard_export_handler.get_user_exports(request.user, dashboard.id)
            serializer = ExportListSerializer(exports, many=True)
            return Response({'exports': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting exports: {str(e)}")
            return Response({'error': 'Failed to get exports'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get status of a specific export job."""
        export_id = request.query_params.get('export_id')
        if not export_id:
            return Response({'error': 'export_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            export_status = dashboard_export_handler.get_export_status(export_id, request.user)
            return Response(export_status, status=status.HTTP_200_OK)
        except (PermissionDenied, ValidationError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error getting export status: {str(e)}")
            return Response({'error': 'Failed to get export status'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def cancel(self, request):
        """Cancel a pending export job."""
        export_id = request.data.get('export_id')
        if not export_id:
            return Response({'error': 'export_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            success = dashboard_export_handler.cancel_export_job(export_id, request.user)
            if success:
                return Response({'message': 'Export cancelled successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Export cannot be cancelled'}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error cancelling export: {str(e)}")
            return Response({'error': 'Failed to cancel export'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['delete'])
    def delete_export(self, request):
        """Delete an export file."""
        export_id = request.query_params.get('export_id')
        if not export_id:
            return Response({'error': 'export_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            success = dashboard_export_handler.delete_export_file(export_id, request.user)
            if success:
                return Response({'message': 'Export deleted successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Export not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error deleting export: {str(e)}")
            return Response({'error': 'Failed to delete export'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def download(self, request):
        """Download an export file."""
        export_id = request.query_params.get('export_id')
        if not export_id:
            return Response({'error': 'export_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            export_job = DashboardExport.objects.get(id=export_id, requested_by=request.user)
            
            if export_job.status != 'completed' or not export_job.file_path:
                return Response({'error': 'Export file not available'}, status=status.HTTP_404_NOT_FOUND)
            
            if not default_storage.exists(export_job.file_path):
                return Response({'error': 'Export file not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Get file content
            file_content = default_storage.open(export_job.file_path).read()
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(export_job.file_path)
            if not content_type:
                if export_job.export_format == 'pdf':
                    content_type = 'application/pdf'
                elif export_job.export_format == 'png':
                    content_type = 'image/png'
                elif export_job.export_format == 'csv':
                    content_type = 'text/csv'
                else:
                    content_type = 'application/octet-stream'
            
            # Create response
            response = HttpResponse(file_content, content_type=content_type)
            filename = f"dashboard_{export_job.dashboard.name}_{export_job.created_at.strftime('%Y%m%d_%H%M%S')}.{export_job.export_format}"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except DashboardExport.DoesNotExist:
            return Response({'error': 'Export not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error downloading export: {str(e)}")
            return Response({'error': 'Failed to download export'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    @validate_body(ScheduleExportSerializer, return_validated=True)
    def schedule_export(self, request, pk=None, validated_data=None):
        """Schedule recurring exports for a dashboard."""
        dashboard = self.get_dashboard(pk)
        
        try:
            export_job = dashboard_export_handler.create_export_job(
                dashboard=dashboard,
                user=request.user,
                export_format=validated_data['export_format'],
                configuration=validated_data.get('configuration'),
                delivery_email=validated_data['delivery_email'],
                schedule_config=validated_data['schedule_config']
            )
            
            serializer = ExportStatusSerializer(export_job)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except (PermissionDenied, ValidationError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error scheduling export: {str(e)}")
            return Response({'error': 'Failed to schedule export'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def my_exports(self, request):
        """Get all export jobs for the current user."""
        try:
            exports = dashboard_export_handler.get_user_exports(request.user)
            serializer = ExportListSerializer(exports, many=True)
            return Response({'exports': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting user exports: {str(e)}")
            return Response({'error': 'Failed to get exports'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)