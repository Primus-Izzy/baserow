"""
Comprehensive integration tests for API endpoints and database operations
in the Baserow Monday.com expansion.
"""
import pytest
import json
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from baserow.contrib.database.models import Database, Table
from baserow.contrib.database.fields.handler import FieldHandler
from baserow.contrib.database.views.handler import ViewHandler
from baserow.contrib.database.rows.handler import RowHandler
from baserow.core.models import Workspace

User = get_user_model()


class TestFieldTypeAPIIntegration(APITestCase):
    """Integration tests for field type API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='password'
        )
        self.workspace = Workspace.objects.create(name='Test Workspace')
        self.database = Database.objects.create(
            workspace=self.workspace,
            name='Test Database'
        )
        self.table = Table.objects.create(
            database=self.database,
            name='Test Table',
            order=1
        )
        self.client.force_authenticate(user=self.user)
    
    def test_formula_field_api_crud(self):
        """Test CRUD operations for formula fields via API."""
        # Create formula field
        url = reverse('api:database:fields:list', kwargs={'table_id': self.table.id})
        data = {
            'type': 'formula',
            'name': 'Test Formula',
            'formula_expression': '2 + 2'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        field_id = response.data['id']
        
        # Read formula field
        url = reverse('api:database:fields:item', kwargs={'field_id': field_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['formula_expression'], '2 + 2')
        
        # Update formula field
        data = {'formula_expression': '3 + 3'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['formula_expression'], '3 + 3')
        
        # Delete formula field
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_rollup_field_api_operations(self):
        """Test rollup field API operations."""
        # Create linked table and fields
        linked_table = Table.objects.create(
            database=self.database,
            name='Linked Table',
            order=2
        )
        
        link_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='link_row',
            name='Link Field',
            link_row_table=linked_table
        )
        
        number_field = FieldHandler().create_field(
            user=self.user,
            table=linked_table,
            type_name='number',
            name='Amount'
        )
        
        # Create rollup field via API
        url = reverse('api:database:fields:list', kwargs={'table_id': self.table.id})
        data = {
            'type': 'rollup',
            'name': 'Total Amount',
            'linked_field_id': link_field.id,
            'target_field_id': number_field.id,
            'aggregation_function': 'SUM'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['aggregation_function'], 'SUM')
    
    def test_progress_bar_field_api_operations(self):
        """Test progress bar field API operations."""
        url = reverse('api:database:fields:list', kwargs={'table_id': self.table.id})
        data = {
            'type': 'progress_bar',
            'name': 'Task Progress',
            'min_value': 0,
            'max_value': 100,
            'color_scheme': 'blue'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['color_scheme'], 'blue')
    
    def test_people_field_api_operations(self):
        """Test people field API operations."""
        url = reverse('api:database:fields:list', kwargs={'table_id': self.table.id})
        data = {
            'type': 'people',
            'name': 'Assignees',
            'multiple_collaborators': True,
            'notify_on_assignment': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['multiple_collaborators'])
    
    def test_field_validation_errors(self):
        """Test API validation errors for field creation."""
        url = reverse('api:database:fields:list', kwargs={'table_id': self.table.id})
        
        # Test invalid formula
        data = {
            'type': 'formula',
            'name': 'Invalid Formula',
            'formula_expression': 'invalid_syntax('
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test missing required fields
        data = {
            'type': 'rollup',
            'name': 'Incomplete Rollup'
            # Missing linked_field_id and target_field_id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestViewTypeAPIIntegration(APITestCase):
    """Integration tests for view type API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='password'
        )
        self.workspace = Workspace.objects.create(name='Test Workspace')
        self.database = Database.objects.create(
            workspace=self.workspace,
            name='Test Database'
        )
        self.table = Table.objects.create(
            database=self.database,
            name='Test Table',
            order=1
        )
        self.client.force_authenticate(user=self.user)
    
    def test_kanban_view_api_crud(self):
        """Test CRUD operations for kanban views via API."""
        # Create single select field for kanban
        status_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='single_select',
            name='Status'
        )
        
        # Create kanban view
        url = reverse('api:database:views:list', kwargs={'table_id': self.table.id})
        data = {
            'type': 'kanban',
            'name': 'Task Board',
            'single_select_field': status_field.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        view_id = response.data['id']
        
        # Read kanban view
        url = reverse('api:database:views:item', kwargs={'view_id': view_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['single_select_field'], status_field.id)
        
        # Update kanban view
        data = {'name': 'Updated Task Board'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Task Board')
    
    def test_timeline_view_api_operations(self):
        """Test timeline view API operations."""
        # Create date fields
        start_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='date',
            name='Start Date'
        )
        
        end_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='date',
            name='End Date'
        )
        
        # Create timeline view
        url = reverse('api:database:views:list', kwargs={'table_id': self.table.id})
        data = {
            'type': 'timeline',
            'name': 'Project Timeline',
            'start_date_field': start_field.id,
            'end_date_field': end_field.id,
            'zoom_level': 'week'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['zoom_level'], 'week')
    
    def test_calendar_view_api_operations(self):
        """Test calendar view API operations."""
        # Create date field
        date_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='date',
            name='Event Date'
        )
        
        # Create calendar view
        url = reverse('api:database:views:list', kwargs={'table_id': self.table.id})
        data = {
            'type': 'calendar',
            'name': 'Event Calendar',
            'date_field': date_field.id,
            'display_mode': 'month'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['display_mode'], 'month')
    
    def test_enhanced_form_view_api_operations(self):
        """Test enhanced form view API operations."""
        url = reverse('api:database:views:list', kwargs={'table_id': self.table.id})
        data = {
            'type': 'form',
            'name': 'Enhanced Form',
            'public': True,
            'custom_branding': True,
            'brand_colors': {'primary': '#007bff'}
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['public'])
        self.assertTrue(response.data['custom_branding'])
    
    def test_view_data_retrieval(self):
        """Test retrieving view data via API."""
        # Create a view
        view = ViewHandler().create_view(
            user=self.user,
            table=self.table,
            type_name='grid',
            name='Test View'
        )
        
        # Get view data
        url = reverse('api:database:views:list_rows', kwargs={'view_id': view.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)


class TestAutomationAPIIntegration(APITestCase):
    """Integration tests for automation API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='password'
        )
        self.workspace = Workspace.objects.create(name='Test Workspace')
        self.database = Database.objects.create(
            workspace=self.workspace,
            name='Test Database'
        )
        self.table = Table.objects.create(
            database=self.database,
            name='Test Table',
            order=1
        )
        self.client.force_authenticate(user=self.user)
    
    def test_automation_crud_operations(self):
        """Test CRUD operations for automations via API."""
        # Create automation
        url = reverse('api:database:automations:list', kwargs={'table_id': self.table.id})
        data = {
            'name': 'Test Automation',
            'is_active': True,
            'triggers': [
                {
                    'type': 'record_created',
                    'configuration': {}
                }
            ],
            'actions': [
                {
                    'type': 'update_field',
                    'configuration': {
                        'field_id': 1,
                        'value': 'Updated'
                    }
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        automation_id = response.data['id']
        
        # Read automation
        url = reverse('api:database:automations:item', kwargs={'automation_id': automation_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Automation')
        
        # Update automation
        data = {'is_active': False}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_active'])
    
    def test_automation_execution_api(self):
        """Test automation execution via API."""
        # This would test triggering automations through API calls
        pass
    
    def test_automation_template_api(self):
        """Test automation template API endpoints."""
        url = reverse('api:database:automation_templates:list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)


class TestCollaborationAPIIntegration(APITestCase):
    """Integration tests for collaboration API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='password'
        )
        self.workspace = Workspace.objects.create(name='Test Workspace')
        self.database = Database.objects.create(
            workspace=self.workspace,
            name='Test Database'
        )
        self.table = Table.objects.create(
            database=self.database,
            name='Test Table',
            order=1
        )
        self.client.force_authenticate(user=self.user)
    
    def test_comment_api_operations(self):
        """Test comment API operations."""
        # Create a row first
        row = RowHandler().create_row_for_table(
            user=self.user,
            table=self.table,
            values={}
        )
        
        # Create comment
        url = reverse('api:database:comments:list', kwargs={'table_id': self.table.id})
        data = {
            'row_id': row.id,
            'content': 'This is a test comment',
            'mentions': []
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment_id = response.data['id']
        
        # Read comments
        url = reverse('api:database:comments:list', kwargs={'table_id': self.table.id})
        response = self.client.get(url, {'row_id': row.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['results']) > 0)
        
        # Update comment
        url = reverse('api:database:comments:item', kwargs={'comment_id': comment_id})
        data = {'content': 'Updated comment'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Updated comment')
    
    def test_activity_log_api(self):
        """Test activity log API endpoints."""
        url = reverse('api:database:activity_log:list', kwargs={'table_id': self.table.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_notification_api_operations(self):
        """Test notification API operations."""
        # Get notifications
        url = reverse('api:database:notifications:list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Mark notification as read
        # This would require creating a notification first
        pass


class TestDashboardAPIIntegration(APITestCase):
    """Integration tests for dashboard API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='password'
        )
        self.workspace = Workspace.objects.create(name='Test Workspace')
        self.client.force_authenticate(user=self.user)
    
    def test_dashboard_crud_operations(self):
        """Test CRUD operations for dashboards via API."""
        # Create dashboard
        url = reverse('api:dashboard:dashboards:list', kwargs={'workspace_id': self.workspace.id})
        data = {
            'name': 'Test Dashboard',
            'layout': {'widgets': []},
            'is_public': False
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dashboard_id = response.data['id']
        
        # Read dashboard
        url = reverse('api:dashboard:dashboards:item', kwargs={'dashboard_id': dashboard_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Dashboard')
    
    def test_widget_crud_operations(self):
        """Test CRUD operations for dashboard widgets via API."""
        # This would test widget creation, reading, updating, and deletion
        pass
    
    def test_dashboard_sharing_api(self):
        """Test dashboard sharing API endpoints."""
        # This would test public dashboard link generation and management
        pass


class TestBatchOperationsAPI(APITestCase):
    """Integration tests for batch operations API."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='password'
        )
        self.workspace = Workspace.objects.create(name='Test Workspace')
        self.database = Database.objects.create(
            workspace=self.workspace,
            name='Test Database'
        )
        self.table = Table.objects.create(
            database=self.database,
            name='Test Table',
            order=1
        )
        self.client.force_authenticate(user=self.user)
    
    def test_batch_row_operations(self):
        """Test batch row operations via API."""
        # Create text field
        text_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='text',
            name='Name'
        )
        
        # Batch create rows
        url = reverse('api:database:rows:batch_create', kwargs={'table_id': self.table.id})
        data = {
            'rows': [
                {f'field_{text_field.id}': 'Row 1'},
                {f'field_{text_field.id}': 'Row 2'},
                {f'field_{text_field.id}': 'Row 3'}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['rows']), 3)
    
    def test_batch_field_operations(self):
        """Test batch field operations via API."""
        # Batch create fields
        url = reverse('api:database:fields:batch_create', kwargs={'table_id': self.table.id})
        data = {
            'fields': [
                {'type': 'text', 'name': 'Field 1'},
                {'type': 'number', 'name': 'Field 2'},
                {'type': 'date', 'name': 'Field 3'}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['fields']), 3)


class TestWebhookAPIIntegration(APITestCase):
    """Integration tests for webhook API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='password'
        )
        self.workspace = Workspace.objects.create(name='Test Workspace')
        self.database = Database.objects.create(
            workspace=self.workspace,
            name='Test Database'
        )
        self.table = Table.objects.create(
            database=self.database,
            name='Test Table',
            order=1
        )
        self.client.force_authenticate(user=self.user)
    
    def test_webhook_crud_operations(self):
        """Test CRUD operations for webhooks via API."""
        # Create webhook
        url = reverse('api:database:webhooks:list', kwargs={'table_id': self.table.id})
        data = {
            'url': 'https://example.com/webhook',
            'events': ['row.created', 'row.updated'],
            'active': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        webhook_id = response.data['id']
        
        # Read webhook
        url = reverse('api:database:webhooks:item', kwargs={'webhook_id': webhook_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['url'], 'https://example.com/webhook')
    
    def test_webhook_delivery_testing(self):
        """Test webhook delivery testing via API."""
        # This would test webhook delivery and retry mechanisms
        pass


@pytest.mark.django_db
class TestDatabaseOperationsIntegration:
    """Integration tests for database operations."""
    
    def test_complex_query_performance(self):
        """Test performance of complex database queries."""
        # This would test query performance with large datasets
        pass
    
    def test_transaction_handling(self):
        """Test database transaction handling."""
        # This would test transaction rollback and commit scenarios
        pass
    
    def test_migration_operations(self):
        """Test database migration operations."""
        # This would test schema migrations for new features
        pass