from django.contrib.auth import get_user_model
from django.db import models

from baserow.contrib.database.table.models import Table
from baserow.contrib.database.views.models import View

User = get_user_model()


class UserPresence(models.Model):
    """
    Tracks user presence in specific table/view contexts for real-time collaboration.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    view = models.ForeignKey(View, on_delete=models.CASCADE, null=True, blank=True)
    web_socket_id = models.CharField(max_length=255)
    last_seen = models.DateTimeField(auto_now=True)
    cursor_position = models.JSONField(default=dict, blank=True)
    is_typing = models.BooleanField(default=False)
    typing_field_id = models.PositiveIntegerField(null=True, blank=True)
    typing_row_id = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ["user", "table", "view", "web_socket_id"]
        indexes = [
            models.Index(fields=["table", "view"]),
            models.Index(fields=["last_seen"]),
        ]

    def __str__(self):
        return f"{self.user.email} in table {self.table.id}"


class CollaborationSession(models.Model):
    """
    Represents an active collaboration session for conflict resolution.
    """

    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    row_id = models.PositiveIntegerField()
    field_id = models.PositiveIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    web_socket_id = models.CharField(max_length=255)
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    lock_data = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ["table", "row_id", "field_id"]
        indexes = [
            models.Index(fields=["table", "row_id"]),
            models.Index(fields=["last_activity"]),
        ]

    def __str__(self):
        return f"Session for row {self.row_id}, field {self.field_id} by {self.user.email}"


class Comment(models.Model):
    """
    Comments on table rows for collaboration.
    """

    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    row_id = models.PositiveIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_resolved = models.BooleanField(default=False)
    mentions = models.ManyToManyField(User, related_name="mentioned_in_comments", blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["table", "row_id"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["parent"]),
        ]
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.user.email} on row {self.row_id}"


class ActivityLog(models.Model):
    """
    Comprehensive activity logging for collaboration tracking.
    """

    ACTION_TYPES = [
        ("row_created", "Row Created"),
        ("row_updated", "Row Updated"),
        ("row_deleted", "Row Deleted"),
        ("field_created", "Field Created"),
        ("field_updated", "Field Updated"),
        ("field_deleted", "Field Deleted"),
        ("view_created", "View Created"),
        ("view_updated", "View Updated"),
        ("view_deleted", "View Deleted"),
        ("comment_created", "Comment Created"),
        ("comment_updated", "Comment Updated"),
        ("comment_deleted", "Comment Deleted"),
        ("comment_resolved", "Comment Resolved"),
        ("comment_unresolved", "Comment Unresolved"),
        ("user_joined", "User Joined"),
        ("user_left", "User Left"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    details = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["table", "timestamp"]),
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["action_type", "timestamp"]),
        ]
        ordering = ["-timestamp"]

    def __str__(self):
        user_str = self.user.email if self.user else "System"
        return f"{user_str} - {self.get_action_type_display()} at {self.timestamp}"