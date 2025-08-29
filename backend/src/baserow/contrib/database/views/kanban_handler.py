"""
Handler for Kanban view specific operations including drag-and-drop functionality.
"""

from typing import Optional, Dict, Any

from django.contrib.auth.models import AbstractUser

from baserow.contrib.database.fields.models import SelectOption
from baserow.contrib.database.rows.handler import RowHandler
from baserow.contrib.database.views.models import KanbanView
from baserow.core.exceptions import UserNotInWorkspace


class KanbanViewHandler:
    """
    Handler for Kanban view operations.
    """

    def move_card(
        self,
        user: AbstractUser,
        kanban_view: KanbanView,
        row_id: int,
        to_column_value: Optional[str] = None,
        before_row_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Moves a card (row) between columns in a Kanban view by updating the
        underlying single select field value.

        :param user: The user performing the move operation.
        :param kanban_view: The Kanban view instance.
        :param row_id: The ID of the row/card being moved.
        :param to_column_value: The target column value (single select option value).
        :param before_row_id: Optional row ID to position the card before.
        :return: Dictionary containing the updated row data.
        :raises ValueError: If the Kanban view doesn't have a single select field configured.
        :raises SelectOption.DoesNotExist: If the target column option doesn't exist.
        """

        if not kanban_view.single_select_field:
            raise ValueError("Kanban view must have a single select field configured.")

        # Get the table model
        model = kanban_view.table.get_model()
        
        # Verify the row exists
        try:
            row = model.objects.get(pk=row_id)
        except model.DoesNotExist:
            raise ValueError(f"Row with ID {row_id} does not exist.")

        # Find the select option for the target column
        target_option = None
        if to_column_value:
            try:
                target_option = SelectOption.objects.get(
                    field=kanban_view.single_select_field,
                    value=to_column_value
                )
            except SelectOption.DoesNotExist:
                raise ValueError(f"Target column option '{to_column_value}' does not exist.")

        # Update the row's single select field value
        row_handler = RowHandler()
        field_name = f"field_{kanban_view.single_select_field.id}"
        update_data = {field_name: target_option.id if target_option else None}
        
        updated_row = row_handler.update_row_by_id(
            user,
            kanban_view.table,
            row_id,
            update_data
        )

        return {
            "row": updated_row,
            "moved_to_column": to_column_value,
            "target_option_id": target_option.id if target_option else None,
        }

    def get_kanban_columns(self, kanban_view: KanbanView) -> list:
        """
        Returns the available columns for a Kanban view based on the single select field options.

        :param kanban_view: The Kanban view instance.
        :return: List of column data including option details.
        """

        if not kanban_view.single_select_field:
            return []

        columns = []
        
        # Add a column for null/empty values
        columns.append({
            "id": None,
            "value": None,
            "color": "#E0E0E0",
            "name": "No Status",
            "order": -1,
        })

        # Add columns for each select option
        for option in kanban_view.single_select_field.select_options.all():
            columns.append({
                "id": option.id,
                "value": option.value,
                "color": option.color,
                "name": option.value,
                "order": option.order,
            })

        return sorted(columns, key=lambda x: x["order"])

    def get_cards_for_column(
        self, 
        kanban_view: KanbanView, 
        column_value: Optional[str] = None,
        limit: Optional[int] = None
    ) -> list:
        """
        Returns the cards (rows) for a specific column in the Kanban view.

        :param kanban_view: The Kanban view instance.
        :param column_value: The column value to filter by. None for empty/null column.
        :param limit: Optional limit on the number of cards to return.
        :return: List of row data for the specified column.
        """

        if not kanban_view.single_select_field:
            return []

        # Get the table model
        model = kanban_view.table.get_model()
        field_name = f"field_{kanban_view.single_select_field.id}"

        # Build the query
        if column_value is None:
            # Get rows with null/empty values
            queryset = model.objects.filter(**{f"{field_name}__isnull": True})
        else:
            # Get rows with the specific select option value
            try:
                option = SelectOption.objects.get(
                    field=kanban_view.single_select_field,
                    value=column_value
                )
                queryset = model.objects.filter(**{field_name: option.id})
            except SelectOption.DoesNotExist:
                return []

        # Apply view filters if any
        # TODO: Apply view filters and sorting here
        
        if limit:
            queryset = queryset[:limit]

        return list(queryset)

    def update_card_configuration(
        self,
        user: AbstractUser,
        kanban_view: KanbanView,
        configuration: Dict[str, Any]
    ) -> KanbanView:
        """
        Updates the card configuration for a Kanban view.

        :param user: The user performing the update.
        :param kanban_view: The Kanban view instance.
        :param configuration: The new card configuration.
        :return: The updated Kanban view instance.
        """

        kanban_view.card_configuration = configuration
        kanban_view.save(update_fields=["card_configuration"])
        return kanban_view

    def update_column_configuration(
        self,
        user: AbstractUser,
        kanban_view: KanbanView,
        configuration: Dict[str, Any]
    ) -> KanbanView:
        """
        Updates the column configuration for a Kanban view.

        :param user: The user performing the update.
        :param kanban_view: The Kanban view instance.
        :param configuration: The new column configuration.
        :return: The updated Kanban view instance.
        """

        kanban_view.column_configuration = configuration
        kanban_view.save(update_fields=["column_configuration"])
        return kanban_view