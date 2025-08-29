"""
API views for enhanced automation actions.
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from baserow.contrib.automation.nodes.enhanced_action_models import (
    NotificationActionNode,
    WebhookActionNode,
    StatusChangeActionNode,
    ConditionalBranchNode,
    DelayActionNode,
    WorkflowExecutionLog,
    ActionTemplate,
)
from baserow.contrib.automation.nodes.action_template_handler import (
    ActionTemplateHandler
)
from baserow.contrib.automation.api.enhanced_actions.serializers import (
    NotificationActionNodeSerializer,
    WebhookActionNodeSerializer,
    StatusChangeActionNodeSerializer,
    ConditionalBranchNodeSerializer,
    DelayActionNodeSerializer,
    WorkflowExecutionLogSerializer,
    ActionTemplateSerializer,
    ActionTemplateCreateSerializer,
    ActionTemplateApplySerializer,
)


class NotificationActionNodeViewSet(viewsets.ModelViewSet):
    """ViewSet for notification action nodes."""
    
    queryset = NotificationActionNode.objects.all()
    serializer_class = NotificationActionNodeSerializer
    permission_classes = [IsAuthenticated]


class WebhookActionNodeViewSet(viewsets.ModelViewSet):
    """ViewSet for webhook action nodes."""
    
    queryset = WebhookActionNode.objects.all()
    serializer_class = WebhookActionNodeSerializer
    permission_classes = [IsAuthenticated]


class StatusChangeActionNodeViewSet(viewsets.ModelViewSet):
    """ViewSet for status change action nodes."""
    
    queryset = StatusChangeActionNode.objects.all()
    serializer_class = StatusChangeActionNodeSerializer
    permission_classes = [IsAuthenticated]


class ConditionalBranchNodeViewSet(viewsets.ModelViewSet):
    """ViewSet for conditional branch nodes."""
    
    queryset = ConditionalBranchNode.objects.all()
    serializer_class = ConditionalBranchNodeSerializer
    permission_classes = [IsAuthenticated]


class DelayActionNodeViewSet(viewsets.ModelViewSet):
    """ViewSet for delay action nodes."""
    
    queryset = DelayActionNode.objects.all()
    serializer_class = DelayActionNodeSerializer
    permission_classes = [IsAuthenticated]


class WorkflowExecutionLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for workflow execution logs (read-only)."""
    
    queryset = WorkflowExecutionLog.objects.all()
    serializer_class = WorkflowExecutionLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter logs by workflow if specified."""
        queryset = super().get_queryset()
        workflow_id = self.request.query_params.get('workflow_id')
        
        if workflow_id:
            queryset = queryset.filter(workflow_id=workflow_id)
        
        return queryset.order_by('-created_at')


class ActionTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for action templates."""
    
    queryset = ActionTemplate.objects.all()
    serializer_class = ActionTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return ActionTemplateCreateSerializer
        return ActionTemplateSerializer
    
    def get_queryset(self):
        """Filter templates by category if specified."""
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        
        if category:
            queryset = queryset.filter(category=category)
        
        return queryset.order_by('-usage_count', 'name')
    
    def perform_create(self, serializer):
        """Set the created_by field when creating templates."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get the most popular templates."""
        limit = int(request.query_params.get('limit', 10))
        templates = ActionTemplate.objects.order_by('-usage_count')[:limit]
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get templates grouped by category."""
        categories = ActionTemplate.objects.values_list('category', flat=True).distinct()
        result = {}
        
        for category in categories:
            templates = ActionTemplate.objects.filter(category=category).order_by('-usage_count')[:5]
            result[category] = ActionTemplateSerializer(templates, many=True).data
        
        return Response(result)
    
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """Apply a template to a workflow."""
        template = self.get_object()
        serializer = ActionTemplateApplySerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    handler = ActionTemplateHandler()
                    
                    # Get workflow
                    from baserow.contrib.automation.workflows.models import AutomationWorkflow
                    workflow = AutomationWorkflow.objects.get(
                        id=serializer.validated_data['workflow_id']
                    )
                    
                    # Apply template
                    created_nodes = handler.apply_template(
                        template=template,
                        workflow=workflow,
                        configuration_overrides=serializer.validated_data['configuration_overrides'],
                        user=request.user
                    )
                    
                    return Response({
                        'status': 'success',
                        'message': f'Template "{template.name}" applied successfully',
                        'created_nodes_count': len(created_nodes)
                    })
                    
            except ValueError as e:
                return Response({
                    'status': 'error',
                    'message': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
            
            except Exception as e:
                return Response({
                    'status': 'error',
                    'message': f'Failed to apply template: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def initialize_system_templates(self, request):
        """Initialize system templates (admin only)."""
        if not request.user.is_staff:
            return Response({
                'status': 'error',
                'message': 'Only administrators can initialize system templates'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            handler = ActionTemplateHandler()
            handler.create_system_templates()
            
            return Response({
                'status': 'success',
                'message': 'System templates initialized successfully'
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Failed to initialize system templates: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)