from rest_framework import serializers

from baserow.contrib.database.views.models import KanbanViewFieldOptions


class KanbanViewFieldOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = KanbanViewFieldOptions
        fields = (
            "hidden",
            "order",
            "show_in_card",
            "card_display_style",
        )


class KanbanViewFilterSerializer(serializers.Serializer):
    field_ids = serializers.ListField(
        allow_empty=False,
        required=False,
        default=None,
        child=serializers.IntegerField(),
        help_text="Only the fields related to the provided ids are added to the "
        "response. If None are provided all fields will be returned.",
    )
    row_ids = serializers.ListField(
        allow_empty=False,
        child=serializers.IntegerField(),
        help_text="Only rows related to the provided ids are added to the response.",
    )


class KanbanViewMoveCardSerializer(serializers.Serializer):
    """
    Serializer for handling drag-and-drop card moves between columns.
    """
    row_id = serializers.IntegerField(
        help_text="The ID of the row/card being moved."
    )
    from_column_value = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        required=False,
        help_text="The original column value (single select option value)."
    )
    to_column_value = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        required=False,
        help_text="The target column value (single select option value)."
    )
    before_row_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="The ID of the row that this card should be placed before. "
        "If null, the card will be placed at the end of the column."
    )