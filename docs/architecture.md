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
- `orchestrator/integrations`: external API provider clients and templates.
- `shared/api`: reusable async HTTP API client and shared API exceptions.

## Request Flows

### Public Entry Flow

1. User sends `/ask <text>` or plain text.
2. Bot validates and normalizes input.
3. Bot calls orchestrator suggestion endpoint.
4. Orchestrator returns `questions` and `is_confident`.
5. Bot renders response using the confidence flag.

### Suggestion Pipeline (Orchestrator)

#### 1. Formulation-Level Similarity and Max Pooling

1. Compute embedding for the input question.
2. Query `formulations` by cosine distance with
   `SUGGESTION__SEARCH__RELATED_THRESHOLD`.
3. Aggregate matches to question level with max pooling:
   each question keeps its best-matching formulation score.

#### 2. Candidate Retrieval

1. Fetch top pooled question candidates (up to `request.max_similar_amount + 1`).
2. If no similar candidates exist, return popular questions (up to
   `request.max_popular_amount`) with `is_confident=false`.

#### 3. Obvious-Match Shortcut

1. Check obvious-match condition:
   `best_similarity >= 1 - 1e-6`, or
   `best_similarity >= SUGGESTION__SEARCH__BEST_MATCH_THRESHOLD` and
   `(best_similarity - second_similarity) >= SUGGESTION__SEARCH__OBVIOUS_MARGIN`.
2. If obvious, skip rerank and compose.
3. Increase rating of top candidate.
4. Trim similar list to `request.max_similar_amount`, then complete with popular
   questions and return `is_confident=true`.

#### 4. Reranking

1. Enter reranking only when obvious-match shortcut is not triggered.
2. If rerank is enabled, send candidates (`id`, `question_text`, base
   similarity) to rerank provider.
3. Provider returns ordered candidate IDs (most relevant first).
4. Service reorders candidates by returned ID order.
5. IDs missing in rerank output are pushed to the end.
6. If rerank is disabled or fails, original candidate order is preserved.

#### 5. Confidence Check (After Rerank/Original Order)

1. Evaluate confident-match condition:
   `best_similarity >= SUGGESTION__SEARCH__BEST_MATCH_THRESHOLD` and
   `(best_similarity - second_similarity) >= SUGGESTION__SEARCH__BEST_MATCH_MARGIN`.
2. If not confident, trim similar list to `request.max_similar_amount`, skip rating
   update, skip compose, and continue to final assembly.

#### 6. Composition (Confident Path Only)

1. Composition runs only for confident matches from phase 5.
2. If compose is disabled, top answer stays unchanged.
3. `best_candidate` is the top question after rerank/original order.
4. Supporting candidates are selected from
   `questions[1 : 1 + SUGGESTION__COMPOSE__SUPPORTING_TOP_K]`.
5. Supporting candidate is included only when
   `candidate_similarity >= best_similarity - SUGGESTION__COMPOSE__SUPPORTING_MARGIN`.
6. Compose provider receives `query`, `best_candidate`, and
   `supporting_candidates`, and returns a single composed answer.
7. On compose failure, service falls back to the original top answer text.

#### 7. Rating Update

1. Rating is updated only in obvious/confident branches.
2. Only top candidate rating is increased.
3. Gain formula:
   if `best_similarity < threshold - 1e-6` -> `0`,
   if `threshold == 1` -> `1`,
   else `norm^2`, where
   `norm = (best_similarity - threshold) / (1 - threshold)` and
   `threshold = SUGGESTION__SEARCH__BEST_MATCH_THRESHOLD`.

#### 8. Final Assembly

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

### Question Create/Update with Formulation Generation

1. Admin create/update flow collects `generate_formulations_amount` (0 means skip).
2. Orchestrator validates amount against `SUGGESTION__GENERATION__MAX_AMOUNT`.
3. If generation is enabled, provider returns alternative question texts.
4. Each generated text gets an embedding and is stored in `formulations`.
5. Base formulation from canonical question text is always stored on create.

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

### `formulations`

- `id` (PK)
- `question_id` (FK -> `questions.id`, indexed, `ON DELETE CASCADE`)
- `question_text` (varchar, size from env schema config)
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
- `requests.yml` -> external API request templates

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
- Admin: `/settings`, `/ban`, `/unban`, `/state`
- Dynamic commands: loaded from `config/commands.yml`
