import uvicorn

from orchestrator.core.config import config
from shared.logging.setup import setup_logging


def main() -> None:
    setup_logging()
    uvicorn.run(
        "orchestrator.main:app",
        host=config.api.host,
        port=config.api.port,
        log_config=None,
    )


if __name__ == "__main__":
    main()
