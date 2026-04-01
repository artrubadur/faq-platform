import asyncio

from bot.main import startup
from shared.logging.setup import setup_logging


def main() -> None:
    setup_logging()
    try:
        asyncio.run(startup())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
