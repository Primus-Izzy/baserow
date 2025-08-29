import pytest
from django.urls import reverse
from rest_framework import status

from baserow.contrib.database.collaboration.models import Comment


@pytest.mark.django_db
def test_create_comment_with_mentions(api_client, data_fixture):
    """Test creating a comment with @mentions via API."""
    workspace = data_fixture.create_workspace()
    user1 = data_fixture.create_user_for_workspace(workspace)
    user2 = data_fixture.create_user_for_workspace(workspace)
    commenter = data_fixture.create_user_for_workspace(workspace)
    
    table = data_fixture.create_database_table(workspace=workspace)
    
    api_client.force_authenticate(user=commenter)
    
    url = reverse(
        "api:database:collaboration:collaboration-create-row-comment",
        kwargs={"table_id": table.id, "row_id": 1},
    )
    
    content = f"Hello @{user1.id} and @{user2.id}, please review this!"
    response = api_client.post(url, {"content": content}, format="json")
    
    assert response.status_code == status.HTTP_201_CREATED
    
    comment_data = response.json()
    assert comment_data["content"] == content
    assert len(comment_data["mentions"]) == 2
    
    # Verify mentions in database
    comment = Comment.objects.get(id=comment_data["id"])
    assert comment.mentions.count() == 2


@pytest.mark.django_db
def test_get_comments_with_pagination(api_client, data_fixture):
    """Test getting comments with pagination."""
    workspace = data_fixture.create_workspace()
    user = data_fixture.create_user_for_workspace(workspace)
    table = data_fixture.create_database_table(workspace=workspace)
    
    # Create multiple comments
    for i in range(15):
        Comment.objects.create(
            table=table,
            row_id=1,
            user=user,
            content=f"Comment {i}",
        )
    
    api_client.force_authenticate(user=user)
    
    url = reverse(
        "api:database:collaboration:collaboration-row-comments",
        kwargs={"table_id": table.id, "row_id": 1},
    )
    
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "results" in data
    assert "count" in data
    assert data["count"] == 15


@pytest.mark.django_db
def test_get_comments_with_user_filter(api_client, data_fixture):
    """Test getting comments filtered by user."""
    workspace = data_fixture.create_workspace()
    user1 = data_fixture.create_user_for_workspace(workspace)
    user2 = data_fixture.create_user_for_workspace(workspace)
    table = data_fixture.create_database_table(workspace=workspace)
    
    # Create comments from different users
    Comment.objects.create(table=table, row_id=1, user=user1, content="Comment by user1")
    Comment.objects.create(table=table, row_id=1, user=user2, content="Comment by user2")
    Comment.objects.create(table=table, row_id=1, user=user1, content="Another comment by user1")
    
    api_client.force_authenticate(user=user1)
    
    url = reverse(
        "api:database:collaboration:collaboration-row-comments",
        kwargs={"table_id": table.id, "row_id": 1},
    )
    
    # Filter by user1
    response = api_client.get(url, {"user_id": user1.id})
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["count"] == 2
    
    for comment in data["results"]:
        assert comment["user"] == user1.id


@pytest.mark.django_db
def test_get_comments_exclude_resolved(api_client, data_fixture):
    """Test getting comments excluding resolved ones."""
    workspace = data_fixture.create_workspace()
    user = data_fixture.create_user_for_workspace(workspace)
    table = data_fixture.create_database_table(workspace=workspace)
    
    # Create comments with different resolution status
    Comment.objects.create(table=table, row_id=1, user=user, content="Unresolved comment")
    Comment.objects.create(
        table=table, row_id=1, user=user, content="Resolved comment", is_resolved=True
    )
    
    api_client.force_authenticate(user=user)
    
    url = reverse(
        "api:database:collaboration:collaboration-row-comments",
        kwargs={"table_id": table.id, "row_id": 1},
    )
    
    # Exclude resolved comments
    response = api_client.get(url, {"include_resolved": "false"})
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["count"] == 1
    assert data["results"][0]["content"] == "Unresolved comment"


@pytest.mark.django_db
def test_update_comment(api_client, data_fixture):
    """Test updating a comment via API."""
    workspace = data_fixture.create_workspace()
    user = data_fixture.create_user_for_workspace(workspace)
    table = data_fixture.create_database_table(workspace=workspace)
    
    comment = Comment.objects.create(
        table=table, row_id=1, user=user, content="Original content"
    )
    
    api_client.force_authenticate(user=user)
    
    url = reverse(
        "api:database:collaboration:collaboration-update-comment",
        kwargs={"comment_id": comment.id},
    )
    
    new_content = "Updated content"
    response = api_client.patch(url, {"content": new_content}, format="json")
    
    assert response.status_code == status.HTTP_200_OK
    
    comment_data = response.json()
    assert comment_data["content"] == new_content
    
    # Verify in database
    comment.refresh_from_db()
    assert comment.content == new_content


