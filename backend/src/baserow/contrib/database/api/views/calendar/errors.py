"""
Calendar view API error definitions.
"""

ERROR_CALENDAR_VIEW_INVALID_DATE_FIELD = (
    "ERROR_CALENDAR_VIEW_INVALID_DATE_FIELD",
    "The provided field is not a valid date field for calendar view.",
    400,
)

ERROR_CALENDAR_VIEW_RECURRING_PATTERN_INVALID = (
    "ERROR_CALENDAR_VIEW_RECURRING_PATTERN_INVALID",
    "The provided recurring pattern configuration is invalid.",
    400,
)

ERROR_CALENDAR_VIEW_EXTERNAL_SYNC_FAILED = (
    "ERROR_CALENDAR_VIEW_EXTERNAL_SYNC_FAILED",
    "Failed to synchronize with external calendar service.",
    500,
)

ERROR_CALENDAR_VIEW_EXTERNAL_CALENDAR_NOT_FOUND = (
    "ERROR_CALENDAR_VIEW_EXTERNAL_CALENDAR_NOT_FOUND",
    "The specified external calendar was not found.",
    404,
)