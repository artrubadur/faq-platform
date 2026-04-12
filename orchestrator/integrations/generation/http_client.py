from orchestrator.core.config import config
from shared.api.client import ApiClient

if config.suggestion.generation.enabled:
    generation_http_client: ApiClient | None = ApiClient(config.clients.generation)
else:
    generation_http_client = None


async def close_generation_http_client() -> None:
    if generation_http_client is not None:
        await generation_http_client.close()
