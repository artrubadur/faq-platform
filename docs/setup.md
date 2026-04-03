# Setup and Configuration

This guide documents how to run and configure the FAQ bot in local and Docker
environments.

## Prerequisites

- Python 3.12
- Poetry
- PostgreSQL (with `pgvector` extension)
- Redis
- Telegram bot token
- Embedding/rerank/compose API credentials

## Local Setup

### 1. Install dependencies

```bash
poetry install
```

### 2. Prepare local env files

```bash
cp env/bot.env.example env/bot.env
cp env/orchestrator.env.example env/orchestrator.env
```

Set required values:

- `env/bot.env`: `BOT__TOKEN`, Redis settings, orchestrator client settings
- `env/orchestrator.env`: DB settings, suggestion settings, `REQUESTS__*`,
  and `ADMIN__IDS`

### 3. Prepare runtime YAML configs

Create orchestrator request config at runtime path:

```bash
cp config/orchestrator/requests.yml config/requests.yml
```

Runtime files:

- `config/logging.yml` (already present)
- `config/requests.yml` (required by orchestrator)

Reference template:

- `config/orchestrator/requests.yml`

### 4. Start infra

Option A: use local services.

Option B: start infra only with Docker:

```bash
docker compose up -d db redis
```

### 5. Run orchestrator

```bash
poetry run python -m orchestrator
```

### 6. Run bot

```bash
poetry run python -m bot
```

## Docker Setup (Full Stack)

```bash
cp env/bot.env.example env/bot.env
cp env/orchestrator.env.example env/orchestrator.env
cp .env.example .env
docker compose up --build
```

The compose stack includes:

- `db` (`pgvector/pgvector:pg17`)
- `redis` (`redis:7.4-alpine`)
- `orchestrator` (from `orchestrator/Dockerfile`)
- `bot` (from `bot/Dockerfile`)

## Environment Variables

### Compose interpolation (`.env`)

Use `.env` only for Docker Compose interpolation (volume source overrides):

- `COMPOSE__LOGGING_PATH`
- `COMPOSE__ORCHESTRATOR_REQUESTS_PATH`
- `COMPOSE__BOT_CONSTANTS_PATH`
- `COMPOSE__BOT_MESSAGES_PATH`
- `COMPOSE__BOT_COMMANDS_PATH`

### Bot runtime (`env/bot.env`)

- `BOT__TOKEN` (required)

Redis:

- `REDIS__HOST` (required)
- `REDIS__PASSWORD` (required)
- `REDIS__LONG_TTL` (default `86400`)
- `REDIS__SHORT_TTL` (default `300`)

Question limits:

- `QUESTION_LIMITS__MAX_QUESTION_TEXT_LEN` (default `384`)
- `QUESTION_LIMITS__MAX_ANSWER_TEXT_LEN` (default `384`)
- `QUESTION_LIMITS__MAX_SIMILAR_AMOUNT` (default `7`)
- `QUESTION_LIMITS__MAX_POPULAR_AMOUNT` (default `7`)
- `QUESTION_LIMITS__MAX_AMOUNT` (default `7`)

Validation rule:

- `MAX_SIMILAR_AMOUNT <= MAX_AMOUNT`
- `MAX_POPULAR_AMOUNT <= MAX_AMOUNT`

Rate limiting:

- `RATE_LIMIT__ENABLED` (default `true`)
- `RATE_LIMIT__MAX_REQUESTS` (default `5`)
- `RATE_LIMIT__WINDOW` (default `10`)
- `RATE_LIMIT__SKIP_ADMIN` (default `true`)

Orchestrator API client:

- `ORCHESTRATOR_CLIENT__BASE_URL` (required)
- `ORCHESTRATOR_CLIENT__TIMEOUT` (default `5`)
- `ORCHESTRATOR_CLIENT__RETRIES` (default `1`)
- `ORCHESTRATOR_CLIENT__RETRY_DELAY` (default `0.2`)

### Orchestrator runtime (`env/orchestrator.env`)

Database:

- `DB__NAME` (required)
- `DB__USER` (required)
- `DB__PASSWORD` (required)
- `DB__HOST` (required)

Suggestion search thresholds:

- `SUGGESTION__SEARCH__BEST_MATCH_THRESHOLD` (default `0.7`)
- `SUGGESTION__SEARCH__BEST_MATCH_MARGIN` (default `0.05`)
- `SUGGESTION__SEARCH__RELATED_THRESHOLD` (default `0.6`)
- `SUGGESTION__SEARCH__OBVIOUS_MARGIN` (default `0.3`)

Suggestion behavior:

