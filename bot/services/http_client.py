from bot.core.config import config
from shared.http.client import InternalApiClient

orchestrator_client = InternalApiClient(
    base_url=config.orchestrator_client.base_url,
    timeout=config.orchestrator_client.timeout,
    retries=config.orchestrator_client.retries,
    retry_delay=config.orchestrator_client.retry_delay,
)


async def close_orchestrator_client() -> None:
    await orchestrator_client.close()
