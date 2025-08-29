"""
API views for third-party integrations.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

from baserow.api.decorators import validate_body, map_exceptions
from baserow.api.errors import ERROR_USER_NOT_IN_GROUP
from baserow.api.pagination import PageNumberPagination
from baserow.core.exceptions import UserNotInGroup
from baserow.core.models import Group
from baserow.contrib.database.models import Table
from baserow.contrib.database.api.tables.errors import ERROR_TABLE_DOES_NOT_EXIST
from baserow.contrib.database.table.exceptions import TableDoesNotExist
from baserow.contrib.database.integrations.zapier.models import (
    ZapierIntegration, ZapierExecution, MakeIntegration, MakeExecution
)
from baserow.contrib.database.integrations.zapier.handler import (
    ZapierIntegrationHandler, MakeIntegrationHandler
)

from .serializers import (
    ZapierIntegrationSerializer,
    ZapierExecutionSerializer,
    MakeIntegrationSerializer,
    MakeExecutionSerializer,
    ZapierTriggerTestSerializer,
    ZapierActionTestSerializer,
    MakeWebhookTestSerializer,
    MakeModuleTestSerializer,
    IntegrationStatsSerializer
)


class ZapierIntegrationViewSet(ModelViewSet):
    """ViewSet for Zapier integration CRUD operations."""
    
    serializer_class = ZapierIntegrationSerializer
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        """Get Zapier integrations for the user's groups."""
        return ZapierIntegration.objects.filter(
            group__users=self.request.user
        ).select_related('group', 'table', 'created_by')
    
    @map_exceptions({
        UserNotInGroup: ERROR_USER_NOT_IN_GROUP,
        TableDoesNotExist: ERROR_TABLE_DOES_NOT_EXIST,
    })
    def perform_create(self, serializer):
        """Create a new Zapier integration."""
        group_id = self.request.data.get('group_id')
        if not group_id:
            raise serializers.ValidationError("group_id is required")
        
        # Validate user has access to group
        group = Group.objects.get(id=group_id)
        if not group.has_user(self.request.user):
            raise UserNotInGroup()
        
        # Validate table
        table_id = serializer.validated_data.get('table')
        table = Table.objects.get(id=table_id.id, database__group=group)
        
        # Create integration using handler
        handler = ZapierIntegrationHandler()
        integration = handler.create_integration(
            user=self.request.user,
            group=group,
            table=table,
            **serializer.validated_data
        )
        
        serializer.instance = integration
    
    @action(detail=True, methods=['post'])
    @validate_body(ZapierTriggerTestSerializer)
    def test_trigger(self, request, pk=None, data=None):
        """Test a Zapier trigger integration."""
        integration = self.get_object()
        
        if integration.integration_type != 'trigger':
            return Response(
                {'error': 'This endpoint is only for trigger integrations'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        handler = ZapierIntegrationHandler()
        sample_data = data.get('sample_data', {
            'row': {
                'id': 1,
                'field_1': 'Sample text',
                'field_2': 123,
                'created_at': timezone.now().isoformat()
            }
        })
        
        trigger_data = handler.get_trigger_data(integration, sample_data)
        
        return Response({
            'message': 'Trigger test completed',
            'sample_output': trigger_data
        })
    
    @action(detail=True, methods=['post'])
    @validate_body(ZapierActionTestSerializer)
    def test_action(self, request, pk=None, data=None):
        """Test a Zapier action integration."""
        integration = self.get_object()
        
        if integration.integration_type != 'action':
            return Response(
                {'error': 'This endpoint is only for action integrations'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        handler = ZapierIntegrationHandler()
        execution = handler.execute_action(integration, data['input_data'])
        
        return Response({
            'message': 'Action test completed',
            'execution_id': execution.id,
            'status': execution.status,
            'output_data': execution.output_data,
            'error_message': execution.error_message
        })
    
    @action(detail=True, methods=['get'])
    def executions(self, request, pk=None):
        """Get execution history for a Zapier integration."""
        integration = self.get_object()
        executions = integration.executions.all()
        
        # Apply filters
        status_filter = request.query_params.get('status')
        if status_filter:
            executions = executions.filter(status=status_filter)
        
        # Paginate results
        page = self.paginate_queryset(executions)
        if page is not None:
            serializer = ZapierExecutionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ZapierExecutionSerializer(executions, many=True)
        return Response(serializer.data)


class MakeIntegrationViewSet(ModelViewSet):
    """ViewSet for Make.com integration CRUD operations."""
    
    serializer_class = MakeIntegrationSerializer
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        """Get Make.com integrations for the user's groups."""
        return MakeIntegration.objects.filter(
            group__users=self.request.user
        ).select_related('group', 'table', 'created_by')
    
    @map_exceptions({
        UserNotInGroup: ERROR_USER_NOT_IN_GROUP,
        TableDoesNotExist: ERROR_TABLE_DOES_NOT_EXIST,
    })
    def perform_create(self, serializer):
        """Create a new Make.com integration."""
        group_id = self.request.data.get('group_id')
        if not group_id:
            raise serializers.ValidationError("group_id is required")
        
        # Validate user has access to group
        group = Group.objects.get(id=group_id)
        if not group.has_user(self.request.user):
            raise UserNotInGroup()
        
        # Validate table
        table_id = serializer.validated_data.get('table')
        table = Table.objects.get(id=table_id.id, database__group=group)
        
        # Create integration using handler
        handler = MakeIntegrationHandler()
        integration = handler.create_integration(
            user=self.request.user,
            group=group,
            table=table,
            **serializer.validated_data
        )
        
        serializer.instance = integration
    
    @action(detail=True, methods=['post'])
    @validate_body(MakeWebhookTestSerializer)
    def test_webhook(self, request, pk=None, data=None):
        """Test a Make.com webhook integration."""
        integration = self.get_object()
        
        if integration.module_type != 'trigger':
            return Response(
                {'error': 'This endpoint is only for trigger modules'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        handler = MakeIntegrationHandler()
        sample_data = data.get('sample_data', {
            'row': {
                'id': 1,
                'field_1': 'Sample text',
                'field_2': 123,
                'created_at': timezone.now().isoformat()
            }
        })
        
        webhook_data = handler.get_webhook_data(integration, sample_data)
        
        return Response({
            'message': 'Webhook test completed',
            'sample_output': webhook_data
        })
    
    @action(detail=True, methods=['post'])
    @validate_body(MakeModuleTestSerializer)
    def test_module(self, request, pk=None, data=None):
        """Test a Make.com module integration."""
        integration = self.get_object()
        
        if integration.module_type == 'trigger':
            return Response(
                {'error': 'Use test_webhook endpoint for trigger modules'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        handler = MakeIntegrationHandler()
        execution = handler.execute_module(integration, data['input_data'])
        
        return Response({
            'message': 'Module test completed',
            'execution_id': execution.id,
            'status': execution.status,
            'output_data': execution.output_data,
            'error_message': execution.error_message
        })
    
    @action(detail=True, methods=['get'])
    def executions(self, request, pk=None):
        """Get execution history for a Make.com integration."""
        integration = self.get_object()
        executions = integration.executions.all()
        
        # Apply filters
        status_filter = request.query_params.get('status')
        if status_filter:
            executions = executions.filter(status=status_filter)
        
        # Paginate results
        page = self.paginate_queryset(executions)
        if page is not None:
            serializer = MakeExecutionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = MakeExecutionSerializer(executions, many=True)
        return Response(serializer.data)


class IntegrationStatsView(APIView):
    """API view for integration statistics."""
    
    def get(self, request, group_id):
        """Get integration statistics for a group."""
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
        
        # Get Zapier statistics
        zapier_integrations = ZapierIntegration.objects.filter(group=group)
        zapier_stats = zapier_integrations.aggregate(
            total_executions=Sum('total_executions'),
            successful_executions=Sum('successful_executions'),
            failed_executions=Sum('failed_executions')
        )
        
        # Get Make.com statistics
        make_integrations = MakeIntegration.objects.filter(group=group)
        make_stats = make_integrations.aggregate(
            total_executions=Sum('total_executions'),
            successful_executions=Sum('successful_executions'),
            failed_executions=Sum('failed_executions')
        )
        
        # Combine statistics
        total_integrations = zapier_integrations.count() + make_integrations.count()
        active_integrations = (
            zapier_integrations.filter(is_active=True).count() +
            make_integrations.filter(is_active=True).count()
        )
        
        total_executions = (
            (zapier_stats['total_executions'] or 0) +
            (make_stats['total_executions'] or 0)
        )
        successful_executions = (
            (zapier_stats['successful_executions'] or 0) +
            (make_stats['successful_executions'] or 0)
        )
        failed_executions = (
            (zapier_stats['failed_executions'] or 0) +
            (make_stats['failed_executions'] or 0)
        )
        
        success_rate = (
            (successful_executions / total_executions * 100)
            if total_executions > 0 else 0
        )
        
        # Get recent executions
        recent_zapier = ZapierExecution.objects.filter(
            integration__group=group,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).order_by('-created_at')[:5]
        
        recent_make = MakeExecution.objects.filter(
            integration__group=group,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).order_by('-created_at')[:5]
        
        recent_executions = []
        for execution in recent_zapier:
            recent_executions.append({
                'type': 'zapier',
                'id': execution.id,
                'status': execution.status,
                'created_at': execution.created_at
            })
        
        for execution in recent_make:
            recent_executions.append({
                'type': 'make',
                'id': execution.id,
                'status': execution.status,
                'created_at': execution.created_at
            })
        
        # Sort by creation time
        recent_executions.sort(key=lambda x: x['created_at'], reverse=True)
        recent_executions = recent_executions[:10]
        
        stats_data = {
            'total_integrations': total_integrations,
            'active_integrations': active_integrations,
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'failed_executions': failed_executions,
            'success_rate': round(success_rate, 2),
            'zapier_integrations': zapier_integrations.count(),
            'make_integrations': make_integrations.count(),
            'recent_executions': recent_executions
        }
        
        return Response(IntegrationStatsSerializer(stats_data).data)