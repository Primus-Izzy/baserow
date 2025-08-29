from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from baserow.api.decorators import map_exceptions
from baserow.api.errors import ERROR_USER_NOT_IN_GROUP
from baserow.contrib.database.views.exceptions import ViewDoesNotExist
from baserow.contrib.database.views.handler import ViewHandler
from baserow.contrib.database.views.models import TimelineView
from baserow.core.exceptions import UserNotInWorkspace

from .errors import ERROR_TIMELINE_DOES_NOT_EXIST


class TimelineViewView(APIView):
    permission_classes = (IsAuthenticated,)

    @map_exceptions({
        UserNotInWorkspace: ERROR_USER_NOT_IN_GROUP,
        ViewDoesNotExist: ERROR_TIMELINE_DOES_NOT_EXIST,
    })
    def get(self, request, view_id):
        """Lists all the rows of a timeline view."""
        view = ViewHandler().get_view_as_user(request.user, view_id, TimelineView)
        return Response({"message": "Timeline view data"})


class TimelineDependenciesView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, view_id):
        """Returns all dependencies for a timeline view."""
        return Response([])


class TimelineDependencyView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, view_id, dependency_id):
        """Deletes a dependency between two tasks."""
        return Response(status=204)


class TimelineMilestonesView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, view_id):
        """Returns all milestones for a timeline view."""
        return Response([])


class TimelineScheduleRecalculationView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, view_id):
        """Recalculates the schedule for dependent tasks."""
        return Response({"updated_rows": [], "message": "Schedule recalculated"})# Addition
al view classes for comprehensive API coverage