from orchestrator.core.config import config
from shared.api.client import ApiClient

if config.suggestion.rerank.enabled:
    rerank_http_client: ApiClient | None = ApiClient(config.clients.rerank)
else:
    rerank_http_client = None


async def close_rerank_http_client() -> None:
    if rerank_http_client is not None:
        await rerank_http_client.close()
