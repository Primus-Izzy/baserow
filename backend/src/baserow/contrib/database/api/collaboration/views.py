from django.db import transaction
from drf_spectacular.openapi import OpenApiParameter, OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from baserow.api.decorators import map_exceptions, validate_body
from baserow.api.pagination import PageNumberPagination
from baserow.api.schemas import get_error_schema
from baserow.contrib.database.api.tables.errors import ERROR_TABLE_DOES_NOT_EXIST
from baserow.contrib.database.collaboration.handler import CollaborationHandler
from baserow.contrib.database.collaboration.models import ActivityLog, Comment
from baserow.contrib.database.table.exceptions import TableDoesNotExist
from baserow.contrib.database.table.handler import TableHandler
from baserow.core.exceptions import UserNotInWorkspace

from .serializers import (
    ActivityLogSerializer,
    CollaborationStatsSerializer,
    CommentSerializer,
    CreateCommentSerializer,
    UserPresenceSerializer,
)


class CollaborationViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_table(self, table_id):
        """Get table and check permissions."""
        handler = TableHandler()
        table = handler.get_table(table_id)
        
        # Check if user has access to the table
        if not table.database.workspace.has_user(self.request.user):
            raise UserNotInWorkspace()
            
        return table

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="table_id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="The table ID to get active users for.",
            ),
            OpenApiParameter(
                name="view_id",
                location=OpenApiParameter.QUERY,
                type=OpenApiTypes.INT,
                description="Optional view ID to filter active users.",
                required=False,
            ),
        ],
        tags=["Database collaboration"],
        operation_id="get_active_users",
        description="Get list of active users in a table or view.",
        responses={
            200: UserPresenceSerializer(many=True),
            404: get_error_schema(["ERROR_TABLE_DOES_NOT_EXIST"]),
        },
    )
    @map_exceptions({TableDoesNotExist: ERROR_TABLE_DOES_NOT_EXIST})
    @action(detail=False, methods=["GET"], url_path=r"tables/(?P<table_id>\d+)/active-users")
    def active_users(self, request, table_id):
        """Get active users for a table."""
        table = self.get_table(table_id)
        view_id = request.query_params.get("view_id")
        view = None
        
        if view_id:
            from baserow.contrib.database.views.handler import ViewHandler
            view_handler = ViewHandler()
            view = view_handler.get_view(view_id)
        
        handler = CollaborationHandler()
        active_users = handler.get_active_users(table, view)
        
        serializer = UserPresenceSerializer(active_users, many=True)
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="table_id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="The table ID to get comments for.",
            ),
            OpenApiParameter(
                name="row_id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="The row ID to get comments for.",
            ),
            OpenApiParameter(
                name="include_resolved",
                location=OpenApiParameter.QUERY,
                type=OpenApiTypes.BOOL,
                description="Include resolved comments in results.",
                required=False,
            ),
            OpenApiParameter(
                name="user_id",
                location=OpenApiParameter.QUERY,
                type=OpenApiTypes.INT,
                description="Filter comments by specific user ID.",
                required=False,
            ),
        ],
        tags=["Database collaboration"],
        operation_id="get_row_comments",
        description="Get comments for a specific row with filtering and pagination.",
        responses={
            200: CommentSerializer(many=True),
            404: get_error_schema(["ERROR_TABLE_DOES_NOT_EXIST"]),
        },
    )
    @map_exceptions({TableDoesNotExist: ERROR_TABLE_DOES_NOT_EXIST})
    @action(
        detail=False,
        methods=["GET"],
        url_path=r"tables/(?P<table_id>\d+)/rows/(?P<row_id>\d+)/comments",
    )
    def row_comments(self, request, table_id, row_id):
        """Get comments for a specific row with filtering and pagination."""
        table = self.get_table(table_id)
        
        # Parse query parameters
        include_resolved = request.query_params.get("include_resolved", "true").lower() == "true"
        user_id = request.query_params.get("user_id")
        
        user_filter = None
        if user_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user_filter = User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass
        
        handler = CollaborationHandler()
        comments = handler.get_comments(
            table=table, 
            row_id=int(row_id), 
            include_resolved=include_resolved,
            user=user_filter,
        )
        
        # Filter to only root comments (replies are included in serializer)
        root_comments = [c for c in comments if c.parent is None]
        
        # Apply pagination
        page = self.paginate_queryset(root_comments)
        serializer = CommentSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="table_id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="The table ID to create comment for.",
            ),
            OpenApiParameter(
                name="row_id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="The row ID to create comment for.",
            ),
        ],
        tags=["Database collaboration"],
        operation_id="create_row_comment",
        description="Create a comment on a specific row.",
        request=CreateCommentSerializer,
        responses={
            201: CommentSerializer,
            404: get_error_schema(["ERROR_TABLE_DOES_NOT_EXIST"]),
        },
    )
    @map_exceptions({TableDoesNotExist: ERROR_TABLE_DOES_NOT_EXIST})
    @validate_body(CreateCommentSerializer)
    @action(
        detail=False,
        methods=["POST"],
        url_path=r"tables/(?P<table_id>\d+)/rows/(?P<row_id>\d+)/comments",
    )
    def create_row_comment(self, request, table_id, row_id, data):
        """Create a comment on a specific row."""
        table = self.get_table(table_id)
        
        with transaction.atomic():
            handler = CollaborationHandler()
            comment = handler.create_comment(
                user=request.user,
                table=table,
                row_id=int(row_id),
                content=data["content"],
                parent=data.get("parent"),
            )
            
            # Log the activity
            handler.log_activity(
                table=table,
                action_type="comment_created",
                user=request.user,
                details={
                    "row_id": int(row_id),
                    "comment_id": comment.id,
                    "content_preview": data["content"][:100],
                    "mentions_count": comment.mentions.count(),
                },
                ip_address=request.META.get("REMOTE_ADDR"),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )
        
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="comment_id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="The comment ID to update.",
            ),
        ],
        tags=["Database collaboration"],
        operation_id="update_comment",
        description="Update a comment.",
        request=CreateCommentSerializer,
        responses={
            200: CommentSerializer,
            404: get_error_schema(["ERROR_TABLE_DOES_NOT_EXIST"]),
        },
    )
    @map_exceptions({TableDoesNotExist: ERROR_TABLE_DOES_NOT_EXIST})
    @validate_body(CreateCommentSerializer)
    @action(
        detail=False,
        methods=["PATCH"],
        url_path=r"comments/(?P<comment_id>\d+)",
    )
    def update_comment(self, request, comment_id, data):
        """Update a comment."""
        try:
            comment = Comment.objects.select_related("table", "user").get(
                id=comment_id, user=request.user
            )
        except Comment.DoesNotExist:
            return Response(
                {"error": "Comment not found or access denied"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        table = comment.table
        
        # Check table access
        if not table.database.workspace.has_user(request.user):
            raise UserNotInWorkspace()
        
        with transaction.atomic():
            handler = CollaborationHandler()
            comment = handler.update_comment(
                comment=comment,
                content=data["content"],
            )
            
            # Log the activity
            handler.log_activity(
                table=table,
                action_type="comment_updated",
                user=request.user,
                details={
                    "row_id": comment.row_id,
                    "comment_id": comment.id,
                    "content_preview": data["content"][:100],
                },
                ip_address=request.META.get("REMOTE_ADDR"),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )
        
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="comment_id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="The comment ID to delete.",
            ),
        ],
        tags=["Database collaboration"],
        operation_id="delete_comment",
        description="Delete a comment.",
        responses={
            204: None,
            404: get_error_schema(["ERROR_TABLE_DOES_NOT_EXIST"]),
        },
    )
    @map_exceptions({TableDoesNotExist: ERROR_TABLE_DOES_NOT_EXIST})
    @action(
        detail=False,
        methods=["DELETE"],
        url_path=r"comments/(?P<comment_id>\d+)",
    )
    def delete_comment(self, request, comment_id):
        """Delete a comment."""
        try:
            comment = Comment.objects.select_related("table", "user").get(
                id=comment_id, user=request.user
            )
        except Comment.DoesNotExist:
            return Response(
                {"error": "Comment not found or access denied"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        table = comment.table
        
        # Check table access
        if not table.database.workspace.has_user(request.user):
            raise UserNotInWorkspace()
        
        with transaction.atomic():
            handler = CollaborationHandler()
            
            # Log the activity before deletion
            handler.log_activity(
                table=table,
                action_type="comment_deleted",
                user=request.user,
                details={
                    "row_id": comment.row_id,
                    "comment_id": comment.id,
                    "content_preview": comment.content[:100],
                },
                ip_address=request.META.get("REMOTE_ADDR"),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )
            
            comment.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="comment_id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="The comment ID to resolve/unresolve.",
            ),
        ],
        tags=["Database collaboration"],
        operation_id="toggle_comment_resolution",
        description="Toggle comment resolution status.",
        responses={
            200: CommentSerializer,
            404: get_error_schema(["ERROR_TABLE_DOES_NOT_EXIST"]),
        },
    )
    @map_exceptions({TableDoesNotExist: ERROR_TABLE_DOES_NOT_EXIST})
    @action(
        detail=False,
        methods=["POST"],
        url_path=r"comments/(?P<comment_id>\d+)/toggle-resolution",
    )
    def toggle_comment_resolution(self, request, comment_id):
        """Toggle comment resolution status."""
        try:
            comment = Comment.objects.select_related("table", "user").get(id=comment_id)
        except Comment.DoesNotExist:
            return Response(
                {"error": "Comment not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        table = comment.table
        
        # Check table access
        if not table.database.workspace.has_user(request.user):
            raise UserNotInWorkspace()
        
        with transaction.atomic():
            handler = CollaborationHandler()
            
            # Toggle resolution status
            comment.is_resolved = not comment.is_resolved
            comment.save()
            
            # Log the activity
            action_type = "comment_resolved" if comment.is_resolved else "comment_unresolved"
            handler.log_activity(
                table=table,
                action_type=action_type,
                user=request.user,
                details={
                    "row_id": comment.row_id,
                    "comment_id": comment.id,
                    "is_resolved": comment.is_resolved,
                },
                ip_address=request.META.get("REMOTE_ADDR"),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )
        
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="table_id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="The table ID to get activity log for.",
            ),
            OpenApiParameter(
                name="user_id",
                location=OpenApiParameter.QUERY,
                type=OpenApiTypes.INT,
                description="Filter by specific user ID.",
                required=False,
            ),
            OpenApiParameter(
                name="action_types",
                location=OpenApiParameter.QUERY,
                type=OpenApiTypes.STR,
                description="Comma-separated list of action types to filter by.",
                required=False,
            ),
        ],
        tags=["Database collaboration"],
        operation_id="get_activity_log",
        description="Get activity log for a table.",
        responses={
            200: ActivityLogSerializer(many=True),
            404: get_error_schema(["ERROR_TABLE_DOES_NOT_EXIST"]),
        },
    )
    @map_exceptions({TableDoesNotExist: ERROR_TABLE_DOES_NOT_EXIST})
    @action(
        detail=False,
        methods=["GET"],
        url_path=r"tables/(?P<table_id>\d+)/activity-log",
    )
    def activity_log(self, request, table_id):
        """Get activity log for a table."""
        table = self.get_table(table_id)
        
        user_id = request.query_params.get("user_id")
        action_types_param = request.query_params.get("action_types")
        
        user = None
        if user_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass
        
        action_types = None
        if action_types_param:
            action_types = [t.strip() for t in action_types_param.split(",")]
        
        handler = CollaborationHandler()
        activity_entries = handler.get_activity_log(
            table=table,
            user=user,
            action_types=action_types,
            limit=100,
        )
        
        page = self.paginate_queryset(activity_entries)
        serializer = ActivityLogSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="table_id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="The table ID to get collaboration stats for.",
            ),
        ],
        tags=["Database collaboration"],
        operation_id="get_collaboration_stats",
        description="Get collaboration statistics for a table.",
        responses={
            200: CollaborationStatsSerializer,
            404: get_error_schema(["ERROR_TABLE_DOES_NOT_EXIST"]),
        },
    )
    @map_exceptions({TableDoesNotExist: ERROR_TABLE_DOES_NOT_EXIST})
    @action(
        detail=False,
        methods=["GET"],
        url_path=r"tables/(?P<table_id>\d+)/collaboration-stats",
    )
    def collaboration_stats(self, request, table_id):
        """Get collaboration statistics for a table."""
        table = self.get_table(table_id)
        
        handler = CollaborationHandler()
        stats = handler.get_collaboration_stats(table)
        
        serializer = CollaborationStatsSerializer(stats)
        return Response(serializer.data)