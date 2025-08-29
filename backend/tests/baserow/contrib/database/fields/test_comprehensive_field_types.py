"""
Comprehensive unit tests for all new field types in the Baserow Monday.com expansion.
"""
import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model

from baserow.contrib.database.fields.models import (
    FormulaField, RollupField, LookupField, ProgressBarField, PeopleField
)
from baserow.contrib.database.fields.handler import FieldHandler
from baserow.contrib.database.models import Database, Table
from baserow.core.models import Workspace

User = get_user_model()


class TestFormulaField(TestCase):
    """Test cases for Formula field type."""
    
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
    
    def test_formula_field_creation(self):
        """Test creating a formula field."""
        field_handler = FieldHandler()
        formula_field = field_handler.create_field(
            user=self.user,
            table=self.table,
            type_name='formula',
            name='Test Formula',
            formula_expression='field("Number Field") * 2'
        )
        
        self.assertIsInstance(formula_field, FormulaField)
        self.assertEqual(formula_field.name, 'Test Formula')
        self.assertEqual(formula_field.formula_expression, 'field("Number Field") * 2')
    
    def test_formula_evaluation(self):
        """Test formula evaluation with dependencies."""
        # Create a number field first
        number_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='number',
            name='Number Field'
        )
        
        # Create formula field
        formula_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='formula',
            name='Double Number',
            formula_expression=f'field("{number_field.name}") * 2'
        )
        
        # Test evaluation
        row_data = {f'field_{number_field.id}': 5}
        result = formula_field.evaluate(row_data)
        self.assertEqual(result, 10)
    
    def test_formula_dependency_tracking(self):
        """Test that formula dependencies are tracked correctly."""
        number_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='number',
            name='Base Number'
        )
        
        formula_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='formula',
            name='Calculated',
            formula_expression=f'field("{number_field.name}") + 10'
        )
        
        self.assertIn(number_field.id, formula_field.dependencies)
    
    def test_formula_syntax_validation(self):
        """Test formula syntax validation."""
        with self.assertRaises(ValueError):
            FieldHandler().create_field(
                user=self.user,
                table=self.table,
                type_name='formula',
                name='Invalid Formula',
                formula_expression='invalid_syntax('
            )
    
    def test_circular_dependency_detection(self):
        """Test detection of circular dependencies in formulas."""
        field1 = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='formula',
            name='Field 1',
            formula_expression='10'
        )
        
        field2 = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='formula',
            name='Field 2',
            formula_expression=f'field("{field1.name}") + 5'
        )
        
        # Try to create circular dependency
        with self.assertRaises(ValueError):
            field1.formula_expression = f'field("{field2.name}") + 1'
            field1.save()


class TestRollupField(TestCase):
    """Test cases for Rollup field type."""
    
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
        self.main_table = Table.objects.create(
            database=self.database,
            name='Main Table',
            order=1
        )
        self.linked_table = Table.objects.create(
            database=self.database,
            name='Linked Table',
            order=2
        )
    
    def test_rollup_field_creation(self):
        """Test creating a rollup field."""
        # Create link field
        link_field = FieldHandler().create_field(
            user=self.user,
            table=self.main_table,
            type_name='link_row',
            name='Link Field',
            link_row_table=self.linked_table
        )
        
        # Create number field in linked table
        number_field = FieldHandler().create_field(
            user=self.user,
            table=self.linked_table,
            type_name='number',
            name='Amount'
        )
        
        # Create rollup field
        rollup_field = FieldHandler().create_field(
            user=self.user,
            table=self.main_table,
            type_name='rollup',
            name='Total Amount',
            linked_field=link_field,
            target_field=number_field,
            aggregation_function='SUM'
        )
        
        self.assertIsInstance(rollup_field, RollupField)
        self.assertEqual(rollup_field.aggregation_function, 'SUM')
    
    def test_rollup_calculation_sum(self):
        """Test rollup calculation with SUM function."""
        # Setup fields and data
        link_field = FieldHandler().create_field(
            user=self.user,
            table=self.main_table,
            type_name='link_row',
            name='Orders',
            link_row_table=self.linked_table
        )
        
        amount_field = FieldHandler().create_field(
            user=self.user,
            table=self.linked_table,
            type_name='number',
            name='Amount'
        )
        
        rollup_field = FieldHandler().create_field(
            user=self.user,
            table=self.main_table,
            type_name='rollup',
            name='Total',
            linked_field=link_field,
            target_field=amount_field,
            aggregation_function='SUM'
        )
        
        # Mock linked data
        with patch.object(rollup_field, 'get_linked_values') as mock_get_values:
            mock_get_values.return_value = [100, 200, 300]
            result = rollup_field.calculate_rollup(row_id=1)
            self.assertEqual(result, 600)
    
    def test_rollup_calculation_average(self):
        """Test rollup calculation with AVERAGE function."""
        rollup_field = RollupField(aggregation_function='AVERAGE')
        
        with patch.object(rollup_field, 'get_linked_values') as mock_get_values:
            mock_get_values.return_value = [10, 20, 30]
            result = rollup_field.calculate_rollup(row_id=1)
            self.assertEqual(result, 20)
    
    def test_rollup_calculation_count(self):
        """Test rollup calculation with COUNT function."""
        rollup_field = RollupField(aggregation_function='COUNT')
        
        with patch.object(rollup_field, 'get_linked_values') as mock_get_values:
            mock_get_values.return_value = [1, 2, 3, 4, 5]
            result = rollup_field.calculate_rollup(row_id=1)
            self.assertEqual(result, 5)


