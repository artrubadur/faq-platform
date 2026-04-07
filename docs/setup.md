# Setup Guide

This guide focuses on launch steps.

For environment variables and YAML details, see
[configuration.md](configuration.md).

For migration workflows and advanced revision tasks, see
[migrations.md](migrations.md).

## Prerequisites

- Python 3.12
- Poetry
- Docker and Docker Compose
- Telegram bot token
- Credentials for embedding/rerank/compose providers

## 1. Prepare files

```bash
cp env/bot.env.example env/bot.env
cp env/orchestrator.env.example env/orchestrator.env
cp .env.example .env
cp config/orchestrator/requests.yml config/requests.yml
```

Runtime files used by services:

- `config/logging.yml`
- `config/requests.yml`
- `config/messages.yml`
- `config/constants.yml`
- `config/commands.yml`

## 2. Install dependencies (local run)

```bash
poetry install
```

## 3. Run database migrations

Local:

```bash
poetry run alembic upgrade head
```

Docker:

```bash
docker compose up -d db
docker compose run --rm orchestrator alembic upgrade head
```

## 4. Launch pipeline

Choose infrastructure mode before starting services:

- Option A: use local infrastructure services.
- Option B: run only infrastructure in Docker:

```bash
docker compose up -d db redis
```

### Polling mode

Set `BOT__MODE="polling"` and `BOT__TOKEN` in `env/bot.env`.

Local:

```bash
docker compose up -d db redis
poetry run python -m orchestrator
poetry run python -m bot
```

Docker:

```bash
docker compose up --build
```

### Webhook mode

Set these values in `env/bot.env`:

- `BOT__MODE="webhook"`
- `BOT__TOKEN`
- `BOT__WEBHOOK__BASE_URL` as your public HTTPS base URL
- `BOT__WEBHOOK__PATH` as incoming webhook path
- `BOT__WEBHOOK__SECRET_TOKEN` for request verification
- `BOT__WEBHOOK__DROP_PENDING_UPDATES` if you need pending updates cleanup

Local:

```bash
docker compose up -d db redis
poetry run python -m orchestrator
poetry run python -m bot
```

Docker:

```bash
docker compose up --build
```

Notes:

- Effective webhook URL is `BOT__WEBHOOK__BASE_URL + BOT__WEBHOOK__PATH`.
- The bot listens on `0.0.0.0:8080` in webhook mode.
- Docker publishes `8080:8080` for the bot service.
- Telegram requires HTTPS on the public endpoint.

## 5. Manual webhook checks

Set webhook:

```bash
curl -X POST "https://api.telegram.org/bot<BOT__TOKEN>/setWebhook" \
  -d "url=<BOT__WEBHOOK__BASE_URL><BOT__WEBHOOK__PATH>" \
  -d "secret_token=<BOT__WEBHOOK__SECRET_TOKEN>"
```

Get webhook info:

```bash
curl -X GET "https://api.telegram.org/bot<BOT__TOKEN>/getWebhookInfo"
```

Optional reset before switching to polling:

```bash
curl -X POST "https://api.telegram.org/bot<BOT__TOKEN>/deleteWebhook" \
  -d "drop_pending_updates=true"
```

## 6. Troubleshooting

- Startup fails with missing request templates or missing request credentials:
  check `config/requests.yml`, `REQUESTS__FOLDER_ID`, and `REQUESTS__IAM_TOKEN`.
- Database startup has vector-related errors:
  ensure `init.sql` was applied and extension exists in PostgreSQL.
- Admin commands are unavailable:
  verify `ADMIN__IDS`, ensure user has started the bot, and restart orchestrator.

## 7. Startup sequence reference

Orchestrator startup order:

1. Logging setup
2. Table creation
3. Schema constraint reconciliation
4. Admin role synchronization
5. API startup

Bot startup order:

1. Logging setup
2. Middleware registration
3. Router registration
4. Mode-specific launch: polling or webhook server
