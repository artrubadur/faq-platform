"""split_questions_and_formulations

Revision ID: 7a6a4ef0f89d
Revises: 1b813c1b8b65
Create Date: 2026-04-11 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "7a6a4ef0f89d"
down_revision: Union[str, Sequence[str], None] = "1b813c1b8b65"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    if op.get_context().as_sql:
        return False

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return inspector.has_table(table_name)


def _column_exists(table_name: str, column_name: str) -> bool:
    if op.get_context().as_sql:
        return False

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table(table_name):
        return False

    return any(col["name"] == column_name for col in inspector.get_columns(table_name))


def _index_exists(table_name: str, index_name: str) -> bool:
    if op.get_context().as_sql:
        return False

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table(table_name):
        return False

    return any(
        index["name"] == index_name for index in inspector.get_indexes(table_name)
    )


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    if not _table_exists("formulations"):
        op.create_table(
            "formulations",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("question_id", sa.Integer(), nullable=False),
            sa.Column("question_text", sa.String(length=384), nullable=False),
            sa.Column("embedding", Vector(dim=256), nullable=False),
            sa.ForeignKeyConstraint(
                ["question_id"],
                ["questions.id"],
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _index_exists("formulations", "ix_formulations_question_id"):
        op.create_index(
            "ix_formulations_question_id",
            "formulations",
            ["question_id"],
            unique=False,
        )

    if _column_exists("questions", "embedding"):
        op.execute(
            """
            INSERT INTO formulations (question_id, question_text, embedding)
            SELECT q.id, q.question_text, q.embedding
            FROM questions q
            LEFT JOIN formulations aq
              ON aq.question_id = q.id AND aq.question_text = q.question_text
            WHERE q.embedding IS NOT NULL AND aq.id IS NULL
            """
        )
        op.drop_column("questions", "embedding")


def downgrade() -> None:
    """Downgrade schema."""
    if _table_exists("questions") and not _column_exists("questions", "embedding"):
        op.add_column(
            "questions",
            sa.Column("embedding", Vector(dim=256), nullable=True),
        )

    if _table_exists("questions") and _table_exists("formulations"):
        op.execute(
            """
            UPDATE questions AS q
            SET embedding = a.embedding
            FROM (
              SELECT DISTINCT ON (question_id)
                question_id,
                embedding
              FROM formulations
              ORDER BY question_id, id
            ) AS a
            WHERE q.id = a.question_id
            """
        )

    if _table_exists("formulations"):
        op.drop_table("formulations")
