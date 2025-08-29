"""
API views for enhanced automation triggers.

This module contains API views for managing enhanced trigger types including
date-based triggers, linked record change triggers, webhook triggers,
conditional triggers, and trigger templates.
"""

import logging
from typing import Dict, Any

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView

from baserow.api.decorators import validate_body, map_exceptions
from baserow.api.errors import ERROR_USER_NOT_IN_WORKSPACE
from baserow.api.schemas import get_error_schema
from baserow.core.exceptions import UserNotInWorkspace
from baserow.contrib.automation.nodes.enhanced_trigger_models import (
    DateBasedTriggerNode,
    LinkedRecordChangeTriggerNode,
    WebhookTriggerNode,
    ConditionalTriggerNode,
    TriggerTemplate,
)
from baserow.contrib.automation.nodes.trigger_template_handler import (
    TriggerTemplateHandler
)
from baserow.contrib.automation.api.enhanced_triggers.serializers import (
    DateBasedTriggerNodeSerializer,
    LinkedRecordChangeTriggerNodeSerializer,
    WebhookTriggerNodeSerializer,
    ConditionalTriggerNodeSerializer,
    TriggerTemplateSerializer,
    TriggerTemplateApplicationSerializer,
    WebhookRequestSerializer,
    TriggerValidationSerializer,
)
from baserow.contrib.automation.workflows.models import AutomationWorkflow

logger = logging.getLogger(__name__)


