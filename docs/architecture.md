# Architecture

## High-Level Components

- `bot/main.py`: Telegram bot bootstrap and polling entrypoint.
- `bot/dispatch`: routers, handlers, FSM middlewares, instance wiring.
- `bot/dialogs`: outgoing message builders, keyboards, callback payloads.
- `bot/services`: validation and orchestrator API gateway calls.
- `orchestrator/main.py`: FastAPI bootstrap and lifecycle hooks.
- `orchestrator/api`: REST routes, dependency injection, error handlers.
- `orchestrator/repositories`: SQLAlchemy-based DB access layer.
- `orchestrator/db`: models, async session/engine, schema reconciliation.
- `orchestrator/integrations`: external embedding provider client/templates.

## Request Flows

### Public Flow

1. User sends `/ask <text>` or plain text.
2. Input is validated and normalized.
3. Embedding is computed via configured request template.
4. DB similarity search (`pgvector` cosine distance).
5. The top match may receive a rating increase based on confidence and the gap
   from the second match.
6. If confidence is high, best answer is returned.
7. If confidence is low, fallback text + suggestions are returned.

Rating update details:

- Rating is updated only when at least one similar question is found and the top
  similarity reaches `SEARCH__BEST_MATCH_THRESHOLD`.
- If the threshold is exactly `1`, the top question receives `+1.0`.
- Otherwise, the gain is based on two factors:
  - normalized confidence above the threshold
  - similarity gap between the first and second match
- The final gain is `norm^2 * gap`, clamped to `[0, 1]`, and applied only to
  the best match.

### Admin Flow

1. Admin sends `/settings`.
2. Inline menu routes into users/questions CRUD flows.
3. Multi-step operations are tracked in FSM state.
4. Confirm/save callbacks apply DB writes.
5. List screens support ordering, page size, and page navigation.

## Storage Model

### PostgreSQL

### `users`

- `id` (PK)
- `telegram_id` (unique/indexed)
- `username` (nullable unique/indexed)
- `role` (`user`, `admin`, `banned`)

### `questions`

- `id` (PK)
- `question_text` (varchar, size from env schema config)
- `answer_text` (varchar, size from env schema config)
- `rating` (float, default `0.0`)
- `embedding` (`vector(dim)`, dim from env schema config)

## Redis

Used for FSM state and temp metadata via custom `TempStorage`:

- short scope TTL (`REDIS__SHORT_TTL`)
- long scope TTL (`REDIS__LONG_TTL`)

## Middlewares

Applied in startup order:

1. `BannedMiddleware`
2. `RateLimitMiddleware` (if enabled)
3. `LastMessageMiddleware`
4. `LogHandlerMiddleware`
5. `AdminMiddleware` (admin router only)

Role resolution uses:

- cached `sender_role` from long Redis state, or
- DB lookup fallback (defaults to `user` if not found)

## Configuration System

Environment is loaded by pydantic settings with nested delimiter `__`.

YAML-driven runtime customization:

- `messages.yml` -> response texts and format templates
- `constants.yml` -> startup-resolved constants
- `commands.yml` -> dynamic public commands
- `requests.yml` -> embedding API request templates

## Schema Synchronization

On startup, DB schema is reconciled with env-defined constraints:

- adjusts `question_text` and `answer_text` column lengths
- validates shrink operations against existing row lengths
- reconciles embedding vector dimension
- recomputes embeddings if dimension changed and table is not empty

## Logging and Notifications

Logging is configured from YAML and supports:

- stdout/file sinks
- duplicate suppression with repeat counters
- throttled Telegram notifications to admins for warning/error logs

## Notable Commands

- Public: `/start`, `/ask`, plain text question handling
- Admin: `/settings`, `/ban`, `/unban`, `/state`, `/goto`, `/error`
- Dynamic commands: loaded from `config/commands.yml`
