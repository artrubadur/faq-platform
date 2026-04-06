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
- `orchestrator/integrations`: external embedding/rerank/compose provider clients and templates.
- `shared/api`: reusable async HTTP API client and shared API exceptions.

## Request Flows

### Public Entry Flow

1. User sends `/ask <text>` or plain text.
2. Bot validates and normalizes input.
3. Bot calls orchestrator suggestion endpoint.
4. Orchestrator returns `questions` and `is_confident`.
5. Bot renders response using the confidence flag.

### Suggestion Pipeline (Orchestrator)

#### 1. Candidate Retrieval

1. Compute embedding for the input question.
2. Query DB by cosine distance with `SUGGESTION__SEARCH__RELATED_THRESHOLD`.
3. Fetch up to `QUESTION_LIMITS__MAX_SIMILAR_AMOUNT + 1` similar candidates.
4. Build `similarity_by_question_id` map from retrieved rows.
5. If no similar candidates exist, return only popular questions and
   `is_confident=false`.

#### 2. Obvious-Match Shortcut

1. Check obvious-match condition:
   `best_similarity >= 1 - 1e-6`, or
   `best_similarity >= SUGGESTION__SEARCH__BEST_MATCH_THRESHOLD` and
   `(best_similarity - second_similarity) >= SUGGESTION__SEARCH__OBVIOUS_MARGIN`.
2. If obvious, skip rerank and skip compose.
3. Increase rating of top candidate.
4. Return top similar questions (trimmed to `max_similar_amount` = `QUESTION_LIMITS__MAX_SIMILAR_AMOUNT`) plus popular
   completion, with `is_confident=true`.

#### 3. Reranking Phase

1. Enter reranking only when obvious-match shortcut is not triggered.
2. If `SUGGESTION__RERANK__ENABLED=true`, send candidates (`id`, question text,
   base similarity) to rerank provider.
3. Provider returns ordered candidate IDs (most relevant first).
4. Service reorders candidates by returned ID order.
5. IDs missing in rerank output are pushed to the end.
6. If rerank provider is disabled or rerank request fails, original candidate
   order is preserved.

#### 4. Confidence Check (After Rerank/Original Order)

1. Evaluate confident-match condition:
   `best_similarity >= SUGGESTION__SEARCH__BEST_MATCH_THRESHOLD` and
   `(best_similarity - second_similarity) >= SUGGESTION__SEARCH__BEST_MATCH_MARGIN`.
2. If not confident, trim similar list to `max_similar_amount`, skip rating
   update, skip compose, and continue to final assembly.

#### 5. Composition Phase (Confident Path Only)

1. Composition runs only for confident matches from phase 4.
2. If `SUGGESTION__COMPOSE__ENABLED=false`, top answer stays unchanged.
3. `best_candidate` is the top question after rerank/original order.
4. Supporting candidates are selected from
   `questions[1 : 1 + SUGGESTION__COMPOSE__SUPPORTING_TOP_K]`.
5. Supporting candidate is included only when
   `candidate_similarity >= best_similarity - SUGGESTION__COMPOSE__SUPPORTING_MARGIN`.
6. Compose provider receives `query`, `best_candidate`, and
   `supporting_candidates`, and returns a single composed answer.
7. On compose failure, service falls back to the original top answer text.

#### 6. Rating Update

1. Rating is updated only in confident branches (obvious or phase-4 confident).
2. Only top candidate rating is increased.
3. Gain formula:
   if `best_similarity < threshold` -> `0`,
   if `threshold == 1` -> `1`,
   else `norm^2`, where
   `norm = (best_similarity - threshold) / (1 - threshold)` and
   `threshold = SUGGESTION__SEARCH__BEST_MATCH_THRESHOLD`.

#### 7. Final Assembly

1. Fill response with popular questions using remaining capacity:
   `min(max_amount - len(similar), max_popular_amount)`.
2. Popular items exclude already selected similar IDs.
3. Return combined list and `is_confident` flag.

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
- `requests.yml` -> embedding, rerank, and compose API request templates

## Schema Synchronization

Schema changes are managed by Alembic revisions.

On orchestrator startup:

- checks that DB revision matches current Alembic head
- validates runtime `DB_SCHEMA__*` constraints against actual DB types
- fails fast with migration instructions if schema/revision is out of date

## Logging and Notifications

Logging is configured from YAML and supports:

- stdout/file sinks
- duplicate suppression with repeat counters

## Notable Commands

- Public: `/start`, `/ask`, plain text question handling
- Admin: `/settings`, `/ban`, `/unban`, `/state`, `/goto`, `/error`
- Dynamic commands: loaded from `config/commands.yml`
