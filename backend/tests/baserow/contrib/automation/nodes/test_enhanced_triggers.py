"""
Tests for enhanced automation trigger system.

This module contains tests for the new trigger types including date-based triggers,
linked record change triggers, webhook triggers, conditional triggers, and trigger templates.
"""

import pytest
from datetime import datetime, timedelta
from django.utils import timezone
from django.test import TestCase
from unittest.mock import patch, MagicMock

from baserow.contrib.automation.nodes.enhanced_trigger_models import (
    DateBasedTriggerNode,
    LinkedRecordChangeTriggerNode,
    WebhookTriggerNode,
    ConditionalTriggerNode,
    TriggerTemplate,
)
from baserow.contrib.automation.nodes.enhanced_trigger_service_types import (
    DateBasedTriggerServiceType,
    LinkedRecordChangeTriggerServiceType,
    WebhookTriggerServiceType,
    ConditionalTriggerServiceType,
)
from baserow.contrib.automation.nodes.trigger_template_handler import (
    TriggerTemplateHandler,
)


@pytest.mark.django_db
class TestDateBasedTriggerNode:
    """Test date-based trigger functionality."""
    
    def test_create_date_trigger_node(self, data_fixture):
        """Test creating a date-based trigger node."""
        user = data_fixture.create_user()
        workspace = data_fixture.create_workspace(user=user)
        automation = data_fixture.create_automation_application(workspace=workspace)
        workflow = data_fixture.create_automation_workflow(automation=automation)
        
        table = data_fixture.create_table_for_workspace(workspace=workspace)
        date_field = data_fixture.create_date_field(table=table)
        
        # Create date-based trigger node
        trigger_node = DateBasedTriggerNode.objects.create(
            workflow=workflow,
            date_field=date_field,
            condition_type='date_reached',
            days_offset=0,
            order=1
        )
        
        assert trigger_node.date_field == date_field
        assert trigger_node.condition_type == 'date_reached'
        assert trigger_node.days_offset == 0
        assert trigger_node.workflow == workflow
    
    def test_date_trigger_recurring_pattern(self, data_fixture):
        """Test date trigger with recurring pattern."""
        user = data_fixture.create_user()
        workspace = data_fixture.create_workspace(user=user)
        automation = data_fixture.create_automation_application(workspace=workspace)
        workflow = data_fixture.create_automation_workflow(automation=automation)
        
        table = data_fixture.create_table_for_workspace(workspace=workspace)
        date_field = data_fixture.create_date_field(table=table)
        
        recurring_pattern = {
            'frequency': 'weekly',
            'weekday': 1  # Tuesday
        }
        
        trigger_node = DateBasedTriggerNode.objects.create(
            workflow=workflow,
            date_field=date_field,
            condition_type='recurring',
            recurring_pattern=recurring_pattern,
            check_time='09:00:00',
            order=1
        )
        
        assert trigger_node.recurring_pattern == recurring_pattern
        assert str(trigger_node.check_time) == '09:00:00'


@pytest.mark.django_db
class TestLinkedRecordChangeTriggerNode:
    """Test linked record change trigger functionality."""
    
    def test_create_link_trigger_node(self, data_fixture):
        """Test creating a linked record change trigger node."""
        user = data_fixture.create_user()
        workspace = data_fixture.create_workspace(user=user)
        automation = data_fixture.create_automation_application(workspace=workspace)
        workflow = data_fixture.create_automation_workflow(automation=automation)
        
        table1 = data_fixture.create_table_for_workspace(workspace=workspace)
        table2 = data_fixture.create_table_for_workspace(workspace=workspace)
        link_field = data_fixture.create_link_row_field(table=table1, link_row_table=table2)
        
        trigger_node = LinkedRecordChangeTriggerNode.objects.create(
            workflow=workflow,
            link_field=link_field,
            change_type='any_change',
            monitored_fields=[],
            order=1
        )
        
        assert trigger_node.link_field == link_field
        assert trigger_node.change_type == 'any_change'
        assert trigger_node.workflow == workflow