@pytest.mark.django_db
def test_update_comment_unauthorized(api_client, data_fixture):
    """Test updating a comment by unauthorized user."""
    workspace = data_fixture.create_workspace()
    user1 = data_fixture.create_user_for_workspace(workspace)
    user2 = data_fixture.create_user_for_workspace(workspace)
    table = data_fixture.create_database_table(workspace=workspace)
    
    comment = Comment.objects.create(
        table=table, row_id=1, user=user1, content="Original content"
    )
    
    # Try to update as different user
    api_client.force_authenticate(user=user2)
    
    url = reverse(
        "api:database:collaboration:collaboration-update-comment",
        kwargs={"comment_id": comment.id},
    )
    
    response = api_client.patch(url, {"content": "Hacked content"}, format="json")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_comment(api_client, data_fixture):
    """Test deleting a comment via API."""
    workspace = data_fixture.create_workspace()
    user = data_fixture.create_user_for_workspace(workspace)
    table = data_fixture.create_database_table(workspace=workspace)
    
    comment = Comment.objects.create(
        table=table, row_id=1, user=user, content="To be deleted"
    )
    
    api_client.force_authenticate(user=user)
    
    url = reverse(
        "api:database:collaboration:collaboration-delete-comment",
        kwargs={"comment_id": comment.id},
    )
    
    response = api_client.delete(url)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify comment is deleted
    assert not Comment.objects.filter(id=comment.id).exists()


@pytest.mark.django_db
def test_toggle_comment_resolution(api_client, data_fixture):
    """Test toggling comment resolution status."""
    workspace = data_fixture.create_workspace()
    user = data_fixture.create_user_for_workspace(workspace)
    table = data_fixture.create_database_table(workspace=workspace)
    
    comment = Comment.objects.create(
        table=table, row_id=1, user=user, content="Test comment", is_resolved=False
    )
    
    api_client.force_authenticate(user=user)
    
    url = reverse(
        "api:database:collaboration:collaboration-toggle-comment-resolution",
        kwargs={"comment_id": comment.id},
    )
    
    # Resolve comment
    response = api_client.post(url)
    
    assert response.status_code == status.HTTP_200_OK
    
    comment_data = response.json()
    assert comment_data["is_resolved"] is True
    
    # Verify in database
    comment.refresh_from_db()
    assert comment.is_resolved is True
    
    # Unresolve comment
    response = api_client.post(url)
    
    assert response.status_code == status.HTTP_200_OK
    
    comment_data = response.json()
    assert comment_data["is_resolved"] is False


@pytest.mark.django_db
def test_comment_serializer_includes_mentions(api_client, data_fixture):
    """Test that comment serializer includes mention information."""
    workspace = data_fixture.create_workspace()
    user1 = data_fixture.create_user_for_workspace(workspace)
    user2 = data_fixture.create_user_for_workspace(workspace)
    commenter = data_fixture.create_user_for_workspace(workspace)
    table = data_fixture.create_database_table(workspace=workspace)
    
    comment = Comment.objects.create(
        table=table, row_id=1, user=commenter, content="Test comment"
    )
    comment.mentions.set([user1, user2])
    
    api_client.force_authenticate(user=commenter)
    
    url = reverse(
        "api:database:collaboration:collaboration-row-comments",
        kwargs={"table_id": table.id, "row_id": 1},
    )
    
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    comment_data = data["results"][0]
    
    assert "mentions" in comment_data
    assert len(comment_data["mentions"]) == 2
    
    mention_ids = {mention["id"] for mention in comment_data["mentions"]}
    assert user1.id in mention_ids
    assert user2.id in mention_ids


@pytest.mark.django_db
def test_comment_with_replies_structure(api_client, data_fixture):
    """Test that comment replies are properly nested in response."""
    workspace = data_fixture.create_workspace()
    user = data_fixture.create_user_for_workspace(workspace)
    table = data_fixture.create_database_table(workspace=workspace)
    
    # Create parent comment
    parent_comment = Comment.objects.create(
        table=table, row_id=1, user=user, content="Parent comment"
    )
    
    # Create reply
    reply_comment = Comment.objects.create(
        table=table, row_id=1, user=user, content="Reply comment", parent=parent_comment
    )
    
    api_client.force_authenticate(user=user)
    
    url = reverse(
        "api:database:collaboration:collaboration-row-comments",
        kwargs={"table_id": table.id, "row_id": 1},
    )
    
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    
    # Should only return root comments
    assert data["count"] == 1
    
    parent_data = data["results"][0]
    assert parent_data["content"] == "Parent comment"
    assert "replies" in parent_data
    assert len(parent_data["replies"]) == 1
    
    reply_data = parent_data["replies"][0]
    assert reply_data["content"] == "Reply comment"
    assert reply_data["parent"] == parent_comment.id