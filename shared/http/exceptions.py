class InternalApiError(Exception):
    """Base internal API error."""

    def __init__(self, message: str, data: dict | None = None) -> None:
        super().__init__(message)
        self.data = data or {}


class InternalApiConnectionError(InternalApiError):
    """Connection error to the internal API."""


class InternalApiTimeoutError(InternalApiError):
    """Internal API timeout error."""


class InternalApiRequestError(InternalApiError):
    """General HTTP request error to the internal API."""


class ForbiddenError(InternalApiError):
    """Access to the requested resource is forbidden."""


class BadGatewayError(InternalApiError):
    """Bad gateway error from upstream service."""


class NotFoundError(InternalApiError):
    """Requested entity was not found."""


class ConflictError(InternalApiError):
    """Data conflict error."""


class ValidationError(InternalApiError):
    """Validation error on the API side."""


class TemporaryUnavailableError(InternalApiError):
    """Temporary API unavailability error."""
