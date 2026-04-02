import logging
import sys
from pathlib import Path

import yaml
from loguru import logger

from shared.logging.filter import DuplicateFilter, make_duplicate_patch
from shared.utils.log import serialize_json

LOGGING_PATH = Path("config/logging.yml")


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # type: ignore
            frame = frame.f_back  # type: ignore
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).patch(
            lambda r: r.update(name=record.name)
        ).log(level, record.getMessage())


def setup_logging():
    config = {}

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    if not LOGGING_PATH.exists() or not LOGGING_PATH.is_file():
        return f"No logging configuration loaded: File {str(LOGGING_PATH)} does not exist. Falling back to the default."

    with open(LOGGING_PATH, "r") as f:
        config = yaml.safe_load(f)

    logger.remove()

    cached_limit = config.pop("cached_limit", 0)
    repeat_limit = config.pop("repeat_limit", 2)
    handlers = config.get("handlers", [])

    if cached_limit > 0:
        duplicate_filter = DuplicateFilter(cached_limit, repeat_limit)
        duplicate_patch = make_duplicate_patch(duplicate_filter)
        logger.configure(patcher=duplicate_patch)
        for handler in handlers:
            handler["filter"] = duplicate_filter

    for h in handlers:
        raw_sink = h.pop("sink")

        if raw_sink == "ext://sys.stdout":
            h["sink"] = sys.stdout
        elif raw_sink == "ext://sys.stderr":
            h["sink"] = sys.stderr
        else:
            h["sink"] = raw_sink

        is_json = h.pop("json", False)
        if is_json:
            h["format"] = serialize_json

        logger.add(**h, backtrace=True, diagnose=False)

    return f"Logging configuration has been loaded from {str(LOGGING_PATH)}"
