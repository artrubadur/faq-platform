from orchestrator.core.config import config
from shared.api.client import ApiClient

if config.suggestion.rerank:
    rerank_http_client: ApiClient | None = ApiClient(config.rerank_client)
else:
    rerank_http_client = None


async def close_rerank_http_client() -> None:
    if rerank_http_client is not None:
        await rerank_http_client.close()
