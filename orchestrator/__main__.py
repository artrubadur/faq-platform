import uvicorn
from loguru import logger

from orchestrator.core.config import config
from shared.logging.setup import setup_logging


def main() -> None:
    logging_status = setup_logging()
    logger.info(logging_status)
    uvicorn.run(
        "orchestrator.main:app",
        host=config.api.host,
        port=config.api.port,
        log_config=None,
    )


if __name__ == "__main__":
    main()
