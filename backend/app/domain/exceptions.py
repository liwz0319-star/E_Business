"""
Domain exceptions.
"""

class HTTPClientError(Exception):
    """Base exception for HTTP client errors."""
    pass

class MaxRetriesExceededError(HTTPClientError):
    """Raised when max retries are exceeded."""
    pass

class TimeoutError(HTTPClientError):
    """Raised on request timeout."""
    pass

class ProviderNotFoundError(Exception):
    """Raised when a provider is not found."""
    pass
