import pytest
from datetime import timedelta
from django.utils import timezone

from baserow.contrib.database.collaboration.handler import CollaborationHandler
from baserow.contrib.database.collaboration.models import (
    ActivityLog,
    CollaborationSession,
    Comment,
    UserPresence,
)


@pytest.mark.django_db
def test_update_user_presence(data_fixture):
    """Test updating user presence information."""
    user = data_fixture.create_user()
    table = data_fixture.create_database_table()
    view = data_fixture.create_grid_view(table=table)
    
    handler = CollaborationHandler()
    
    # Create initial presence
    presence = handler.update_user_presence(
        user=user,
        table=table,
        web_socket_id="test-socket-1",
        view=view,
        cursor_position={"x": 100, "y": 200},
        is_typing=True,
        typing_field_id=1,
        typing_row_id=1,
    )
    
    assert presence.user == user
    assert presence.table == table
    assert presence.view == view
    assert presence.cursor_position == {"x": 100, "y": 200}
    assert presence.is_typing is True
    assert presence.typing_field_id == 1
    assert presence.typing_row_id == 1
    
    # Update existing presence
    updated_presence = handler.update_user_presence(
        user=user,
        table=table,
        web_socket_id="test-socket-1",
        view=view,
        cursor_position={"x": 150, "y": 250},
        is_typing=False,
    )
    
    assert updated_presence.id == presence.id
    assert updated_presence.cursor_position == {"x": 150, "y": 250}
    assert updated_presence.is_typing is False
    assert updated_presence.typing_field_id is None
    assert updated_presence.typing_row_id is None


@pytest.mark.django_db
def test_get_active_users(data_fixture):
    """Test getting active users for a table."""
    user1 = data_fixture.create_user()
    user2 = data_fixture.create_user()
    table = data_fixture.create_database_table()
    
    handler = CollaborationHandler()
    
    # Create presence for both users
    handler.update_user_presence(user1, table, "socket-1")
    handler.update_user_presence(user2, table, "socket-2")
    
    active_users = handler.get_active_users(table)
    assert len(active_users) == 2
    
    # Create stale presence (older than 5 minutes)
    stale_time = timezone.now() - timedelta(minutes=10)
    UserPresence.objects.filter(user=user2).update(last_seen=stale_time)
    
    active_users = handler.get_active_users(table, minutes=5)
    assert len(active_users) == 1
    assert active_users[0].user == user1


@pytest.mark.django_db
def test_acquire_edit_lock(data_fixture):
    """Test acquiring edit locks for conflict resolution."""
    user1 = data_fixture.create_user()
    user2 = data_fixture.create_user()
    table = data_fixture.create_database_table()
    
    handler = CollaborationHandler()
    
    # User1 acquires lock
    session1 = handler.acquire_edit_lock(
        user=user1,
        table=table,
        row_id=1,
        field_id=1,
        web_socket_id="socket-1",
        lock_data={"test": "data"},
    )
    
    assert session1 is not None
    assert session1.user == user1
    assert session1.table == table
    assert session1.row_id == 1
    assert session1.field_id == 1
    assert session1.lock_data == {"test": "data"}
    
    # User2 tries to acquire same lock - should fail
    session2 = handler.acquire_edit_lock(
        user=user2,
        table=table,
        row_id=1,
        field_id=1,
        web_socket_id="socket-2",
    )
    
    assert session2 is None
    
    # User1 can update their own lock
    updated_session = handler.acquire_edit_lock(
        user=user1,
        table=table,
        row_id=1,
        field_id=1,
        web_socket_id="socket-1",
        lock_data={"updated": "data"},
    )
    
    assert updated_session.id == session1.id
    assert updated_session.lock_data == {"updated": "data"}


@pytest.mark.django_db
def test_release_edit_lock(data_fixture):
    """Test releasing edit locks."""
    user = data_fixture.create_user()
    table = data_fixture.create_database_table()
    
    handler = CollaborationHandler()
    
    # Acquire lock
    session = handler.acquire_edit_lock(
        user=user,
        table=table,
        row_id=1,
        field_id=1,
        web_socket_id="socket-1",
    )
    
    assert session is not None
    
    # Release lock
    handler.release_edit_lock(user, table, 1, 1)
    
    # Verify lock is released
    assert not CollaborationSession.objects.filter(
        table=table, row_id=1, field_id=1
    ).exists()


