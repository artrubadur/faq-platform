import logging
import sys
from pathlib import Path
from typing import Any, Callable

import yaml
from loguru import logger

from shared.logging.filter import DuplicateFilter, make_duplicate_patch
from shared.utils.log import serialize_json

LOGGING_PATH = Path("config/logging.yml")
STREAM_SINKS = {"ext://sys.stdout": sys.stdout, "ext://sys.stderr": sys.stderr}
RecordFilter = Callable[[dict[str, Any]], bool]


def _level_no(level: Any) -> int:
    if isinstance(level, int):
        return level

    if isinstance(level, str):
        try:
            return logger.level(level).no
        except ValueError:
            try:
                return int(level)
            except ValueError as exc:
                raise ValueError(f"Invalid logging level: {level}") from exc

    raise ValueError(f"Invalid logging level type: {type(level).__name__}")


def _parse_activation_rules(raw_rules: Any) -> list[tuple[str, bool | int]]:
    if not raw_rules:
        return []

    if isinstance(raw_rules, dict):
        return [
            (str(name), level if isinstance(level, bool) else _level_no(level))
            for name, level in raw_rules.items()
        ]

    rules: list[tuple[str, bool | int]] = []
    for rule in raw_rules:
        if not isinstance(rule, (list, tuple)) or len(rule) != 2:
            raise ValueError(f"Activation rule must contain 2 items, got: {rule}")
        name, level = rule
        resolved_level = level if isinstance(level, bool) else _level_no(level)
        rules.append((str(name), resolved_level))
    return rules


def _build_activation_filter(
    rules: list[tuple[str, bool | int]],
) -> RecordFilter | None:
    if not rules:
        return None

    def activation_filter(record: dict[str, Any]) -> bool:
        record_name = record.get("name") or ""
        matched_rule: bool | int | None = None
        matched_prefix_len = -1

        for rule_name, rule_level in rules:
            is_match = (
                rule_name == ""
                or record_name == rule_name
                or record_name.startswith(f"{rule_name}.")
            )
            if is_match and len(rule_name) > matched_prefix_len:
                matched_prefix_len = len(rule_name)
                matched_rule = rule_level

        if matched_rule is None:
            return True
        if isinstance(matched_rule, bool):
            return matched_rule
        return record["level"].no >= matched_rule

    return activation_filter


def _combine_filters(base_filter: Any, extra_filter: RecordFilter | None):
    if extra_filter is None:
        return base_filter
    if base_filter is None:
        return extra_filter
    if callable(base_filter):
        return lambda record: base_filter(record) and extra_filter(record)
    raise ValueError(
        "Only callable handler filters are supported when "
        "'cached_limit' or 'activation' are configured."
    )


def _prepare_handlers(
    handlers: list[dict[str, Any]],
    extra_filter: RecordFilter | None,
) -> None:
    for handler in handlers:
        handler["sink"] = STREAM_SINKS.get(handler["sink"], handler["sink"])
        if handler.pop("json", False):
            handler["format"] = serialize_json
        handler.setdefault("backtrace", True)
        handler.setdefault("diagnose", False)
        if extra_filter is not None:
            handler["filter"] = _combine_filters(handler.get("filter"), extra_filter)


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).patch(
            lambda r: r.update(name=record.name)
        ).log(level, record.getMessage())


def setup_logging():
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    if not LOGGING_PATH.is_file():
        return (
            "No logging configuration loaded: "
            f"File {LOGGING_PATH} does not exist. Falling back to the default."
        )

    config = yaml.safe_load(LOGGING_PATH.read_text(encoding="utf-8")) or {}
    logger.remove()

    cached_limit = config.pop("cached_limit", 0)
    repeat_limit = config.pop("repeat_limit", 2)
    duplicate_filter = (
        DuplicateFilter(cached_limit, repeat_limit) if cached_limit > 0 else None
    )
    activation_filter = _build_activation_filter(
        _parse_activation_rules(config.pop("activation", []))
    )

    handlers = config.get("handlers", [])
    _prepare_handlers(handlers, _combine_filters(duplicate_filter, activation_filter))  # type: ignore

    config["handlers"] = handlers
    if duplicate_filter is not None:
        config["patcher"] = make_duplicate_patch(duplicate_filter)

    logger.configure(**config)
    return f"Logging configuration has been loaded from {LOGGING_PATH}"
