import asyncio
from typing import TypeVar

import httpx
from pydantic import BaseModel, ConfigDict, Field

from shared.api.exceptions import (
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

    if status == 403:
        raise ForbiddenError(message, data) from exc
    if status == 404:
        raise NotFoundError(message, data) from exc
    if status == 409:
        raise ConflictError(message, data) from exc
    if status == 422:
        raise ValidationError(message, data) from exc
    if status == 502:
        raise BadGatewayError(message, data) from exc
    if status in (502, 503, 504):
        raise TemporaryUnavailableError(message, data)

    raise InternalApiRequestError(message, data) from exc


class ApiClientConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    base_url: str | None = None
    timeout: float = Field(default=5.0, gt=0)
    retries: int = Field(default=2, ge=0)
    retry_delay: float = Field(default=0.5, ge=0)


class ApiClient:
    def __init__(
        self,
        config: ApiClientConfig,
    ) -> None:
        client_kwargs: dict = {
            "timeout": httpx.Timeout(config.timeout),
        }
        if config.base_url is not None:
            client_kwargs["base_url"] = config.base_url

        self._client = httpx.AsyncClient(**client_kwargs)
        self._retries = config.retries
        self._retry_delay = config.retry_delay

    async def close(self) -> None:
        await self._client.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        *,
        headers: dict | None = None,
        params: dict | None = None,
        json_data: dict | None = None,
    ) -> dict | list:

        last_error: Exception = InternalApiRequestError("You'll never see me")

        for attempt in range(self._retries + 1):
            try:
                response = await self._client.request(
                    method,
                    path,
                    headers=headers,
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

        raise last_error

    async def request(
        self,
        method: str,
        path: str,
        *,
        headers: dict | None = None,
        params: dict | None = None,
        json_data: dict | None = None,
    ) -> dict | list:
        return await self._request(
            method,
            path,
            headers=headers,
            params=params,
            json_data=json_data,
        )

    async def get(self, path: str, params: dict | None = None) -> dict | list:
        return await self._request("GET", path, params=params)

    async def post(self, path: str, json_data: dict | None = None) -> dict | list:
        return await self._request("POST", path, json_data=json_data)

    async def put(self, path: str, json_data: dict | None = None) -> dict | list:
        return await self._request("PUT", path, json_data=json_data)

    async def patch(self, path: str, json_data: dict | None = None) -> dict | list:
        return await self._request("PATCH", path, json_data=json_data)

    async def delete(self, path: str, json_data: dict | None = None) -> dict | list:
        return await self._request("DELETE", path, json_data=json_data)
