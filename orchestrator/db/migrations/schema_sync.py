from loguru import logger

from orchestrator.db.migrations.utils import get_column_length, get_vector_dimension
from orchestrator.db.models import Question


def _build_schema_mismatch_error(mismatches: list[str]) -> RuntimeError:
    lines = [
        "Database schema does not match runtime DB_SCHEMA constraints.",
        "Apply migrations: `alembic upgrade head`.",
        "Detected mismatches:",
    ]
    lines.extend(f"- {mismatch}" for mismatch in mismatches)
    return RuntimeError("\n".join(lines))


async def ensure_schema_constraints(
    question_text_max_len: int,
    answer_text_max_len: int,
    embedding_dim: int,
):
    logger.debug("Checking schema constraints")

    mismatches: list[str] = []

    checks = [
        (Question.question_text, question_text_max_len),
        (Question.answer_text, answer_text_max_len),
    ]

    for column_attr, expected_max_len in checks:
        column_name: str = column_attr.property.columns[0].name
        current_max_len = await get_column_length(column_attr)
        if current_max_len is None:
            mismatches.append(
                f"questions.{column_name}: column missing in DB, expected VARCHAR({expected_max_len})"
            )
            continue

        if current_max_len != expected_max_len:
            mismatches.append(
                f"questions.{column_name}: db VARCHAR({current_max_len}), expected VARCHAR({expected_max_len})"
            )

    current_embedding_dim = await get_vector_dimension(Question.embedding)
    if current_embedding_dim is None:
        mismatches.append(
            f"questions.embedding: column/type missing in DB, expected vector({embedding_dim})"
        )
    elif current_embedding_dim != embedding_dim:
        mismatches.append(
            f"questions.embedding: db vector({current_embedding_dim}), expected vector({embedding_dim})"
        )

    if mismatches:
        raise _build_schema_mismatch_error(mismatches)

    logger.debug("Schema constraints are up to date")
