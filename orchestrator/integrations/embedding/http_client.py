from orchestrator.core.config import config
from shared.http.client import InternalApiClient

embedding_http_client = InternalApiClient(
    timeout=config.embedding_http.timeout,
    retries=config.embedding_http.retries,
    retry_delay=config.embedding_http.retry_delay,
)


async def close_embedding_http_client() -> None:
    await embedding_http_client.close()
