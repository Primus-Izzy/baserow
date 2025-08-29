"""
Exceptions for the granular permission system.
"""

from baserow.core.exceptions import PermissionException


class GranularPermissionException(PermissionException):
    """Base exception for granular permission system."""
    pass


class CustomRoleNotFound(GranularPermissionException):
    """Raised when a custom role is not found."""
    pass


class CustomRoleAlreadyExists(GranularPermissionException):
    """Raised when trying to create a custom role that already exists."""
    pass


class InvalidPermissionLevel(GranularPermissionException):
    """Raised when an invalid permission level is specified."""
    pass


class PermissionNotFound(GranularPermissionException):
    """Raised when a specific permission is not found."""
    pass


class ConditionalPermissionEvaluationError(GranularPermissionException):
    """Raised when there's an error evaluating a conditional permission."""
    pass


class APIKeyNotFound(GranularPermissionException):
    """Raised when an API key is not found."""
    pass


class APIKeyInactive(GranularPermissionException):
    """Raised when an API key is inactive."""
    pass


class APIKeyExpired(GranularPermissionException):
    """Raised when an API key has expired."""
    pass


class APIKeyRateLimitExceeded(GranularPermissionException):
    """Raised when an API key exceeds its rate limit."""
    pass


class InsufficientTablePermission(GranularPermissionException):
    """Raised when a user lacks sufficient table permissions."""
    pass


class InsufficientFieldPermission(GranularPermissionException):
    """Raised when a user lacks sufficient field permissions."""
    pass


class InsufficientViewPermission(GranularPermissionException):
    """Raised when a user lacks sufficient view permissions."""
    pass


class InsufficientRowPermission(GranularPermissionException):
    """Raised when a user lacks sufficient row permissions."""
    pass