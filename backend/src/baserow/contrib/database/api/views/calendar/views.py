"""
Calendar view API views.
"""

from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from baserow.api.decorators import map_exceptions, validate_body
from baserow.api.errors import ERROR_USER_NOT_IN_GROUP
from baserow.api.schemas import get_error_schema
from baserow.contrib.database.api.views.errors import (
    ERROR_VIEW_DOES_NOT_EXIST,
    ERROR_VIEW_NOT_IN_TABLE,
)
from baserow.contrib.database.api.views.utils import get_view_ownership_type
from baserow.contrib.database.fields.exceptions import FieldNotInTable
from baserow.contrib.database.views.exceptions import ViewDoesNotExist, ViewNotInTable
from baserow.contrib.database.views.handler import ViewHandler
from baserow.contrib.database.views.models import CalendarView
from baserow.core.exceptions import UserNotInGroup

from .errors import (
    ERROR_CALENDAR_VIEW_INVALID_DATE_FIELD,
    ERROR_CALENDAR_VIEW_RECURRING_PATTERN_INVALID,
    ERROR_CALENDAR_VIEW_EXTERNAL_SYNC_FAILED,
)
from .serializers import (
    CalendarViewSerializer,
    CalendarRecurringPatternSerializer,
    CalendarExternalSyncSerializer,
    CalendarEventMoveSerializer,
    CalendarEventsSerializer,
)


class CalendarViewView(APIView):
    """
    API view for managing calendar views.
    """

    @map_exceptions(
        {
            UserNotInGroup: ERROR_USER_NOT_IN_GROUP,
            ViewDoesNotExist: ERROR_VIEW_DOES_NOT_EXIST,
            ViewNotInTable: ERROR_VIEW_NOT_IN_TABLE,
        }
    )
    def get(self, request, view_id):
        """
        Get calendar view configuration.
        """
        view = ViewHandler().get_view(view_id, CalendarView)
        view.table.database.group.has_user(
            request.user, raise_error=True, allow_if_template=True
        )

        serializer = CalendarViewSerializer(view)
        return Response(serializer.data)

    @transaction.atomic
    @map_exceptions(
        {
            UserNotInGroup: ERROR_USER_NOT_IN_GROUP,
            ViewDoesNotExist: ERROR_VIEW_DOES_NOT_EXIST,
            ViewNotInTable: ERROR_VIEW_NOT_IN_TABLE,
            FieldNotInTable: ERROR_CALENDAR_VIEW_INVALID_DATE_FIELD,
        }
    )
    @validate_body(CalendarViewSerializer, partial=True)
    def patch(self, request, data, view_id):
        """
        Update calendar view configuration.
        """
        view = ViewHandler().get_view(view_id, CalendarView)
        view.table.database.group.has_user(request.user, raise_error=True)

        view_handler = ViewHandler()
        view = view_handler.update_view(request.user, view, **data)

        serializer = CalendarViewSerializer(view)
        return Response(serializer.data)


class CalendarViewMoveEventView(APIView):
    """
    API view for moving calendar events between dates.
    """

    @transaction.atomic
    @map_exceptions(
        {
            UserNotInGroup: ERROR_USER_NOT_IN_GROUP,
            ViewDoesNotExist: ERROR_VIEW_DOES_NOT_EXIST,
            ViewNotInTable: ERROR_VIEW_NOT_IN_TABLE,
        }
    )
    @validate_body(CalendarEventMoveSerializer)
    def post(self, request, data, view_id):
        """
        Move a calendar event to a new date.
        """
        view = ViewHandler().get_view(view_id, CalendarView)
        view.table.database.group.has_user(request.user, raise_error=True)

        # Import here to avoid circular imports
        from baserow.contrib.database.views.calendar_handler import CalendarViewHandler
        
        calendar_handler = CalendarViewHandler()
        updated_row = calendar_handler.move_event(
            request.user,
            view,
            data["row_id"],
            data["new_date"],
            update_end_date=data.get("update_end_date", False)
        )

        return Response(
            {"row_id": updated_row.id, "success": True},
            status=status.HTTP_200_OK
        )


class CalendarViewEventsView(APIView):
    """
    API view for retrieving calendar events within a date range.
    """

    @map_exceptions(
        {
            UserNotInGroup: ERROR_USER_NOT_IN_GROUP,
            ViewDoesNotExist: ERROR_VIEW_DOES_NOT_EXIST,
            ViewNotInTable: ERROR_VIEW_NOT_IN_TABLE,
        }
    )
    @validate_body(CalendarEventsSerializer)
    def post(self, request, data, view_id):
        """
        Get calendar events within a specified date range.
        """
        view = ViewHandler().get_view(view_id, CalendarView)
        view.table.database.group.has_user(
            request.user, raise_error=True, allow_if_template=True
        )

        # Import here to avoid circular imports
        from baserow.contrib.database.views.calendar_handler import CalendarViewHandler
        
        calendar_handler = CalendarViewHandler()
        events = calendar_handler.get_events_in_range(
            request.user,
            view,
            data["start_date"],
            data["end_date"],
            include_recurring=data.get("include_recurring", True)
        )

        return Response({"events": events}, status=status.HTTP_200_OK)