@pytest.mark.django_db
class TestWebhookTriggerNode:
    """Test webhook trigger functionality."""
    
    def test_create_webhook_trigger_node(self, data_fixture):
        """Test creating a webhook trigger node."""
        user = data_fixture.create_user()
        workspace = data_fixture.create_workspace(user=user)
        automation = data_fixture.create_automation_application(workspace=workspace)
        workflow = data_fixture.create_automation_workflow(automation=automation)
        
        trigger_node = WebhookTriggerNode.objects.create(
            workflow=workflow,
            webhook_url_path='test_webhook_123',
            auth_type='api_key',
            auth_token='secret_token',
            allowed_methods=['POST'],
            order=1
        )
        
        assert trigger_node.webhook_url_path == 'test_webhook_123'
        assert trigger_node.auth_type == 'api_key'
        assert trigger_node.allowed_methods == ['POST']
    
    def test_webhook_trigger_unique_path(self, data_fixture):
        """Test that webhook paths must be unique."""
        user = data_fixture.create_user()
        workspace = data_fixture.create_workspace(user=user)
        automation = data_fixture.create_automation_application(workspace=workspace)
        workflow = data_fixture.create_automation_workflow(automation=automation)
        
        # Create first webhook trigger
        WebhookTriggerNode.objects.create(
            workflow=workflow,
            webhook_url_path='unique_path',
            auth_type='api_key',
            order=1
        )
        
        # Try to create second with same path - should raise error
        with pytest.raises(Exception):  # IntegrityError due to unique constraint
            WebhookTriggerNode.objects.create(
                workflow=workflow,
                webhook_url_path='unique_path',
                auth_type='api_key',
                order=2
            )


@pytest.mark.django_db
class TestConditionalTriggerNode:
    """Test conditional trigger functionality."""
    
    def test_create_conditional_trigger_node(self, data_fixture):
        """Test creating a conditional trigger node."""
        user = data_fixture.create_user()
        workspace = data_fixture.create_workspace(user=user)
        automation = data_fixture.create_automation_application(workspace=workspace)
        workflow = data_fixture.create_automation_workflow(automation=automation)
        
        # Create base trigger
        base_trigger = data_fixture.create_automation_node(
            workflow=workflow,
            type='rows_created'
        )
        
        condition_groups = [
            {
                'conditions': [
                    {
                        'field': 'status',
                        'operator': 'equals',
                        'value': 'active'
                    }
                ],
                'logic': 'and'
            }
        ]
        
        trigger_node = ConditionalTriggerNode.objects.create(
            workflow=workflow,
            base_trigger=base_trigger,
            condition_groups=condition_groups,
            evaluation_mode='all_must_match',
            order=1
        )
        
        assert trigger_node.base_trigger == base_trigger
        assert trigger_node.condition_groups == condition_groups
        assert trigger_node.evaluation_mode == 'all_must_match'


@pytest.mark.django_db
class TestTriggerTemplate:
    """Test trigger template functionality."""
    
    def test_create_trigger_template(self):
        """Test creating a trigger template."""
        trigger_config = {
            'type': 'date_based_trigger',
            'date_field': 'due_date',
            'condition_type': 'days_before',
            'days_offset': 1
        }
        
        action_templates = [
            {
                'type': 'smtp_email',
                'to_field': 'assigned_to',
                'subject': 'Task Due Tomorrow',
                'body': 'Your task is due tomorrow.'
            }
        ]
        
        template = TriggerTemplate.objects.create(
            name='Due Date Reminder',
            description='Send reminders for tasks due soon',
            category='project_management',
            trigger_config=trigger_config,
            action_templates=action_templates,
            required_field_types=['date', 'email']
        )
        
        assert template.name == 'Due Date Reminder'
        assert template.category == 'project_management'
        assert template.trigger_config == trigger_config
        assert template.action_templates == action_templates
        assert template.is_active is True
        assert template.usage_count == 0


