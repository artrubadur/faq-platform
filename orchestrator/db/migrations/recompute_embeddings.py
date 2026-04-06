import argparse
import asyncio

from loguru import logger
from sqlalchemy import select, update

from orchestrator.core.config import config
from orchestrator.db.migrations.utils import get_vector_dimension
from orchestrator.db.models.question import Question
from orchestrator.db.session import engine
from shared.logging.setup import setup_logging


async def _fetch_questions_batch(last_id: int, limit: int) -> list[tuple[int, str]]:
    query = (
        select(Question.id, Question.question_text)
        .where(Question.id > last_id)
        .order_by(Question.id)
        .limit(limit)
    )

    async with engine.connect() as conn:
        result = await conn.execute(query)
        rows = result.all()

    return [(int(row.id), str(row.question_text)) for row in rows]


async def _update_embeddings_batch(updates: list[tuple[int, list[float]]]) -> None:
    if not updates:
        return

    async with engine.begin() as conn:
        for question_id, embedding in updates:
            await conn.execute(
                update(Question)
                .where(Question.id == question_id)
                .values(embedding=embedding)
            )


async def recompute_all_embeddings(batch_size: int, start_id: int) -> None:
    from orchestrator.integrations.embedding import embedding_provider

    embedding_dim = config.db_schema.question_embedding_dim
    current_embedding_dim = await get_vector_dimension(Question.embedding)

    if current_embedding_dim is None:
        raise RuntimeError(
            "questions.embedding: column/type missing in DB, "
            f"expected vector({embedding_dim})"
        )
    if current_embedding_dim != embedding_dim:
        raise RuntimeError(
            "Embedding dimension mismatch before recompute: "
            f"db vector({current_embedding_dim}), expected vector({embedding_dim})\n"
            "Apply migrations: `alembic upgrade head`."
        )

    logger.info(
        "Recomputing all embeddings in questions.embedding",
        batch_size=batch_size,
        start_id=start_id,
        embedding_dim=embedding_dim,
    )

    processed = 0
    last_id = start_id

    while True:
        batch = await _fetch_questions_batch(last_id=last_id, limit=batch_size)
        if not batch:
            break

        updates: list[tuple[int, list[float]]] = []
        for question_id, question_text in batch:
            embedding = await embedding_provider.compute_embedding(question_text)
            if len(embedding) != embedding_dim:
                raise RuntimeError(
                    "Embedding provider returned invalid vector length during recompute. "
                    f"Expected {embedding_dim}, got {len(embedding)} for question id={question_id}."
                )

            updates.append((question_id, embedding))
            last_id = question_id
            processed += 1

        await _update_embeddings_batch(updates)
        logger.info(
            "Embedding recompute progress", processed=processed, last_id=last_id
        )

    logger.info("Embedding recompute completed successfully", processed=processed)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Recompute all question embeddings in questions.embedding."
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Rows per batch (default: 100).",
    )
    parser.add_argument(
        "--start-id",
        type=int,
        default=0,
        help="Start from questions with id > value (default: 0).",
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if args.batch_size <= 0:
        parser.error("--batch-size must be greater than 0")
    if args.start_id < 0:
        parser.error("--start-id must be greater than or equal to 0")

    logger.info(setup_logging())
    try:
        asyncio.run(
            recompute_all_embeddings(
                batch_size=args.batch_size,
                start_id=args.start_id,
            )
        )
    except Exception:
        logger.exception("Embedding recompute failed")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
