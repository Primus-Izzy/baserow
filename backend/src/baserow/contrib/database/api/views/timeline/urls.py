from django.urls import path

from .views import (
    TimelineViewView,
    TimelineDependenciesView,
    TimelineDependencyView,
    TimelineMilestonesView,
    TimelineScheduleRecalculationView,
)

app_name = "baserow.contrib.database.api.views.timeline"

urlpatterns = [
    path(
        "<int:view_id>/",
        TimelineViewView.as_view(),
        name="list",
    ),
    path(
        "<int:view_id>/dependencies/",
        TimelineDependenciesView.as_view(),
        name="dependencies",
    ),
    path(
        "<int:view_id>/dependencies/<int:dependency_id>/",
        TimelineDependencyView.as_view(),
        name="dependency",
    ),
    path(
        "<int:view_id>/milestones/",
        TimelineMilestonesView.as_view(),
        name="milestones",
    ),
    path(
        "<int:view_id>/recalculate/",
        TimelineScheduleRecalculationView.as_view(),
        name="recalculate",
    ),
]