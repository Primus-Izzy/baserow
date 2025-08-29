"""
People field notification system integration.
This module handles notifications when users are added or removed from people fields.
"""

from typing import List, Union

from django.contrib.auth import get_user_model

from baserow.contrib.database.fields.models import PeopleField

User = get_user_model()


class PeopleFieldNotificationHandler:
    """
    Handles notifications for people field changes.
    This is a placeholder implementation that can be extended when
    the notification system is fully implemented.
    """

    @staticmethod
    def notify_users_added(
        field: PeopleField,
        users: Union[List[User], List[int]],
        row_id: int,
        table_name: str,
        changed_by_user: User = None
    ):
        """
        Notify users when they are added to a people field.
        
        :param field: The people field instance
        :param users: List of users or user IDs that were added
        :param row_id: The ID of the row that was updated
        :param table_name: The name of the table
        :param changed_by_user: The user who made the change
        """
        if not field.notify_when_added:
            return

        # TODO: Implement actual notification system integration
        # For now, this is a placeholder that logs the notification
        user_ids = []
        if users and len(users) > 0:
            if isinstance(users[0], int):
                user_ids = users
            else:
                user_ids = [user.id for user in users]

        # Placeholder logging - replace with actual notification system
        print(f"NOTIFICATION: Users {user_ids} added to field '{field.name}' in row {row_id} of table '{table_name}'")

    @staticmethod
    def notify_users_removed(
        field: PeopleField,
        users: Union[List[User], List[int]],
        row_id: int,
        table_name: str,
        changed_by_user: User = None
    ):
        """
        Notify users when they are removed from a people field.
        
        :param field: The people field instance
        :param users: List of users or user IDs that were removed
        :param row_id: The ID of the row that was updated
        :param table_name: The name of the table
        :param changed_by_user: The user who made the change
        """
        if not field.notify_when_removed:
            return

        # TODO: Implement actual notification system integration
        # For now, this is a placeholder that logs the notification
        user_ids = []
        if users and len(users) > 0:
            if isinstance(users[0], int):
                user_ids = users
            else:
                user_ids = [user.id for user in users]

        # Placeholder logging - replace with actual notification system
        print(f"NOTIFICATION: Users {user_ids} removed from field '{field.name}' in row {row_id} of table '{table_name}'")

    @staticmethod
    def notify_field_assignment_changed(
        field: PeopleField,
        added_users: Union[List[User], List[int]],
        removed_users: Union[List[User], List[int]],
        row_id: int,
        table_name: str,
        changed_by_user: User = None
    ):
        """
        Notify users when their assignment to a people field changes.
        
        :param field: The people field instance
        :param added_users: List of users or user IDs that were added
        :param removed_users: List of users or user IDs that were removed
        :param row_id: The ID of the row that was updated
        :param table_name: The name of the table
        :param changed_by_user: The user who made the change
        """
        if added_users:
            PeopleFieldNotificationHandler.notify_users_added(
                field, added_users, row_id, table_name, changed_by_user
            )
        
        if removed_users:
            PeopleFieldNotificationHandler.notify_users_removed(
                field, removed_users, row_id, table_name, changed_by_user
            )