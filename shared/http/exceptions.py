# TODO: Implement and translate
class InternalApiError(Exception):
    """Базовая ошибка внутреннего API."""

    def __init__(self, message: str, data: dict | None = None) -> None:
        super().__init__(message)
        self.data = data or {}


class InternalApiConnectionError(InternalApiError):
    """Ошибка соединения с внутренним API."""


class InternalApiTimeoutError(InternalApiError):
    """Таймаут внутреннего API."""


class InternalApiRequestError(InternalApiError):
    """Общая ошибка HTTP-запроса к внутреннему API."""


class ForbiddenError(InternalApiError):
    """Forbidden"""


class BadGatewayError(InternalApiError):
    """BadGatewayError"""


class NotFoundError(InternalApiError):
    """Сущность не найдена."""


class ConflictError(InternalApiError):
    """Конфликт данных."""


class ValidationError(InternalApiError):
    """Ошибка валидации на стороне API."""


class TemporaryUnavailableError(InternalApiError):
    """Временная недоступность API."""
