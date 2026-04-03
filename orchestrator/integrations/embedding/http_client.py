from orchestrator.core.config import config
from shared.api.client import ApiClient

embedding_http_client = ApiClient(config.clients.embedding)


async def close_embedding_http_client() -> None:
    await embedding_http_client.close()
