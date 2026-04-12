# Database Migrations (Alembic)

Practical guide for creating/applying migrations, running them in Docker, and
keeping runtime config in sync.

## Core Rules

- Create revision files on host (not inside `docker compose run --rm ...`).
- If you apply migrations in Docker, rebuild `orchestrator` image after adding a new revision file.
- `-x` flags must be placed before `revision`.
- After schema changes, sync related values in `env/orchestrator.env` and `env/bot.env`.

## Where State Lives

- Migration files: `orchestrator/db/alembic/versions/*.py`
- Current DB revision pointer: table `alembic_version`
- Revision chain: each migration file links to previous one via `down_revision`

## Command Reference

Local:

```bash
poetry run alembic revision -m "describe_change"
poetry run alembic revision --autogenerate -m "describe_change"
poetry run alembic upgrade head
poetry run alembic current
poetry run alembic history
poetry run alembic downgrade -1
poetry run alembic downgrade <revision_id>
```

Docker:

```bash
docker compose run --rm orchestrator alembic upgrade head
docker compose run --rm orchestrator alembic current
docker compose run --rm orchestrator alembic downgrade -1
docker compose run --rm orchestrator alembic downgrade <revision_id>
```

Recommended Docker migration sequence:

```bash
# 1) Create migration file locally (stored in repository)
poetry run alembic revision -m "describe_change"

# 2) Rebuild orchestrator image so container sees new migration file
docker compose build orchestrator

# 3) Apply migration in Docker
docker compose run --rm orchestrator alembic upgrade head
```

## Template `-x` Revisions

Examples:

```bash
# Change question_text length (reversible if old_q_len provided)
poetry run alembic -x old_q_len=384 -x new_q_len=256 revision -m "q_len_256"

# Change answer_text length (reversible if old_a_len provided)
poetry run alembic -x old_a_len=384 -x new_a_len=256 revision -m "a_len_256"

# Change embedding vector dim (downgrade is manual)
poetry run alembic -x new_dim=512 revision -m "embedding_dim_512"

# Set formulations.embedding to NOT NULL after recompute
poetry run alembic -x embedding_not_null revision -m "embedding_not_null"
```

Notes:

- For reversible text-length downgrade, pass both `old_*` and `new_*` values at revision generation time.
- Correct order is: `alembic -x ... revision ...`, not `alembic revision ... -x ...`.

## Text Length Change Checklist

1. Create/apply migration for length change.
2. Sync runtime config values.
   - `env/orchestrator.env`: `DB_SCHEMA__QUESTION_TEXT_MAX_LEN`, `DB_SCHEMA__ANSWER_TEXT_MAX_LEN`
   - `env/bot.env`: `QUESTION_LIMITS__MAX_QUESTION_TEXT_LEN`, `QUESTION_LIMITS__MAX_ANSWER_TEXT_LEN`
3. Restart services (Docker example: `docker compose up -d --force-recreate orchestrator bot`).

Why:

- Orchestrator validates DB schema against `DB_SCHEMA__*` at startup.
- Bot validates user input by `QUESTION_LIMITS__*`.

## Embedding Dimension Change Checklist

1. Create/apply dimension migration:
   `alembic -x new_dim=<N> revision ...` then `alembic upgrade head`.
2. Sync `DB_SCHEMA__QUESTION_EMBEDDING_DIM=<N>` in `env/orchestrator.env`.
3. Recompute embeddings.
4. Create/apply `-x embedding_not_null` migration (optional but recommended after backfill).
5. Restart orchestrator service.

Recompute commands:

```bash
poetry run python -m orchestrator.db.migrations.recompute_embeddings
poetry run python -m orchestrator.db.migrations.recompute_embeddings --batch-size 100 --start-id 0
docker compose run --rm orchestrator python -m orchestrator.db.migrations.recompute_embeddings
```

Recompute notes:

- Script checks DB vector dimension against `DB_SCHEMA__QUESTION_EMBEDDING_DIM`.
- Script requires valid embedding provider settings (`REQUESTS__*`, API access).
