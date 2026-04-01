# FAQ Bot

Telegram FAQ bot with semantic search, pgvector-backed similarity lookup, and an
admin UI for managing users and questions.

## Features

- Semantic question search using external embeddings.
- PostgreSQL + pgvector storage for questions and embeddings.
- Redis-backed temporary state with separate short and long TTL scopes.
- Admin workflows for question/user CRUD, pagination, bans, and diagnostics.
- Runtime text customization via YAML (`messages`, `constants`, `commands`).
- Configurable rate limiting middleware.

## Quick Start (Local)

### 1. Prerequisites

- Python 3.12
- Poetry
- PostgreSQL with `vector` extension (`pgvector`)
- Redis

### 2. Install dependencies

```bash
poetry install
```

### 3. Configure environment

```bash
cp env/bot.env.example env/bot.env
cp env/orchestrator.env.example env/orchestrator.env
cp .env.example .env
```

Configure your embedding API request template in `config/requests.yml` and
update:

- `env/bot.env` (`BOT__TOKEN`, Redis settings, orchestrator client URL/timeouts)
- `env/orchestrator.env` (DB settings, search/schema settings,
  embedding provider credentials `REQUESTS__*`, admin list `ADMIN__IDS`)

### 4. Start dependencies (if needed)

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

## Quick Start (Docker Compose)

```bash
cp env/bot.env.example env/bot.env
cp env/orchestrator.env.example env/orchestrator.env
cp .env.example .env
docker compose up --build
```

This starts `db`, `redis`, `orchestrator`, and `bot`.

## Command Reference

### Public

- `/start` - welcome message and registration in users table.
- `/ask <question>` - semantic FAQ search.
- Any plain text message - treated as a question.
- Extra public commands from `config/commands.yml`.

### Admin

- `/settings` - open admin UI (users/questions CRUD + list).
- `/ban <telegram_id>`
- `/unban <telegram_id>`
- `/state ...` - inspect and mutate FSM state.

Admin routes require `admin` role and are controlled by `ADMIN__IDS` + DB role
sync at orchestrator startup.

## Documentation

- [Setup and Configuration](docs/setup-and-configuration.md)
- [Architecture](docs/architecture.md)
- [Messages Customization](docs/messages.md)
- [Custom Commands](docs/commands.md)
