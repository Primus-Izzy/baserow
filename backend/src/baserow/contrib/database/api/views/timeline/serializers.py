from rest_framework import serializers

from baserow.contrib.database.views.models import (
    TimelineViewFieldOptions,
    TimelineDependency,
    TimelineMilestone,
)


class TimelineViewFieldOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimelineViewFieldOptions
        fields = (
            "hidden",
            "order",
            "show_in_timeline",
            "color_field",
        )


class TimelineDependencySerializer(serializers.ModelSerializer):
    class Meta:
        model = TimelineDependency
        fields = (
            "id",
            "predecessor_row_id",
            "successor_row_id",
            "dependency_type",
            "lag_days",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class TimelineMilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimelineMilestone
        fields = (
            "id",
            "name",
            "date_field",
            "row_id",
            "color",
            "icon",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class TimelineViewFilterSerializer(serializers.Serializer):
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


class TimelineScheduleRecalculationSerializer(serializers.Serializer):
    """
    Serializer for triggering schedule recalculation for dependent tasks.
    """
    row_id = serializers.IntegerField(
        help_text="The ID of the row whose schedule change should trigger recalculation."
    )
    new_start_date = serializers.DateTimeField(
        required=False,
        allow_null=True,
        help_text="New start date for the task."
    )
    new_end_date = serializers.DateTimeField(
        required=False,
        allow_null=True,
        help_text="New end date for the task."
    )


class CreateTimelineDependencySerializer(serializers.Serializer):
    """
    Serializer for creating timeline dependencies.
    """
    predecessor_row_id = serializers.IntegerField(
        help_text="ID of the row that must be completed first"
    )
    successor_row_id = serializers.IntegerField(
        help_text="ID of the row that depends on the predecessor"
    )
    dependency_type = serializers.ChoiceField(
        choices=TimelineDependency.DEPENDENCY_TYPE_CHOICES.choices,
        default=TimelineDependency.DEPENDENCY_TYPE_CHOICES.FINISH_TO_START,
        help_text="Type of dependency relationship"
    )
    lag_days = serializers.IntegerField(
        default=0,
        help_text="Number of days to wait after dependency is met (can be negative for overlap)"
    )


class CreateTimelineMilestoneSerializer(serializers.Serializer):
    """
    Serializer for creating timeline milestones.
    """
    name = serializers.CharField(
        max_length=255,
        help_text="Name of the milestone"
    )
    date_field = serializers.IntegerField(
        help_text="ID of the date field that determines the milestone date"
    )
    row_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Optional row ID if milestone is tied to a specific row"
    )
    color = serializers.CharField(
        max_length=7,
        default="#FF0000",
        help_text="Color for the milestone indicator in hex format"
    )
    icon = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        help_text="Icon name for the milestone indicator"
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional description for the milestone"
    )
    is_active = serializers.BooleanField(
        default=True,
        help_text="Whether this milestone is currently active"
    )