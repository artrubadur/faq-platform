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
- `orchestrator/integrations`: external embedding/rerank provider clients and templates.
- `shared/api`: reusable async HTTP API client and shared API exceptions.

## Request Flows

### Public Flow

1. User sends `/ask <text>` or plain text.
2. Input is validated and normalized.
3. Bot calls orchestrator suggestion endpoint.
4. Orchestrator returns either confident best match or suggestion list.
5. Bot formats and sends response to user.

### Suggestion Pipeline

1. Embedding is computed via configured request template.
2. DB similarity search (`pgvector` cosine distance) fetches
   `max_similar_amount + 1` candidates.
3. If the top match is obvious, rerank is skipped and the result is marked
   confident immediately.
4. Otherwise, similar candidates may be reranked by an external LLM
   (`SUGGESTION__RERANK`) and then checked for confidence.
5. On non-confident match, the extra probe candidate is dropped.
6. Similar results are supplemented with popular questions (up to limits).
7. If no similar questions are found, only popular questions are returned.

### Rating Update Details

1. Rating is updated only when at least one similar question is found and the
   top candidate is considered confident.
2. Obvious match is true when `top_similarity >= 1 - 1e-6`, or when both
   conditions hold: `top_similarity >= SEARCH__BEST_MATCH_THRESHOLD` and
   `(top_similarity - second_similarity) >= SEARCH__OBVIOUS_MARGIN`.
3. Regular confident match (after optional rerank) requires both
   `top_similarity >= SEARCH__BEST_MATCH_THRESHOLD` and
   `(top_similarity - second_similarity) >= SEARCH__BEST_MATCH_MARGIN`.
4. If the threshold is exactly `1`, the top question receives `+1.0`.
5. Otherwise, gain is based on normalized confidence above threshold.
6. The final gain is `norm^2` and is applied only to the best match, where
   `norm = (top_similarity - SEARCH__BEST_MATCH_THRESHOLD) / (1 - SEARCH__BEST_MATCH_THRESHOLD)`.

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
- `requests.yml` -> embedding and rerank API request templates

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
