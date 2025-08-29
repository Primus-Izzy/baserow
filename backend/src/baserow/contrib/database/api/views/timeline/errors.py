from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

ERROR_TIMELINE_DOES_NOT_EXIST = (
    "ERROR_TIMELINE_DOES_NOT_EXIST",
    HTTP_404_NOT_FOUND,
    "The requested timeline view does not exist.",
)

ERROR_TIMELINE_DEPENDENCY_CIRCULAR = (
    "ERROR_TIMELINE_DEPENDENCY_CIRCULAR",
    HTTP_400_BAD_REQUEST,
    "Creating this dependency would result in a circular dependency.",
)

ERROR_TIMELINE_DEPENDENCY_SELF_REFERENCE = (
    "ERROR_TIMELINE_DEPENDENCY_SELF_REFERENCE",
    HTTP_400_BAD_REQUEST,
    "A task cannot depend on itself.",
)

ERROR_TIMELINE_MILESTONE_INVALID_FIELD = (
    "ERROR_TIMELINE_MILESTONE_INVALID_FIELD",
    HTTP_400_BAD_REQUEST,
    "The specified field is not a valid date field for milestones.",
)

ERROR_TIMELINE_INVALID_DATE_SETTINGS = (
    "ERROR_TIMELINE_INVALID_DATE_SETTINGS",
    HTTP_400_BAD_REQUEST,
    "The timeline view has invalid date field settings.",
)