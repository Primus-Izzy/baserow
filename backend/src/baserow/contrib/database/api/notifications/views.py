"""
API Views for Notification System
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.contrib.auth import get_user_model

from baserow.api.decorators import validate_body, map_exceptions
from baserow.api.pagination import PageNumberPagination
from baserow.contrib.database.notifications.models import (
    Notification,
    NotificationType,
    NotificationTemplate,
    UserNotificationPreference
)
from baserow.contrib.database.notifications.handler import notification_handler
from baserow.contrib.database.notifications.exceptions import NotificationError

from .serializers import (
    NotificationSerializer,
    NotificationTypeSerializer,
    NotificationTemplateSerializer,
    UserNotificationPreferenceSerializer,
    BulkNotificationPreferenceUpdateSerializer,
    MarkNotificationsReadSerializer,
    NotificationStatsSerializer,
    CreateNotificationSerializer
)

User = get_user_model()


class NotificationPagination(PageNumberPagination):
    """Custom pagination for notifications."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class NotificationViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """ViewSet for managing user notifications."""
    
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = NotificationPagination
    
    def get_queryset(self):
        """Get notifications for the current user."""
        queryset = Notification.objects.filter(
            recipient=self.request.user,
            delivery_method='in_app'
        ).select_related('notification_type').order_by('-created_at')
        
        # Filter by workspace if provided
        workspace_id = self.request.query_params.get('workspace_id')
        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)
        
        # Filter by read status
        unread_only = self.request.query_params.get('unread_only', 'false').lower() == 'true'
        if unread_only:
            queryset = queryset.filter(read_at__isnull=True)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    @validate_body(MarkNotificationsReadSerializer)
    @map_exceptions({NotificationError: 'ERROR_NOTIFICATION_OPERATION_FAILED'})
    def mark_read(self, request, data):
        """Mark multiple notifications as read."""
        notification_ids = data['notification_ids']
        
        count = notification_handler.mark_notifications_as_read(
            request.user, 
            notification_ids
        )
        
        return Response({
            'marked_read': count
        })
    
    @action(detail=False, methods=['post'])
    @map_exceptions({NotificationError: 'ERROR_NOTIFICATION_OPERATION_FAILED'})
    def mark_all_read(self, request):
        """Mark all notifications as read for the current user."""
        workspace_id = request.data.get('workspace_id')
        
        queryset = Notification.objects.filter(
            recipient=request.user,
            delivery_method='in_app',
            read_at__isnull=True
        )
        
        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)
        
        count = queryset.update(read_at=timezone.now())
        
        return Response({
            'marked_read': count
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get notification statistics for the current user."""
        workspace_id = request.query_params.get('workspace_id')
        
        base_queryset = Notification.objects.filter(
            recipient=request.user,
            delivery_method='in_app'
        )
        
        if workspace_id:
            base_queryset = base_queryset.filter(workspace_id=workspace_id)
        
        # Calculate statistics
        total_notifications = base_queryset.count()
        unread_notifications = base_queryset.filter(read_at__isnull=True).count()
        
        # Notifications by type
        notifications_by_type = dict(
            base_queryset.values('notification_type__name')
            .annotate(count=Count('id'))
            .values_list('notification_type__name', 'count')
        )
        
        # Recent activity (last 7 days)
        from datetime import timedelta
        from django.utils import timezone
        
        recent_cutoff = timezone.now() - timedelta(days=7)
        recent_activity = list(
            base_queryset.filter(created_at__gte=recent_cutoff)
            .values('created_at__date')
            .annotate(count=Count('id'))
            .order_by('created_at__date')
        )
        
        stats_data = {
            'total_notifications': total_notifications,
            'unread_notifications': unread_notifications,
            'notifications_by_type': notifications_by_type,
            'recent_activity': recent_activity
        }
        
        serializer = NotificationStatsSerializer(stats_data)
        return Response(serializer.data)


class NotificationTypeViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """ViewSet for notification types."""
    
    queryset = NotificationType.objects.all()
    serializer_class = NotificationTypeSerializer
    permission_classes = [IsAuthenticated]


