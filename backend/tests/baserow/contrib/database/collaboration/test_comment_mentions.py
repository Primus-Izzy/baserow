import pytest
from unittest.mock import patch

from baserow.contrib.database.collaboration.handler import CollaborationHandler
from baserow.contrib.database.collaboration.models import Comment
from baserow.contrib.database.collaboration.notification_types import (
    CommentMentionNotificationType,
)


@pytest.mark.django_db
def test_parse_mentions_from_content(data_fixture):
    """Test parsing @mentions from comment content."""
    workspace = data_fixture.create_workspace()
    user1 = data_fixture.create_user_for_workspace(workspace)
    user2 = data_fixture.create_user_for_workspace(workspace)
    user3 = data_fixture.create_user()  # Not in workspace
    
    # Test content with mentions
    content = f"Hello @{user1.id} and @{user2.id}, please check this. Also @{user3.id}"
    
    mentioned_users = CommentMentionNotificationType.parse_mentions_from_content(
        content, workspace
    )
    
    # Should only include users from the workspace
    assert len(mentioned_users) == 2
    mentioned_ids = {user.id for user in mentioned_users}
    assert user1.id in mentioned_ids
    assert user2.id in mentioned_ids
    assert user3.id not in mentioned_ids


@pytest.mark.django_db
def test_parse_mentions_no_mentions(data_fixture):
    """Test parsing content with no mentions."""
    workspace = data_fixture.create_workspace()
    
    content = "This is a regular comment with no mentions"
    
    mentioned_users = CommentMentionNotificationType.parse_mentions_from_content(
        content, workspace
    )
    
    assert len(mentioned_users) == 0


@pytest.mark.django_db
def test_parse_mentions_invalid_ids(data_fixture):
    """Test parsing content with invalid user IDs."""
    workspace = data_fixture.create_workspace()
    
    content = "Hello @999999 and @invalid, this should not work"
    
    mentioned_users = CommentMentionNotificationType.parse_mentions_from_content(
        content, workspace
    )
    
    assert len(mentioned_users) == 0


@pytest.mark.django_db
@patch('baserow.core.notifications.handler.NotificationHandler.create_notification_for_users')
def test_create_comment_with_mentions(mock_create_notification, data_fixture):
    """Test creating a comment with @mentions creates notifications."""
    workspace = data_fixture.create_workspace()
    user1 = data_fixture.create_user_for_workspace(workspace)
    user2 = data_fixture.create_user_for_workspace(workspace)
    commenter = data_fixture.create_user_for_workspace(workspace)
    
    table = data_fixture.create_database_table(workspace=workspace)
    
    handler = CollaborationHandler()
    
    content = f"Hello @{user1.id} and @{user2.id}, please review this!"
    
    comment = handler.create_comment(
        user=commenter,
        table=table,
        row_id=1,
        content=content,
    )
    
    # Check that comment was created with mentions
    assert comment.mentions.count() == 2
    mentioned_ids = set(comment.mentions.values_list("id", flat=True))
    assert user1.id in mentioned_ids
    assert user2.id in mentioned_ids
    
    # Check that notifications were created (called twice, once for each user)
    assert mock_create_notification.call_count == 2


@pytest.mark.django_db
@patch('baserow.core.notifications.handler.NotificationHandler.create_notification_for_users')
def test_create_comment_self_mention_ignored(mock_create_notification, data_fixture):
    """Test that self-mentions don't create notifications."""
    workspace = data_fixture.create_workspace()
    user1 = data_fixture.create_user_for_workspace(workspace)
    commenter = data_fixture.create_user_for_workspace(workspace)
    
    table = data_fixture.create_database_table(workspace=workspace)
    
    handler = CollaborationHandler()
    
    # Commenter mentions themselves and another user
    content = f"Hello @{user1.id} and @{commenter.id}, please review this!"
    
    comment = handler.create_comment(
        user=commenter,
        table=table,
        row_id=1,
        content=content,
    )
    
    # Check that comment was created with both mentions
    assert comment.mentions.count() == 2
    
    # Check that only one notification was created (not for self-mention)
    assert mock_create_notification.call_count == 1


@pytest.mark.django_db
@patch('baserow.core.notifications.handler.NotificationHandler.create_notification_for_users')
def test_update_comment_new_mentions(mock_create_notification, data_fixture):
    """Test updating a comment with new mentions."""
    workspace = data_fixture.create_workspace()
    user1 = data_fixture.create_user_for_workspace(workspace)
    user2 = data_fixture.create_user_for_workspace(workspace)
    user3 = data_fixture.create_user_for_workspace(workspace)
    commenter = data_fixture.create_user_for_workspace(workspace)
    
    table = data_fixture.create_database_table(workspace=workspace)
    
    handler = CollaborationHandler()
    
    # Create comment with initial mention
    initial_content = f"Hello @{user1.id}, please review this!"
    comment = handler.create_comment(
        user=commenter,
        table=table,
        row_id=1,
        content=initial_content,
    )
    
    # Reset mock call count
    mock_create_notification.reset_mock()
    
    # Update comment with additional mentions
    updated_content = f"Hello @{user1.id}, @{user2.id}, and @{user3.id}, please review this!"
    updated_comment = handler.update_comment(
        comment=comment,
        content=updated_content,
    )
    
    # Check that all mentions are now present
    assert updated_comment.mentions.count() == 3
    
    # Check that notifications were only sent to newly mentioned users (user2 and user3)
    assert mock_create_notification.call_count == 2


@pytest.mark.django_db
def test_update_comment_remove_mentions(data_fixture):
    """Test updating a comment to remove mentions."""
    workspace = data_fixture.create_workspace()
    user1 = data_fixture.create_user_for_workspace(workspace)
    user2 = data_fixture.create_user_for_workspace(workspace)
    commenter = data_fixture.create_user_for_workspace(workspace)
    
    table = data_fixture.create_database_table(workspace=workspace)
    
    handler = CollaborationHandler()
    
    # Create comment with mentions
    initial_content = f"Hello @{user1.id} and @{user2.id}, please review this!"
    comment = handler.create_comment(
        user=commenter,
        table=table,
        row_id=1,
        content=initial_content,
    )
    
    assert comment.mentions.count() == 2
    
    # Update comment to remove mentions
    updated_content = "Hello everyone, please review this!"
    updated_comment = handler.update_comment(
        comment=comment,
        content=updated_content,
    )
    
    # Check that mentions were removed
    assert updated_comment.mentions.count() == 0


@pytest.mark.django_db
def test_comment_mention_notification_data():
    """Test comment mention notification data structure."""
    data = CommentMentionNotificationType.get_notification_title_for_email(
        type("MockNotification", (), {
            "sender": type("MockUser", (), {"first_name": "John"})(),
            "data": {
                "row_id": 123,
                "table_name": "Test Table",
            }
        })(),
        {}
    )
    
    assert "John mentioned you in a comment" in data
    assert "row 123" in data
    assert "Test Table" in data


@pytest.mark.django_db
def test_comment_mention_notification_description():
    """Test comment mention notification description."""
    # Test short content
    short_content = "This is a short comment"
    description = CommentMentionNotificationType.get_notification_description_for_email(
        type("MockNotification", (), {
            "data": {"comment_content": short_content}
        })(),
        {}
    )
    
    assert description == short_content
    
    # Test long content (should be truncated)
    long_content = "This is a very long comment " * 20  # > 200 chars
    description = CommentMentionNotificationType.get_notification_description_for_email(
        type("MockNotification", (), {
            "data": {"comment_content": long_content}
        })(),
        {}
    )
    
    assert len(description) <= 203  # 200 + "..."
    assert description.endswith("...")