class TestDateBasedTriggerServiceType:
    """Test date-based trigger service type functionality."""
    
    def test_check_recurring_condition_daily(self):
        """Test daily recurring condition check."""
        service_type = DateBasedTriggerServiceType()
        
        # Mock trigger node with daily pattern
        trigger_node = MagicMock()
        trigger_node.recurring_pattern = {'frequency': 'daily'}
        trigger_node.check_time = None
        
        now = timezone.now()
        result = service_type._check_recurring_condition(trigger_node, now)
        
        assert result is True  # Daily should always return True
    
    def test_check_recurring_condition_weekly(self):
        """Test weekly recurring condition check."""
        service_type = DateBasedTriggerServiceType()
        
        # Mock trigger node with weekly pattern
        trigger_node = MagicMock()
        trigger_node.recurring_pattern = {'frequency': 'weekly', 'weekday': 1}  # Tuesday
        
        # Test on Tuesday (weekday 1)
        tuesday = datetime(2024, 1, 2)  # A Tuesday
        with patch('django.utils.timezone.now', return_value=tuesday):
            result = service_type._check_recurring_condition(trigger_node, tuesday)
            assert result is True
        
        # Test on Wednesday (weekday 2)
        wednesday = datetime(2024, 1, 3)  # A Wednesday
        with patch('django.utils.timezone.now', return_value=wednesday):
            result = service_type._check_recurring_condition(trigger_node, wednesday)
            assert result is False


class TestWebhookTriggerServiceType:
    """Test webhook trigger service type functionality."""
    
    def test_validate_api_key_auth(self):
        """Test API key authentication validation."""
        service_type = WebhookTriggerServiceType()
        
        # Mock trigger node with API key auth
        trigger_node = MagicMock()
        trigger_node.auth_type = 'api_key'
        trigger_node.auth_token = 'secret_key_123'
        trigger_node.allowed_methods = ['POST']
        
        # Test valid API key in headers
        headers = {'X-API-Key': 'secret_key_123'}
        result = service_type._validate_webhook_request(
            trigger_node, {}, 'POST', headers
        )
        assert result is True
        
        # Test invalid API key
        headers = {'X-API-Key': 'wrong_key'}
        result = service_type._validate_webhook_request(
            trigger_node, {}, 'POST', headers
        )
        assert result is False
        
        # Test missing API key
        headers = {}
        result = service_type._validate_webhook_request(
            trigger_node, {}, 'POST', headers
        )
        assert result is False
    
    def test_validate_bearer_token_auth(self):
        """Test Bearer token authentication validation."""
        service_type = WebhookTriggerServiceType()
        
        # Mock trigger node with Bearer token auth
        trigger_node = MagicMock()
        trigger_node.auth_type = 'bearer_token'
        trigger_node.auth_token = 'bearer_token_123'
        trigger_node.allowed_methods = ['POST']
        
        # Test valid Bearer token
        headers = {'Authorization': 'Bearer bearer_token_123'}
        result = service_type._validate_webhook_request(
            trigger_node, {}, 'POST', headers
        )
        assert result is True
        
        # Test invalid Bearer token
        headers = {'Authorization': 'Bearer wrong_token'}
        result = service_type._validate_webhook_request(
            trigger_node, {}, 'POST', headers
        )
        assert result is False