class DateBasedTriggerNodeViewSet(ModelViewSet):
    """ViewSet for managing date-based trigger nodes."""
    
    serializer_class = DateBasedTriggerNodeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get date-based trigger nodes accessible to the user."""
        return DateBasedTriggerNode.objects.filter(
            workflow__automation__workspace__members=self.request.user
        ).select_related('date_field', 'workflow')
    
    @map_exceptions({UserNotInWorkspace: ERROR_USER_NOT_IN_WORKSPACE})
    def create(self, request, *args, **kwargs):
        """Create a new date-based trigger node."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Validate user has access to the workflow
        workflow_id = request.data.get('workflow_id')
        try:
            workflow = AutomationWorkflow.objects.get(
                id=workflow_id,
                automation__workspace__members=request.user
            )
        except AutomationWorkflow.DoesNotExist:
            raise UserNotInWorkspace()
        
        serializer.validated_data['workflow'] = workflow
        trigger_node = serializer.save()
        
        return Response(
            self.get_serializer(trigger_node).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def test_trigger(self, request, pk=None):
        """Test a date-based trigger manually."""
        trigger_node = self.get_object()
        
        try:
            from baserow.contrib.automation.nodes.enhanced_trigger_service_types import (
                DateBasedTriggerServiceType
            )
            
            service_type = DateBasedTriggerServiceType()
            # Simulate trigger check
            matching_rows = service_type._get_matching_rows(trigger_node, timezone.now())
            
            return Response({
                'success': True,
                'matching_rows_count': len(matching_rows),
                'sample_rows': matching_rows[:5]  # Return first 5 for preview
            })
        
        except Exception as e:
            logger.error(f"Error testing date trigger {pk}: {e}")
            return Response(
                {'error': 'Failed to test trigger', 'details': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class LinkedRecordChangeTriggerNodeViewSet(ModelViewSet):
    """ViewSet for managing linked record change trigger nodes."""
    
    serializer_class = LinkedRecordChangeTriggerNodeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get linked record change trigger nodes accessible to the user."""
        return LinkedRecordChangeTriggerNode.objects.filter(
            workflow__automation__workspace__members=self.request.user
        ).select_related('link_field', 'workflow')
    
    @map_exceptions({UserNotInWorkspace: ERROR_USER_NOT_IN_WORKSPACE})
    def create(self, request, *args, **kwargs):
        """Create a new linked record change trigger node."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Validate user has access to the workflow
        workflow_id = request.data.get('workflow_id')
        try:
            workflow = AutomationWorkflow.objects.get(
                id=workflow_id,
                automation__workspace__members=request.user
            )
        except AutomationWorkflow.DoesNotExist:
            raise UserNotInWorkspace()
        
        serializer.validated_data['workflow'] = workflow
        trigger_node = serializer.save()
        
        return Response(
            self.get_serializer(trigger_node).data,
            status=status.HTTP_201_CREATED
        )


class WebhookTriggerNodeViewSet(ModelViewSet):
    """ViewSet for managing webhook trigger nodes."""
    
    serializer_class = WebhookTriggerNodeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get webhook trigger nodes accessible to the user."""
        return WebhookTriggerNode.objects.filter(
            workflow__automation__workspace__members=self.request.user
        ).select_related('workflow')
    
    @map_exceptions({UserNotInWorkspace: ERROR_USER_NOT_IN_WORKSPACE})
    def create(self, request, *args, **kwargs):
        """Create a new webhook trigger node."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Validate user has access to the workflow
        workflow_id = request.data.get('workflow_id')
        try:
            workflow = AutomationWorkflow.objects.get(
                id=workflow_id,
                automation__workspace__members=request.user
            )
        except AutomationWorkflow.DoesNotExist:
            raise UserNotInWorkspace()
        
        # Generate unique webhook path if not provided
        if not serializer.validated_data.get('webhook_url_path'):
            import uuid
            serializer.validated_data['webhook_url_path'] = f"webhook_{uuid.uuid4().hex[:8]}"
        
        serializer.validated_data['workflow'] = workflow
        trigger_node = serializer.save()
        
        return Response(
            self.get_serializer(trigger_node).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['get'])
    def webhook_url(self, request, pk=None):
        """Get the full webhook URL for this trigger."""
        trigger_node = self.get_object()
        
        # Build full webhook URL
        base_url = request.build_absolute_uri('/')[:-1]  # Remove trailing slash
        webhook_url = f"{base_url}/api/automation/webhooks/{trigger_node.webhook_url_path}/"
        
        return Response({
            'webhook_url': webhook_url,
            'webhook_path': trigger_node.webhook_url_path,
            'auth_type': trigger_node.auth_type,
            'allowed_methods': trigger_node.allowed_methods,
        })


class ConditionalTriggerNodeViewSet(ModelViewSet):
    """ViewSet for managing conditional trigger nodes."""
    
    serializer_class = ConditionalTriggerNodeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get conditional trigger nodes accessible to the user."""
        return ConditionalTriggerNode.objects.filter(
            workflow__automation__workspace__members=self.request.user
        ).select_related('base_trigger', 'workflow')
    
    @map_exceptions({UserNotInWorkspace: ERROR_USER_NOT_IN_WORKSPACE})
    def create(self, request, *args, **kwargs):
        """Create a new conditional trigger node."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Validate user has access to the workflow
        workflow_id = request.data.get('workflow_id')
        try:
            workflow = AutomationWorkflow.objects.get(
                id=workflow_id,
                automation__workspace__members=request.user
            )
        except AutomationWorkflow.DoesNotExist:
            raise UserNotInWorkspace()
        
        serializer.validated_data['workflow'] = workflow
        trigger_node = serializer.save()
        
        return Response(
            self.get_serializer(trigger_node).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def test_conditions(self, request, pk=None):
        """Test conditional trigger evaluation with sample data."""
        trigger_node = self.get_object()
        sample_data = request.data.get('sample_data', {})
        sample_rows = request.data.get('sample_rows', [])
        
        try:
            from baserow.contrib.automation.nodes.enhanced_trigger_service_types import (
                ConditionalTriggerServiceType
            )
            
            service_type = ConditionalTriggerServiceType()
            result = service_type.evaluate_conditions(
                trigger_node, sample_data, sample_rows
            )
            
            return Response({
                'conditions_met': result,
                'evaluation_mode': trigger_node.evaluation_mode,
                'condition_groups_count': len(trigger_node.condition_groups),
            })
        
        except Exception as e:
            logger.error(f"Error testing conditional trigger {pk}: {e}")
            return Response(
                {'error': 'Failed to test conditions', 'details': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class TriggerTemplateViewSet(ModelViewSet):
    """ViewSet for managing trigger templates."""
    
    serializer_class = TriggerTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get available trigger templates."""
        return TriggerTemplate.objects.filter(is_active=True)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get available template categories."""
        categories = TriggerTemplate.objects.values_list(
            'category', flat=True
        ).distinct()
        
        return Response({
            'categories': list(categories)
        })
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get templates grouped by category."""
        category = request.query_params.get('category')
        
        handler = TriggerTemplateHandler()
        if category:
            templates = handler.get_templates_by_category(category)
        else:
            templates = handler.get_available_templates()
        
        return Response({
            'templates': TriggerTemplateSerializer(templates, many=True).data
        })
    
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """Get a preview of what the template will create."""
        template = self.get_object()
        
        handler = TriggerTemplateHandler()
        preview = handler.get_template_preview(template.id)
        
        return Response(preview)
    
    @action(detail=True, methods=['post'])
    @validate_body(TriggerTemplateApplicationSerializer)
    def apply(self, request, pk=None):
        """Apply a template to a workflow."""
        template = self.get_object()
        serializer = TriggerTemplateApplicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        workflow_id = request.data.get('workflow_id')
        field_mappings = serializer.validated_data['field_mappings']
        
        try:
            workflow = AutomationWorkflow.objects.get(
                id=workflow_id,
                automation__workspace__members=request.user
            )
        except AutomationWorkflow.DoesNotExist:
            raise UserNotInWorkspace()
        
        try:
            handler = TriggerTemplateHandler()
            result = handler.apply_template(
                template.id, workflow, field_mappings, request.user
            )
            
            return Response({
                'success': True,
                'trigger_node_id': result['trigger_node'].id,
                'action_node_ids': [node.id for node in result['action_nodes']],
                'template_applied': result['template_applied'],
            })
        
        except Exception as e:
            logger.error(f"Error applying template {pk}: {e}")
            return Response(
                {'error': 'Failed to apply template', 'details': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


@method_decorator(csrf_exempt, name='dispatch')
class WebhookEndpointView(APIView):
    """
    Public endpoint for receiving webhook requests.
    This view handles incoming webhook requests and triggers automations.
    """
    
    permission_classes = []  # Public endpoint
    
    def dispatch(self, request, webhook_path, *args, **kwargs):
        """Handle webhook requests for any HTTP method."""
        try:
            from baserow.contrib.automation.tasks import process_webhook_trigger
            
            # Extract request data
            request_data = {}
            if hasattr(request, 'data') and request.data:
                request_data = request.data
            elif request.body:
                import json
                try:
                    request_data = json.loads(request.body.decode('utf-8'))
                except json.JSONDecodeError:
                    request_data = {'raw_body': request.body.decode('utf-8')}
            
            # Extract headers
            headers = {}
            for key, value in request.META.items():
                if key.startswith('HTTP_'):
                    header_name = key[5:].replace('_', '-').title()
                    headers[header_name] = value
            
            # Process webhook asynchronously
            task_result = process_webhook_trigger.delay(
                webhook_path=webhook_path,
                request_data=request_data,
                request_method=request.method,
                headers=headers
            )
            
            # For synchronous response, we can wait a short time
            try:
                result = task_result.get(timeout=5)  # 5 second timeout
                return JsonResponse(result, status=result.get('status', 200))
            except:
                # If async processing takes too long, return accepted
                return JsonResponse(
                    {'message': 'Webhook received and processing'},
                    status=202
                )
        
        except Exception as e:
            logger.error(f"Error processing webhook {webhook_path}: {e}")
            return JsonResponse(
                {'error': 'Internal server error'},
                status=500
            )


class TriggerValidationView(APIView):
    """View for validating trigger configurations."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Validate trigger configurations for a workspace."""
        workspace_id = request.data.get('workspace_id')
        
        if not workspace_id:
            return Response(
                {'error': 'workspace_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from baserow.contrib.automation.tasks import validate_trigger_configurations
            
            # Run validation
            validation_results = validate_trigger_configurations()
            
            # Filter results for the specific workspace if needed
            # (Implementation depends on how validation results are structured)
            
            return Response({
                'validation_results': validation_results,
                'timestamp': timezone.now().isoformat(),
            })
        
        except Exception as e:
            logger.error(f"Error validating triggers: {e}")
            return Response(
                {'error': 'Failed to validate triggers', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TriggerUsageStatsView(APIView):
    """View for getting trigger usage statistics."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get trigger usage statistics."""
        try:
            from django.db.models import Count, Avg
            
            # Get template usage stats
            template_stats = TriggerTemplate.objects.aggregate(
                total_templates=Count('id'),
                avg_usage=Avg('usage_count'),
                active_templates=Count('id', filter=models.Q(is_active=True))
            )
            
            # Get popular templates
            popular_templates = (
                TriggerTemplate.objects
                .filter(is_active=True)
                .order_by('-usage_count')[:10]
                .values('name', 'category', 'usage_count')
            )
            
            # Get category distribution
            category_stats = (
                TriggerTemplate.objects
                .filter(is_active=True)
                .values('category')
                .annotate(count=Count('id'))
                .order_by('-count')
            )
            
            return Response({
                'template_stats': template_stats,
                'popular_templates': list(popular_templates),
                'category_distribution': list(category_stats),
            })
        
        except Exception as e:
            logger.error(f"Error getting trigger usage stats: {e}")
            return Response(
                {'error': 'Failed to get usage statistics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )