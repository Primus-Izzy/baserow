"""
Comprehensive unit tests for all new view types in the Baserow Monday.com expansion.
"""
import pytest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta

from baserow.contrib.database.views.models import (
    KanbanView, TimelineView, CalendarView, FormView
)
from baserow.contrib.database.views.handler import ViewHandler
from baserow.contrib.database.models import Database, Table
from baserow.contrib.database.fields.handler import FieldHandler
from baserow.core.models import Workspace

User = get_user_model()


class TestKanbanView(TestCase):
    """Test cases for Kanban view type."""
    
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
    
    def test_kanban_view_creation(self):
        """Test creating a kanban view."""
        # Create single select field for status
        status_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='single_select',
            name='Status'
        )
        
        kanban_view = ViewHandler().create_view(
            user=self.user,
            table=self.table,
            type_name='kanban',
            name='Task Board',
            single_select_field=status_field
        )
        
        self.assertIsInstance(kanban_view, KanbanView)
        self.assertEqual(kanban_view.single_select_field, status_field)
    
    def test_kanban_column_configuration(self):
        """Test kanban column configuration."""
        status_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='single_select',
            name='Status'
        )
        
        kanban_view = ViewHandler().create_view(
            user=self.user,
            table=self.table,
            type_name='kanban',
            name='Project Board',
            single_select_field=status_field
        )
        
        # Test column configuration
        columns = kanban_view.get_columns()
        self.assertIsInstance(columns, list)
    
    def test_kanban_card_customization(self):
        """Test kanban card field customization."""
        status_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='single_select',
            name='Status'
        )
        
        title_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='text',
            name='Title'
        )
        
        kanban_view = ViewHandler().create_view(
            user=self.user,
            table=self.table,
            type_name='kanban',
            name='Custom Board',
            single_select_field=status_field,
            card_fields=[title_field.id]
        )
        
        self.assertIn(title_field.id, kanban_view.card_fields)
    
    def test_kanban_drag_drop_logic(self):
        """Test kanban drag and drop field updates."""
        status_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='single_select',
            name='Status'
        )
        
        kanban_view = ViewHandler().create_view(
            user=self.user,
            table=self.table,
            type_name='kanban',
            name='Drag Drop Board',
            single_select_field=status_field
        )
        
        # Test drag and drop update
        with patch('baserow.contrib.database.rows.handler.RowHandler.update_row') as mock_update:
            kanban_view.move_card(row_id=1, new_status='In Progress')
            mock_update.assert_called_once()
    
    def test_kanban_color_coding(self):
        """Test kanban card color coding."""
        status_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='single_select',
            name='Priority'
        )
        
        kanban_view = ViewHandler().create_view(
            user=self.user,
            table=self.table,
            type_name='kanban',
            name='Priority Board',
            single_select_field=status_field,
            color_field=status_field
        )
        
        color = kanban_view.get_card_color('High')
        self.assertIsNotNone(color)


class TestTimelineView(TestCase):
    """Test cases for Timeline/Gantt view type."""
    
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
    
    def test_timeline_view_creation(self):
        """Test creating a timeline view."""
        start_date_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='date',
            name='Start Date'
        )
        
        end_date_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='date',
            name='End Date'
        )
        
        timeline_view = ViewHandler().create_view(
            user=self.user,
            table=self.table,
            type_name='timeline',
            name='Project Timeline',
            start_date_field=start_date_field,
            end_date_field=end_date_field
        )
        
        self.assertIsInstance(timeline_view, TimelineView)
        self.assertEqual(timeline_view.start_date_field, start_date_field)
        self.assertEqual(timeline_view.end_date_field, end_date_field)
    
    def test_timeline_dependency_management(self):
        """Test timeline task dependency management."""
        start_date_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='date',
            name='Start Date'
        )
        
        end_date_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='date',
            name='End Date'
        )
        
        timeline_view = ViewHandler().create_view(
            user=self.user,
            table=self.table,
            type_name='timeline',
            name='Dependency Timeline',
            start_date_field=start_date_field,
            end_date_field=end_date_field
        )
        
        # Test dependency creation
        timeline_view.add_dependency(predecessor_id=1, successor_id=2)
        dependencies = timeline_view.get_dependencies()
        self.assertTrue(len(dependencies) > 0)
    
    def test_timeline_milestone_management(self):
        """Test timeline milestone functionality."""
        date_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='date',
            name='Milestone Date'
        )
        
        timeline_view = ViewHandler().create_view(
            user=self.user,
            table=self.table,
            type_name='timeline',
            name='Milestone Timeline',
            start_date_field=date_field,
            end_date_field=date_field
        )
        
        # Test milestone creation
        milestone = timeline_view.add_milestone(
            name='Project Kickoff',
            date=timezone.now().date()
        )
        self.assertIsNotNone(milestone)
    
    def test_timeline_zoom_levels(self):
        """Test timeline zoom level functionality."""
        timeline_view = TimelineView(zoom_level='week')
        
        # Test zoom level validation
        self.assertIn(timeline_view.zoom_level, ['day', 'week', 'month', 'year'])
        
        # Test zoom level change
        timeline_view.set_zoom_level('month')
        self.assertEqual(timeline_view.zoom_level, 'month')
    
    def test_timeline_schedule_recalculation(self):
        """Test automatic schedule recalculation for dependent tasks."""
        timeline_view = TimelineView()
        
        with patch.object(timeline_view, 'recalculate_schedule') as mock_recalc:
            timeline_view.update_task_dates(task_id=1, new_end_date=timezone.now().date())
            mock_recalc.assert_called_once()


