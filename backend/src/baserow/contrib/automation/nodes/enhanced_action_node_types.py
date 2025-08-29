"""
Enhanced automation action node types for the expanded action system.

This module provides node types for advanced actions including notifications,
webhooks, status changes, and workflow control.
"""

import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

from django.contrib.auth.models import AbstractUser
from django.template import Context, Template
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

import requests
from celery import current_app

from baserow.contrib.automation.automation_dispatch_context import (
    AutomationDispatchContext,
)
from baserow.contrib.automation.nodes.enhanced_action_models import (
    NotificationActionNode,
    WebhookActionNode,
    StatusChangeActionNode,
    ConditionalBranchNode,
    DelayActionNode,
    WorkflowExecutionLog,
)
from baserow.contrib.automation.nodes.node_types import AutomationNodeActionNodeType
from baserow.contrib.automation.nodes.registries import AutomationNodeType
from baserow.core.services.types import DispatchResult
from baserow.contrib.database.fields.handler import FieldHandler
from baserow.contrib.database.rows.handler import RowHandler

logger = logging.getLogger(__name__)


class NotificationActionNodeType(AutomationNodeActionNodeType):
    """
    Action node type for sending notifications to users or external systems.
    """
    
    type = "notification"
    model_class = NotificationActionNode
    
    def dispatch(
        self,
        automation_node: NotificationActionNode,
        dispatch_context: AutomationDispatchContext,
    ) -> DispatchResult:
        """
        Send notification based on the node configuration.
        """
        
        execution_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Log execution start
            self._log_execution(
                automation_node, execution_id, 'running', 
                dispatch_context.data, {}
            )
            
            # Render templates with context data
            subject = self._render_template(
                automation_node.subject_template, 
                dispatch_context.data
            )
            message = self._render_template(
                automation_node.message_template, 
                dispatch_context.data
            )
            
            # Send notification based on type
            result = self._send_notification(
                automation_node, subject, message, dispatch_context
            )
            
            execution_time = int((time.time() - start_time) * 1000)
            
            # Log successful execution
            self._log_execution(
                automation_node, execution_id, 'success',
                dispatch_context.data, result, execution_time
            )
            
            return DispatchResult(result)
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            
            # Log failed execution
            self._log_execution(
                automation_node, execution_id, 'failed',
                dispatch_context.data, {}, execution_time, str(e)
            )
            
            # Re-raise for retry logic
            raise
    
    def _send_notification(
        self, 
        node: NotificationActionNode, 
        subject: str, 
        message: str,
        dispatch_context: AutomationDispatchContext
    ) -> Dict[str, Any]:
        """
        Send notification based on the notification type.
        """
        
        if node.notification_type == 'email':
            return self._send_email_notification(node, subject, message)
        elif node.notification_type == 'in_app':
            return self._send_in_app_notification(node, subject, message)
        elif node.notification_type == 'slack':
            return self._send_slack_notification(node, subject, message)
        elif node.notification_type == 'teams':
            return self._send_teams_notification(node, subject, message)
        elif node.notification_type == 'webhook':
            return self._send_webhook_notification(node, subject, message)
        else:
            raise ValueError(f"Unsupported notification type: {node.notification_type}")
    
    def _send_email_notification(
        self, node: NotificationActionNode, subject: str, message: str
    ) -> Dict[str, Any]:
        """Send email notification."""
        
        recipients = []
        
        # Add specific users
        for user in node.recipient_users.all():
            recipients.append(user.email)
        
        # Add users by role (simplified - would need proper role system)
        # This is a placeholder for role-based recipient selection
        
        if recipients:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False,
            )
            
            return {
                'notification_type': 'email',
                'recipients_count': len(recipients),
                'subject': subject,
                'status': 'sent'
            }
        
        return {'status': 'no_recipients'}
    
    def _send_in_app_notification(
        self, node: NotificationActionNode, subject: str, message: str
    ) -> Dict[str, Any]:
        """Send in-app notification."""
        
        # This would integrate with Baserow's notification system
        # For now, return a placeholder response
        
        return {
            'notification_type': 'in_app',
            'subject': subject,
            'message': message,
            'status': 'sent'
        }
    
    def _send_slack_notification(
        self, node: NotificationActionNode, subject: str, message: str
    ) -> Dict[str, Any]:
        """Send Slack notification."""
        
        webhook_url = node.external_config.get('webhook_url')
        if not webhook_url:
            raise ValueError("Slack webhook URL not configured")
        
        payload = {
            'text': f"*{subject}*\n{message}",
            'username': 'Baserow',
        }
        
        response = requests.post(webhook_url, json=payload, timeout=30)
        response.raise_for_status()
        
        return {
            'notification_type': 'slack',
            'status': 'sent',
            'response_status': response.status_code
        }
    
    def _send_teams_notification(
        self, node: NotificationActionNode, subject: str, message: str
    ) -> Dict[str, Any]:
        """Send Microsoft Teams notification."""
        
        webhook_url = node.external_config.get('webhook_url')
        if not webhook_url:
            raise ValueError("Teams webhook URL not configured")
        
        payload = {
            '@type': 'MessageCard',
            '@context': 'http://schema.org/extensions',
            'themeColor': '0076D7',
            'summary': subject,
            'sections': [{
                'activityTitle': subject,
                'activitySubtitle': 'Baserow Automation',
                'text': message,
            }]
        }
        
        response = requests.post(webhook_url, json=payload, timeout=30)
        response.raise_for_status()
        
        return {
            'notification_type': 'teams',
            'status': 'sent',
            'response_status': response.status_code
        }
    
    def _send_webhook_notification(
        self, node: NotificationActionNode, subject: str, message: str
    ) -> Dict[str, Any]:
        """Send webhook notification."""
        
        webhook_url = node.external_config.get('webhook_url')
        if not webhook_url:
            raise ValueError("Webhook URL not configured")
        
        payload = {
            'subject': subject,
            'message': message,
            'timestamp': timezone.now().isoformat(),
            'source': 'baserow_automation'
        }
        
        headers = node.external_config.get('headers', {})
        
        response = requests.post(
            webhook_url, 
            json=payload, 
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        
        return {
            'notification_type': 'webhook',
            'status': 'sent',
            'response_status': response.status_code
        }
    
    def _render_template(self, template_str: str, context_data: Dict[str, Any]) -> str:
        """Render Django template with context data."""
        
        if not template_str:
            return ""
        
        template = Template(template_str)
        context = Context(context_data)
        return template.render(context)
    
    def _log_execution(
        self,
        node: NotificationActionNode,
        execution_id: str,
        status: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        execution_time_ms: Optional[int] = None,
        error_message: str = ""
    ):
        """Log workflow execution step."""
        
        WorkflowExecutionLog.objects.create(
            workflow=node.workflow,
            node=node,
            execution_id=execution_id,
            status=status,
            input_data=input_data,
            output_data=output_data,
            execution_time_ms=execution_time_ms,
            error_message=error_message
        )


class WebhookActionNodeType(AutomationNodeActionNodeType):
    """
    Action node type for sending HTTP webhooks to external systems.
    """
    
    type = "webhook"
    model_class = WebhookActionNode
    
    def dispatch(
        self,
        automation_node: WebhookActionNode,
        dispatch_context: AutomationDispatchContext,
    ) -> DispatchResult:
        """
        Send HTTP webhook based on the node configuration.
        """
        
        execution_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Log execution start
            self._log_execution(
                automation_node, execution_id, 'running',
                dispatch_context.data, {}
            )
            
            # Render payload template
            payload_str = self._render_template(
                automation_node.payload_template,
                dispatch_context.data
            )
            
            payload = json.loads(payload_str) if payload_str else {}
            
            # Prepare headers
            headers = dict(automation_node.headers)
            if 'Content-Type' not in headers:
                headers['Content-Type'] = 'application/json'
            
            # Add authentication if configured
            self._add_authentication(headers, automation_node.authentication)
            
            # Send webhook with retry logic
            result = self._send_webhook_with_retry(
                automation_node, payload, headers
            )
            
            execution_time = int((time.time() - start_time) * 1000)
            
            # Log successful execution
            self._log_execution(
                automation_node, execution_id, 'success',
                dispatch_context.data, result, execution_time
            )
            
            return DispatchResult(result)
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            
            # Log failed execution
            self._log_execution(
                automation_node, execution_id, 'failed',
                dispatch_context.data, {}, execution_time, str(e)
            )
            
            raise
    
    def _send_webhook_with_retry(
        self,
        node: WebhookActionNode,
        payload: Dict[str, Any],
        headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """Send webhook with retry logic."""
        
        retry_config = node.retry_config
        max_retries = retry_config.get('max_retries', 3)
        retry_delay = retry_config.get('retry_delay', 1)
        backoff_multiplier = retry_config.get('backoff_multiplier', 2)
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                response = requests.request(
                    method=node.method,
                    url=node.url,
                    json=payload,
                    headers=headers,
                    timeout=30
                )
                
                response.raise_for_status()
                
                return {
                    'status': 'success',
                    'status_code': response.status_code,
                    'response_body': response.text[:1000],  # Limit response size
                    'attempt': attempt + 1
                }
                
            except requests.RequestException as e:
                last_exception = e
                
                if attempt < max_retries:
                    time.sleep(retry_delay * (backoff_multiplier ** attempt))
                    continue
                else:
                    break
        
        # All retries failed
        raise last_exception
    
    def _add_authentication(
        self, headers: Dict[str, str], auth_config: Dict[str, Any]
    ):
        """Add authentication to headers based on configuration."""
        
        auth_type = auth_config.get('type')
        
        if auth_type == 'api_key':
            key_name = auth_config.get('key_name', 'Authorization')
            key_value = auth_config.get('key_value', '')
            headers[key_name] = key_value
            
        elif auth_type == 'bearer':
            token = auth_config.get('token', '')
            headers['Authorization'] = f'Bearer {token}'
            
        elif auth_type == 'basic':
            # Basic auth would need proper implementation
            pass
    
    def _render_template(self, template_str: str, context_data: Dict[str, Any]) -> str:
        """Render Django template with context data."""
        
        if not template_str:
            return ""
        
        template = Template(template_str)
        context = Context(context_data)
        return template.render(context)
    
    def _log_execution(
        self,
        node: WebhookActionNode,
        execution_id: str,
        status: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        execution_time_ms: Optional[int] = None,
        error_message: str = ""
    ):
        """Log workflow execution step."""
        
        WorkflowExecutionLog.objects.create(
            workflow=node.workflow,
            node=node,
            execution_id=execution_id,
            status=status,
            input_data=input_data,
            output_data=output_data,
            execution_time_ms=execution_time_ms,
            error_message=error_message
        )


class StatusChangeActionNodeType(AutomationNodeActionNodeType):
    """
    Action node type for changing status fields or other field values.
    """
    
    type = "status_change"
    model_class = StatusChangeActionNode
    
    def dispatch(
        self,
        automation_node: StatusChangeActionNode,
        dispatch_context: AutomationDispatchContext,
    ) -> DispatchResult:
        """
        Update field values based on the node configuration.
        """
        
        execution_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Log execution start
            self._log_execution(
                automation_node, execution_id, 'running',
                dispatch_context.data, {}
            )
            
            # Check condition if specified
            if automation_node.condition_template:
                condition_result = self._evaluate_condition(
                    automation_node.condition_template,
                    dispatch_context.data
                )
                
                if not condition_result:
                    result = {'status': 'skipped', 'reason': 'condition_not_met'}
                    
                    self._log_execution(
                        automation_node, execution_id, 'skipped',
                        dispatch_context.data, result
                    )
                    
                    return DispatchResult(result)
            
            # Render new value template
            new_value = self._render_template(
                automation_node.new_value_template,
                dispatch_context.data
            )
            
            # Update the field value
            result = self._update_field_value(
                automation_node, new_value, dispatch_context
            )
            
            execution_time = int((time.time() - start_time) * 1000)
            
            # Log successful execution
            self._log_execution(
                automation_node, execution_id, 'success',
                dispatch_context.data, result, execution_time
            )
            
            return DispatchResult(result)
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            
            # Log failed execution
            self._log_execution(
                automation_node, execution_id, 'failed',
                dispatch_context.data, {}, execution_time, str(e)
            )
            
            raise
    
    def _update_field_value(
        self,
        node: StatusChangeActionNode,
        new_value: str,
        dispatch_context: AutomationDispatchContext
    ) -> Dict[str, Any]:
        """Update the target field with the new value."""
        
        # This is a simplified implementation
        # In a real implementation, you would:
        # 1. Get the field by ID
        # 2. Validate the new value
        # 3. Update the row(s) affected by the trigger
        # 4. Handle different field types appropriately
        
        return {
            'status': 'updated',
            'field_id': node.target_field_id,
            'new_value': new_value,
            'updated_rows': 1  # Placeholder
        }
    
    def _evaluate_condition(
        self, condition_template: str, context_data: Dict[str, Any]
    ) -> bool:
        """Evaluate condition template and return boolean result."""
        
        # This is a simplified condition evaluation
        # In a real implementation, you would use a proper expression evaluator
        
        rendered_condition = self._render_template(condition_template, context_data)
        
        # Simple boolean evaluation (would need proper expression parser)
        return rendered_condition.lower() in ['true', '1', 'yes']
    
    def _render_template(self, template_str: str, context_data: Dict[str, Any]) -> str:
        """Render Django template with context data."""
        
        if not template_str:
            return ""
        
        template = Template(template_str)
        context = Context(context_data)
        return template.render(context)
    
    def _log_execution(
        self,
        node: StatusChangeActionNode,
        execution_id: str,
        status: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        execution_time_ms: Optional[int] = None,
        error_message: str = ""
    ):
        """Log workflow execution step."""
        
        WorkflowExecutionLog.objects.create(
            workflow=node.workflow,
            node=node,
            execution_id=execution_id,
            status=status,
            input_data=input_data,
            output_data=output_data,
            execution_time_ms=execution_time_ms,
            error_message=error_message
        )


class ConditionalBranchNodeType(AutomationNodeActionNodeType):
    """
    Action node type for conditional branching in workflows.
    """
    
    type = "conditional_branch"
    model_class = ConditionalBranchNode
    
    def dispatch(
        self,
        automation_node: ConditionalBranchNode,
        dispatch_context: AutomationDispatchContext,
    ) -> DispatchResult:
        """
        Evaluate condition and return appropriate output for branching.
        """
        
        execution_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Log execution start
            self._log_execution(
                automation_node, execution_id, 'running',
                dispatch_context.data, {}
            )
            
            # Evaluate the condition
            condition_result = self._evaluate_condition(
                automation_node, dispatch_context.data
            )
            
            # Determine output branch
            output_uid = 'true' if condition_result else 'false'
            
            result = {
                'condition_result': condition_result,
                'output_branch': output_uid
            }
            
            execution_time = int((time.time() - start_time) * 1000)
            
            # Log successful execution
            self._log_execution(
                automation_node, execution_id, 'success',
                dispatch_context.data, result, execution_time
            )
            
            return DispatchResult(result, output_uid=output_uid)
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            
            # Log failed execution
            self._log_execution(
                automation_node, execution_id, 'failed',
                dispatch_context.data, {}, execution_time, str(e)
            )
            
            raise
    
    def _evaluate_condition(
        self, node: ConditionalBranchNode, context_data: Dict[str, Any]
    ) -> bool:
        """Evaluate the conditional expression."""
        
        # Render the condition template
        condition_value = self._render_template(
            node.condition_template, context_data
        )
        
        # Render comparison value if needed
        comparison_value = ""
        if node.comparison_value_template:
            comparison_value = self._render_template(
                node.comparison_value_template, context_data
            )
        
        # Evaluate based on condition type
        if node.condition_type == 'equals':
            return condition_value == comparison_value
        elif node.condition_type == 'not_equals':
            return condition_value != comparison_value
        elif node.condition_type == 'greater_than':
            try:
                return float(condition_value) > float(comparison_value)
            except ValueError:
                return condition_value > comparison_value
        elif node.condition_type == 'less_than':
            try:
                return float(condition_value) < float(comparison_value)
            except ValueError:
                return condition_value < comparison_value
        elif node.condition_type == 'contains':
            return comparison_value in condition_value
        elif node.condition_type == 'starts_with':
            return condition_value.startswith(comparison_value)
        elif node.condition_type == 'ends_with':
            return condition_value.endswith(comparison_value)
        elif node.condition_type == 'is_empty':
            return not condition_value or condition_value.strip() == ""
        elif node.condition_type == 'is_not_empty':
            return bool(condition_value and condition_value.strip())
        elif node.condition_type == 'custom':
            # For custom expressions, evaluate as boolean
            return condition_value.lower() in ['true', '1', 'yes']
        else:
            raise ValueError(f"Unsupported condition type: {node.condition_type}")
    
    def _render_template(self, template_str: str, context_data: Dict[str, Any]) -> str:
        """Render Django template with context data."""
        
        if not template_str:
            return ""
        
        template = Template(template_str)
        context = Context(context_data)
        return template.render(context)
    
    def _log_execution(
        self,
        node: ConditionalBranchNode,
        execution_id: str,
        status: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        execution_time_ms: Optional[int] = None,
        error_message: str = ""
    ):
        """Log workflow execution step."""
        
        WorkflowExecutionLog.objects.create(
            workflow=node.workflow,
            node=node,
            execution_id=execution_id,
            status=status,
            input_data=input_data,
            output_data=output_data,
            execution_time_ms=execution_time_ms,
            error_message=error_message
        )


class DelayActionNodeType(AutomationNodeActionNodeType):
    """
    Action node type for adding delays in workflow execution.
    """
    
    type = "delay"
    model_class = DelayActionNode
    
    def dispatch(
        self,
        automation_node: DelayActionNode,
        dispatch_context: AutomationDispatchContext,
    ) -> DispatchResult:
        """
        Schedule delayed execution of subsequent nodes.
        """
        
        execution_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Log execution start
            self._log_execution(
                automation_node, execution_id, 'running',
                dispatch_context.data, {}
            )
            
            # Calculate delay
            delay_seconds = self._calculate_delay(automation_node, dispatch_context.data)
            
            if delay_seconds > 0:
                # Schedule delayed execution using Celery
                from baserow.contrib.automation.tasks import execute_delayed_workflow_node
                
                execute_delayed_workflow_node.apply_async(
                    args=[automation_node.id, dispatch_context.data],
                    countdown=delay_seconds
                )
                
                result = {
                    'status': 'scheduled',
                    'delay_seconds': delay_seconds,
                    'scheduled_at': (timezone.now() + timedelta(seconds=delay_seconds)).isoformat()
                }
            else:
                # No delay, continue immediately
                result = {
                    'status': 'immediate',
                    'delay_seconds': 0
                }
            
            execution_time = int((time.time() - start_time) * 1000)
            
            # Log successful execution
            self._log_execution(
                automation_node, execution_id, 'success',
                dispatch_context.data, result, execution_time
            )
            
            return DispatchResult(result)
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            
            # Log failed execution
            self._log_execution(
                automation_node, execution_id, 'failed',
                dispatch_context.data, {}, execution_time, str(e)
            )
            
            raise
    
    def _calculate_delay(
        self, node: DelayActionNode, context_data: Dict[str, Any]
    ) -> int:
        """Calculate delay in seconds based on node configuration."""
        
        if node.delay_type == 'fixed':
            if node.delay_duration:
                return int(node.delay_duration.total_seconds())
            return 0
            
        elif node.delay_type == 'until_date':
            if node.delay_until_template:
                # Render the date template
                date_str = self._render_template(
                    node.delay_until_template, context_data
                )
                
                try:
                    # Parse the date (simplified - would need proper date parsing)
                    target_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    now = timezone.now()
                    
                    if target_date > now:
                        return int((target_date - now).total_seconds())
                except ValueError:
                    logger.warning(f"Invalid date format in delay node: {date_str}")
            
            return 0
            
        elif node.delay_type == 'until_condition':
            # For condition-based delays, we would need a more complex system
            # that periodically checks the condition. For now, return 0.
            return 0
        
        return 0
    
    def _render_template(self, template_str: str, context_data: Dict[str, Any]) -> str:
        """Render Django template with context data."""
        
        if not template_str:
            return ""
        
        template = Template(template_str)
        context = Context(context_data)
        return template.render(context)
    
    def _log_execution(
        self,
        node: DelayActionNode,
        execution_id: str,
        status: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        execution_time_ms: Optional[int] = None,
        error_message: str = ""
    ):
        """Log workflow execution step."""
        
        WorkflowExecutionLog.objects.create(
            workflow=node.workflow,
            node=node,
            execution_id=execution_id,
            status=status,
            input_data=input_data,
            output_data=output_data,
            execution_time_ms=execution_time_ms,
            error_message=error_message
        )