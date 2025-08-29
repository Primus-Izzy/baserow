"""
Calendar view API serializers.
"""

from rest_framework import serializers

from baserow.contrib.database.api.views.serializers import FieldOptionsSerializer
from baserow.contrib.database.fields.models import Field
from baserow.contrib.database.views.models import (
    CalendarView,
    CalendarViewFieldOptions,
    CalendarRecurringPattern,
    CalendarExternalSync,
)


class CalendarViewFieldOptionsSerializer(FieldOptionsSerializer):
    """
    Serializer for CalendarViewFieldOptions model.
    """

    class Meta(FieldOptionsSerializer.Meta):
        model = CalendarViewFieldOptions
        fields = FieldOptionsSerializer.Meta.fields + (
            "show_in_event",
            "event_display_style",
        )


class CalendarViewSerializer(serializers.ModelSerializer):
    """
    Serializer for CalendarView model.
    """

    date_field = serializers.PrimaryKeyRelatedField(
        queryset=Field.objects.all(),
        required=False,
        default=None,
        allow_null=True,
        help_text="Date field used to position events on the calendar",
    )
    event_title_field = serializers.PrimaryKeyRelatedField(
        queryset=Field.objects.all(),
        required=False,
        default=None,
        allow_null=True,
        help_text="Field used as the event title",
    )
    event_color_field = serializers.PrimaryKeyRelatedField(
        queryset=Field.objects.all(),
        required=False,
        default=None,
        allow_null=True,
        help_text="Field used to determine event colors",
    )
    recurring_pattern_field = serializers.PrimaryKeyRelatedField(
        queryset=Field.objects.all(),
        required=False,
        default=None,
        allow_null=True,
        help_text="Field containing recurring event pattern configuration",
    )

    class Meta:
        model = CalendarView
        fields = (
            "date_field",
            "display_mode",
            "event_title_field",
            "event_color_field",
            "enable_recurring_events",
            "recurring_pattern_field",
            "external_calendar_config",
            "enable_external_sync",
        )


class CalendarRecurringPatternSerializer(serializers.ModelSerializer):
    """
    Serializer for CalendarRecurringPattern model.
    """

    class Meta:
        model = CalendarRecurringPattern
        fields = (
            "id",
            "row_id",
            "pattern_type",
            "interval",
            "days_of_week",
            "end_date",
            "max_occurrences",
            "exceptions",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_days_of_week(self, value):
        """
        Validate that days_of_week contains valid day numbers (0-6).
        """
        if not isinstance(value, list):
            raise serializers.ValidationError("days_of_week must be a list")
        
        for day in value:
            if not isinstance(day, int) or day < 0 or day > 6:
                raise serializers.ValidationError(
                    "days_of_week must contain integers between 0 (Monday) and 6 (Sunday)"
                )
        
        return value

    def validate_interval(self, value):
        """
        Validate that interval is a positive integer.
        """
        if value < 1:
            raise serializers.ValidationError("interval must be a positive integer")
        return value

    def validate(self, data):
        """
        Validate the recurring pattern configuration.
        """
        pattern_type = data.get("pattern_type")
        
        # Weekly patterns should have days_of_week specified
        if pattern_type == "weekly" and not data.get("days_of_week"):
            raise serializers.ValidationError(
                "Weekly patterns must specify days_of_week"
            )
        
        # Ensure either end_date or max_occurrences is specified, but not both
        end_date = data.get("end_date")
        max_occurrences = data.get("max_occurrences")
        
        if end_date and max_occurrences:
            raise serializers.ValidationError(
                "Cannot specify both end_date and max_occurrences"
            )
        
        return data


class CalendarExternalSyncSerializer(serializers.ModelSerializer):
    """
    Serializer for CalendarExternalSync model.
    """

    class Meta:
        model = CalendarExternalSync
        fields = (
            "id",
            "provider",
            "external_calendar_id",
            "sync_direction",
            "is_active",
            "last_sync",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "last_sync", "created_at", "updated_at")


class CalendarEventMoveSerializer(serializers.Serializer):
    """
    Serializer for moving calendar events between dates.
    """

    row_id = serializers.IntegerField(
        help_text="ID of the row/event to move"
    )
    new_date = serializers.DateField(
        help_text="New date for the event"
    )
    update_end_date = serializers.BooleanField(
        default=False,
        help_text="Whether to also update the end date (maintaining duration)"
    )


class CalendarEventsSerializer(serializers.Serializer):
    """
    Serializer for calendar events data.
    """

    start_date = serializers.DateField(
        help_text="Start date for events to retrieve"
    )
    end_date = serializers.DateField(
        help_text="End date for events to retrieve"
    )
    include_recurring = serializers.BooleanField(
        default=True,
        help_text="Whether to include recurring event instances"
    )

    def validate(self, data):
        """
        Validate that start_date is before end_date.
        """
        if data["start_date"] >= data["end_date"]:
            raise serializers.ValidationError(
                "start_date must be before end_date"
            )
        return data