@pytest.mark.django_db
def test_create_comment(data_fixture):
    """Test creating comments."""
    user = data_fixture.create_user()
    table = data_fixture.create_database_table()
    
    handler = CollaborationHandler()
    
    # Create root comment
    comment = handler.create_comment(
        user=user,
        table=table,
        row_id=1,
        content="This is a test comment",
    )
    
    assert comment.user == user
    assert comment.table == table
    assert comment.row_id == 1
    assert comment.content == "This is a test comment"
    assert comment.parent is None
    
    # Create reply
    reply = handler.create_comment(
        user=user,
        table=table,
        row_id=1,
        content="This is a reply",
        parent=comment,
    )
    
    assert reply.parent == comment
    assert reply.content == "This is a reply"


@pytest.mark.django_db
def test_get_comments(data_fixture):
    """Test getting comments for a row."""
    user = data_fixture.create_user()
    table = data_fixture.create_database_table()
    
    handler = CollaborationHandler()
    
    # Create comments
    comment1 = handler.create_comment(user, table, 1, "Comment 1")
    comment2 = handler.create_comment(user, table, 1, "Comment 2")
    reply = handler.create_comment(user, table, 1, "Reply", parent=comment1)
    
    # Create comment for different row
    handler.create_comment(user, table, 2, "Different row comment")
    
    comments = handler.get_comments(table, 1)
    assert len(comments) == 3  # 2 root comments + 1 reply
    
    comment_contents = [c.content for c in comments]
    assert "Comment 1" in comment_contents
    assert "Comment 2" in comment_contents
    assert "Reply" in comment_contents
    assert "Different row comment" not in comment_contents


@pytest.mark.django_db
def test_log_activity(data_fixture):
    """Test logging activity."""
    user = data_fixture.create_user()
    table = data_fixture.create_database_table()
    
    handler = CollaborationHandler()
    
    activity = handler.log_activity(
        table=table,
        action_type="row_created",
        user=user,
        details={"row_id": 1, "field_count": 5},
        ip_address="127.0.0.1",
        user_agent="Test Agent",
    )
    
    assert activity.user == user
    assert activity.table == table
    assert activity.action_type == "row_created"
    assert activity.details == {"row_id": 1, "field_count": 5}
    assert activity.ip_address == "127.0.0.1"
    assert activity.user_agent == "Test Agent"


@pytest.mark.django_db
def test_cleanup_stale_presence(data_fixture):
    """Test cleaning up stale presence records."""
    user = data_fixture.create_user()
    table = data_fixture.create_database_table()
    
    handler = CollaborationHandler()
    
    # Create fresh presence
    handler.update_user_presence(user, table, "socket-1")
    
    # Create stale presence
    stale_time = timezone.now() - timedelta(minutes=15)
    UserPresence.objects.create(
        user=user,
        table=table,
        web_socket_id="socket-2",
        last_seen=stale_time,
    )
    
    assert UserPresence.objects.count() == 2
    
    # Cleanup stale presence (older than 10 minutes)
    handler.cleanup_stale_presence(minutes=10)
    
    assert UserPresence.objects.count() == 1
    remaining = UserPresence.objects.first()
    assert remaining.web_socket_id == "socket-1"


@pytest.mark.django_db
def test_cleanup_stale_sessions(data_fixture):
    """Test cleaning up stale collaboration sessions."""
    user = data_fixture.create_user()
    table = data_fixture.create_database_table()
    
    handler = CollaborationHandler()
    
    # Create fresh session
    handler.acquire_edit_lock(user, table, 1, 1, "socket-1")
    
    # Create stale session
    stale_time = timezone.now() - timedelta(minutes=2)
    CollaborationSession.objects.create(
        table=table,
        row_id=2,
        field_id=1,
        user=user,
        web_socket_id="socket-2",
        last_activity=stale_time,
    )
    
    assert CollaborationSession.objects.count() == 2
    
    # Cleanup stale sessions (older than 60 seconds)
    handler.cleanup_stale_sessions(seconds=60)
    
    assert CollaborationSession.objects.count() == 1
    remaining = CollaborationSession.objects.first()
    assert remaining.row_id == 1


@pytest.mark.django_db
def test_get_collaboration_stats(data_fixture):
    """Test getting collaboration statistics."""
    user1 = data_fixture.create_user()
    user2 = data_fixture.create_user()
    table = data_fixture.create_database_table()
    
    handler = CollaborationHandler()
    
    # Create active users
    handler.update_user_presence(user1, table, "socket-1")
    handler.update_user_presence(user2, table, "socket-2")
    
    # Create active session
    handler.acquire_edit_lock(user1, table, 1, 1, "socket-1")
    
    # Create recent comment
    handler.create_comment(user1, table, 1, "Recent comment")
    
    stats = handler.get_collaboration_stats(table)
    
    assert stats["active_users"] == 2
    assert stats["active_sessions"] == 1
    assert stats["recent_comments"] == 1