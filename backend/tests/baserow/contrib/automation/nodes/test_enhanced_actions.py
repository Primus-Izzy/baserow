"""
Tests for the enhanced automation action system.
"""

import json
import uuid
from datetime import timedelta
from unittest.mock import patch, Mock

import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from baserow.contrib.automation.nodes.enhanced_action_models import (
    NotificationActionNode,
    WebhookActionNode,
    StatusChangeActionNode,
    ConditionalBranchNode,
    DelayActionNode,
    WorkflowExecutionLog,
    ActionTemplate,
)
from baserow.contrib.automation.nodes.enhanced_action_node_types import (
    NotificationActionNodeType,
    WebhookActionNodeType,
    StatusChangeActionNodeType,
    ConditionalBranchNodeType,
    DelayActionNodeType,
)
from baserow.contrib.automation.nodes.action_template_handler import (
    ActionTemplateHandler
)
from baserow.contrib.automation.automation_dispatch_context import (
    AutomationDispatchContext
)
from baserow.contrib.automation.workflows.enhanced_runner import (
    EnhancedAutomationWorkflowRunner,
    WorkflowExecutionContext,
    SequentialActionProcessor,
)


class TestNotificationActionNode(TestCase):
    """Test notification action node functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
    
    def test_notification_node_creation(self):
        """Test creating a notification action node."""
        node = NotificationActionNode.objects.create(
            notification_type='email',
            subject_template='Test Subject: {{ title }}',
            message_template='Test message: {{ content }}',
        )
        
        self.assertEqual(node.notification_type, 'email')
        self.assertEqual(node.subject_template, 'Test Subject: {{ title }}')
        self.assertEqual(node.message_template, 'Test message: {{ content }}')
    
    @patch('django.core.mail.send_mail')
    def test_email_notification_dispatch(self, mock_send_mail):
        """Test dispatching an email notification."""
        # Create notification node
        node = NotificationActionNode.objects.create(
            notification_type='email',
            subject_template='Welcome {{ user_name }}!',
            message_template='Hello {{ user_name }}, welcome to our platform!',
        )
        node.recipient_users.add(self.user)
        
        # Create dispatch context
        context_data = {
            'user_name': 'John Doe',
            'user_email': 'john@example.com'
        }
        dispatch_context = AutomationDispatchContext(context_data)
        
        # Dispatch the notification
        node_type = NotificationActionNodeType()
        result = node_type.dispatch(node, dispatch_context)
        
        # Verify email was sent
        mock_send_mail.assert_called_once()
        call_args = mock_send_mail.call_args
        self.assertEqual(call_args[1]['subject'], 'Welcome John Doe!')
        self.assertIn('Hello John Doe', call_args[1]['message'])
        self.assertIn(self.user.email, call_args[1]['recipient_list'])
    
    @patch('requests.post')
    def test_slack_notification_dispatch(self, mock_post):
        """Test dispatching a Slack notification."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Create notification node
        node = NotificationActionNode.objects.create(
            notification_type='slack',
            subject_template='Task Update',
            message_template='Task {{ task_name }} is now {{ status }}',
            external_config={
                'webhook_url': 'https://hooks.slack.com/test'
            }
        )
        
        # Create dispatch context
        context_data = {
            'task_name': 'Project Setup',
            'status': 'completed'
        }
        dispatch_context = AutomationDispatchContext(context_data)
        
        # Dispatch the notification
        node_type = NotificationActionNodeType()
        result = node_type.dispatch(node, dispatch_context)
        
        # Verify Slack webhook was called
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], 'https://hooks.slack.com/test')
        
        payload = call_args[1]['json']
        self.assertIn('Task Update', payload['text'])
        self.assertIn('Project Setup', payload['text'])