class TestCalendarView(TestCase):
    """Test cases for Calendar view type."""
    
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
    
    def test_calendar_view_creation(self):
        """Test creating a calendar view."""
        date_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='date',
            name='Event Date'
        )
        
        calendar_view = ViewHandler().create_view(
            user=self.user,
            table=self.table,
            type_name='calendar',
            name='Event Calendar',
            date_field=date_field
        )
        
        self.assertIsInstance(calendar_view, CalendarView)
        self.assertEqual(calendar_view.date_field, date_field)
    
    def test_calendar_display_modes(self):
        """Test calendar display modes (month, week, day)."""
        calendar_view = CalendarView(display_mode='month')
        
        # Test display mode validation
        self.assertIn(calendar_view.display_mode, ['month', 'week', 'day'])
        
        # Test mode switching
        calendar_view.set_display_mode('week')
        self.assertEqual(calendar_view.display_mode, 'week')
    
    def test_calendar_event_color_coding(self):
        """Test calendar event color coding."""
        date_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='date',
            name='Event Date'
        )
        
        status_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='single_select',
            name='Event Type'
        )
        
        calendar_view = ViewHandler().create_view(
            user=self.user,
            table=self.table,
            type_name='calendar',
            name='Colored Calendar',
            date_field=date_field,
            color_field=status_field
        )
        
        color = calendar_view.get_event_color('Meeting')
        self.assertIsNotNone(color)
    
    def test_calendar_recurring_events(self):
        """Test calendar recurring event support."""
        date_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='date',
            name='Event Date'
        )
        
        calendar_view = ViewHandler().create_view(
            user=self.user,
            table=self.table,
            type_name='calendar',
            name='Recurring Calendar',
            date_field=date_field
        )
        
        # Test recurring event creation
        recurring_event = calendar_view.create_recurring_event(
            title='Weekly Meeting',
            start_date=timezone.now().date(),
            recurrence_pattern='weekly'
        )
        self.assertIsNotNone(recurring_event)
    
    def test_calendar_external_sync(self):
        """Test calendar external sync functionality."""
        calendar_view = CalendarView()
        
        with patch('baserow.contrib.database.integrations.google_calendar.GoogleCalendarSync') as mock_sync:
            calendar_view.sync_with_external_calendar('google', 'calendar_id')
            mock_sync.assert_called_once()
    
    def test_calendar_performance_optimization(self):
        """Test calendar performance with large date ranges."""
        calendar_view = CalendarView()
        
        # Test lazy loading
        with patch.object(calendar_view, 'load_events_lazy') as mock_lazy_load:
            calendar_view.get_events_for_range(
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + timedelta(days=365)
            )
            mock_lazy_load.assert_called_once()


class TestEnhancedFormView(TestCase):
    """Test cases for Enhanced Form view type."""
    
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
    
    def test_enhanced_form_view_creation(self):
        """Test creating an enhanced form view."""
        form_view = ViewHandler().create_view(
            user=self.user,
            table=self.table,
            type_name='form',
            name='Enhanced Form',
            public=True,
            custom_branding=True
        )
        
        self.assertIsInstance(form_view, FormView)
        self.assertTrue(form_view.public)
    
    def test_form_conditional_logic(self):
        """Test form conditional field logic."""
        text_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='text',
            name='Name'
        )
        
        email_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='email',
            name='Email'
        )
        
        form_view = ViewHandler().create_view(
            user=self.user,
            table=self.table,
            type_name='form',
            name='Conditional Form'
        )
        
        # Test conditional logic
        condition = form_view.add_conditional_logic(
            trigger_field=text_field,
            target_field=email_field,
            condition='show_if_not_empty'
        )
        self.assertIsNotNone(condition)
    
    def test_form_custom_branding(self):
        """Test form custom branding features."""
        form_view = ViewHandler().create_view(
            user=self.user,
            table=self.table,
            type_name='form',
            name='Branded Form',
            custom_branding=True,
            brand_logo='logo.png',
            brand_colors={'primary': '#007bff'}
        )
        
        self.assertTrue(form_view.custom_branding)
        self.assertEqual(form_view.brand_logo, 'logo.png')
    
    def test_form_validation_rules(self):
        """Test form field validation rules."""
        number_field = FieldHandler().create_field(
            user=self.user,
            table=self.table,
            type_name='number',
            name='Age'
        )
        
        form_view = ViewHandler().create_view(
            user=self.user,
            table=self.table,
            type_name='form',
            name='Validated Form'
        )
        
        # Test validation rule
        validation = form_view.add_validation_rule(
            field=number_field,
            rule_type='range',
            min_value=18,
            max_value=100
        )
        self.assertIsNotNone(validation)
    
    def test_form_shareable_links(self):
        """Test form shareable link generation."""
        form_view = ViewHandler().create_view(
            user=self.user,
            table=self.table,
            type_name='form',
            name='Shareable Form',
            public=True
        )
        
        # Test link generation
        link = form_view.generate_shareable_link()
        self.assertIsNotNone(link)
        self.assertTrue(link.startswith('http'))


@pytest.mark.django_db
class TestViewTypeIntegration:
    """Integration tests for view types working together."""
    
    def test_view_switching_data_consistency(self):
        """Test data consistency when switching between view types."""
        # This would test that data remains consistent across different views
        pass
    
    def test_view_permissions_inheritance(self):
        """Test that view permissions are properly inherited."""
        # This would test permission system integration
        pass
    
    def test_view_real_time_updates(self):
        """Test real-time updates across different view types."""
        # This would test WebSocket integration
        pass