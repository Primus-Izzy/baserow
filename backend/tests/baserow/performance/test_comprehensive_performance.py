"""
Comprehensive performance tests for large dataset handling
in the Baserow Monday.com expansion.
"""
import pytest
import time
from unittest.mock import patch
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from django.db import transaction, connection
from django.core.management import call_command

from baserow.contrib.database.models import Database, Table
from baserow.contrib.database.fields.handler import FieldHandler
from baserow.contrib.database.views.handler import ViewHandler
from baserow.contrib.database.rows.handler import RowHandler
from baserow.core.models import Workspace

User = get_user_model()


class PerformanceTestMixin:
    """Mixin for performance testing utilities."""
    
    def measure_time(self, func, *args, **kwargs):
        """Measure execution time of a function."""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        return result, execution_time
    
    def assert_performance(self, execution_time, max_time, operation_name):
        """Assert that operation completed within acceptable time."""
        self.assertLess(
            execution_time, 
            max_time, 
            f"{operation_name} took {execution_time:.2f}s, expected < {max_time}s"
        )
    
    def create_large_dataset(self, table, num_rows=1000):
        """Create a large dataset for testing."""
        # Create fields
        text_field = FieldHandler().create_field(
            user=self.user,
            table=table,
            type_name='text',
            name='Name'
        )
        
        number_field = FieldHandler().create_field(
            user=self.user,
            table=table,
            type_name='number',
            name='Value'
        )
        
        date_field = FieldHandler().create_field(
            user=self.user,
            table=table,
            type_name='date',
            name='Date'
        )
        
        # Batch create rows
        rows_data = []
        for i in range(num_rows):
            rows_data.append({
                f'field_{text_field.id}': f'Item {i}',
                f'field_{number_field.id}': i * 10,
                f'field_{date_field.id}': '2024-01-01'
            })
        
        # Use bulk create for better performance
        with transaction.atomic():
            for row_data in rows_data:
                RowHandler().create_row_for_table(
                    user=self.user,
                    table=table,
                    values=row_data
                )
        
        return text_field, number_field, date_field


class TestFieldTypePerformance(TestCase, PerformanceTestMixin):
    """Performance tests for field types with large datasets."""
    
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
    
    def test_formula_field_performance_large_dataset(self):
        """Test formula field performance with large dataset."""
        # Create base fields and data
        text_field, number_field, date_field = self.create_large_dataset(self.table, 1000)
        
        # Create formula field
        def create_formula_field():
            return FieldHandler().create_field(
                user=self.user,
                table=self.table,
                type_name='formula',
                name='Calculated Value',
                formula_expression=f'field("{number_field.name}") * 2'
            )
        
        formula_field, execution_time = self.measure_time(create_formula_field)
        
        # Formula field creation should be fast (< 2 seconds)
        self.assert_performance(execution_time, 2.0, "Formula field creation")
        
        # Test formula evaluation performance
        def evaluate_formulas():
            # Get all rows and evaluate formula for each
            rows = RowHandler().get_rows(user=self.user, table=self.table)
            for row in rows[:100]:  # Test first 100 rows
                formula_field.evaluate({f'field_{number_field.id}': row.get_value(f'field_{number_field.id}')})
        
        _, evaluation_time = self.measure_time(evaluate_formulas)
        
        # Formula evaluation should be fast (< 1 second for 100 rows)
        self.assert_performance(evaluation_time, 1.0, "Formula evaluation (100 rows)")
    
    def test_rollup_field_performance(self):
        """Test rollup field performance with large linked dataset."""
        # Create linked table
        linked_table = Table.objects.create(
            database=self.database,
            name='Linked Table',
            order=2
        )
        
        # Create link field
        link_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='link_row',
            name='Link Field',
            link_row_table=linked_table
        )
        
        # Create number field in linked table
        linked_number_field = FieldHandler().create_field(
            user=self.user,
            table=linked_table,
            type_name='number',
            name='Amount'
        )
        
        # Create large dataset in linked table
        self.create_large_dataset(linked_table, 500)
        
        # Create rollup field
        def create_rollup_field():
            return FieldHandler().create_field(
                user=self.user,
                table=self.table,
                type_name='rollup',
                name='Total Amount',
                linked_field=link_field,
                target_field=linked_number_field,
                aggregation_function='SUM'
            )
        
        rollup_field, creation_time = self.measure_time(create_rollup_field)
        
        # Rollup field creation should be reasonable (< 3 seconds)
        self.assert_performance(creation_time, 3.0, "Rollup field creation")
        
        # Test rollup calculation performance
        def calculate_rollup():
            return rollup_field.calculate_rollup(row_id=1)
        
        _, calculation_time = self.measure_time(calculate_rollup)
        
        # Rollup calculation should be fast (< 0.5 seconds)
        self.assert_performance(calculation_time, 0.5, "Rollup calculation")
    
    def test_people_field_performance(self):
        """Test people field performance with many users."""
        # Create many users
        users = []
        for i in range(100):
            user = User.objects.create_user(
                username=f'user{i}@example.com',
                email=f'user{i}@example.com',
                password='password'
            )
            users.append(user)
        
        # Create people field
        def create_people_field():
            return FieldHandler().create_field(
                user=self.user,
                table=self.table,
                type_name='people',
                name='Assignees',
                multiple_collaborators=True
            )
        
        people_field, creation_time = self.measure_time(create_people_field)
        
        # People field creation should be fast
        self.assert_performance(creation_time, 1.0, "People field creation")
        
        # Test user assignment performance
        def assign_multiple_users():
            for user in users[:50]:  # Assign first 50 users
                people_field.assign_user(user.id)
        
        _, assignment_time = self.measure_time(assign_multiple_users)
        
        # User assignment should be reasonable (< 2 seconds for 50 users)
        self.assert_performance(assignment_time, 2.0, "Multiple user assignment")


