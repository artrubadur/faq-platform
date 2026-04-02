from orchestrator.core.config import config
from shared.http.client import InternalApiClient

if config.suggestion.rerank:
    rerank_http_client: InternalApiClient | None = InternalApiClient(
        timeout=config.rerank_http.timeout,
        retries=config.rerank_http.retries,
        retry_delay=config.rerank_http.retry_delay,
    )
else:
    rerank_http_client = None


async def close_rerank_http_client() -> None:
    if rerank_http_client is not None:
        await rerank_http_client.close()
