# Configuration Reference

This guide describes runtime configuration for bot, orchestrator, and Docker
Compose.

## Configuration files map

- `.env`: Docker Compose interpolation only
- `env/bot.env`: bot runtime settings
- `env/orchestrator.env`: orchestrator runtime settings
- `config/logging.yml`: shared logging config
- `config/requests.yml`: orchestrator request templates
- `config/messages.yml`: bot message texts and formatting
- `config/constants.yml`: bot placeholders/constants
- `config/commands.yml`: bot custom public commands

## Docker Compose interpolation (`.env`)

Use `.env` only for mount source overrides:

- `COMPOSE__LOGGING_PATH`
- `COMPOSE__ORCHESTRATOR_REQUESTS_PATH`
- `COMPOSE__BOT_CONSTANTS_PATH`
- `COMPOSE__BOT_MESSAGES_PATH`
- `COMPOSE__BOT_COMMANDS_PATH`

## Bot runtime (`env/bot.env`)

Core:

- `BOT__TOKEN` required
- `BOT__MODE` supports `polling` or `webhook` (default `polling`)

Webhook:

- `BOT__WEBHOOK__BASE_URL` required only when mode is `webhook`
- `BOT__WEBHOOK__PATH` default `/telegram/webhook`
- `BOT__WEBHOOK__SECRET_TOKEN` optional, recommended
- `BOT__WEBHOOK__DROP_PENDING_UPDATES` default `false`

Webhook behavior subtleties:

- Empty base URL is treated as missing.
- Path cannot be empty.
- If path does not start with `/`, it is normalized automatically.
- Effective webhook URL is `BOT__WEBHOOK__BASE_URL + BOT__WEBHOOK__PATH`.
- When mode is `webhook`, missing base URL causes startup validation error.

Redis:

- `REDIS__HOST` required
- `REDIS__PASSWORD` required
- `REDIS__LONG_TTL` default `86400`
- `REDIS__SHORT_TTL` default `300`

Question limits:

- `QUESTION_LIMITS__MAX_QUESTION_TEXT_LEN` default `384`
- `QUESTION_LIMITS__MAX_ANSWER_TEXT_LEN` default `384`
- `QUESTION_LIMITS__MAX_SIMILAR_AMOUNT` default `7`
- `QUESTION_LIMITS__MAX_POPULAR_AMOUNT` default `7`
- `QUESTION_LIMITS__MAX_AMOUNT` default `7`

Validation rules:

- `MAX_SIMILAR_AMOUNT <= MAX_AMOUNT`
- `MAX_POPULAR_AMOUNT <= MAX_AMOUNT`

Rate limit:

- `RATE_LIMIT__ENABLED` default `true`
- `RATE_LIMIT__MAX_REQUESTS` default `5`
- `RATE_LIMIT__WINDOW` default `10`
- `RATE_LIMIT__SKIP_ADMIN` default `true`

Orchestrator client:

- `ORCHESTRATOR_CLIENT__BASE_URL` required
- `ORCHESTRATOR_CLIENT__TIMEOUT` default `5`
- `ORCHESTRATOR_CLIENT__RETRIES` default `1`
- `ORCHESTRATOR_CLIENT__RETRY_DELAY` default `0.2`

## Orchestrator runtime (`env/orchestrator.env`)

Database:

- `DB__NAME` required
- `DB__USER` required
- `DB__PASSWORD` required
- `DB__HOST` required

Schema constraints:

- `DB_SCHEMA__QUESTION_TEXT_MAX_LEN` default `384`
- `DB_SCHEMA__ANSWER_TEXT_MAX_LEN` default `384`
- `DB_SCHEMA__QUESTION_EMBEDDING_DIM` default `256`

Suggestion search thresholds:

- `SUGGESTION__SEARCH__BEST_MATCH_THRESHOLD` default `0.7`
- `SUGGESTION__SEARCH__BEST_MATCH_MARGIN` default `0.05`
- `SUGGESTION__SEARCH__RELATED_THRESHOLD` default `0.6`
- `SUGGESTION__SEARCH__OBVIOUS_MARGIN` default `0.3`

Suggestion behavior:

- `SUGGESTION__RERANK__ENABLED` default `true`
- `SUGGESTION__COMPOSE__ENABLED` default `true`
- `SUGGESTION__COMPOSE__SUPPORTING_MARGIN` default `0.15`
- `SUGGESTION__COMPOSE__SUPPORTING_TOP_K` default `2`

Provider clients:

- `CLIENTS__EMBEDDING__BASE_URL` optional
- `CLIENTS__EMBEDDING__TIMEOUT` default `5`
- `CLIENTS__EMBEDDING__RETRIES` default `1`
- `CLIENTS__EMBEDDING__RETRY_DELAY` default `0.2`
- `CLIENTS__RERANK__BASE_URL` optional
- `CLIENTS__RERANK__TIMEOUT` default `5`
- `CLIENTS__RERANK__RETRIES` default `1`
- `CLIENTS__RERANK__RETRY_DELAY` default `0.2`
- `CLIENTS__COMPOSE__BASE_URL` optional
- `CLIENTS__COMPOSE__TIMEOUT` default `5`
- `CLIENTS__COMPOSE__RETRIES` default `1`
- `CLIENTS__COMPOSE__RETRY_DELAY` default `0.2`

Request template variables:

- `REQUESTS__FOLDER_ID` required by Yandex templates
- `REQUESTS__IAM_TOKEN` required by Yandex templates

Admin/API:

- `ADMIN__IDS` default `[]`
- `API__HOST` default `0.0.0.0`
- `API__PORT` default `8000`

## YAML runtime files

### `config/requests.yml` (required)

Defines request/response templates for embedding, rerank, and compose flows:

- request method, URL, headers, body
- payload insertion path (`path.target`)
- response extraction path (`path.source`)

Section requirements:

- `embedding` always required
- `rerank` required only when rerank is enabled
- `compose` required only when compose is enabled

Reference template: `config/orchestrator/requests.yml`

### `config/messages.yml` (optional)

Overrides user/admin texts, formatting, and labels.

### `config/constants.yml` (optional)

Provides placeholders used in messages and command text.

### `config/commands.yml` (optional)

Adds custom public commands.
