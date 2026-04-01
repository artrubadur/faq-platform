import asyncio
from typing import TypeVar

import httpx

from bot.core.config import config
from shared.http.exceptions import (
    BadGatewayError,
    ConflictError,
    ForbiddenError,
    InternalApiConnectionError,
    InternalApiRequestError,
    InternalApiTimeoutError,
    NotFoundError,
    TemporaryUnavailableError,
    ValidationError,
)

T = TypeVar("T")


def extract_payload(response: httpx.Response) -> tuple[str, dict | None]:
    try:
        payload = response.json()
        message = str(payload.get("message", response.text))
        data = payload.get("data")
        return message, data
    except Exception:
        return response.text, None


def raise_api_error(exc: httpx.HTTPStatusError) -> None:
    message, data = extract_payload(exc.response)
    status = exc.response.status_code

    # TODO: check usage
    if status == 403:
        raise ForbiddenError(message, data) from exc
    if status == 404:
        raise NotFoundError(message, data) from exc
    if status == 409:
        raise ConflictError(message, data) from exc
    if status == 422:
        raise ValidationError(message, data) from exc
    if status == 501:
        raise BadGatewayError(message, data) from exc
    if status in (502, 503, 504):
        raise TemporaryUnavailableError(message, data)

    raise InternalApiRequestError(message, data) from exc


class InternalApiClient:
    def __init__(
        self,
        base_url: str,
        timeout: float,
        retries: int = 2,
        retry_delay: float = 0.5,
    ) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=httpx.Timeout(timeout),
        )
        self._retries = retries
        self._retry_delay = retry_delay

    async def close(self) -> None:
        await self._client.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        json_data: dict | None = None,
    ) -> dict:
        last_error: Exception | None = None

        for attempt in range(self._retries + 1):
            try:
                response = await self._client.request(
                    method,
                    path,
                    params=params,
                    json=json_data,
                )
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as exc:
                try:
                    raise_api_error(exc)
                except TemporaryUnavailableError as unavailable_exc:
                    last_error = unavailable_exc
                except Exception:
                    raise

            except httpx.ConnectError:
                last_error = InternalApiConnectionError(
                    "Failed to connect to internal API"
                )

            except httpx.TimeoutException:
                last_error = InternalApiTimeoutError("Internal API request timed out")

            if attempt < self._retries:
                await asyncio.sleep(self._retry_delay)

        assert last_error is not None
        raise last_error

    async def get(self, path: str, params: dict | None = None) -> dict:
        return await self._request("GET", path, params=params)

    async def post(self, path: str, json_data: dict | None = None) -> dict:
        return await self._request("POST", path, json_data=json_data)

    async def patch(self, path: str, json_data: dict | None = None) -> dict:
        return await self._request("PATCH", path, json_data=json_data)

    async def delete(self, path: str, json_data: dict | None = None) -> dict:
        return await self._request("DELETE", path, json_data=json_data)


client = InternalApiClient(
    config.orchestrator.base_url,
    config.orchestrator.timeout,
    config.orchestrator.retries,
    config.orchestrator.retry_delay,
)
