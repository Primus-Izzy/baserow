"""
Calendar view API URL patterns.
"""

from django.urls import path

from .views import (
    CalendarViewView,
    CalendarViewMoveEventView,
    CalendarViewEventsView,
    CalendarViewRecurringPatternsView,
    CalendarViewExternalSyncView,
)

app_name = "baserow.contrib.database.api.views.calendar"

urlpatterns = [
    path(
        "<int:view_id>/",
        CalendarViewView.as_view(),
        name="calendar_view",
    ),
    path(
        "<int:view_id>/move-event/",
        CalendarViewMoveEventView.as_view(),
        name="move_event",
    ),
    path(
        "<int:view_id>/events/",
        CalendarViewEventsView.as_view(),
        name="events",
    ),
    path(
        "<int:view_id>/recurring-patterns/",
        CalendarViewRecurringPatternsView.as_view(),
        name="recurring_patterns",
    ),
    path(
        "<int:view_id>/external-sync/",
        CalendarViewExternalSyncView.as_view(),
        name="external_sync",
    ),
    path(
        "<int:view_id>/external-sync/<int:sync_id>/sync/",
        CalendarViewExternalSyncView.as_view(),
        {"action": "sync"},
        name="trigger_sync",
    ),
]