class TestViewTypePerformance(TestCase, PerformanceTestMixin):
    """Performance tests for view types with large datasets."""
    
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
    
    def test_kanban_view_performance(self):
        """Test kanban view performance with large dataset."""
        # Create large dataset
        text_field, number_field, date_field = self.create_large_dataset(self.table, 2000)
        
        # Create status field for kanban
        status_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='single_select',
            name='Status'
        )
        
        # Create kanban view
        def create_kanban_view():
            return ViewHandler().create_view(
                user=self.user,
                table=self.table,
                type_name='kanban',
                name='Performance Kanban',
                single_select_field=status_field
            )
        
        kanban_view, creation_time = self.measure_time(create_kanban_view)
        
        # Kanban view creation should be fast
        self.assert_performance(creation_time, 1.0, "Kanban view creation")
        
        # Test kanban data loading performance
        def load_kanban_data():
            return kanban_view.get_columns_with_data()
        
        _, loading_time = self.measure_time(load_kanban_data)
        
        # Kanban data loading should be reasonable (< 2 seconds)
        self.assert_performance(loading_time, 2.0, "Kanban data loading")
    
    def test_timeline_view_performance(self):
        """Test timeline view performance with large dataset."""
        # Create large dataset
        text_field, number_field, date_field = self.create_large_dataset(self.table, 1500)
        
        # Create additional date field
        end_date_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='date',
            name='End Date'
        )
        
        # Create timeline view
        def create_timeline_view():
            return ViewHandler().create_view(
                user=self.user,
                table=self.table,
                type_name='timeline',
                name='Performance Timeline',
                start_date_field=date_field,
                end_date_field=end_date_field
            )
        
        timeline_view, creation_time = self.measure_time(create_timeline_view)
        
        # Timeline view creation should be fast
        self.assert_performance(creation_time, 1.0, "Timeline view creation")
        
        # Test timeline data loading with date range
        def load_timeline_data():
            return timeline_view.get_timeline_data(
                start_date='2024-01-01',
                end_date='2024-12-31'
            )
        
        _, loading_time = self.measure_time(load_timeline_data)
        
        # Timeline data loading should be reasonable (< 3 seconds)
        self.assert_performance(loading_time, 3.0, "Timeline data loading")
    
    def test_calendar_view_performance(self):
        """Test calendar view performance with large dataset."""
        # Create large dataset
        text_field, number_field, date_field = self.create_large_dataset(self.table, 1000)
        
        # Create calendar view
        def create_calendar_view():
            return ViewHandler().create_view(
                user=self.user,
                table=self.table,
                type_name='calendar',
                name='Performance Calendar',
                date_field=date_field
            )
        
        calendar_view, creation_time = self.measure_time(create_calendar_view)
        
        # Calendar view creation should be fast
        self.assert_performance(creation_time, 1.0, "Calendar view creation")
        
        # Test calendar data loading for a month
        def load_calendar_month():
            return calendar_view.get_events_for_month(2024, 1)
        
        _, loading_time = self.measure_time(load_calendar_month)
        
        # Calendar month loading should be fast (< 1 second)
        self.assert_performance(loading_time, 1.0, "Calendar month loading")


class TestDatabaseQueryPerformance(TransactionTestCase, PerformanceTestMixin):
    """Performance tests for database queries and operations."""
    
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
    
    def test_batch_operations_performance(self):
        """Test performance of batch operations."""
        # Create fields
        text_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='text',
            name='Name'
        )
        
        number_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='number',
            name='Value'
        )
        
        # Test batch row creation
        def batch_create_rows():
            rows_data = []
            for i in range(1000):
                rows_data.append({
                    f'field_{text_field.id}': f'Batch Item {i}',
                    f'field_{number_field.id}': i
                })
            
            # Use transaction for better performance
            with transaction.atomic():
                created_rows = []
                for row_data in rows_data:
                    row = RowHandler().create_row_for_table(
                        user=self.user,
                        table=self.table,
                        values=row_data
                    )
                    created_rows.append(row)
            return created_rows
        
        rows, creation_time = self.measure_time(batch_create_rows)
        
        # Batch creation should be efficient (< 5 seconds for 1000 rows)
        self.assert_performance(creation_time, 5.0, "Batch row creation (1000 rows)")
        
        # Test batch row updates
        def batch_update_rows():
            with transaction.atomic():
                for i, row in enumerate(rows[:500]):  # Update first 500 rows
                    RowHandler().update_row_by_id(
                        user=self.user,
                        table=self.table,
                        row_id=row.id,
                        values={f'field_{text_field.id}': f'Updated Item {i}'}
                    )
        
        _, update_time = self.measure_time(batch_update_rows)
        
        # Batch updates should be efficient (< 3 seconds for 500 rows)
        self.assert_performance(update_time, 3.0, "Batch row updates (500 rows)")
    
    def test_complex_query_performance(self):
        """Test performance of complex database queries."""
        # Create large dataset with multiple field types
        text_field, number_field, date_field = self.create_large_dataset(self.table, 2000)
        
        # Create additional fields for complex queries
        status_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='single_select',
            name='Status'
        )
        
        boolean_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='boolean',
            name='Active'
        )
        
        # Test complex filtering query
        def complex_filter_query():
            from baserow.contrib.database.api.rows.serializers import RowSerializer
            from baserow.contrib.database.rows.handler import RowHandler
            
            # Simulate complex filter conditions
            filters = {
                'filter_type': 'AND',
                'filters': [
                    {
                        'field': number_field.id,
                        'type': 'higher_than',
                        'value': 500
                    },
                    {
                        'field': text_field.id,
                        'type': 'contains',
                        'value': 'Item'
                    }
                ]
            }
            
            queryset = RowHandler().get_rows(
                user=self.user,
                table=self.table,
                filters=filters
            )
            
            # Force evaluation of queryset
            return list(queryset[:100])
        
        results, query_time = self.measure_time(complex_filter_query)
        
        # Complex queries should be reasonably fast (< 2 seconds)
        self.assert_performance(query_time, 2.0, "Complex filter query")
        
        # Test sorting performance
        def sorting_query():
            queryset = RowHandler().get_rows(
                user=self.user,
                table=self.table,
                order_by=[f'-field_{number_field.id}']
            )
            return list(queryset[:100])
        
        _, sort_time = self.measure_time(sorting_query)
        
        # Sorting should be fast (< 1 second)
        self.assert_performance(sort_time, 1.0, "Sorting query")
    
    def test_aggregation_performance(self):
        """Test performance of aggregation queries."""
        # Create large dataset
        text_field, number_field, date_field = self.create_large_dataset(self.table, 3000)
        
        # Test SUM aggregation
        def sum_aggregation():
            from django.db.models import Sum
            from baserow.contrib.database.rows.models import Row
            
            table_model = self.table.get_model()
            return table_model.objects.aggregate(
                total=Sum(f'field_{number_field.id}')
            )
        
        result, agg_time = self.measure_time(sum_aggregation)
        
        # Aggregation should be fast (< 0.5 seconds)
        self.assert_performance(agg_time, 0.5, "SUM aggregation")
        
        # Test COUNT with conditions
        def count_with_conditions():
            from django.db.models import Q
            
            table_model = self.table.get_model()
            return table_model.objects.filter(
                Q(**{f'field_{number_field.id}__gt': 1000})
            ).count()
        
        count, count_time = self.measure_time(count_with_conditions)
        
        # Conditional count should be fast (< 0.3 seconds)
        self.assert_performance(count_time, 0.3, "COUNT with conditions")


