from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger

from shared.api.exceptions import (
    BadGatewayError,
    ConflictError,
    ForbiddenError,
    InternalApiError,
    NotFoundError,
    TemporaryUnavailableError,
    ValidationError,
)


def _error_payload(message: str, data: Any | None = None) -> dict[str, Any]:
    return {
        "message": message,
        "data": data,
    }


def _error_response(
    status_code: int,
    message: str,
    data: Any | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=_error_payload(message, data),
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(InternalApiError)
    async def internal_api_error_handler(
        _request: Request,
        exc: InternalApiError,
    ) -> JSONResponse:
        if isinstance(exc, NotFoundError):
            return _error_response(404, str(exc), exc.data)
        if isinstance(exc, ConflictError):
            return _error_response(409, str(exc), exc.data)
        if isinstance(exc, ForbiddenError):
            return _error_response(403, str(exc), exc.data)
        if isinstance(exc, ValidationError):
            return _error_response(422, str(exc), exc.data)
        if isinstance(exc, BadGatewayError):
            return _error_response(502, str(exc), exc.data)
        if isinstance(exc, TemporaryUnavailableError):
            return _error_response(503, str(exc), exc.data)

        return _error_response(500, str(exc), exc.data)

    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return _error_response(
            422,
            "Request validation failed",
            {"errors": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.exception(
            "Unhandled exception in orchestrator",
            method=request.method,
            path=request.url.path,
        )
        return _error_response(500, "Unexpected internal error")
