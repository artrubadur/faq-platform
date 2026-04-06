from alembic.config import Config as AlembicConfig
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from loguru import logger
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncConnection

_ALEMBIC_INI_PATH = "alembic.ini"


def _get_alembic_config() -> AlembicConfig:
    return AlembicConfig(_ALEMBIC_INI_PATH)


def _get_expected_heads() -> tuple[str, ...]:
    script = ScriptDirectory.from_config(_get_alembic_config())
    return tuple(script.get_heads())


def _get_current_heads(sync_conn: Connection) -> tuple[str, ...]:
    migration_context = MigrationContext.configure(sync_conn)
    return tuple(migration_context.get_current_heads())


def _build_outdated_schema_error(
    expected_heads: tuple[str, ...],
    current_heads: tuple[str, ...],
) -> RuntimeError:
    expected_str = ", ".join(expected_heads) if expected_heads else "<none>"
    current_str = ", ".join(current_heads) if current_heads else "<none>"

    stamp_target = "head" if len(expected_heads) == 1 else "heads"

    message_lines = [
        "Database revision is out of date.",
        f"Expected Alembic head(s): {expected_str}.",
        f"Current DB head(s): {current_str}.",
        "Apply migrations: `alembic upgrade head`.",
    ]

    if not current_heads:
        message_lines.extend(
            [
                "If this database was created before Alembic and schema already matches,",
                f"run one-time baseline: `alembic stamp {stamp_target}`.",
            ]
        )

    return RuntimeError("\n".join(message_lines))


async def ensure_database_revision_is_up_to_date(connection: AsyncConnection) -> None:
    expected_heads = _get_expected_heads()
    current_heads = await connection.run_sync(_get_current_heads)

    if set(current_heads) != set(expected_heads):
        raise _build_outdated_schema_error(expected_heads, current_heads)

    logger.debug(
        "Alembic revision is up to date",
        heads=current_heads,
    )