class TestProgressBarField(TestCase):
    """Test cases for Progress Bar field type."""
    
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
    
    def test_progress_bar_field_creation(self):
        """Test creating a progress bar field."""
        progress_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='progress_bar',
            name='Task Progress',
            min_value=0,
            max_value=100,
            color_scheme='blue'
        )
        
        self.assertIsInstance(progress_field, ProgressBarField)
        self.assertEqual(progress_field.min_value, 0)
        self.assertEqual(progress_field.max_value, 100)
        self.assertEqual(progress_field.color_scheme, 'blue')
    
    def test_progress_calculation_from_numeric(self):
        """Test progress calculation from numeric field."""
        number_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='number',
            name='Completed Tasks'
        )
        
        progress_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='progress_bar',
            name='Progress',
            source_field=number_field,
            max_value=10
        )
        
        # Test percentage calculation
        percentage = progress_field.calculate_percentage(7)
        self.assertEqual(percentage, 70)
    
    def test_progress_color_schemes(self):
        """Test different color schemes for progress bars."""
        progress_field = ProgressBarField(color_scheme='gradient')
        
        # Test color calculation based on percentage
        color = progress_field.get_color_for_percentage(25)
        self.assertIsNotNone(color)
        
        color = progress_field.get_color_for_percentage(75)
        self.assertIsNotNone(color)


class TestPeopleField(TestCase):
    """Test cases for People/Owner field type."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='password'
        )
        self.user2 = User.objects.create_user(
            username='test2@example.com',
            email='test2@example.com',
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
    
    def test_people_field_creation(self):
        """Test creating a people field."""
        people_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='people',
            name='Assignees',
            multiple_collaborators=True
        )
        
        self.assertIsInstance(people_field, PeopleField)
        self.assertTrue(people_field.multiple_collaborators)
    
    def test_people_field_user_assignment(self):
        """Test assigning users to people field."""
        people_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='people',
            name='Owner',
            multiple_collaborators=False
        )
        
        # Test single user assignment
        people_field.assign_user(self.user.id)
        assigned_users = people_field.get_assigned_users()
        self.assertIn(self.user.id, assigned_users)
    
    def test_people_field_permissions(self):
        """Test people field respects user permissions."""
        people_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='people',
            name='Team Members'
        )
        
        # Test permission checking
        has_permission = people_field.user_has_permission(self.user, 'view')
        self.assertTrue(has_permission)
    
    def test_people_field_notifications(self):
        """Test people field integration with notifications."""
        people_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='people',
            name='Reviewers',
            notify_on_assignment=True
        )
        
        with patch('baserow.contrib.database.notifications.handler.NotificationHandler.send_notification') as mock_notify:
            people_field.assign_user(self.user2.id)
            mock_notify.assert_called_once()


class TestLookupField(TestCase):
    """Test cases for Lookup field type."""
    
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
        self.main_table = Table.objects.create(
            database=self.database,
            name='Main Table',
            order=1
        )
        self.linked_table = Table.objects.create(
            database=self.database,
            name='Linked Table',
            order=2
        )
    
    def test_lookup_field_creation(self):
        """Test creating a lookup field."""
        link_field = FieldHandler().create_field(
            user=self.user,
            table=self.main_table,
            type_name='link_row',
            name='Product Link',
            link_row_table=self.linked_table
        )
        
        text_field = FieldHandler().create_field(
            user=self.user,
            table=self.linked_table,
            type_name='text',
            name='Product Name'
        )
        
        lookup_field = FieldHandler().create_field(
            user=self.user,
            table=self.main_table,
            type_name='lookup',
            name='Product Name Lookup',
            linked_field=link_field,
            target_field=text_field
        )
        
        self.assertIsInstance(lookup_field, LookupField)
        self.assertEqual(lookup_field.target_field, text_field)
    
    def test_lookup_value_retrieval(self):
        """Test lookup field value retrieval."""
        lookup_field = LookupField()
        
        with patch.object(lookup_field, 'get_linked_value') as mock_get_value:
            mock_get_value.return_value = 'Test Product'
            result = lookup_field.lookup_value(row_id=1)
            self.assertEqual(result, 'Test Product')
    
    def test_lookup_field_performance(self):
        """Test lookup field query optimization."""
        # This would test that lookup fields use efficient queries
        # and don't cause N+1 query problems
        pass


@pytest.mark.django_db
class TestFieldTypeIntegration:
    """Integration tests for field types working together."""
    
    def test_formula_with_rollup_dependency(self):
        """Test formula field that depends on rollup field."""
        # This would test complex field dependencies
        pass
    
    def test_progress_bar_with_formula_source(self):
        """Test progress bar field using formula as source."""
        # This would test progress bar with formula calculations
        pass
    
    def test_people_field_with_lookup_display(self):
        """Test people field displaying lookup values."""
        # This would test complex field interactions
        pass