from datetime import datetime, timedelta
from typing import Dict, List, Optional

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from baserow.contrib.database.collaboration.models import (
    ActivityLog,
    CollaborationSession,
    Comment,
    UserPresence,
)
from baserow.contrib.database.table.models import Table
from baserow.contrib.database.views.models import View

User = get_user_model()


class CollaborationHandler:
    """
    Handler for managing real-time collaboration features.
    """

    def update_user_presence(
        self,
        user: User,
        table: Table,
        web_socket_id: str,
        view: Optional[View] = None,
        cursor_position: Optional[Dict] = None,
        is_typing: bool = False,
        typing_field_id: Optional[int] = None,
        typing_row_id: Optional[int] = None,
    ) -> UserPresence:
        """
        Update or create user presence information.
        """
        defaults = {
            "last_seen": timezone.now(),
            "cursor_position": cursor_position or {},
            "is_typing": is_typing,
            "typing_field_id": typing_field_id,
            "typing_row_id": typing_row_id,
        }

        presence, created = UserPresence.objects.update_or_create(
            user=user,
            table=table,
            view=view,
            web_socket_id=web_socket_id,
            defaults=defaults,
        )

        return presence

    def remove_user_presence(
        self, user: User, table: Table, web_socket_id: str, view: Optional[View] = None
    ):
        """
        Remove user presence when they disconnect.
        """
        UserPresence.objects.filter(
            user=user, table=table, view=view, web_socket_id=web_socket_id
        ).delete()

    def get_active_users(
        self, table: Table, view: Optional[View] = None, minutes: int = 5
    ) -> List[UserPresence]:
        """
        Get list of active users in a table/view within the specified time window.
        """
        cutoff_time = timezone.now() - timedelta(minutes=minutes)
        return list(
            UserPresence.objects.filter(
                table=table, view=view, last_seen__gte=cutoff_time
            ).select_related("user")
        )

    def cleanup_stale_presence(self, minutes: int = 10):
        """
        Clean up stale presence records.
        """
        cutoff_time = timezone.now() - timedelta(minutes=minutes)
        UserPresence.objects.filter(last_seen__lt=cutoff_time).delete()

    def acquire_edit_lock(
        self,
        user: User,
        table: Table,
        row_id: int,
        field_id: int,
        web_socket_id: str,
        lock_data: Optional[Dict] = None,
    ) -> Optional[CollaborationSession]:
        """
        Attempt to acquire an edit lock for conflict resolution.
        Returns the session if successful, None if already locked by another user.
        """
        try:
            with transaction.atomic():
                # Check if there's an existing lock
                existing_session = CollaborationSession.objects.filter(
                    table=table, row_id=row_id, field_id=field_id
                ).first()

                if existing_session:
                    # Check if the lock is stale (older than 30 seconds)
                    if existing_session.last_activity < timezone.now() - timedelta(
                        seconds=30
                    ):
                        existing_session.delete()
                    elif existing_session.user != user:
                        # Lock is held by another user
                        return None
                    else:
                        # Update existing session
                        existing_session.last_activity = timezone.now()
                        existing_session.lock_data = lock_data or {}
                        existing_session.save()
                        return existing_session

                # Create new session
                session = CollaborationSession.objects.create(
                    table=table,
                    row_id=row_id,
                    field_id=field_id,
                    user=user,
                    web_socket_id=web_socket_id,
                    lock_data=lock_data or {},
                )
                return session

        except Exception:
            return None

    def release_edit_lock(
        self, user: User, table: Table, row_id: int, field_id: int
    ):
        """
        Release an edit lock.
        """
        CollaborationSession.objects.filter(
            table=table, row_id=row_id, field_id=field_id, user=user
        ).delete()

    def get_active_edit_sessions(self, table: Table) -> List[CollaborationSession]:
        """
        Get all active edit sessions for a table.
        """
        cutoff_time = timezone.now() - timedelta(seconds=30)
        return list(
            CollaborationSession.objects.filter(
                table=table, last_activity__gte=cutoff_time
            ).select_related("user")
        )

    def cleanup_stale_sessions(self, seconds: int = 60):
        """
        Clean up stale collaboration sessions.
        """
        cutoff_time = timezone.now() - timedelta(seconds=seconds)
        CollaborationSession.objects.filter(last_activity__lt=cutoff_time).delete()

    def create_comment(
        self,
        user: User,
        table: Table,
        row_id: int,
        content: str,
        parent: Optional[Comment] = None,
        mentions: Optional[List[User]] = None,
    ) -> Comment:
        """
        Create a new comment on a row with @mention support.
        """
        from baserow.contrib.database.collaboration.notification_types import (
            CommentMentionNotificationType,
        )
        
        comment = Comment.objects.create(
            table=table, row_id=row_id, user=user, content=content, parent=parent
        )

        # Parse mentions from content if not explicitly provided
        if mentions is None:
            workspace = table.database.workspace
            mentions = CommentMentionNotificationType.parse_mentions_from_content(
                content, workspace
            )

        if mentions:
            comment.mentions.set(mentions)
            
            # Create notifications for mentioned users
            CommentMentionNotificationType.create_comment_mention_notifications(
                sender=user,
                comment_content=content,
                table=table,
                row_id=row_id,
                mentioned_users=mentions,
            )

        return comment

    def update_comment(
        self,
        comment: Comment,
        content: str,
    ) -> Comment:
        """
        Update an existing comment with new content and handle mentions.
        """
        from baserow.contrib.database.collaboration.notification_types import (
            CommentMentionNotificationType,
        )
        
        # Parse new mentions from updated content
        workspace = comment.table.database.workspace
        new_mentions = CommentMentionNotificationType.parse_mentions_from_content(
            content, workspace
        )
        
        # Get existing mentions
        existing_mentions = set(comment.mentions.all())
        new_mentions_set = set(new_mentions)
        
        # Find newly mentioned users (not previously mentioned)
        newly_mentioned = new_mentions_set - existing_mentions
        
        # Update comment content
        comment.content = content
        comment.save()
        
        # Update mentions
        comment.mentions.set(new_mentions)
        
        # Send notifications only to newly mentioned users
        if newly_mentioned:
            CommentMentionNotificationType.create_comment_mention_notifications(
                sender=comment.user,
                comment_content=content,
                table=comment.table,
                row_id=comment.row_id,
                mentioned_users=list(newly_mentioned),
            )
        
        return comment

    def get_comments(
        self, 
        table: Table, 
        row_id: int, 
        include_resolved: bool = True,
        user: Optional[User] = None,
    ) -> List[Comment]:
        """
        Get comments for a specific row with optional filtering.
        """
        queryset = Comment.objects.filter(table=table, row_id=row_id).select_related(
            "user", "parent"
        ).prefetch_related("mentions")

        if not include_resolved:
            queryset = queryset.filter(is_resolved=False)
            
        if user:
            queryset = queryset.filter(user=user)

        return list(queryset)

    def log_activity(
        self,
        table: Table,
        action_type: str,
        user: Optional[User] = None,
        details: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ActivityLog:
        """
        Log an activity for audit trail.
        """
        return ActivityLog.objects.create(
            user=user,
            table=table,
            action_type=action_type,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
        )

    def get_activity_log(
        self,
        table: Table,
        user: Optional[User] = None,
        action_types: Optional[List[str]] = None,
        limit: int = 100,
    ) -> List[ActivityLog]:
        """
        Get activity log entries for a table.
        """
        queryset = ActivityLog.objects.filter(table=table).select_related("user")

        if user:
            queryset = queryset.filter(user=user)

        if action_types:
            queryset = queryset.filter(action_type__in=action_types)

        return list(queryset[:limit])

    def cleanup_stale_data(self, presence_minutes: int = 10, session_seconds: int = 60):
        """
        Clean up stale presence and session data.
        This should be called periodically by a background task.
        """
        self.cleanup_stale_presence(presence_minutes)
        self.cleanup_stale_sessions(session_seconds)

    def get_collaboration_stats(self, table: Table) -> Dict:
        """
        Get collaboration statistics for a table.
        """
        active_users_count = len(self.get_active_users(table))
        active_sessions_count = len(self.get_active_edit_sessions(table))
        recent_comments_count = Comment.objects.filter(
            table=table,
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        return {
            "active_users": active_users_count,
            "active_sessions": active_sessions_count,
            "recent_comments": recent_comments_count,
        }