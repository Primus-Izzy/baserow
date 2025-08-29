import re
from dataclasses import dataclass
from typing import List

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from baserow.core.notifications.handler import NotificationHandler
from baserow.core.notifications.registries import (
    EmailNotificationTypeMixin,
    NotificationType,
)

User = get_user_model()


@dataclass
class CommentMentionNotificationData:
    """Data for comment mention notifications."""
    
    comment_id: int
    comment_content: str
    table_id: int
    table_name: str
    row_id: int
    database_id: int
    database_name: str
    workspace_id: int


class CommentMentionNotificationType(EmailNotificationTypeMixin, NotificationType):
    """Notification type for when a user is mentioned in a comment."""
    
    type = "comment_mention"
    has_web_frontend_route = True

    @classmethod
    def get_notification_title_for_email(cls, notification, context):
        return _(
            "%(sender)s mentioned you in a comment on row %(row_id)s in %(table_name)s."
        ) % {
            "sender": notification.sender.first_name,
            "row_id": notification.data["row_id"],
            "table_name": notification.data["table_name"],
        }

    @classmethod
    def get_notification_description_for_email(cls, notification, context):
        content = notification.data["comment_content"]
        # Truncate long comments for email
        if len(content) > 200:
            content = content[:200] + "..."
        return content

    @classmethod
    def create_comment_mention_notifications(
        cls,
        sender: User,
        comment_content: str,
        table,
        row_id: int,
        mentioned_users: List[User],
    ):
        """
        Create notifications for users mentioned in a comment.
        
        :param sender: The user who created the comment
        :param comment_content: The content of the comment
        :param table: The table where the comment was made
        :param row_id: The ID of the row being commented on
        :param mentioned_users: List of users mentioned in the comment
        """
        if not mentioned_users:
            return

        workspace = table.database.workspace
        data = CommentMentionNotificationData(
            comment_id=0,  # Will be set after comment creation
            comment_content=comment_content,
            table_id=table.id,
            table_name=table.name,
            row_id=row_id,
            database_id=table.database.id,
            database_name=table.database.name,
            workspace_id=workspace.id,
        )

        notification_handler = NotificationHandler()
        
        for user in mentioned_users:
            # Don't notify the sender about their own mention
            if user == sender:
                continue
                
            # Check if user has access to the workspace
            if not workspace.has_user(user):
                continue

            notification_handler.create_notification_for_users(
                notification_type=cls.type,
                recipients=[user],
                sender=sender,
                workspace=workspace,
                data=data.__dict__,
            )

    @classmethod
    def parse_mentions_from_content(cls, content: str, workspace) -> List[User]:
        """
        Parse @mentions from comment content and return list of valid users.
        
        :param content: The comment content to parse
        :param workspace: The workspace to validate users against
        :return: List of mentioned users
        """
        # Find all @user_id patterns in the content
        mentioned_user_ids = set(map(int, re.findall(r"@(\d+)", content)))
        
        if not mentioned_user_ids:
            return []

        # Get workspace user IDs for validation
        workspace_user_ids = set(
            workspace.users.values_list("id", flat=True)
        )
        
        # Filter to only valid workspace users
        valid_mentioned_user_ids = mentioned_user_ids & workspace_user_ids
        
        if not valid_mentioned_user_ids:
            return []

        # Return the actual user objects
        return list(
            User.objects.filter(id__in=valid_mentioned_user_ids)
        )