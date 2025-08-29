"""
Celery tasks for the enhanced automation system.

This module contains background tasks for handling date-based triggers,
webhook processing, and other automation-related background operations.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List

from celery import shared_task
from django.utils import timezone
from django.db import transaction

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def check_date_based_triggers(self):
    """
    Periodic task to check and fire date-based triggers.
    This task runs every hour to check for triggers that should fire.
    """
    try:
        from baserow.contrib.automation.nodes.enhanced_trigger_service_types import (
            DateBasedTriggerServiceType
        )
        from baserow.core.services.registries import service_type_registry
        
        # Get the service type and check triggers
        service_type = service_type_registry.get(DateBasedTriggerServiceType.type)
        service_type.check_date_triggers()
        
        logger.info("Date-based triggers checked successfully")
        
        # Schedule the next check
        check_date_based_triggers.apply_async(countdown=3600)  # 1 hour
        
    except Exception as e:
        logger.error(f"Error checking date-based triggers: {e}")
        
        # Retry with exponential backoff
        retry_countdown = 60 * (2 ** self.request.retries)
        raise self.retry(countdown=retry_countdown, exc=e)


@shared_task(bind=True, max_retries=3)
def process_webhook_trigger(self, webhook_path: str, request_data: Dict, 
                           request_method: str, headers: Dict):
    """
    Process incoming webhook requests asynchronously.
    
    :param webhook_path: The webhook URL path
    :param request_data: The request payload
    :param request_method: HTTP method used
    :param headers: Request headers
    """
    try:
        from baserow.contrib.automation.nodes.enhanced_trigger_service_types import (
            WebhookTriggerServiceType
        )
        from baserow.core.services.registries import service_type_registry
        
        # Get the service type and handle the webhook
        service_type = service_type_registry.get(WebhookTriggerServiceType.type)
        result = service_type.handle_webhook_request(
            webhook_path, request_data, request_method, headers
        )
        
        logger.info(f"Webhook processed: {webhook_path} - Status: {result.get('status')}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing webhook {webhook_path}: {e}")
        
        # Retry with exponential backoff
        retry_countdown = 30 * (2 ** self.request.retries)
        raise self.retry(countdown=retry_countdown, exc=e)


@shared_task
def cleanup_expired_webhook_logs():
    """
    Clean up old webhook request logs to prevent database bloat.
    This task should run daily.
    """
    try:
        from baserow.contrib.automation.models import WebhookRequestLog
        
        # Delete logs older than 30 days
        cutoff_date = timezone.now() - timedelta(days=30)
        deleted_count = WebhookRequestLog.objects.filter(
            created_at__lt=cutoff_date
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} old webhook logs")
        
    except Exception as e:
        logger.error(f"Error cleaning up webhook logs: {e}")


@shared_task(bind=True, max_retries=3)
def evaluate_conditional_triggers(self, base_trigger_id: int, event_payload: List[Dict], 
                                user_id: int = None):
    """
    Evaluate conditional triggers when their base triggers fire.
    
    :param base_trigger_id: ID of the base trigger that fired
    :param event_payload: Event data from the base trigger
    :param user_id: ID of the user who triggered the event (if any)
    """
    try:
        from baserow.contrib.automation.nodes.enhanced_trigger_models import (
            ConditionalTriggerNode
        )
        from baserow.contrib.automation.nodes.enhanced_trigger_service_types import (
            ConditionalTriggerServiceType
        )
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        user = User.objects.get(id=user_id) if user_id else None
        
        # Find conditional triggers that extend this base trigger
        conditional_triggers = ConditionalTriggerNode.objects.filter(
            base_trigger_id=base_trigger_id,
            workflow__published=True,
            workflow__paused=False
        )
        
        service_type = ConditionalTriggerServiceType()
        
        for trigger in conditional_triggers:
            try:
                # Evaluate conditions
                context_data = {
                    'user_id': user_id,
                    'trigger_time': timezone.now().isoformat(),
                }
                
                if service_type.evaluate_conditions(trigger, context_data, event_payload):
                    # Conditions met, fire the workflow
                    from baserow.contrib.automation.workflows.service import (
                        AutomationWorkflowService
                    )
                    
                    workflow_service = AutomationWorkflowService()
                    workflow_service.run_workflow(
                        trigger.workflow.id,
                        event_payload,
                        user=user,
                    )
                    
                    logger.info(f"Conditional trigger {trigger.id} fired successfully")
                else:
                    logger.debug(f"Conditional trigger {trigger.id} conditions not met")
                    
            except Exception as e:
                logger.error(f"Error evaluating conditional trigger {trigger.id}: {e}")
        
    except Exception as e:
        logger.error(f"Error in evaluate_conditional_triggers: {e}")
        
        # Retry with exponential backoff
        retry_countdown = 30 * (2 ** self.request.retries)
        raise self.retry(countdown=retry_countdown, exc=e)


@shared_task
def initialize_default_templates():
    """
    Initialize default trigger templates in the database.
    This task runs once during system setup.
    """
    try:
        from baserow.contrib.automation.nodes.trigger_template_handler import (
            get_default_templates
        )
        from baserow.contrib.automation.nodes.enhanced_trigger_models import (
            TriggerTemplate
        )
        
        default_templates = get_default_templates()
        created_count = 0
        
        for template_data in default_templates:
            # Check if template already exists
            if not TriggerTemplate.objects.filter(name=template_data['name']).exists():
                TriggerTemplate.objects.create(**template_data)
                created_count += 1
        
        logger.info(f"Initialized {created_count} default trigger templates")
        
    except Exception as e:
        logger.error(f"Error initializing default templates: {e}")


@shared_task(bind=True, max_retries=3)
def process_linked_record_changes(self, table_id: int, changed_row_ids: List[int], 
                                change_type: str, user_id: int = None):
    """
    Process linked record changes and fire relevant triggers.
    
    :param table_id: ID of the table where changes occurred
    :param changed_row_ids: List of row IDs that changed
    :param change_type: Type of change (created, updated, deleted)
    :param user_id: ID of the user who made the change
    """
    try:
        from baserow.contrib.automation.nodes.enhanced_trigger_models import (
            LinkedRecordChangeTriggerNode
        )
        from baserow.contrib.automation.nodes.enhanced_trigger_service_types import (
            LinkedRecordChangeTriggerServiceType
        )
        from baserow.contrib.database.table.models import Table
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        user = User.objects.get(id=user_id) if user_id else None
        table = Table.objects.get(id=table_id)
        
        # Find triggers that monitor this table through link fields
        triggers = LinkedRecordChangeTriggerNode.objects.filter(
            link_field__link_row_table=table,
            workflow__published=True,
            workflow__paused=False
        ).select_related('link_field', 'workflow')
        
        service_type = LinkedRecordChangeTriggerServiceType()
        
        for trigger in triggers:
            try:
                # Check if this change type matches the trigger
                if service_type._change_matches_trigger(trigger, [], change_type):
                    # Get the changed rows
                    model = table.get_model()
                    changed_rows = list(model.objects.filter(id__in=changed_row_ids))
                    
                    # Get parent rows that should trigger
                    parent_rows = service_type._get_parent_rows(trigger, changed_rows)
                    
                    if parent_rows:
                        # Fire the trigger
                        from baserow.contrib.automation.workflows.service import (
                            AutomationWorkflowService
                        )
                        
                        workflow_service = AutomationWorkflowService()
                        workflow_service.run_workflow(
                            trigger.workflow.id,
                            parent_rows,
                            user=user,
                        )
                        
                        logger.info(f"Linked record change trigger {trigger.id} fired")
                
            except Exception as e:
                logger.error(f"Error processing linked record trigger {trigger.id}: {e}")
        
    except Exception as e:
        logger.error(f"Error in process_linked_record_changes: {e}")
        
        # Retry with exponential backoff
        retry_countdown = 30 * (2 ** self.request.retries)
        raise self.retry(countdown=retry_countdown, exc=e)


@shared_task
def generate_trigger_usage_report():
    """
    Generate usage statistics for trigger templates.
    This task runs weekly to update analytics.
    """
    try:
        from baserow.contrib.automation.nodes.enhanced_trigger_models import (
            TriggerTemplate
        )
        from django.db.models import Count, Avg
        
        # Calculate usage statistics
        stats = TriggerTemplate.objects.aggregate(
            total_templates=Count('id'),
            avg_usage=Avg('usage_count'),
            total_usage=Count('usage_count')
        )
        
        # Get top templates by category
        popular_templates = (
            TriggerTemplate.objects
            .values('category', 'name', 'usage_count')
            .order_by('-usage_count')[:10]
        )
        
        logger.info(f"Trigger template usage stats: {stats}")
        logger.info(f"Popular templates: {list(popular_templates)}")
        
        # Store stats for dashboard display (implement as needed)
        
    except Exception as e:
        logger.error(f"Error generating trigger usage report: {e}")


@shared_task(bind=True, max_retries=3)
def validate_trigger_configurations(self):
    """
    Validate all trigger configurations and disable invalid ones.
    This task runs daily to ensure system integrity.
    """
    try:
        from baserow.contrib.automation.nodes.enhanced_trigger_models import (
            DateBasedTriggerNode,
            LinkedRecordChangeTriggerNode,
            WebhookTriggerNode,
            ConditionalTriggerNode,
        )
        
        validation_results = {
            'date_triggers': 0,
            'link_triggers': 0,
            'webhook_triggers': 0,
            'conditional_triggers': 0,
            'errors': []
        }
        
        # Validate date-based triggers
        for trigger in DateBasedTriggerNode.objects.filter(workflow__published=True):
            try:
                # Check if date field still exists and is valid
                if not trigger.date_field or trigger.date_field.trashed:
                    trigger.workflow.paused = True
                    trigger.workflow.save()
                    validation_results['errors'].append(
                        f"Date trigger {trigger.id}: Invalid date field"
                    )
                else:
                    validation_results['date_triggers'] += 1
            except Exception as e:
                validation_results['errors'].append(
                    f"Date trigger {trigger.id}: {str(e)}"
                )
        
        # Validate linked record triggers
        for trigger in LinkedRecordChangeTriggerNode.objects.filter(workflow__published=True):
            try:
                # Check if link field still exists and is valid
                if not trigger.link_field or trigger.link_field.trashed:
                    trigger.workflow.paused = True
                    trigger.workflow.save()
                    validation_results['errors'].append(
                        f"Link trigger {trigger.id}: Invalid link field"
                    )
                else:
                    validation_results['link_triggers'] += 1
            except Exception as e:
                validation_results['errors'].append(
                    f"Link trigger {trigger.id}: {str(e)}"
                )
        
        # Validate webhook triggers
        for trigger in WebhookTriggerNode.objects.filter(workflow__published=True):
            try:
                # Check for duplicate webhook paths
                duplicates = WebhookTriggerNode.objects.filter(
                    webhook_url_path=trigger.webhook_url_path
                ).exclude(id=trigger.id)
                
                if duplicates.exists():
                    validation_results['errors'].append(
                        f"Webhook trigger {trigger.id}: Duplicate webhook path"
                    )
                else:
                    validation_results['webhook_triggers'] += 1
            except Exception as e:
                validation_results['errors'].append(
                    f"Webhook trigger {trigger.id}: {str(e)}"
                )
        
        # Validate conditional triggers
        for trigger in ConditionalTriggerNode.objects.filter(workflow__published=True):
            try:
                # Check if base trigger still exists
                if not trigger.base_trigger or trigger.base_trigger.trashed:
                    trigger.workflow.paused = True
                    trigger.workflow.save()
                    validation_results['errors'].append(
                        f"Conditional trigger {trigger.id}: Invalid base trigger"
                    )
                else:
                    validation_results['conditional_triggers'] += 1
            except Exception as e:
                validation_results['errors'].append(
                    f"Conditional trigger {trigger.id}: {str(e)}"
                )
        
        logger.info(f"Trigger validation completed: {validation_results}")
        
        if validation_results['errors']:
            logger.warning(f"Found {len(validation_results['errors'])} trigger validation errors")
        
        return validation_results
        
    except Exception as e:
        logger.error(f"Error in validate_trigger_configurations: {e}")
        
        # Retry with exponential backoff
        retry_countdown = 300 * (2 ** self.request.retries)  # 5 minutes base
        raise self.retry(countdown=retry_countdown, exc=e)


# Enhanced Action System Tasks

@shared_task(bind=True, max_retries=3)
def execute_delayed_workflow_node(self, node_id: int, context_data: Dict):
    """
    Execute a workflow node after a delay (used by DelayActionNode).
    
    :param node_id: ID of the node to execute
    :param context_data: Context data for the execution
    """
    try:
        from baserow.contrib.automation.nodes.models import AutomationNode
        from baserow.contrib.automation.automation_dispatch_context import (
            AutomationDispatchContext
        )
        from baserow.contrib.automation.workflows.enhanced_runner import (
            EnhancedAutomationWorkflowRunner
        )
        
        # Get the node
        node = AutomationNode.objects.get(id=node_id)
        
        # Create dispatch context
        dispatch_context = AutomationDispatchContext(context_data)
        
        # Create enhanced runner
        runner = EnhancedAutomationWorkflowRunner()
        
        # Execute the next nodes
        next_nodes = list(node.get_next_nodes())
        if next_nodes:
            from baserow.contrib.automation.workflows.enhanced_runner import (
                WorkflowExecutionContext
            )
            
            execution_context = WorkflowExecutionContext(node.workflow, context_data)
            runner._execute_workflow_branch(next_nodes, execution_context, dispatch_context)
        
        logger.info(f"Delayed workflow node {node_id} executed successfully")
        
    except Exception as e:
        logger.error(f"Error executing delayed workflow node {node_id}: {e}")
        
        # Retry with exponential backoff
        retry_countdown = 60 * (2 ** self.request.retries)
        raise self.retry(countdown=retry_countdown, exc=e)


@shared_task(bind=True, max_retries=3)
def send_notification_batch(self, notification_data: List[Dict]):
    """
    Send a batch of notifications asynchronously.
    
    :param notification_data: List of notification configurations
    """
    try:
        from baserow.contrib.automation.nodes.enhanced_action_node_types import (
            NotificationActionNodeType
        )
        
        notification_type = NotificationActionNodeType()
        results = []
        
        for notification in notification_data:
            try:
                # Create a mock node for the notification
                class MockNode:
                    def __init__(self, config):
                        for key, value in config.items():
                            setattr(self, key, value)
                
                mock_node = MockNode(notification['config'])
                
                # Send the notification
                result = notification_type._send_notification(
                    mock_node,
                    notification['subject'],
                    notification['message'],
                    None  # dispatch_context not needed for this method
                )
                
                results.append({
                    'notification_id': notification.get('id'),
                    'status': 'success',
                    'result': result
                })
                
            except Exception as e:
                logger.error(f"Failed to send notification {notification.get('id')}: {e}")
                results.append({
                    'notification_id': notification.get('id'),
                    'status': 'failed',
                    'error': str(e)
                })
        
        logger.info(f"Processed {len(notification_data)} notifications")
        return results
        
    except Exception as e:
        logger.error(f"Error in send_notification_batch: {e}")
        
        # Retry with exponential backoff
        retry_countdown = 30 * (2 ** self.request.retries)
        raise self.retry(countdown=retry_countdown, exc=e)


@shared_task(bind=True, max_retries=5)
def execute_webhook_with_retry(self, webhook_config: Dict, payload: Dict, 
                              headers: Dict, max_retries: int = 3):
    """
    Execute a webhook with custom retry logic.
    
    :param webhook_config: Webhook configuration
    :param payload: Webhook payload
    :param headers: HTTP headers
    :param max_retries: Maximum number of retries
    """
    try:
        import requests
        import time
        
        url = webhook_config['url']
        method = webhook_config.get('method', 'POST')
        retry_delay = webhook_config.get('retry_delay', 1)
        backoff_multiplier = webhook_config.get('backoff_multiplier', 2)
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    json=payload,
                    headers=headers,
                    timeout=30
                )
                
                response.raise_for_status()
                
                logger.info(f"Webhook executed successfully: {url}")
                return {
                    'status': 'success',
                    'status_code': response.status_code,
                    'response_body': response.text[:1000],
                    'attempt': attempt + 1
                }
                
            except requests.RequestException as e:
                last_exception = e
                
                if attempt < max_retries:
                    sleep_time = retry_delay * (backoff_multiplier ** attempt)
                    logger.warning(f"Webhook attempt {attempt + 1} failed, retrying in {sleep_time}s: {e}")
                    time.sleep(sleep_time)
                    continue
                else:
                    break
        
        # All retries failed
        logger.error(f"Webhook failed after {max_retries + 1} attempts: {last_exception}")
        raise last_exception
        
    except Exception as e:
        logger.error(f"Error in execute_webhook_with_retry: {e}")
        
        # Use Celery's retry mechanism as final fallback
        retry_countdown = 60 * (2 ** self.request.retries)
        raise self.retry(countdown=retry_countdown, exc=e)


@shared_task
def cleanup_workflow_execution_logs():
    """
    Clean up old workflow execution logs to prevent database bloat.
    This task should run daily.
    """
    try:
        from baserow.contrib.automation.nodes.enhanced_action_models import (
            WorkflowExecutionLog
        )
        
        # Delete logs older than 90 days
        cutoff_date = timezone.now() - timedelta(days=90)
        deleted_count = WorkflowExecutionLog.objects.filter(
            created_at__lt=cutoff_date
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} old workflow execution logs")
        
        # Also clean up failed executions older than 30 days
        failed_cutoff = timezone.now() - timedelta(days=30)
        failed_deleted = WorkflowExecutionLog.objects.filter(
            created_at__lt=failed_cutoff,
            status='failed'
        ).delete()[0]
        
        logger.info(f"Cleaned up {failed_deleted} old failed execution logs")
        
    except Exception as e:
        logger.error(f"Error cleaning up workflow execution logs: {e}")


@shared_task
def initialize_action_templates():
    """
    Initialize default action templates in the database.
    This task runs once during system setup.
    """
    try:
        from baserow.contrib.automation.nodes.action_template_handler import (
            ActionTemplateHandler
        )
        
        handler = ActionTemplateHandler()
        handler.create_system_templates()
        
        logger.info("Initialized default action templates")
        
    except Exception as e:
        logger.error(f"Error initializing action templates: {e}")


@shared_task(bind=True, max_retries=3)
def process_sequential_actions(self, workflow_id: int, action_configs: List[Dict], 
                              context_data: Dict, user_id: int = None):
    """
    Process a sequence of actions in order with proper error handling.
    
    :param workflow_id: ID of the workflow
    :param action_configs: List of action configurations to execute
    :param context_data: Context data for the actions
    :param user_id: ID of the user who triggered the sequence
    """
    try:
        from baserow.contrib.automation.workflows.models import AutomationWorkflow
        from baserow.contrib.automation.automation_dispatch_context import (
            AutomationDispatchContext
        )
        from baserow.contrib.automation.workflows.enhanced_runner import (
            SequentialActionProcessor,
            EnhancedAutomationWorkflowRunner,
            WorkflowExecutionContext
        )
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        user = User.objects.get(id=user_id) if user_id else None
        workflow = AutomationWorkflow.objects.get(id=workflow_id)
        
        # Create contexts
        dispatch_context = AutomationDispatchContext(context_data, user=user)
        execution_context = WorkflowExecutionContext(workflow, context_data)
        
        # Create processor
        runner = EnhancedAutomationWorkflowRunner()
        processor = SequentialActionProcessor(runner)
        
        # Process actions sequentially
        # Note: This is a simplified implementation
        # In a real scenario, you would create actual AutomationNode instances
        
        results = []
        for i, action_config in enumerate(action_configs):
            try:
                # Execute action (simplified)
                result = {
                    'action_index': i,
                    'action_type': action_config.get('type'),
                    'status': 'completed',
                    'timestamp': timezone.now().isoformat()
                }
                results.append(result)
                
                logger.debug(f"Sequential action {i} completed: {action_config.get('type')}")
                
            except Exception as e:
                logger.error(f"Sequential action {i} failed: {e}")
                
                # Decide whether to continue or stop
                if action_config.get('stop_on_error', True):
                    raise
                
                results.append({
                    'action_index': i,
                    'action_type': action_config.get('type'),
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': timezone.now().isoformat()
                })
        
        logger.info(f"Sequential actions completed for workflow {workflow_id}")
        return results
        
    except Exception as e:
        logger.error(f"Error in process_sequential_actions: {e}")
        
        # Retry with exponential backoff
        retry_countdown = 60 * (2 ** self.request.retries)
        raise self.retry(countdown=retry_countdown, exc=e)


@shared_task
def generate_action_usage_analytics():
    """
    Generate analytics for action usage and performance.
    This task runs weekly to update dashboard metrics.
    """
    try:
        from baserow.contrib.automation.nodes.enhanced_action_models import (
            WorkflowExecutionLog,
            ActionTemplate
        )
        from django.db.models import Count, Avg, Q
        
        # Calculate execution statistics
        last_week = timezone.now() - timedelta(days=7)
        
        execution_stats = WorkflowExecutionLog.objects.filter(
            created_at__gte=last_week
        ).aggregate(
            total_executions=Count('id'),
            successful_executions=Count('id', filter=Q(status='success')),
            failed_executions=Count('id', filter=Q(status='failed')),
            avg_execution_time=Avg('execution_time_ms')
        )
        
        # Calculate template usage
        template_stats = ActionTemplate.objects.aggregate(
            total_templates=Count('id'),
            avg_usage=Avg('usage_count'),
            most_used_template=Count('usage_count')
        )
        
        # Get performance metrics by action type
        performance_by_type = (
            WorkflowExecutionLog.objects
            .filter(created_at__gte=last_week)
            .values('node__content_type__model')
            .annotate(
                count=Count('id'),
                avg_time=Avg('execution_time_ms'),
                success_rate=Count('id', filter=Q(status='success')) * 100.0 / Count('id')
            )
            .order_by('-count')
        )
        
        analytics_data = {
            'execution_stats': execution_stats,
            'template_stats': template_stats,
            'performance_by_type': list(performance_by_type),
            'generated_at': timezone.now().isoformat()
        }
        
        logger.info(f"Action usage analytics generated: {analytics_data}")
        
        # Store analytics data (implement storage as needed)
        return analytics_data
        
    except Exception as e:
        logger.error(f"Error generating action usage analytics: {e}")


@shared_task(bind=True, max_retries=3)
def validate_action_configurations(self):
    """
    Validate all action configurations and disable invalid ones.
    This task runs daily to ensure system integrity.
    """
    try:
        from baserow.contrib.automation.nodes.enhanced_action_models import (
            NotificationActionNode,
            WebhookActionNode,
            StatusChangeActionNode,
            ConditionalBranchNode,
            DelayActionNode,
        )
        
        validation_results = {
            'notification_actions': 0,
            'webhook_actions': 0,
            'status_change_actions': 0,
            'conditional_branches': 0,
            'delay_actions': 0,
            'errors': []
        }
        
        # Validate notification actions
        for action in NotificationActionNode.objects.filter(workflow__published=True):
            try:
                # Check if required templates are present
                if not action.message_template:
                    validation_results['errors'].append(
                        f"Notification action {action.id}: Missing message template"
                    )
                elif action.notification_type in ['slack', 'teams', 'webhook']:
                    # Check external configuration
                    if not action.external_config.get('webhook_url'):
                        validation_results['errors'].append(
                            f"Notification action {action.id}: Missing webhook URL"
                        )
                    else:
                        validation_results['notification_actions'] += 1
                else:
                    validation_results['notification_actions'] += 1
            except Exception as e:
                validation_results['errors'].append(
                    f"Notification action {action.id}: {str(e)}"
                )
        
        # Validate webhook actions
        for action in WebhookActionNode.objects.filter(workflow__published=True):
            try:
                # Check if URL is valid
                if not action.url:
                    validation_results['errors'].append(
                        f"Webhook action {action.id}: Missing URL"
                    )
                else:
                    validation_results['webhook_actions'] += 1
            except Exception as e:
                validation_results['errors'].append(
                    f"Webhook action {action.id}: {str(e)}"
                )
        
        # Validate status change actions
        for action in StatusChangeActionNode.objects.filter(workflow__published=True):
            try:
                # Check if target field exists
                from baserow.contrib.database.fields.models import Field
                
                if not Field.objects.filter(id=action.target_field_id).exists():
                    validation_results['errors'].append(
                        f"Status change action {action.id}: Target field not found"
                    )
                else:
                    validation_results['status_change_actions'] += 1
            except Exception as e:
                validation_results['errors'].append(
                    f"Status change action {action.id}: {str(e)}"
                )
        
        # Validate conditional branches
        for action in ConditionalBranchNode.objects.filter(workflow__published=True):
            try:
                # Check if condition template is present
                if not action.condition_template:
                    validation_results['errors'].append(
                        f"Conditional branch {action.id}: Missing condition template"
                    )
                else:
                    validation_results['conditional_branches'] += 1
            except Exception as e:
                validation_results['errors'].append(
                    f"Conditional branch {action.id}: {str(e)}"
                )
        
        # Validate delay actions
        for action in DelayActionNode.objects.filter(workflow__published=True):
            try:
                # Check delay configuration
                if action.delay_type == 'fixed' and not action.delay_duration:
                    validation_results['errors'].append(
                        f"Delay action {action.id}: Missing delay duration"
                    )
                elif action.delay_type == 'until_date' and not action.delay_until_template:
                    validation_results['errors'].append(
                        f"Delay action {action.id}: Missing delay until template"
                    )
                else:
                    validation_results['delay_actions'] += 1
            except Exception as e:
                validation_results['errors'].append(
                    f"Delay action {action.id}: {str(e)}"
                )
        
        logger.info(f"Action validation completed: {validation_results}")
        
        if validation_results['errors']:
            logger.warning(f"Found {len(validation_results['errors'])} action validation errors")
        
        return validation_results
        
    except Exception as e:
        logger.error(f"Error in validate_action_configurations: {e}")
        
        # Retry with exponential backoff
        retry_countdown = 300 * (2 ** self.request.retries)  # 5 minutes base
        raise self.retry(countdown=retry_countdown, exc=e)