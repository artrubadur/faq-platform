from loguru import logger

from bot.main import run
from shared.logging.setup import setup_logging


def main() -> None:
    logging_status = setup_logging()
    logger.info(logging_status)
    try:
        run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
