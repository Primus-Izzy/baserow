"""
Notification System Exceptions
"""


class NotificationError(Exception):
    """Base exception for notification system errors."""
    pass


class TemplateRenderError(NotificationError):
    """Exception raised when template rendering fails."""
    pass


class DeliveryError(NotificationError):
    """Exception raised when notification delivery fails."""
    pass


class PreferenceError(NotificationError):
    """Exception raised when handling user preferences fails."""
    pass


class BatchingError(NotificationError):
    """Exception raised when batching notifications fails."""
    pass