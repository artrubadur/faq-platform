# Message Customization System

`messages.yml` controls user-visible texts, parse mode, message formatting
templates, button labels, and Telegram link preview options for public sender
messages.

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
link_preview: null # bool / null / {is_disabled, url, media_size, show_above_text}

responses:
  public:
    start:
      text: "Hello, {first_name}!"
      link_preview:
        is_disabled: true
```

Public response fields (`responses.public.*`) support two shapes:

1. plain string
2. object with:
   - `text` (required string)
   - `link_preview` (optional)

All non-public message fields remain plain string templates.

## Parse Mode

Top-level `parse_mode` affects outgoing messages:

- `html`
- `markdown`
- `markdownv2`
- `null`

## Link Preview

Top-level `link_preview` is a default for all `responses.public.*` sender
messages (`start`, `failed`, `error`, `banned`, `rate_limited`).

Per-field override:

```yaml
responses:
  public:
    start:
      text: "Hello"
      link_preview: null
```

Behavior:

- `link_preview: null` -> no explicit options (`None`)
- `link_preview: false` -> disable previews (`is_disabled=True`)
- `link_preview: true` -> explicitly enable previews (`is_disabled=False`)
- `link_preview: { ... }` -> map to `LinkPreviewOptions`

Supported dict fields:

- `is_disabled` (`bool`)
- `url` (`str`)
- `media_size` (`large` or `small`)
- `show_above_text` (`bool`)

`media_size` maps to Telegram flags:

- `large` -> `prefer_large_media=True`
- `small` -> `prefer_small_media=True`

## Variable Sources

Templates use `{variable}` placeholders. Values come from:

1. runtime context passed by handlers/dialogs
2. message context for public messages:
   - `id`, `first_name`, `last_name`, `username`, `full_name`, `date`
3. constants from `constants.yml` (resolved at startup)

Example:

```yaml
responses:
  public:
    start: "Hello, {first_name}. Date: {date}"
```

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

## Validation and Errors

On startup, messages config validation checks:

- invalid placeholder references
- invalid parse mode values
- invalid `link_preview` shape/type
- invalid `responses.public.*` object shape

At runtime, common behavior:

- Public search failures use `responses.public.failed`.
- Admin workflow validation/input errors use `responses.admin.invalid`.
- Global unexpected errors in public handlers use `responses.public.error`.
