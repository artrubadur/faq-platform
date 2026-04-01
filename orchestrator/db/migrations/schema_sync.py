from loguru import logger
from sqlalchemy import func, inspect, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from orchestrator.db.models import Question
from orchestrator.db.session import engine
from orchestrator.integrations.embedding.provider import embedding_provider


async def _find_rows_exceeding_length(
    column: InstrumentedAttribute[str],
    new_max_len: int,
) -> list[tuple[int, int]]:
    lengths_sq = select(
        Question.id.label("id"),
        func.length(column).label("value_length"),
    ).subquery()
    query = select(lengths_sq.c.id, lengths_sq.c.value_length).where(
        lengths_sq.c.value_length > new_max_len
    )

    async with engine.connect() as conn:
        result = await conn.execute(query)
        rows = result.all()

    return [(int(row.id), int(row.value_length)) for row in rows]


async def _adjusting_varchar_length(
    column: InstrumentedAttribute[str], current_max_len: int, expected_max_len: int
):
    if expected_max_len < current_max_len:
        invalid_rows = await _find_rows_exceeding_length(column, expected_max_len)
        if len(invalid_rows) > 0:
            rows_str = ", ".join(
                f"{row_id}:{value_length}" for row_id, value_length in invalid_rows
            )
            raise RuntimeError(
                f"Cannot shrink 'questions.{column}' to {expected_max_len}. "
                "Rows exceeding the new limit (id:length): "
                f"{rows_str}"
            )

    async with engine.begin() as conn:
        await conn.execute(
            text(
                f"ALTER TABLE questions ALTER COLUMN {column.property.columns[0].name} TYPE VARCHAR({expected_max_len})"
            )
        )


async def _recompute_embeddings_to_temp_column(embedding_dim: int) -> None:
    async with engine.begin() as conn:
        await conn.execute(text("ALTER TABLE questions DROP COLUMN embedding"))
        await conn.execute(
            text(f"ALTER TABLE questions ADD COLUMN embedding vector({embedding_dim})")
        )

        session = AsyncSession(bind=conn, expire_on_commit=False)
        try:
            result = await session.execute(select(Question).order_by(Question.id))
            questions = result.scalars().all()

            for question in questions:
                embedding = await embedding_provider.compute_embedding(
                    question.question_text
                )
                if len(embedding) != embedding_dim:
                    raise RuntimeError(
                        "Embedding provider returned invalid vector length during migration. "
                        f"Expected {embedding_dim}, got {len(embedding)} for question id={question.id}."
                    )

                question.embedding = embedding

            await session.flush()
        finally:
            await session.close()

    logger.warning("Automatic embedding backfill finished successfully")


async def _is_questions_empty() -> bool:
    async with engine.connect() as conn:
        first_question_id = await conn.scalar(select(Question.id).limit(1))
    return first_question_id is None


def _read_column_type_attr(
    sync_conn,
    table_name: str,
    column_name: str,
    type_attr: str,
):
    db_col = next(
        (
            c
            for c in inspect(sync_conn).get_columns(table_name)
            if c["name"] == column_name
        ),
        None,
    )
    return getattr(db_col["type"], type_attr, None) if db_col else None


async def _get_vector_dimension(column: InstrumentedAttribute) -> int | None:
    sa_col = column.property.columns[0]

    async with engine.connect() as conn:
        return await conn.run_sync(
            _read_column_type_attr,
            sa_col.table.name,
            sa_col.name,
            "dim",
        )


async def _get_column_length(column: InstrumentedAttribute[str]) -> int | None:
    sa_col = column.property.columns[0]

    async with engine.connect() as conn:
        return await conn.run_sync(
            _read_column_type_attr,
            sa_col.table.name,
            sa_col.name,
            "length",
        )


async def ensure_schema_constraints(
    question_text_max_len: int, answer_text_max_len: int, embedding_dim: int
):
    logger.debug("Checking schema constraints")

    checks = [
        (Question.question_text, question_text_max_len),
        (Question.answer_text, answer_text_max_len),
    ]

    for column_attr, expected_max_len in checks:
        column_name: str = column_attr.property.columns[0].name
        current_max_len = await _get_column_length(column_attr)
        if current_max_len is None or current_max_len == expected_max_len:
            continue

        logger.warning(
            "Adjusting varchar length to match schema constants",
            table="questions",
            column=column_name,
            db=current_max_len,
            expected=expected_max_len,
        )
        await _adjusting_varchar_length(column_attr, current_max_len, expected_max_len)

    current_embedding_dim = await _get_vector_dimension(Question.embedding)
    if current_embedding_dim is None:
        return

    if current_embedding_dim == embedding_dim:
        logger.debug("Schema constraints are up to date")
        return

    if await _is_questions_empty():
        logger.warning(
            "Adjusting embedding dimension to match schema constants",
            table="questions",
            column="embedding",
            db=current_embedding_dim,
            expected=embedding_dim,
        )
        async with engine.begin() as conn:
            await conn.execute(
                text(
                    f"ALTER TABLE questions ALTER COLUMN embedding TYPE vector({embedding_dim})"
                )
            )
        return

    logger.warning(
        "Embedding dimension mismatch detected; starting auto-recompute migration",
        db=current_embedding_dim,
        expected=embedding_dim,
    )
    await _recompute_embeddings_to_temp_column(embedding_dim)
