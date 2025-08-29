"""
API views for webhook management.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta

from baserow.api.decorators import validate_body, map_exceptions
from baserow.api.errors import ERROR_USER_NOT_IN_GROUP
from baserow.api.pagination import PageNumberPagination
from baserow.core.exceptions import UserNotInGroup
from baserow.contrib.database.models import Table
from baserow.contrib.database.api.tables.errors import ERROR_TABLE_DOES_NOT_EXIST
from baserow.contrib.database.table.exceptions import TableDoesNotExist
from baserow.contrib.database.webhooks.models import Webhook, WebhookDelivery, WebhookLog
from baserow.contrib.database.webhooks.handler import WebhookHandler

from .serializers import (
    WebhookSerializer,
    CreateWebhookSerializer,
    WebhookDeliverySerializer,
    WebhookLogSerializer,
    WebhookTestSerializer,
    WebhookStatsSerializer
)


class WebhookViewSet(ModelViewSet):
    """ViewSet for webhook CRUD operations."""
    
    serializer_class = WebhookSerializer
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        """Get webhooks for the user's groups."""
        return Webhook.objects.filter(
            group__users=self.request.user
        ).select_related('group', 'table', 'created_by')
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return CreateWebhookSerializer
        return WebhookSerializer
    
    @map_exceptions({
        UserNotInGroup: ERROR_USER_NOT_IN_GROUP,
        TableDoesNotExist: ERROR_TABLE_DOES_NOT_EXIST,
    })
    def perform_create(self, serializer):
        """Create a new webhook."""
        group_id = self.request.data.get('group_id')
        if not group_id:
            raise serializers.ValidationError("group_id is required")
        
        # Validate user has access to group
        group = Group.objects.get(id=group_id)
        if not group.has_user(self.request.user):
            raise UserNotInGroup()
        
        # Validate table if specified
        table = None
        table_id = serializer.validated_data.get('table')
        if table_id:
            table = Table.objects.get(id=table_id, database__group=group)
        
        # Create webhook using handler
        handler = WebhookHandler()
        webhook = handler.create_webhook(
            user=self.request.user,
            group=group,
            table=table,
            **serializer.validated_data
        )
        
        serializer.instance = webhook
    
    @action(detail=True, methods=['post'])
    @validate_body(WebhookTestSerializer)
    def test(self, request, pk=None, data=None):
        """Test a webhook by sending a test payload."""
        webhook = self.get_object()
        handler = WebhookHandler()
        
        test_payload = data.get('test_payload', {
            'event': 'test',
            'timestamp': timezone.now().isoformat(),
            'data': {'message': 'This is a test webhook delivery'}
        })
        
        delivery = handler.trigger_webhook(
            webhook,
            'test',
            test_payload
        )
        
        return Response({
            'message': 'Test webhook queued for delivery',
            'delivery_id': delivery.id if delivery else None
        })
    
    @action(detail=True, methods=['get'])
    def deliveries(self, request, pk=None):
        """Get delivery history for a webhook."""
        webhook = self.get_object()
        deliveries = webhook.deliveries.all()
        
        # Apply filters
        status_filter = request.query_params.get('status')
        if status_filter:
            deliveries = deliveries.filter(status=status_filter)
        
        # Paginate results
        page = self.paginate_queryset(deliveries)
        if page is not None:
            serializer = WebhookDeliverySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = WebhookDeliverySerializer(deliveries, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Get activity logs for a webhook."""
        webhook = self.get_object()
        logs = webhook.logs.all()
        
        # Apply filters
        event_type = request.query_params.get('event_type')
        if event_type:
            logs = logs.filter(event_type=event_type)
        
        # Paginate results
        page = self.paginate_queryset(logs)
        if page is not None:
            serializer = WebhookLogSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = WebhookLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pause a webhook."""
        webhook = self.get_object()
        handler = WebhookHandler()
        
        handler.update_webhook(webhook, status='paused')
        
        return Response({
            'message': f'Webhook "{webhook.name}" has been paused'
        })
    
    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """Resume a paused webhook."""
        webhook = self.get_object()
        handler = WebhookHandler()
        
        handler.update_webhook(webhook, status='active')
        
        return Response({
            'message': f'Webhook "{webhook.name}" has been resumed'
        })


class WebhookStatsView(APIView):
    """API view for webhook statistics."""
    
    def get(self, request, group_id):
        """Get webhook statistics for a group."""
        # Validate user has access to group
        try:
            group = Group.objects.get(id=group_id)
            if not group.has_user(request.user):
                raise UserNotInGroup()
        except Group.DoesNotExist:
            return Response(
                {'error': 'Group not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get webhook statistics
        webhooks = Webhook.objects.filter(group=group)
        
        total_webhooks = webhooks.count()
        active_webhooks = webhooks.filter(status='active').count()
        
        # Aggregate delivery statistics
        delivery_stats = webhooks.aggregate(
            total_deliveries=models.Sum('total_deliveries'),
            successful_deliveries=models.Sum('successful_deliveries'),
            failed_deliveries=models.Sum('failed_deliveries')
        )
        
        total_deliveries = delivery_stats['total_deliveries'] or 0
        successful_deliveries = delivery_stats['successful_deliveries'] or 0
        failed_deliveries = delivery_stats['failed_deliveries'] or 0
        
        success_rate = (
            (successful_deliveries / total_deliveries * 100)
            if total_deliveries > 0 else 0
        )
        
        # Get recent deliveries
        recent_deliveries = WebhookDelivery.objects.filter(
            webhook__group=group,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).order_by('-created_at')[:10]
        
        stats_data = {
            'total_webhooks': total_webhooks,
            'active_webhooks': active_webhooks,
            'total_deliveries': total_deliveries,
            'successful_deliveries': successful_deliveries,
            'failed_deliveries': failed_deliveries,
            'success_rate': round(success_rate, 2),
            'recent_deliveries': WebhookDeliverySerializer(recent_deliveries, many=True).data
        }
        
        return Response(WebhookStatsSerializer(stats_data).data)