from orchestrator.core.config import config
from shared.http.client import InternalApiClient

embedding_http_client = InternalApiClient(
    timeout=config.orchestrator.timeout,
    retries=config.orchestrator.retries,
    retry_delay=config.orchestrator.retry_delay,
)


async def close_embedding_http_client() -> None:
    await embedding_http_client.close()