class TestWebhookActionNode(TestCase):
    """Test webhook action node functionality."""
    
    @patch('requests.request')
    def test_webhook_dispatch_success(self, mock_request):
        """Test successful webhook dispatch."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"success": true}'
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        # Create webhook node
        node = WebhookActionNode.objects.create(
            url='https://api.example.com/webhook',
            method='POST',
            payload_template='{"event": "{{ event_type }}", "data": {{ data }}}',
            headers={'Content-Type': 'application/json'},
            retry_config={'max_retries': 3, 'retry_delay': 1}
        )
        
        # Create dispatch context
        context_data = {
            'event_type': 'user_created',
            'data': '{"user_id": 123, "name": "John Doe"}'
        }
        dispatch_context = AutomationDispatchContext(context_data)
        
        # Dispatch the webhook
        node_type = WebhookActionNodeType()
        result = node_type.dispatch(node, dispatch_context)
        
        # Verify webhook was called
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        self.assertEqual(call_args[1]['method'], 'POST')
        self.assertEqual(call_args[1]['url'], 'https://api.example.com/webhook')
        
        # Verify result
        self.assertEqual(result.data['status'], 'success')
        self.assertEqual(result.data['status_code'], 200)
    
    @patch('requests.request')
    @patch('time.sleep')
    def test_webhook_retry_logic(self, mock_sleep, mock_request):
        """Test webhook retry logic on failure."""
        # Mock failed responses followed by success
        mock_response_fail = Mock()
        mock_response_fail.raise_for_status.side_effect = Exception('Connection error')
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.text = '{"success": true}'
        mock_response_success.raise_for_status.return_value = None
        
        mock_request.side_effect = [
            Exception('Connection error'),
            Exception('Connection error'),
            mock_response_success
        ]
        
        # Create webhook node
        node = WebhookActionNode.objects.create(
            url='https://api.example.com/webhook',
            method='POST',
            retry_config={'max_retries': 3, 'retry_delay': 1, 'backoff_multiplier': 2}
        )
        
        # Create dispatch context
        dispatch_context = AutomationDispatchContext({'test': 'data'})
        
        # Dispatch the webhook
        node_type = WebhookActionNodeType()
        result = node_type.dispatch(node, dispatch_context)
        
        # Verify retries occurred
        self.assertEqual(mock_request.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)  # 2 retries before success
        
        # Verify final success
        self.assertEqual(result.data['status'], 'success')
        self.assertEqual(result.data['attempt'], 3)


class TestConditionalBranchNode(TestCase):
    """Test conditional branch node functionality."""
    
    def test_equals_condition(self):
        """Test equals condition evaluation."""
        node = ConditionalBranchNode.objects.create(
            condition_template='{{ status }}',
            condition_type='equals',
            comparison_value_template='completed'
        )
        
        # Test true condition
        context_data = {'status': 'completed'}
        dispatch_context = AutomationDispatchContext(context_data)
        
        node_type = ConditionalBranchNodeType()
        result = node_type.dispatch(node, dispatch_context)
        
        self.assertEqual(result.output_uid, 'true')
        self.assertTrue(result.data['condition_result'])
        
        # Test false condition
        context_data = {'status': 'pending'}
        dispatch_context = AutomationDispatchContext(context_data)
        
        result = node_type.dispatch(node, dispatch_context)
        
        self.assertEqual(result.output_uid, 'false')
        self.assertFalse(result.data['condition_result'])
    
    def test_greater_than_condition(self):
        """Test greater than condition evaluation."""
        node = ConditionalBranchNode.objects.create(
            condition_template='{{ amount }}',
            condition_type='greater_than',
            comparison_value_template='100'
        )
        
        # Test true condition
        context_data = {'amount': '150'}
        dispatch_context = AutomationDispatchContext(context_data)
        
        node_type = ConditionalBranchNodeType()
        result = node_type.dispatch(node, dispatch_context)
        
        self.assertEqual(result.output_uid, 'true')
        self.assertTrue(result.data['condition_result'])
    
    def test_contains_condition(self):
        """Test contains condition evaluation."""
        node = ConditionalBranchNode.objects.create(
            condition_template='{{ description }}',
            condition_type='contains',
            comparison_value_template='urgent'
        )
        
        # Test true condition
        context_data = {'description': 'This is an urgent task'}
        dispatch_context = AutomationDispatchContext(context_data)
        
        node_type = ConditionalBranchNodeType()
        result = node_type.dispatch(node, dispatch_context)
        
        self.assertEqual(result.output_uid, 'true')
        self.assertTrue(result.data['condition_result'])


class TestDelayActionNode(TestCase):
    """Test delay action node functionality."""
    
    def test_fixed_delay_calculation(self):
        """Test fixed delay calculation."""
        node = DelayActionNode.objects.create(
            delay_type='fixed',
            delay_duration=timedelta(minutes=30)
        )
        
        node_type = DelayActionNodeType()
        delay_seconds = node_type._calculate_delay(node, {})
        
        self.assertEqual(delay_seconds, 1800)  # 30 minutes = 1800 seconds
    
    def test_until_date_delay_calculation(self):
        """Test until date delay calculation."""
        node = DelayActionNode.objects.create(
            delay_type='until_date',
            delay_until_template='{{ target_date }}'
        )
        
        # Set target date 1 hour in the future
        future_date = timezone.now() + timedelta(hours=1)
        context_data = {'target_date': future_date.isoformat()}
        
        node_type = DelayActionNodeType()
        delay_seconds = node_type._calculate_delay(node, context_data)
        
        # Should be approximately 3600 seconds (1 hour)
        self.assertGreater(delay_seconds, 3500)
        self.assertLess(delay_seconds, 3700)


class TestActionTemplateHandler(TestCase):
    """Test action template handler functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        self.handler = ActionTemplateHandler()
    
    def test_create_template(self):
        """Test creating an action template."""
        template_config = {
            'nodes': [
                {
                    'type': 'notification',
                    'service': {
                        'notification_type': 'email',
                        'subject_template': 'Test Subject',
                        'message_template': 'Test Message'
                    }
                }
            ]
        }
        
        template = self.handler.create_template(
            name='Test Template',
            description='A test template',
            category='notification',
            template_config=template_config,
            required_fields=['recipient_email'],
            user=self.user
        )
        
        self.assertEqual(template.name, 'Test Template')
        self.assertEqual(template.category, 'notification')
        self.assertEqual(template.created_by, self.user)
        self.assertFalse(template.is_system_template)
    
    def test_get_templates_by_category(self):
        """Test getting templates by category."""
        # Create templates in different categories
        self.handler.create_template(
            name='Email Template',
            description='Email notification template',
            category='notification',
            template_config={'nodes': []},
            required_fields=[],
            user=self.user
        )
        
        self.handler.create_template(
            name='Webhook Template',
            description='Webhook integration template',
            category='integration',
            template_config={'nodes': []},
            required_fields=[],
            user=self.user
        )
        
        # Get templates by category
        notification_templates = self.handler.get_templates_by_category('notification')
        integration_templates = self.handler.get_templates_by_category('integration')
        
        self.assertEqual(len(notification_templates), 1)
        self.assertEqual(len(integration_templates), 1)
        self.assertEqual(notification_templates[0].name, 'Email Template')
        self.assertEqual(integration_templates[0].name, 'Webhook Template')
    
    def test_validate_required_fields(self):
        """Test validation of required fields."""
        template = ActionTemplate.objects.create(
            name='Test Template',
            description='Test',
            category='notification',
            template_config={'nodes': []},
            required_fields=['field1', 'field2'],
            created_by=self.user
        )
        
        # Test with missing fields
        with self.assertRaises(ValueError) as context:
            self.handler._validate_required_fields(template, {'field1': 'value1'})
        
        self.assertIn('field2', str(context.exception))
        
        # Test with all fields present
        try:
            self.handler._validate_required_fields(
                template, 
                {'field1': 'value1', 'field2': 'value2'}
            )
        except ValueError:
            self.fail('Validation should not raise ValueError when all fields are present')