class CalendarViewRecurringPatternsView(APIView):
    """
    API view for managing recurring patterns in calendar views.
    """

    @map_exceptions(
        {
            UserNotInGroup: ERROR_USER_NOT_IN_GROUP,
            ViewDoesNotExist: ERROR_VIEW_DOES_NOT_EXIST,
            ViewNotInTable: ERROR_VIEW_NOT_IN_TABLE,
        }
    )
    def get(self, request, view_id):
        """
        Get all recurring patterns for a calendar view.
        """
        view = ViewHandler().get_view(view_id, CalendarView)
        view.table.database.group.has_user(
            request.user, raise_error=True, allow_if_template=True
        )

        patterns = view.recurring_patterns.all()
        serializer = CalendarRecurringPatternSerializer(patterns, many=True)
        return Response(serializer.data)

    @transaction.atomic
    @map_exceptions(
        {
            UserNotInGroup: ERROR_USER_NOT_IN_GROUP,
            ViewDoesNotExist: ERROR_VIEW_DOES_NOT_EXIST,
            ViewNotInTable: ERROR_VIEW_NOT_IN_TABLE,
        }
    )
    @validate_body(CalendarRecurringPatternSerializer)
    def post(self, request, data, view_id):
        """
        Create a new recurring pattern for a calendar view.
        """
        view = ViewHandler().get_view(view_id, CalendarView)
        view.table.database.group.has_user(request.user, raise_error=True)

        # Import here to avoid circular imports
        from baserow.contrib.database.views.calendar_handler import CalendarViewHandler
        
        calendar_handler = CalendarViewHandler()
        pattern = calendar_handler.create_recurring_pattern(
            request.user, view, **data
        )

        serializer = CalendarRecurringPatternSerializer(pattern)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CalendarViewExternalSyncView(APIView):
    """
    API view for managing external calendar synchronization.
    """

    @map_exceptions(
        {
            UserNotInGroup: ERROR_USER_NOT_IN_GROUP,
            ViewDoesNotExist: ERROR_VIEW_DOES_NOT_EXIST,
            ViewNotInTable: ERROR_VIEW_NOT_IN_TABLE,
        }
    )
    def get(self, request, view_id):
        """
        Get all external sync configurations for a calendar view.
        """
        view = ViewHandler().get_view(view_id, CalendarView)
        view.table.database.group.has_user(
            request.user, raise_error=True, allow_if_template=True
        )

        syncs = view.external_syncs.all()
        serializer = CalendarExternalSyncSerializer(syncs, many=True)
        return Response(serializer.data)

    @transaction.atomic
    @map_exceptions(
        {
            UserNotInGroup: ERROR_USER_NOT_IN_GROUP,
            ViewDoesNotExist: ERROR_VIEW_DOES_NOT_EXIST,
            ViewNotInTable: ERROR_VIEW_NOT_IN_TABLE,
        }
    )
    @validate_body(CalendarExternalSyncSerializer)
    def post(self, request, data, view_id):
        """
        Create a new external sync configuration.
        """
        view = ViewHandler().get_view(view_id, CalendarView)
        view.table.database.group.has_user(request.user, raise_error=True)

        # Import here to avoid circular imports
        from baserow.contrib.database.views.calendar_handler import CalendarViewHandler
        
        calendar_handler = CalendarViewHandler()
        sync_config = calendar_handler.create_external_sync(
            request.user, view, **data
        )

        serializer = CalendarExternalSyncSerializer(sync_config)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    @transaction.atomic
    @map_exceptions(
        {
            UserNotInGroup: ERROR_USER_NOT_IN_GROUP,
            ViewDoesNotExist: ERROR_VIEW_DOES_NOT_EXIST,
            ViewNotInTable: ERROR_VIEW_NOT_IN_TABLE,
        }
    )
    def sync(self, request, view_id, sync_id):
        """
        Trigger synchronization with an external calendar.
        """
        view = ViewHandler().get_view(view_id, CalendarView)
        view.table.database.group.has_user(request.user, raise_error=True)

        # Import here to avoid circular imports
        from baserow.contrib.database.views.calendar_handler import CalendarViewHandler
        
        calendar_handler = CalendarViewHandler()
        try:
            result = calendar_handler.sync_external_calendar(
                request.user, view, sync_id
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )