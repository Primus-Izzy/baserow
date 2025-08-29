class IntegrationError(Exception):
    """Base exception for integration errors"""
    pass


class AuthenticationError(IntegrationError):
    """Raised when authentication fails"""
    pass


class SyncError(IntegrationError):
    """Raised when sync operations fail"""
    pass


class ProviderNotFoundError(IntegrationError):
    """Raised when integration provider is not found"""
    pass


class TokenExpiredError(AuthenticationError):
    """Raised when access token has expired"""
    pass


class RateLimitError(IntegrationError):
    """Raised when API rate limit is exceeded"""
    pass


class ExternalServiceError(IntegrationError):
    """Raised when external service returns an error"""
    pass