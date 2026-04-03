from bot.core.config import config
from shared.api.client import ApiClient

orchestrator_client = ApiClient(config.orchestrator_client)


async def close_orchestrator_client() -> None:
    await orchestrator_client.close()