class TestConditionalTriggerServiceType:
    """Test conditional trigger service type functionality."""
    
    def test_evaluate_single_condition_equals(self):
        """Test evaluating a single equals condition."""
        service_type = ConditionalTriggerServiceType()
        
        condition = {
            'field': 'status',
            'operator': 'equals',
            'value': 'active'
        }
        
        context_data = {'status': 'active'}
        rows = []
        
        result = service_type._evaluate_single_condition(condition, context_data, rows)
        assert result is True
        
        # Test with different value
        context_data = {'status': 'inactive'}
        result = service_type._evaluate_single_condition(condition, context_data, rows)
        assert result is False
    
    def test_evaluate_condition_group_and_logic(self):
        """Test evaluating condition group with AND logic."""
        service_type = ConditionalTriggerServiceType()
        
        group = {
            'conditions': [
                {'field': 'status', 'operator': 'equals', 'value': 'active'},
                {'field': 'priority', 'operator': 'equals', 'value': 'high'}
            ],
            'logic': 'and'
        }
        
        # Test when both conditions are true
        context_data = {'status': 'active', 'priority': 'high'}
        result = service_type._evaluate_condition_group(group, context_data, [])
        assert result is True
        
        # Test when one condition is false
        context_data = {'status': 'active', 'priority': 'low'}
        result = service_type._evaluate_condition_group(group, context_data, [])
        assert result is False
    
    def test_evaluate_condition_group_or_logic(self):
        """Test evaluating condition group with OR logic."""
        service_type = ConditionalTriggerServiceType()
        
        group = {
            'conditions': [
                {'field': 'status', 'operator': 'equals', 'value': 'active'},
                {'field': 'priority', 'operator': 'equals', 'value': 'high'}
            ],
            'logic': 'or'
        }
        
        # Test when one condition is true
        context_data = {'status': 'active', 'priority': 'low'}
        result = service_type._evaluate_condition_group(group, context_data, [])
        assert result is True
        
        # Test when both conditions are false
        context_data = {'status': 'inactive', 'priority': 'low'}
        result = service_type._evaluate_condition_group(group, context_data, [])
        assert result is False


@pytest.mark.django_db
class TestTriggerTemplateHandler:
    """Test trigger template handler functionality."""
    
    def test_get_available_templates(self, data_fixture):
        """Test getting available templates."""
        # Create some test templates
        TriggerTemplate.objects.create(
            name='Test Template 1',
            description='Test description',
            category='notifications',
            trigger_config={'type': 'rows_created'},
            action_templates=[],
            is_active=True
        )
        
        TriggerTemplate.objects.create(
            name='Test Template 2',
            description='Test description',
            category='project_management',
            trigger_config={'type': 'date_based_trigger'},
            action_templates=[],
            is_active=False  # Inactive
        )
        
        handler = TriggerTemplateHandler()
        templates = handler.get_available_templates()
        
        # Should only return active templates
        assert len(templates) == 1
        assert templates[0]['name'] == 'Test Template 1'
        assert templates[0]['category'] == 'notifications'
    
    def test_template_compatibility_check(self, data_fixture):
        """Test template compatibility with table field types."""
        user = data_fixture.create_user()
        workspace = data_fixture.create_workspace(user=user)
        table = data_fixture.create_table_for_workspace(workspace=workspace)
        
        # Create fields of different types
        data_fixture.create_date_field(table=table)
        data_fixture.create_text_field(table=table)
        
        # Create template requiring date field
        template = TriggerTemplate.objects.create(
            name='Date Template',
            description='Requires date field',
            category='notifications',
            trigger_config={'type': 'date_based_trigger'},
            action_templates=[],
            required_field_types=['date'],
            is_active=True
        )
        
        handler = TriggerTemplateHandler()
        
        # Should be compatible since table has date field
        is_compatible = handler._is_template_compatible(template, table)
        assert is_compatible is True
        
        # Create template requiring field type not in table
        template2 = TriggerTemplate.objects.create(
            name='Link Template',
            description='Requires link field',
            category='notifications',
            trigger_config={'type': 'linked_record_change_trigger'},
            action_templates=[],
            required_field_types=['link_row'],
            is_active=True
        )
        
        # Should not be compatible since table has no link field
        is_compatible = handler._is_template_compatible(template2, table)
        assert is_compatible is False