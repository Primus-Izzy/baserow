import pytest
from django.test import TestCase

from baserow.contrib.database.collaboration.handler import CollaborationHandler
from baserow.contrib.database.collaboration.models import UserPresence


class TestCollaborationIntegration(TestCase):
    """Simple integration test for collaboration features."""
    
    def setUp(self):
        from django.contrib.auth import get_user_model
        from baserow.contrib.database.table.models import Database, Table
        from baserow.core.models import Workspace
        
        User = get_user_model()
        
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password",
            first_name="Test User"
        )
        
        self.workspace = Workspace.objects.create(name="Test Workspace")
        self.workspace.users.add(self.user)
        
        self.database = Database.objects.create(
            workspace=self.workspace,
            name="Test Database"
        )
        
        self.table = Table.objects.create(
            database=self.database,
            name="Test Table",
            order=1
        )
        
        self.handler = CollaborationHandler()
    
    def test_basic_collaboration_flow(self):
        """Test basic collaboration functionality."""
        
        # Test user presence
        presence = self.handler.update_user_presence(
            user=self.user,
            table=self.table,
            web_socket_id="test-socket",
            cursor_position={"x": 100, "y": 200}
        )
        
        self.assertEqual(presence.user, self.user)
        self.assertEqual(presence.table, self.table)
        self.assertEqual(presence.cursor_position, {"x": 100, "y": 200})
        
        # Test getting active users
        active_users = self.handler.get_active_users(self.table)
        self.assertEqual(len(active_users), 1)
        self.assertEqual(active_users[0].user, self.user)
        
        # Test edit lock
        session = self.handler.acquire_edit_lock(
            user=self.user,
            table=self.table,
            row_id=1,
            field_id=1,
            web_socket_id="test-socket"
        )
        
        self.assertIsNotNone(session)
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.table, self.table)
        
        # Test comment creation
        comment = self.handler.create_comment(
            user=self.user,
            table=self.table,
            row_id=1,
            content="Test comment"
        )
        
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.table, self.table)
        self.assertEqual(comment.content, "Test comment")
        
        # Test activity logging
        activity = self.handler.log_activity(
            table=self.table,
            action_type="row_created",
            user=self.user,
            details={"test": "data"}
        )
        
        self.assertEqual(activity.user, self.user)
        self.assertEqual(activity.table, self.table)
        self.assertEqual(activity.action_type, "row_created")
        
        print("✓ All collaboration features working correctly")
    
    def test_collaboration_stats(self):
        """Test collaboration statistics."""
        
        # Create some test data
        self.handler.update_user_presence(
            user=self.user,
            table=self.table,
            web_socket_id="test-socket"
        )
        
        self.handler.acquire_edit_lock(
            user=self.user,
            table=self.table,
            row_id=1,
            field_id=1,
            web_socket_id="test-socket"
        )
        
        self.handler.create_comment(
            user=self.user,
            table=self.table,
            row_id=1,
            content="Test comment"
        )
        
        # Get stats
        stats = self.handler.get_collaboration_stats(self.table)
        
        self.assertEqual(stats["active_users"], 1)
        self.assertEqual(stats["active_sessions"], 1)
        self.assertEqual(stats["recent_comments"], 1)
        
        print("✓ Collaboration statistics working correctly")