class TestEnhancedWorkflowRunner(TestCase):
    """Test enhanced workflow runner functionality."""
    
    def setUp(self):
        self.runner = EnhancedAutomationWorkflowRunner()
    
    def test_workflow_execution_context(self):
        """Test workflow execution context functionality."""
        from baserow.contrib.automation.workflows.models import AutomationWorkflow
        
        # Create a mock workflow
        workflow = Mock()
        workflow.id = 1
        
        initial_data = {'test': 'data'}
        context = WorkflowExecutionContext(workflow, initial_data)
        
        self.assertEqual(context.workflow, workflow)
        self.assertEqual(context.data, initial_data)
        self.assertEqual(context.status, 'running')
        self.assertEqual(len(context.execution_path), 0)
        
        # Test adding node output
        context.add_node_output(123, {'result': 'success'})
        
        self.assertEqual(len(context.execution_path), 1)
        self.assertEqual(context.execution_path[0], 123)
        self.assertEqual(context.get_node_output(123), {'result': 'success'})
        
        # Test updating data
        context.update_data({'new_field': 'new_value'})
        
        self.assertEqual(context.data['test'], 'data')
        self.assertEqual(context.data['new_field'], 'new_value')
    
    def test_is_critical_error(self):
        """Test critical error detection."""
        # Test critical errors
        self.assertTrue(self.runner._is_critical_error(TimeoutError()))
        self.assertTrue(self.runner._is_critical_error(MemoryError()))
        self.assertTrue(self.runner._is_critical_error(KeyboardInterrupt()))
        
        # Test non-critical errors
        self.assertFalse(self.runner._is_critical_error(ValueError()))
        self.assertFalse(self.runner._is_critical_error(RuntimeError()))


