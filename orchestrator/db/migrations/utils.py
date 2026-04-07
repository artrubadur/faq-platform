from sqlalchemy import inspect
from sqlalchemy.orm import InstrumentedAttribute

from orchestrator.db.session import engine


def _read_column_type_attr(
    sync_conn,
    table_name: str,
    column_name: str,
    type_attr: str,
):
    inspector = inspect(sync_conn)
    if not inspector.has_table(table_name):
        return None

    db_col = next(
        (c for c in inspector.get_columns(table_name) if c["name"] == column_name),
        None,
    )
    return getattr(db_col["type"], type_attr, None) if db_col else None


async def get_vector_dimension(column: InstrumentedAttribute) -> int | None:
    sa_col = column.property.columns[0]

    async with engine.connect() as conn:
        return await conn.run_sync(
            _read_column_type_attr,
            sa_col.table.name,
            sa_col.name,
            "dim",
        )


async def get_column_length(column: InstrumentedAttribute[str]) -> int | None:
    sa_col = column.property.columns[0]

    async with engine.connect() as conn:
        return await conn.run_sync(
            _read_column_type_attr,
            sa_col.table.name,
            sa_col.name,
            "length",
        )
