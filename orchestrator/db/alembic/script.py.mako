"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
% if not (embedding_not_null and new_q_len is None and new_a_len is None and new_dim is None):
import sqlalchemy as sa
% endif
% if new_dim is not None:
from pgvector.sqlalchemy import Vector
% endif
${imports if imports else ""}

% if new_q_len is not None:
NEW_Q_LEN = ${new_q_len}
% endif
% if old_q_len is not None:
OLD_Q_LEN = ${old_q_len}
% endif
% if new_a_len is not None:
NEW_A_LEN = ${new_a_len}
% endif
% if old_a_len is not None:
OLD_A_LEN = ${old_a_len}
% endif
% if new_dim is not None:
NEW_DIM = ${new_dim}
% endif

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, Sequence[str], None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    """Upgrade schema."""
% if new_q_len is not None:
    op.alter_column(
        "questions",
        "question_text",
        type_=sa.String(length=NEW_Q_LEN),
    )
% endif
% if new_a_len is not None:
    op.alter_column(
        "questions",
        "answer_text",
        type_=sa.String(length=NEW_A_LEN),
    )
% endif
% if new_dim is not None:
    # Recreate embedding column for the new vector dimension.
    # Then run recompute script and set NOT NULL in a follow-up migration.
    op.drop_column("questions", "embedding")
    op.add_column(
        "questions",
        sa.Column("embedding", Vector(dim=NEW_DIM), nullable=True),
    )
% endif
% if embedding_not_null:
    op.alter_column(
        "questions",
        "embedding",
        nullable=False,
    )
% endif
% if new_q_len is None and new_a_len is None and new_dim is None and not embedding_not_null:
    ${upgrades if upgrades else "pass"}
% endif


def downgrade() -> None:
    """Downgrade schema."""
% if new_dim is not None or embedding_not_null:
    raise NotImplementedError(
        "Auto-generated downgrade is not available for template -x embedding revisions. "
        "Create manual downgrade if required."
    )
% elif new_q_len is not None or new_a_len is not None:
% if (new_q_len is not None and old_q_len is None) or (new_a_len is not None and old_a_len is None):
    raise NotImplementedError(
        "Downgrade for -x new_q_len/new_a_len requires -x old_q_len/-x old_a_len "
        "when revision file is generated."
    )
% else:
% if new_q_len is not None:
    op.alter_column(
        "questions",
        "question_text",
        type_=sa.String(length=OLD_Q_LEN),
    )
% endif
% if new_a_len is not None:
    op.alter_column(
        "questions",
        "answer_text",
        type_=sa.String(length=OLD_A_LEN),
    )
% endif
% endif
% else:
    ${downgrades if downgrades else "pass"}
% endif
