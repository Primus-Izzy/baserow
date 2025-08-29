"""
Calendar view handler for managing calendar-specific operations.
"""

import datetime
from typing import Dict, List, Optional, Any
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, YEARLY
from dateutil.parser import parse as parse_date

from django.contrib.auth.models import AbstractUser
from django.db import transaction
from django.utils import timezone

from baserow.contrib.database.fields.handler import FieldHandler
from baserow.contrib.database.rows.handler import RowHandler
from baserow.contrib.database.views.models import (
    CalendarView,
    CalendarRecurringPattern,
    CalendarExternalSync,
)
from baserow.contrib.database.views.exceptions import ViewDoesNotExist


class CalendarViewHandler:
    """
    Handler for calendar view operations including event management,
    recurring patterns, and external calendar synchronization.
    """

    def move_event(
        self,
        user: AbstractUser,
        view: CalendarView,
        row_id: int,
        new_date: datetime.date,
        update_end_date: bool = False,
    ) -> Any:
        """
        Move a calendar event to a new date by updating the date field.
        
        :param user: The user performing the operation
        :param view: The calendar view
        :param row_id: ID of the row/event to move
        :param new_date: New date for the event
        :param update_end_date: Whether to also update end date maintaining duration
        :return: Updated row object
        """
        if not view.date_field:
            raise ValueError("Calendar view must have a date field configured")

        table = view.table
        model = table.get_model()
        
        try:
            row = model.objects.get(id=row_id)
        except model.DoesNotExist:
            raise ValueError(f"Row with id {row_id} does not exist")

        # Calculate duration if updating end date
        duration = None
        if update_end_date and hasattr(row, f"field_{view.date_field.id}"):
            current_date = getattr(row, f"field_{view.date_field.id}")
            if current_date and hasattr(row, f"field_{view.end_date_field.id}"):
                end_date = getattr(row, f"field_{view.end_date_field.id}")
                if end_date:
                    duration = end_date - current_date

        # Update the date field
        row_handler = RowHandler()
        update_data = {
            f"field_{view.date_field.id}": new_date
        }

        # Update end date if requested and duration was calculated
        if duration and hasattr(row, f"field_{view.end_date_field.id}"):
            update_data[f"field_{view.end_date_field.id}"] = new_date + duration

        updated_row = row_handler.update_row_by_id(
            user, table, row_id, update_data
        )

        return updated_row

    def get_events_in_range(
        self,
        user: AbstractUser,
        view: CalendarView,
        start_date: datetime.date,
        end_date: datetime.date,
        include_recurring: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Get all events within a specified date range, including recurring events.
        
        :param user: The user requesting the events
        :param view: The calendar view
        :param start_date: Start date of the range
        :param end_date: End date of the range
        :param include_recurring: Whether to include recurring event instances
        :return: List of event data
        """
        if not view.date_field:
            return []

        table = view.table
        model = table.get_model()
        date_field_name = f"field_{view.date_field.id}"

        # Get base events within the date range
        queryset = model.objects.filter(
            **{
                f"{date_field_name}__gte": start_date,
                f"{date_field_name}__lte": end_date,
            }
        )

        events = []
        for row in queryset:
            event_data = self._row_to_event_data(view, row)
            events.append(event_data)

        # Add recurring event instances if enabled
        if include_recurring and view.enable_recurring_events:
            recurring_events = self._get_recurring_events_in_range(
                view, start_date, end_date
            )
            events.extend(recurring_events)

        return events

    def create_recurring_pattern(
        self,
        user: AbstractUser,
        view: CalendarView,
        row_id: int,
        pattern_type: str,
        interval: int = 1,
        days_of_week: Optional[List[int]] = None,
        end_date: Optional[datetime.date] = None,
        max_occurrences: Optional[int] = None,
        **kwargs
    ) -> CalendarRecurringPattern:
        """
        Create a recurring pattern for a calendar event.
        
        :param user: The user creating the pattern
        :param view: The calendar view
        :param row_id: ID of the row this pattern applies to
        :param pattern_type: Type of recurring pattern
        :param interval: Interval between recurrences
        :param days_of_week: Days of week for weekly patterns
        :param end_date: End date for the pattern
        :param max_occurrences: Maximum number of occurrences
        :return: Created CalendarRecurringPattern instance
        """
        pattern = CalendarRecurringPattern.objects.create(
            calendar_view=view,
            row_id=row_id,
            pattern_type=pattern_type,
            interval=interval,
            days_of_week=days_of_week or [],
            end_date=end_date,
            max_occurrences=max_occurrences,
            **kwargs
        )
        return pattern

    def create_external_sync(
        self,
        user: AbstractUser,
        view: CalendarView,
        provider: str,
        external_calendar_id: str,
        sync_direction: str = "bidirectional",
        **kwargs
    ) -> CalendarExternalSync:
        """
        Create an external calendar synchronization configuration.
        
        :param user: The user creating the sync
        :param view: The calendar view
        :param provider: External calendar provider
        :param external_calendar_id: ID of the external calendar
        :param sync_direction: Direction of synchronization
        :return: Created CalendarExternalSync instance
        """
        sync_config = CalendarExternalSync.objects.create(
            calendar_view=view,
            provider=provider,
            external_calendar_id=external_calendar_id,
            sync_direction=sync_direction,
            **kwargs
        )
        return sync_config

    def sync_external_calendar(
        self,
        user: AbstractUser,
        view: CalendarView,
        sync_id: int,
    ) -> Dict[str, Any]:
        """
        Trigger synchronization with an external calendar.
        
        :param user: The user triggering the sync
        :param view: The calendar view
        :param sync_id: ID of the sync configuration
        :return: Sync result information
        """
        try:
            sync_config = view.external_syncs.get(id=sync_id)
        except CalendarExternalSync.DoesNotExist:
            raise ValueError(f"External sync configuration {sync_id} not found")

        # This is a placeholder for actual external calendar integration
        # In a real implementation, this would connect to Google Calendar, Outlook, etc.
        
        result = {
            "sync_id": sync_id,
            "provider": sync_config.provider,
            "status": "success",
            "events_imported": 0,
            "events_exported": 0,
            "last_sync": timezone.now().isoformat(),
        }

        # Update the last sync timestamp
        sync_config.last_sync = timezone.now()
        sync_config.save()

        return result

    def _row_to_event_data(self, view: CalendarView, row: Any) -> Dict[str, Any]:
        """
        Convert a table row to calendar event data.
        
        :param view: The calendar view
        :param row: The table row
        :return: Event data dictionary
        """
        event_data = {
            "id": row.id,
            "date": getattr(row, f"field_{view.date_field.id}") if view.date_field else None,
            "title": getattr(row, f"field_{view.event_title_field.id}") if view.event_title_field else f"Event {row.id}",
        }

        # Add color information if color field is configured
        if view.event_color_field:
            color_value = getattr(row, f"field_{view.event_color_field.id}")
            event_data["color"] = self._get_event_color(color_value)

        # Add other visible fields
        field_options = view.get_field_options().filter(show_in_event=True)
        for field_option in field_options:
            field_value = getattr(row, f"field_{field_option.field.id}", None)
            event_data[f"field_{field_option.field.id}"] = field_value

        return event_data

    def _get_event_color(self, color_value: Any) -> str:
        """
        Determine event color based on field value.
        
        :param color_value: Value from the color field
        :return: Color string (hex or color name)
        """
        # This is a simplified implementation
        # In practice, this would map field values to colors based on field type
        if isinstance(color_value, str):
            return color_value
        elif hasattr(color_value, 'color'):
            return color_value.color
        else:
            return "#3174ad"  # Default blue color

    def _get_recurring_events_in_range(
        self,
        view: CalendarView,
        start_date: datetime.date,
        end_date: datetime.date,
    ) -> List[Dict[str, Any]]:
        """
        Generate recurring event instances within a date range.
        
        :param view: The calendar view
        :param start_date: Start date of the range
        :param end_date: End date of the range
        :return: List of recurring event instances
        """
        recurring_events = []
        patterns = view.recurring_patterns.all()

        for pattern in patterns:
            # Get the original event
            table = view.table
            model = table.get_model()
            
            try:
                original_row = model.objects.get(id=pattern.row_id)
            except model.DoesNotExist:
                continue

            original_date = getattr(original_row, f"field_{view.date_field.id}")
            if not original_date:
                continue

            # Generate recurring instances
            instances = self._generate_recurring_instances(
                pattern, original_date, start_date, end_date
            )

            for instance_date in instances:
                # Skip the original event date to avoid duplicates
                if instance_date == original_date:
                    continue

                event_data = self._row_to_event_data(view, original_row)
                event_data["date"] = instance_date
                event_data["is_recurring"] = True
                event_data["pattern_id"] = pattern.id
                recurring_events.append(event_data)

        return recurring_events

    def _generate_recurring_instances(
        self,
        pattern: CalendarRecurringPattern,
        original_date: datetime.date,
        start_date: datetime.date,
        end_date: datetime.date,
    ) -> List[datetime.date]:
        """
        Generate recurring event instances based on the pattern.
        
        :param pattern: The recurring pattern
        :param original_date: Original event date
        :param start_date: Range start date
        :param end_date: Range end date
        :return: List of instance dates
        """
        instances = []

        # Map pattern types to dateutil rrule frequencies
        freq_map = {
            "daily": DAILY,
            "weekly": WEEKLY,
            "monthly": MONTHLY,
            "yearly": YEARLY,
        }

        if pattern.pattern_type not in freq_map:
            return instances

        # Set up rrule parameters
        rrule_kwargs = {
            "freq": freq_map[pattern.pattern_type],
            "interval": pattern.interval,
            "dtstart": original_date,
        }

        # Add end condition
        if pattern.end_date:
            rrule_kwargs["until"] = pattern.end_date
        elif pattern.max_occurrences:
            rrule_kwargs["count"] = pattern.max_occurrences

        # Add days of week for weekly patterns
        if pattern.pattern_type == "weekly" and pattern.days_of_week:
            rrule_kwargs["byweekday"] = pattern.days_of_week

        # Generate instances
        rule = rrule(**rrule_kwargs)
        for dt in rule:
            instance_date = dt.date() if hasattr(dt, 'date') else dt
            
            # Only include instances within the requested range
            if start_date <= instance_date <= end_date:
                # Check if this date is not in exceptions
                if instance_date.isoformat() not in pattern.exceptions:
                    instances.append(instance_date)

        return instances