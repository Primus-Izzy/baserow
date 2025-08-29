import json
from typing import Dict, Optional

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from baserow.contrib.database.collaboration.handler import CollaborationHandler
from baserow.contrib.database.table.handler import TableHandler
from baserow.contrib.database.views.handler import ViewHandler
from baserow.ws.registries import page_registry


class CollaborationConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for handling real-time collaboration features.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collaboration_handler = CollaborationHandler()

    async def connect(self):
        await self.accept()
        user = self.scope["user"]
        web_socket_id = self.scope["web_socket_id"]

        if not user:
            await self.close()
            return

        await self.send_json(
            {
                "type": "collaboration_connected",
                "web_socket_id": web_socket_id,
                "user_id": user.id,
            }
        )

    async def disconnect(self, close_code):
        """
        Handle disconnection by cleaning up user presence.
        """
        user = self.scope.get("user")
        web_socket_id = self.scope.get("web_socket_id")

        if user and web_socket_id:
            await database_sync_to_async(self._cleanup_user_presence)(
                user, web_socket_id
            )

    def _cleanup_user_presence(self, user, web_socket_id):
        """
        Clean up user presence records for this connection.
        """
        from baserow.contrib.database.collaboration.models import UserPresence

        UserPresence.objects.filter(user=user, web_socket_id=web_socket_id).delete()

    async def receive_json(self, content):
        """
        Handle incoming collaboration messages.
        """
        message_type = content.get("type")
        user = self.scope["user"]
        web_socket_id = self.scope["web_socket_id"]

        if not user:
            return

        handlers = {
            "update_presence": self._handle_update_presence,
            "start_typing": self._handle_start_typing,
            "stop_typing": self._handle_stop_typing,
            "cursor_move": self._handle_cursor_move,
            "acquire_lock": self._handle_acquire_lock,
            "release_lock": self._handle_release_lock,
            "create_comment": self._handle_create_comment,
            "get_active_users": self._handle_get_active_users,
        }

        handler = handlers.get(message_type)
        if handler:
            await handler(content, user, web_socket_id)

    async def _handle_update_presence(self, content, user, web_socket_id):
        """
        Update user presence information.
        """
        table_id = content.get("table_id")
        view_id = content.get("view_id")

        if not table_id:
            return

        try:
            table = await database_sync_to_async(TableHandler().get_table)(table_id)
            view = None
            if view_id:
                view = await database_sync_to_async(ViewHandler().get_view)(view_id)

            presence = await database_sync_to_async(
                self.collaboration_handler.update_user_presence
            )(
                user=user,
                table=table,
                web_socket_id=web_socket_id,
                view=view,
                cursor_position=content.get("cursor_position", {}),
            )

            # Broadcast presence update to other users
            await self._broadcast_presence_update(table_id, view_id, presence)

        except Exception as e:
            await self.send_json({"type": "error", "message": str(e)})

    async def _handle_start_typing(self, content, user, web_socket_id):
        """
        Handle user starting to type.
        """
        table_id = content.get("table_id")
        field_id = content.get("field_id")
        row_id = content.get("row_id")

        if not all([table_id, field_id, row_id]):
            return

        try:
            table = await database_sync_to_async(TableHandler().get_table)(table_id)

            await database_sync_to_async(
                self.collaboration_handler.update_user_presence
            )(
                user=user,
                table=table,
                web_socket_id=web_socket_id,
                is_typing=True,
                typing_field_id=field_id,
                typing_row_id=row_id,
            )

            # Broadcast typing indicator
            await self._broadcast_typing_indicator(
                table_id, user.id, field_id, row_id, True
            )

        except Exception as e:
            await self.send_json({"type": "error", "message": str(e)})

    async def _handle_stop_typing(self, content, user, web_socket_id):
        """
        Handle user stopping typing.
        """
        table_id = content.get("table_id")

        if not table_id:
            return

        try:
            table = await database_sync_to_async(TableHandler().get_table)(table_id)

            await database_sync_to_async(
                self.collaboration_handler.update_user_presence
            )(
                user=user,
                table=table,
                web_socket_id=web_socket_id,
                is_typing=False,
                typing_field_id=None,
                typing_row_id=None,
            )

            # Broadcast typing stopped
            await self._broadcast_typing_indicator(table_id, user.id, None, None, False)

        except Exception as e:
            await self.send_json({"type": "error", "message": str(e)})

    async def _handle_cursor_move(self, content, user, web_socket_id):
        """
        Handle cursor movement for live cursor tracking.
        """
        table_id = content.get("table_id")
        cursor_position = content.get("cursor_position", {})

        if not table_id:
            return

        try:
            table = await database_sync_to_async(TableHandler().get_table)(table_id)

            await database_sync_to_async(
                self.collaboration_handler.update_user_presence
            )(
                user=user,
                table=table,
                web_socket_id=web_socket_id,
                cursor_position=cursor_position,
            )

            # Broadcast cursor position
            await self._broadcast_cursor_update(table_id, user.id, cursor_position)

        except Exception as e:
            await self.send_json({"type": "error", "message": str(e)})

    async def _handle_acquire_lock(self, content, user, web_socket_id):
        """
        Handle edit lock acquisition for conflict resolution.
        """
        table_id = content.get("table_id")
        row_id = content.get("row_id")
        field_id = content.get("field_id")

        if not all([table_id, row_id, field_id]):
            return

        try:
            table = await database_sync_to_async(TableHandler().get_table)(table_id)

            session = await database_sync_to_async(
                self.collaboration_handler.acquire_edit_lock
            )(
                user=user,
                table=table,
                row_id=row_id,
                field_id=field_id,
                web_socket_id=web_socket_id,
                lock_data=content.get("lock_data", {}),
            )

            if session:
                await self.send_json(
                    {
                        "type": "lock_acquired",
                        "table_id": table_id,
                        "row_id": row_id,
                        "field_id": field_id,
                        "session_id": session.id,
                    }
                )

                # Broadcast lock status to other users
                await self._broadcast_lock_status(
                    table_id, row_id, field_id, user.id, "acquired"
                )
            else:
                await self.send_json(
                    {
                        "type": "lock_failed",
                        "table_id": table_id,
                        "row_id": row_id,
                        "field_id": field_id,
                        "reason": "already_locked",
                    }
                )

        except Exception as e:
            await self.send_json({"type": "error", "message": str(e)})

    async def _handle_release_lock(self, content, user, web_socket_id):
        """
        Handle edit lock release.
        """
        table_id = content.get("table_id")
        row_id = content.get("row_id")
        field_id = content.get("field_id")

        if not all([table_id, row_id, field_id]):
            return

        try:
            table = await database_sync_to_async(TableHandler().get_table)(table_id)

            await database_sync_to_async(self.collaboration_handler.release_edit_lock)(
                user=user, table=table, row_id=row_id, field_id=field_id
            )

            await self.send_json(
                {
                    "type": "lock_released",
                    "table_id": table_id,
                    "row_id": row_id,
                    "field_id": field_id,
                }
            )

            # Broadcast lock release to other users
            await self._broadcast_lock_status(
                table_id, row_id, field_id, user.id, "released"
            )

        except Exception as e:
            await self.send_json({"type": "error", "message": str(e)})

    async def _handle_create_comment(self, content, user, web_socket_id):
        """
        Handle comment creation.
        """
        table_id = content.get("table_id")
        row_id = content.get("row_id")
        comment_content = content.get("content")

        if not all([table_id, row_id, comment_content]):
            return

        try:
            table = await database_sync_to_async(TableHandler().get_table)(table_id)

            comment = await database_sync_to_async(
                self.collaboration_handler.create_comment
            )(user=user, table=table, row_id=row_id, content=comment_content)

            # Broadcast new comment to other users
            await self._broadcast_comment_created(table_id, row_id, comment)

        except Exception as e:
            await self.send_json({"type": "error", "message": str(e)})

    async def _handle_get_active_users(self, content, user, web_socket_id):
        """
        Get list of active users in the table/view.
        """
        table_id = content.get("table_id")
        view_id = content.get("view_id")

        if not table_id:
            return

        try:
            table = await database_sync_to_async(TableHandler().get_table)(table_id)
            view = None
            if view_id:
                view = await database_sync_to_async(ViewHandler().get_view)(view_id)

            active_users = await database_sync_to_async(
                self.collaboration_handler.get_active_users
            )(table=table, view=view)

            user_data = [
                {
                    "user_id": presence.user.id,
                    "user_name": presence.user.first_name,
                    "user_email": presence.user.email,
                    "cursor_position": presence.cursor_position,
                    "is_typing": presence.is_typing,
                    "typing_field_id": presence.typing_field_id,
                    "typing_row_id": presence.typing_row_id,
                    "last_seen": presence.last_seen.isoformat(),
                }
                for presence in active_users
                if presence.user != user  # Exclude current user
            ]

            await self.send_json(
                {
                    "type": "active_users",
                    "table_id": table_id,
                    "view_id": view_id,
                    "users": user_data,
                }
            )

        except Exception as e:
            await self.send_json({"type": "error", "message": str(e)})

    async def _broadcast_presence_update(self, table_id, view_id, presence):
        """
        Broadcast presence update to collaboration group.
        """
        group_name = f"collaboration-table-{table_id}"
        if view_id:
            group_name = f"collaboration-view-{view_id}"

        await self.channel_layer.group_send(
            group_name,
            {
                "type": "presence_updated",
                "user_id": presence.user.id,
                "user_name": presence.user.first_name,
                "cursor_position": presence.cursor_position,
                "is_typing": presence.is_typing,
                "last_seen": presence.last_seen.isoformat(),
            },
        )

    async def _broadcast_typing_indicator(
        self, table_id, user_id, field_id, row_id, is_typing
    ):
        """
        Broadcast typing indicator to collaboration group.
        """
        await self.channel_layer.group_send(
            f"collaboration-table-{table_id}",
            {
                "type": "typing_indicator",
                "user_id": user_id,
                "field_id": field_id,
                "row_id": row_id,
                "is_typing": is_typing,
            },
        )

    async def _broadcast_cursor_update(self, table_id, user_id, cursor_position):
        """
        Broadcast cursor position update to collaboration group.
        """
        await self.channel_layer.group_send(
            f"collaboration-table-{table_id}",
            {
                "type": "cursor_updated",
                "user_id": user_id,
                "cursor_position": cursor_position,
            },
        )

    async def _broadcast_lock_status(self, table_id, row_id, field_id, user_id, status):
        """
        Broadcast lock status change to collaboration group.
        """
        await self.channel_layer.group_send(
            f"collaboration-table-{table_id}",
            {
                "type": "lock_status_changed",
                "row_id": row_id,
                "field_id": field_id,
                "user_id": user_id,
                "status": status,
            },
        )

    async def _broadcast_comment_created(self, table_id, row_id, comment):
        """
        Broadcast new comment to collaboration group.
        """
        await self.channel_layer.group_send(
            f"collaboration-table-{table_id}",
            {
                "type": "comment_created",
                "row_id": row_id,
                "comment": {
                    "id": comment.id,
                    "content": comment.content,
                    "user_id": comment.user.id,
                    "user_name": comment.user.first_name,
                    "created_at": comment.created_at.isoformat(),
                },
            },
        )

    # Event handlers for group messages
    async def presence_updated(self, event):
        await self.send_json(
            {
                "type": "presence_updated",
                "user_id": event["user_id"],
                "user_name": event["user_name"],
                "cursor_position": event["cursor_position"],
                "is_typing": event["is_typing"],
                "last_seen": event["last_seen"],
            }
        )

    async def typing_indicator(self, event):
        await self.send_json(
            {
                "type": "typing_indicator",
                "user_id": event["user_id"],
                "field_id": event["field_id"],
                "row_id": event["row_id"],
                "is_typing": event["is_typing"],
            }
        )

    async def cursor_updated(self, event):
        await self.send_json(
            {
                "type": "cursor_updated",
                "user_id": event["user_id"],
                "cursor_position": event["cursor_position"],
            }
        )

    async def lock_status_changed(self, event):
        await self.send_json(
            {
                "type": "lock_status_changed",
                "row_id": event["row_id"],
                "field_id": event["field_id"],
                "user_id": event["user_id"],
                "status": event["status"],
            }
        )

    async def comment_created(self, event):
        await self.send_json(
            {
                "type": "comment_created",
                "row_id": event["row_id"],
                "comment": event["comment"],
            }
        )