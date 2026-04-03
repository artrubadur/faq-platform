from orchestrator.core.config import config
from shared.api.client import ApiClient

if config.suggestion.compose.enabled:
    compose_http_client: ApiClient | None = ApiClient(config.clients.compose)
else:
    compose_http_client = None


async def close_compose_http_client() -> None:
    if compose_http_client is not None:
        await compose_http_client.close()