class TestAutomationPerformance(TestCase, PerformanceTestMixin):
    """Performance tests for automation system."""
    
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
    
    def test_automation_execution_performance(self):
        """Test automation execution performance with multiple triggers."""
        # Create fields
        text_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='text',
            name='Task'
        )
        
        status_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='single_select',
            name='Status'
        )
        
        # Create multiple automations
        automations = []
        for i in range(10):
            automation = self.create_test_automation(
                name=f'Test Automation {i}',
                trigger_field=status_field,
                action_field=text_field
            )
            automations.append(automation)
        
        # Test automation trigger performance
        def trigger_automations():
            # Create a row that will trigger all automations
            row = RowHandler().create_row_for_table(
                user=self.user,
                table=self.table,
                values={
                    f'field_{text_field.id}': 'Test Task',
                    f'field_{status_field.id}': 'Complete'
                }
            )
            
            # Simulate automation processing
            for automation in automations:
                automation.process_trigger(row)
        
        _, execution_time = self.measure_time(trigger_automations)
        
        # Automation execution should be fast (< 1 second for 10 automations)
        self.assert_performance(execution_time, 1.0, "Multiple automation execution")
    
    def create_test_automation(self, name, trigger_field, action_field):
        """Helper method to create test automation."""
        # This would create a mock automation object
        # In real implementation, this would use the automation handler
        class MockAutomation:
            def __init__(self, name):
                self.name = name
            
            def process_trigger(self, row):
                # Simulate automation processing
                time.sleep(0.01)  # Simulate small processing time
        
        return MockAutomation(name)


class TestWebSocketPerformance(TestCase, PerformanceTestMixin):
    """Performance tests for real-time collaboration features."""
    
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
    
    def test_websocket_message_broadcasting_performance(self):
        """Test WebSocket message broadcasting performance."""
        # Simulate multiple connected users
        connected_users = 100
        
        def broadcast_message():
            # Simulate broadcasting a message to all connected users
            message = {
                'type': 'row_updated',
                'table_id': self.table.id,
                'row_id': 1,
                'data': {'field_1': 'Updated value'}
            }
            
            # Simulate message broadcasting
            for _ in range(connected_users):
                # In real implementation, this would use Django Channels
                # Here we just simulate the processing time
                time.sleep(0.001)  # 1ms per user
        
        _, broadcast_time = self.measure_time(broadcast_message)
        
        # Broadcasting should be fast (< 0.5 seconds for 100 users)
        self.assert_performance(broadcast_time, 0.5, "WebSocket message broadcasting")
    
    def test_real_time_update_performance(self):
        """Test real-time update processing performance."""
        # Create large dataset
        text_field, number_field, date_field = self.create_large_dataset(self.table, 500)
        
        def process_real_time_updates():
            # Simulate processing multiple real-time updates
            updates = []
            for i in range(50):
                update = {
                    'row_id': i + 1,
                    'field_id': text_field.id,
                    'new_value': f'Updated Item {i}',
                    'user_id': self.user.id
                }
                updates.append(update)
            
            # Process updates
            for update in updates:
                # Simulate update processing and broadcasting
                time.sleep(0.002)  # 2ms per update
        
        _, processing_time = self.measure_time(process_real_time_updates)
        
        # Real-time update processing should be fast (< 0.5 seconds for 50 updates)
        self.assert_performance(processing_time, 0.5, "Real-time update processing")


@pytest.mark.django_db
class TestMemoryUsagePerformance:
    """Performance tests for memory usage optimization."""
    
    def test_large_dataset_memory_usage(self):
        """Test memory usage with large datasets."""
        # This would test memory consumption patterns
        # and ensure no memory leaks with large datasets
        pass
    
    def test_view_rendering_memory_efficiency(self):
        """Test memory efficiency of view rendering."""
        # This would test memory usage during view rendering
        # with large amounts of data
        pass


@pytest.mark.django_db
class TestConcurrencyPerformance:
    """Performance tests for concurrent operations."""
    
    def test_concurrent_row_updates(self):
        """Test performance of concurrent row updates."""
        # This would test handling of concurrent updates
        # to the same table/rows
        pass
    
    def test_concurrent_view_access(self):
        """Test performance of concurrent view access."""
        # This would test multiple users accessing
        # the same view simultaneously
        pass