class TestWorkflowExecutionLog(TestCase):
    """Test workflow execution logging."""
    
    def setUp(self):
        from baserow.contrib.automation.workflows.models import AutomationWorkflow
        from baserow.contrib.automation.nodes.models import AutomationNode
        
        # Create mock objects
        self.workflow = Mock()
        self.workflow.id = 1
        
        self.node = Mock()
        self.node.id = 1
    
    def test_execution_log_creation(self):
        """Test creating workflow execution logs."""
        execution_id = str(uuid.uuid4())
        
        log = WorkflowExecutionLog.objects.create(
            workflow_id=1,
            node_id=1,
            execution_id=execution_id,
            status='success',
            input_data={'test': 'input'},
            output_data={'test': 'output'},
            execution_time_ms=1500
        )
        
        self.assertEqual(log.execution_id, execution_id)
        self.assertEqual(log.status, 'success')
        self.assertEqual(log.input_data, {'test': 'input'})
        self.assertEqual(log.output_data, {'test': 'output'})
        self.assertEqual(log.execution_time_ms, 1500)
    
    def test_execution_log_filtering(self):
        """Test filtering execution logs."""
        execution_id1 = str(uuid.uuid4())
        execution_id2 = str(uuid.uuid4())
        
        # Create logs for different executions
        WorkflowExecutionLog.objects.create(
            workflow_id=1,
            node_id=1,
            execution_id=execution_id1,
            status='success'
        )
        
        WorkflowExecutionLog.objects.create(
            workflow_id=1,
            node_id=2,
            execution_id=execution_id2,
            status='failed'
        )
        
        # Test filtering by execution ID
        logs1 = WorkflowExecutionLog.objects.filter(execution_id=execution_id1)
        logs2 = WorkflowExecutionLog.objects.filter(execution_id=execution_id2)
        
        self.assertEqual(logs1.count(), 1)
        self.assertEqual(logs2.count(), 1)
        self.assertEqual(logs1.first().status, 'success')
        self.assertEqual(logs2.first().status, 'failed')
        
        # Test filtering by status
        success_logs = WorkflowExecutionLog.objects.filter(status='success')
        failed_logs = WorkflowExecutionLog.objects.filter(status='failed')
        
        self.assertEqual(success_logs.count(), 1)
        self.assertEqual(failed_logs.count(), 1)