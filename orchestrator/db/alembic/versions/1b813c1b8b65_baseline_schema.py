"""baseline_schema

Revision ID: 1b813c1b8b65
Revises:
Create Date: 2026-04-05 15:36:06.695391

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "1b813c1b8b65"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    if op.get_context().as_sql:
        return False

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return inspector.has_table(table_name)


def _index_exists(table_name: str, index_name: str) -> bool:
    if op.get_context().as_sql:
        return False

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return any(
        index["name"] == index_name for index in inspector.get_indexes(table_name)
    )


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    if not _table_exists("users"):
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("telegram_id", sa.BigInteger(), nullable=False),
            sa.Column("username", sa.String(length=32), nullable=True),
            sa.Column("role", sa.String(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )

    users_indexes = [
        ("ix_users_telegram_id", ["telegram_id"], True),
        ("ix_users_username", ["username"], True),
        ("ix_users_role", ["role"], False),
    ]

    for index_name, columns, unique in users_indexes:
        if not _index_exists("users", index_name):
            op.create_index(index_name, "users", columns, unique=unique)

    if not _table_exists("questions"):
        op.create_table(
            "questions",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("question_text", sa.String(length=384), nullable=False),
            sa.Column("answer_text", sa.String(length=384), nullable=False),
            sa.Column(
                "rating", sa.Float(), server_default=sa.text("0.0"), nullable=False
            ),
            sa.Column("embedding", Vector(dim=256), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade() -> None:
    """Downgrade schema."""
    if _table_exists("questions"):
        op.drop_table("questions")

    if _table_exists("users"):
        op.drop_table("users")
