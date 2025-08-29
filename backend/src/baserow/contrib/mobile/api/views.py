"""
API views for mobile features
"""

from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from django.utils import timezone
from django.db import transaction

from .serializers import (
    PushSubscriptionSerializer, PushNotificationSerializer, OfflineOperationSerializer,
    MobileSettingsSerializer, CameraUploadSerializer, SyncStatusSerializer,
    NotificationTestSerializer
)
from ..models import PushSubscription, PushNotification, OfflineOperation, MobileSettings, CameraUpload
from ..services.push_notification_service import PushNotificationService
from ..services.offline_sync_service import OfflineSyncService


class PushSubscriptionViewSet(CreateModelMixin, ListModelMixin, GenericViewSet):
    """ViewSet for managing push notification subscriptions"""
    
    serializer_class = PushSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PushSubscription.objects.filter(user=self.request.user, is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def unsubscribe(self, request):
        """Unsubscribe from push notifications"""
        subscription_data = request.data.get('subscription', {})
        endpoint = subscription_data.get('endpoint')
        
        if not endpoint:
            return Response(
                {'error': 'Endpoint is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            subscription = PushSubscription.objects.get(
                user=request.user,
                endpoint=endpoint,
                is_active=True
            )
            subscription.is_active = False
            subscription.save()
            
            return Response({'message': 'Successfully unsubscribed'})
        except PushSubscription.DoesNotExist:
            return Response(
                {'error': 'Subscription not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def test_notification(self, request):
        """Send a test notification"""
        serializer = NotificationTestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            push_service = PushNotificationService()
            subscriptions = self.get_queryset()
            
            for subscription in subscriptions:
                push_service.send_notification(
                    subscription=subscription,
                    title=serializer.validated_data['title'],
                    body=serializer.validated_data['body'],
                    data=serializer.validated_data.get('data', {})
                )
            
            return Response({'message': f'Test notification sent to {subscriptions.count()} devices'})
        except Exception as e:
            return Response(
                {'error': f'Failed to send test notification: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PushNotificationViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """ViewSet for viewing push notification history"""
    
    serializer_class = PushNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PushNotification.objects.filter(
            subscription__user=self.request.user
        ).order_by('-created_at')


class OfflineOperationViewSet(ModelViewSet):
    """ViewSet for managing offline operations"""
    
    serializer_class = OfflineOperationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return OfflineOperation.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def sync_all(self, request):
        """Sync all pending operations"""
        try:
            sync_service = OfflineSyncService()
            pending_operations = self.get_queryset().filter(status='pending')
            
            synced_count = 0
            failed_count = 0
            
            for operation in pending_operations:
                try:
                    sync_service.sync_operation(operation)
                    synced_count += 1
                except Exception as e:
                    operation.mark_failed(str(e))
                    failed_count += 1
            
            return Response({
                'message': f'Sync completed: {synced_count} synced, {failed_count} failed',
                'synced_count': synced_count,
                'failed_count': failed_count
            })
        except Exception as e:
            return Response(
                {'error': f'Sync failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def sync_status(self, request):
        """Get sync status information"""
        pending_count = self.get_queryset().filter(status='pending').count()
        last_sync = self.get_queryset().filter(status='synced').first()
        
        serializer = SyncStatusSerializer(data={
            'is_online': True,  # This would be determined by the client
            'pending_operations': pending_count,
            'last_sync_time': last_sync.synced_at if last_sync else None,
            'sync_in_progress': False  # This would be tracked in cache/session
        })
        serializer.is_valid()
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry a failed operation"""
        operation = self.get_object()
        
        if operation.status != 'failed':
            return Response(
                {'error': 'Only failed operations can be retried'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            sync_service = OfflineSyncService()
            sync_service.sync_operation(operation)
            
            return Response({'message': 'Operation retried successfully'})
        except Exception as e:
            operation.mark_failed(str(e))
            return Response(
                {'error': f'Retry failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MobileSettingsViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    """ViewSet for managing mobile settings"""
    
    serializer_class = MobileSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        settings, created = MobileSettings.objects.get_or_create(user=self.request.user)
        return settings
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current user's mobile settings"""
        settings = self.get_object()
        serializer = self.get_serializer(settings)
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch'])
    def update_current(self, request):
        """Update current user's mobile settings"""
        settings = self.get_object()
        serializer = self.get_serializer(settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CameraUploadViewSet(CreateModelMixin, ListModelMixin, GenericViewSet):
    """ViewSet for handling camera uploads"""
    
    serializer_class = CameraUploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CameraUpload.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def upload_multiple(self, request):
        """Upload multiple files from camera/gallery"""
        files = request.FILES.getlist('files')
        
        if not files:
            return Response(
                {'error': 'No files provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_files = []
        
        with transaction.atomic():
            for file in files:
                serializer = self.get_serializer(data={
                    'file': file,
                    'table_id': request.data.get('table_id'),
                    'row_id': request.data.get('row_id'),
                    'field_id': request.data.get('field_id')
                })
                
                if serializer.is_valid():
                    camera_upload = serializer.save()
                    uploaded_files.append(serializer.data)
                else:
                    return Response(
                        {'error': f'Invalid file: {file.name}', 'details': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        return Response({
            'message': f'Successfully uploaded {len(uploaded_files)} files',
            'files': uploaded_files
        })
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent camera uploads"""
        recent_uploads = self.get_queryset()[:10]
        serializer = self.get_serializer(recent_uploads, many=True)
        return Response(serializer.data)