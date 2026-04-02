import asyncio

from loguru import logger

from bot.main import startup
from shared.logging.setup import setup_logging


def main() -> None:
    logging_status = setup_logging()
    logger.info(logging_status)
    try:
        asyncio.run(startup())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