class NotificationPreferenceViewSet(ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    """ViewSet for managing user notification preferences."""
    
    serializer_class = UserNotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get preferences for the current user."""
        queryset = UserNotificationPreference.objects.filter(
            user=self.request.user
        ).select_related('notification_type')
        
        workspace_id = self.request.query_params.get('workspace_id')
        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    @validate_body(BulkNotificationPreferenceUpdateSerializer)
    @map_exceptions({NotificationError: 'ERROR_NOTIFICATION_PREFERENCE_UPDATE_FAILED'})
    def bulk_update(self, request, data):
        """Bulk update notification preferences."""
        workspace_id = data.get('workspace_id')
        workspace = None
        
        if workspace_id:
            from baserow.core.models import Workspace
            try:
                workspace = Workspace.objects.get(id=workspace_id)
            except Workspace.DoesNotExist:
                return Response(
                    {'error': 'Workspace not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
        updated_preferences = notification_handler.update_user_preferences(
            request.user,
            data['preferences'],
            workspace
        )
        
        return Response({
            'updated_count': len(updated_preferences),
            'updated_types': list(updated_preferences.keys())
        })
    
    @action(detail=False, methods=['post'])
    @map_exceptions({NotificationError: 'ERROR_NOTIFICATION_PREFERENCE_RESET_FAILED'})
    def reset_to_defaults(self, request):
        """Reset all preferences to default values."""
        workspace_id = request.data.get('workspace_id')
        
        queryset = UserNotificationPreference.objects.filter(user=request.user)
        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)
        
        # Reset to defaults
        reset_count = 0
        for preference in queryset:
            preference.in_app_enabled = preference.notification_type.default_enabled
            preference.email_enabled = preference.notification_type.default_enabled
            preference.webhook_enabled = False
            preference.slack_enabled = False
            preference.teams_enabled = False
            preference.email_batch_frequency = 'immediate'
            preference.quiet_hours_enabled = False
            preference.save()
            reset_count += 1
        
        return Response({
            'reset_count': reset_count
        })


class NotificationTemplateViewSet(ModelViewSet):
    """ViewSet for managing notification templates."""
    
    serializer_class = NotificationTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get templates accessible to the current user."""
        # Users can see system templates and their workspace templates
        return NotificationTemplate.objects.filter(
            Q(workspace__isnull=True) |  # System templates
            Q(workspace__members=self.request.user)  # Workspace templates
        ).select_related('notification_type', 'workspace')
    
    def perform_create(self, serializer):
        """Set the creator when creating a template."""
        serializer.save(created_by=self.request.user)


class AdminNotificationViewSet(GenericViewSet):
    """Admin-only viewset for creating notifications."""
    
    permission_classes = [IsAuthenticated]  # Add admin permission check in production
    
    @action(detail=False, methods=['post'])
    @validate_body(CreateNotificationSerializer)
    @map_exceptions({NotificationError: 'ERROR_NOTIFICATION_CREATION_FAILED'})
    def create_notification(self, request, data):
        """Create notifications for multiple users (admin only)."""
        # In production, add proper admin permission check here
        
        notification_type = data['notification_type']
        recipient_ids = data['recipient_ids']
        title = data['title']
        message = data['message']
        notification_data = data.get('data', {})
        delivery_methods = data.get('delivery_methods')
        workspace_id = data.get('workspace_id')
        
        workspace = None
        if workspace_id:
            from baserow.core.models import Workspace
            try:
                workspace = Workspace.objects.get(id=workspace_id)
            except Workspace.DoesNotExist:
                return Response(
                    {'error': 'Workspace not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Get recipients
        recipients = User.objects.filter(id__in=recipient_ids)
        
        created_notifications = []
        for recipient in recipients:
            notifications = notification_handler.create_notification(
                notification_type=notification_type,
                recipient=recipient,
                title=title,
                message=message,
                data=notification_data,
                workspace=workspace,
                delivery_methods=delivery_methods
            )
            created_notifications.extend(notifications)
        
        return Response({
            'created_count': len(created_notifications),
            'recipient_count': len(recipients)
        })