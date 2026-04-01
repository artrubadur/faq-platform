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

## Parse Mode

Top-level `parse_mode` affects most outgoing messages:

- `html`
- `markdown`
- `null`

This parse mode is also used by dynamic custom commands (see
[commands.md](commands.md)).

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

## Constants and Reserved Keys

Constants can be used with dot-path placeholders, for example:

- `{emoji.status.successful}`
- `{brand.name}`

First-level constant keys cannot use reserved runtime names such as:

- `id`, `identity`, `user`, `question`, `exception`, `date`, `content`, `old`,
  `new`, `page`, `max_page`, `rating`, `question_text`, `answer_text`

If a template references an unknown non-reserved field, startup validation fails.

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

## Error and Validation Routing

Common routing behavior in the current implementation:

- Public search failures use `responses.public.failed` with
  `exceptions.search.not_found`.
- Admin workflow validation/input errors use `responses.admin.invalid`.
- Global unexpected errors in public handlers use `responses.public.error`.

## Best Practices

- Keep placeholders unchanged unless you are sure the variable is provided.
- Prefer editing copy in YAML rather than hardcoding text in Python.
- When switching parse mode, recheck HTML/Markdown syntax across all templates.
