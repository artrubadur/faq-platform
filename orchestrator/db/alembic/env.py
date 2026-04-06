import asyncio
import io
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

import orchestrator.db.models  # noqa: F401
from orchestrator.core.config import config as app_config
from orchestrator.db.base import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _build_database_url() -> str:
    return (
        "postgresql+asyncpg://"
        f"{app_config.db.user}:{app_config.db.password}"
        f"@{app_config.db.host}:5432/{app_config.db.name}"
    )


config.set_main_option("sqlalchemy.url", _build_database_url())

target_metadata = Base.metadata


def _to_int_or_none(raw_value: str | None, *, key_name: str) -> int | None:
    if raw_value is None:
        return None
    try:
        return int(raw_value)
    except ValueError as exc:
        raise ValueError(
            f"Invalid -x {key_name}={raw_value!r}. Expected integer value."
        ) from exc


def _to_bool_flag(raw_value: str | None, *, key_name: str) -> bool:
    if raw_value is None:
        return False
    if raw_value == "":
        return True

    normalized_value = raw_value.strip().lower()
    if normalized_value in {"1", "true", "yes", "on"}:
        return True
    if normalized_value in {"0", "false", "no", "off"}:
        return False

    raise ValueError(
        f"Invalid -x {key_name}={raw_value!r}. Expected flag or boolean value."
    )


def _build_template_args() -> dict[str, int | bool | None]:
    x_args = context.get_x_argument(as_dictionary=True)
    template_args: dict[str, int | bool | None] = {
        "old_q_len": _to_int_or_none(x_args.get("old_q_len"), key_name="old_q_len"),
        "new_q_len": _to_int_or_none(x_args.get("new_q_len"), key_name="new_q_len"),
        "old_a_len": _to_int_or_none(x_args.get("old_a_len"), key_name="old_a_len"),
        "new_a_len": _to_int_or_none(x_args.get("new_a_len"), key_name="new_a_len"),
        "new_dim": _to_int_or_none(x_args.get("new_dim"), key_name="new_dim"),
        "embedding_not_null": _to_bool_flag(
            x_args.get("embedding_not_null"),
            key_name="embedding_not_null",
        ),
    }
    _validate_template_args(template_args)
    return template_args


def _validate_template_args(template_args: dict[str, int | bool | None]) -> None:
    old_q_len = template_args.get("old_q_len")
    new_q_len = template_args.get("new_q_len")
    old_a_len = template_args.get("old_a_len")
    new_a_len = template_args.get("new_a_len")

    if old_q_len is not None and new_q_len is None:
        raise ValueError(
            "Invalid -x arguments: old_q_len requires new_q_len. "
            "Use -x old_q_len=<old> -x new_q_len=<new>."
        )
    if old_a_len is not None and new_a_len is None:
        raise ValueError(
            "Invalid -x arguments: old_a_len requires new_a_len. "
            "Use -x old_a_len=<old> -x new_a_len=<new>."
        )


def _is_plain_revision_command() -> bool:
    cmd_opts = getattr(config, "cmd_opts", None)
    if cmd_opts is None:
        return False

    has_revision_message = getattr(cmd_opts, "message", None) is not None
    is_autogenerate = bool(getattr(cmd_opts, "autogenerate", False))
    return has_revision_message and not is_autogenerate


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        template_args=_build_template_args(),
    )

    with context.begin_transaction():
        context.run_migrations()


def run_plain_revision_without_db() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        as_sql=True,
        output_buffer=io.StringIO(),
        compare_type=False,
        template_args=_build_template_args(),
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        template_args=_build_template_args(),
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
elif _is_plain_revision_command():
    run_plain_revision_without_db()
else:
    asyncio.run(run_migrations_online())
