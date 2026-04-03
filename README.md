# FAQ Bot

Telegram FAQ bot with semantic search, pgvector-backed similarity lookup, and an
admin UI for managing users and questions.

## Features

- Semantic question search using external embeddings.
- Optional LLM-based reranking and answer composition for confident matches.
- PostgreSQL + pgvector storage for questions and embeddings.
- Redis-backed temporary state with separate short and long TTL scopes.
- Admin workflows for question/user CRUD, pagination, bans, and diagnostics.
- Runtime text customization via YAML (`messages`, `constants`, `commands`).
- Configurable rate limiting middleware.

## Quick Start

For full setup, environment variables, and runtime config details, see
[docs/setup.md](docs/setup.md).

Minimal Docker start:

```bash
cp env/bot.env.example env/bot.env
cp env/orchestrator.env.example env/orchestrator.env
cp .env.example .env
cp config/orchestrator/requests.yml config/requests.yml
docker compose up --build
```

This starts `db`, `redis`, `orchestrator`, and `bot`.

## Documentation

- [Setup and Configuration](docs/setup.md)
- [Architecture](docs/architecture.md)
- [Messages Customization](docs/messages.md)
- [Custom Commands](docs/commands.md)
