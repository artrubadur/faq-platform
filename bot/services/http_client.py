from bot.core.config import config
from shared.http.client import InternalApiClient

orchestrator_client = InternalApiClient(
    base_url=config.orchestrator.base_url,
    timeout=config.orchestrator.timeout,
    retries=config.orchestrator.retries,
    retry_delay=config.orchestrator.retry_delay,
)


async def close_orchestrator_client() -> None:
    await orchestrator_client.close()
