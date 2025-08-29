from baserow.contrib.database.table.exceptions import TableDoesNotExist
from baserow.contrib.database.table.handler import TableHandler
from baserow.contrib.database.table.operations import (
    ListenToAllDatabaseTableEventsOperationType,
)
from baserow.contrib.database.views.exceptions import ViewDoesNotExist
from baserow.contrib.database.views.handler import ViewHandler
from baserow.core.exceptions import PermissionDenied, UserNotInWorkspace
from baserow.core.handler import CoreHandler
from baserow.ws.registries import PageType


class CollaborationTablePageType(PageType):
    """
    WebSocket page type for real-time collaboration on tables.
    Extends the basic table page with collaboration features.
    """

    type = "collaboration_table"
    parameters = ["table_id"]

    def can_add(self, user, web_socket_id, table_id, **kwargs):
        """
        Check if user can join collaboration for this table.
        """
        if not table_id:
            return False

        try:
            handler = TableHandler()
            table = handler.get_table(table_id)
            CoreHandler().check_permissions(
                user,
                ListenToAllDatabaseTableEventsOperationType.type,
                workspace=table.database.workspace,
                context=table,
            )
        except (UserNotInWorkspace, TableDoesNotExist, PermissionDenied):
            return False

        return True

    def get_group_name(self, table_id, **kwargs):
        return f"collaboration-table-{table_id}"

    def get_permission_channel_group_name(self, table_id, **kwargs):
        return f"permissions-table-{table_id}"


class CollaborationViewPageType(PageType):
    """
    WebSocket page type for real-time collaboration on specific views.
    """

    type = "collaboration_view"
    parameters = ["table_id", "view_id"]

    def can_add(self, user, web_socket_id, table_id, view_id, **kwargs):
        """
        Check if user can join collaboration for this view.
        """
        if not table_id or not view_id:
            return False

        try:
            table_handler = TableHandler()
            table = table_handler.get_table(table_id)
            CoreHandler().check_permissions(
                user,
                ListenToAllDatabaseTableEventsOperationType.type,
                workspace=table.database.workspace,
                context=table,
            )

            view_handler = ViewHandler()
            view = view_handler.get_view(view_id)
            if view.table_id != table_id:
                return False

        except (
            UserNotInWorkspace,
            TableDoesNotExist,
            ViewDoesNotExist,
            PermissionDenied,
        ):
            return False

        return True

    def get_group_name(self, table_id, view_id, **kwargs):
        return f"collaboration-view-{view_id}"

    def get_permission_channel_group_name(self, table_id, **kwargs):
        return f"permissions-table-{table_id}"


class CollaborationRowPageType(PageType):
    """
    WebSocket page type for real-time collaboration on specific rows.
    Used for detailed row editing and commenting.
    """

    type = "collaboration_row"
    parameters = ["table_id", "row_id"]

    def can_add(self, user, web_socket_id, table_id, row_id, **kwargs):
        """
        Check if user can join collaboration for this row.
        """
        if not table_id or not row_id:
            return False

        try:
            handler = TableHandler()
            table = handler.get_table(table_id)
            CoreHandler().check_permissions(
                user,
                ListenToAllDatabaseTableEventsOperationType.type,
                workspace=table.database.workspace,
                context=table,
            )
        except (UserNotInWorkspace, TableDoesNotExist, PermissionDenied):
            return False

        return True

    def get_group_name(self, table_id, row_id, **kwargs):
        return f"collaboration-row-{table_id}-{row_id}"

    def get_permission_channel_group_name(self, table_id, **kwargs):
        return f"permissions-table-{table_id}"