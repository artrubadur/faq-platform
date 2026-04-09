# Message Customization System

`messages.yml` controls user-visible texts, parse mode, formatting templates, and
button labels.

Reference schema and default examples:
[config/bot/messages.example.yml](../config/bot/messages.example.yml)

## Loading Behavior

- Runtime path is `config/messages.yml`.
- In Docker Compose, host file mapping is controlled by
  `COMPOSE__BOT_MESSAGES_PATH` from `.env`.
- Missing file does not break startup; built-in defaults from Python models are
  used.
- Existing values override defaults selectively.

## File Format

```yaml
parse_mode: html # html / markdown / markdownv2 / null

responses:
  public:
    start: "Hello, {first_name}!"
```

## Parse Mode

Top-level `parse_mode` affects outgoing messages:

- `html`
- `markdown`
- `markdownv2`
- `null`

## Variable Sources

Templates use `{variable}` placeholders. Values come from:

1. **Runtime context** passed by handlers/dialogs.
2. **Message context** for public user messages and custom commands:
   - `id`, `first_name`, `last_name`, `username`, `full_name`, `date`
3. **Constants** from `constants.yml` (resolved at startup time).

Example:

```yaml
responses:
  public:
    start: "Hello, {first_name}. Date: {date}"
```

## Primary Public Messages

- `responses.public.start`: welcome message on `/start`.
- `responses.public.failed`: generic failed-answer wrapper (`{exception}` is usually `validation.question.question_text_long`).
- `exceptions.search.not_found`: text used when the bot cannot understand a
  question.
- `responses.public.error`: fallback text for unexpected internal errors.
- `responses.public.banned`: shown to blacklisted users.
- `responses.public.rate_limited`: shown when request rate limit is exceeded.

## Constants

Constants are read from the top-level `constants` object in `constants.yml`.
Use dot-path placeholders from that namespace, for example:

- `{constants.emoji.status.successful}`
- `{constants.brand.name}`

If a template references an unknown field (outside runtime context variables),
startup validation fails.

## Formatting Blocks

`format.*` sections are reusable templates used by output helpers:

- `format.field.*`: primitive field formatting (id, username, rating, date, ...)
- `format.user.*`: structured user rendering
- `format.question.*`: structured question rendering
- `format.edit.*`: update diff rendering
- `format.fallback.*`: values used when fields are absent

Buttons (`button.*`) use plain format substitution and are not passed through
`format.field.*` helpers.

## Runtime Context Conventions

Many templates accept extra placeholders (for example `user`, `question`,
`exception`, `identity`). In `messages.example.yml`, comments like
`# < variable_name` document which values are passed by each call site.

Use those comments as contract hints when editing text templates.

## Validation and Errors

On startup, messages config validation checks:

- invalid placeholder references
- invalid parse mode values

At runtime, common routing behavior in the current implementation:

- Public search failures use `responses.public.failed` with
  `exceptions.search.not_found`.
- Admin workflow validation/input errors use `responses.admin.invalid`.
- Global unexpected errors in public handlers use `responses.public.error`.

## Best Practices

- Keep placeholders unchanged unless you are sure the variable is provided.
- Prefer editing copy in YAML rather than hardcoding text in Python.
- When switching parse mode, recheck HTML/Markdown syntax across all templates.