- `SUGGESTION__RERANK__ENABLED` (default `true`)
- `SUGGESTION__COMPOSE__ENABLED` (default `true`)
- `SUGGESTION__COMPOSE__SUPPORTING_MARGIN` (default `0.15`)
- `SUGGESTION__COMPOSE__SUPPORTING_TOP_K` (default `2`)

Embedding provider API client:

- `CLIENTS__EMBEDDING__BASE_URL` (optional)
- `CLIENTS__EMBEDDING__TIMEOUT` (default `5`)
- `CLIENTS__EMBEDDING__RETRIES` (default `1`)
- `CLIENTS__EMBEDDING__RETRY_DELAY` (default `0.2`)

Rerank provider API client:

- `CLIENTS__RERANK__BASE_URL` (optional)
- `CLIENTS__RERANK__TIMEOUT` (default `5`)
- `CLIENTS__RERANK__RETRIES` (default `1`)
- `CLIENTS__RERANK__RETRY_DELAY` (default `0.2`)

Compose provider API client:

- `CLIENTS__COMPOSE__BASE_URL` (optional)
- `CLIENTS__COMPOSE__TIMEOUT` (default `5`)
- `CLIENTS__COMPOSE__RETRIES` (default `1`)
- `CLIENTS__COMPOSE__RETRY_DELAY` (default `0.2`)

Request template variables:

- `REQUESTS__FOLDER_ID` (required by Yandex embedding/rerank/compose templates)
- `REQUESTS__IAM_TOKEN` (required by Yandex embedding/rerank/compose templates)

Schema constraints:

- `DB_SCHEMA__QUESTION_TEXT_MAX_LEN` (default `384`)
- `DB_SCHEMA__ANSWER_TEXT_MAX_LEN` (default `384`)
- `DB_SCHEMA__QUESTION_EMBEDDING_DIM` (default `256`)

Admin sync:

- `ADMIN__IDS` (default `[]`)

API:

- `API__HOST` (default `0.0.0.0`)
- `API__PORT` (default `8000`)

## YAML Configuration Files

Files with the `.example.yml` suffix match the built-in defaults and can be used
as templates.

Runtime YAML paths inside the apps are fixed:

- `config/logging.yml`
- `config/requests.yml`
- `config/messages.yml`
- `config/constants.yml`
- `config/commands.yml`

In Docker Compose, host files are mounted into these paths via `COMPOSE__*`
variables from `.env`.

### `config/requests.yml` (required)

Defines how embedding, rerank, and compose requests are built/parsed:

- HTTP method/url/headers/body template
- `path.target`: where payload text is injected into request body
- `path.source`: where response value is extracted from response payload

Sections:

- `embedding` is required.
- `rerank` is optional when `SUGGESTION__RERANK__ENABLED=false`.
- `rerank` is required when `SUGGESTION__RERANK__ENABLED=true`.
- `compose` is optional when `SUGGESTION__COMPOSE__ENABLED=false`.
- `compose` is required when `SUGGESTION__COMPOSE__ENABLED=true`.

Reference with Yandex Cloud API template: `config/orchestrator/requests.yml`.

### `config/messages.yml` (optional)

Overrides user/admin texts, parse mode, formatting, and button labels.

See [messages.md](messages.md).

Reference defaults: `config/bot/messages.example.yml`

### `config/constants.yml` (optional)

Provides constant placeholders used in messages and commands.

Reference defaults: `config/bot/constants.example.yml`

### `config/commands.yml` (optional)

Adds dynamic public commands.

See [commands.md](commands.md).

Reference defaults: `config/bot/commands.example.yml`

### Logging config (`config/logging.yml`)

Supports stdout/file/telegram sinks, duplicate suppression, and throttling.

## Startup Sequence

At orchestrator boot (`orchestrator/main.py`):

1. Logging setup
2. Table creation (`Base.metadata.create_all`)
3. Schema constraint reconciliation
4. Admin role sync from `ADMIN__IDS`
5. API startup

At bot boot (`bot/main.py`):

1. Logging setup
2. Middleware registration
3. Router registration
4. Polling start

## Important Operational Notes

- Admin sync promotes users already present in DB; new admins usually need to
  run `/start` first, then orchestrator restart/sync.
- Reducing question/answer varchar limits fails if existing rows exceed limits.
- Changing embedding dimension triggers automatic vector migration:
  - empty `questions` table: direct type change
  - non-empty table: embeddings are recomputed for all rows

## Troubleshooting

- Startup error about missing request templates/settings:
  check `REQUESTS__*` env values, `SUGGESTION__RERANK__ENABLED`,
  `SUGGESTION__COMPOSE__ENABLED`, and `config/requests.yml`.
- `vector` type errors:
  ensure `init.sql` ran and extension exists in PostgreSQL.
- Admin commands not available:
  verify `ADMIN__IDS`, user presence in DB, and role sync.
