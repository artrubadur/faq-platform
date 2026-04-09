# Custom Command System

Custom commands let you add public Telegram commands without changing Python
code. They are loaded from `config/commands.yml`.

Reference schema and default examples:
[config/bot/commands.example.yml](../config/bot/commands.example.yml)

## Loading Behavior

- Runtime path is `config/commands.yml`.
- In Docker Compose, host file mapping is controlled by
  `COMPOSE__BOT_COMMANDS_PATH` from `.env`.
- Missing file does not break startup; built-in defaults from Python models are
  used.
- Reserved command names are rejected during startup validation.

## File Format

```yaml
parse_mode: html # html / markdown / markdownv2 / null
link_preview: null # bool / null / {is_disabled, url, media_size, show_above_text}

commands:
  help: "Contact support at https://example.com"
  about:
    text: |
      Project: FAQ Bot
      Version: 1
    link_preview:
      is_disabled: true
```

- Key = command name (without `/`).
- Value can be:
  - plain string response template
  - object with:
    - `text` (required string)
    - `link_preview` (optional)

## Parse Mode

Top-level `parse_mode` is configured in `commands.yml` (`html`, `markdown`,
`markdownv2`, or `null`) and applies only to dynamic custom commands.

## Link Preview

Top-level `link_preview` defines the default preview behavior for all dynamic
commands.

Per-command override:

```yaml
commands:
  help:
    text: "Visit https://example.com"
    link_preview:
      media_size: large
```

Behavior:

- `link_preview: null` -> no explicit options (`None`)
- `link_preview: false` -> disable previews (`is_disabled=True`)
- `link_preview: true` -> explicitly enable previews (`is_disabled=False`)
- `link_preview: { ... }` -> link preview options

Supported dict fields:

- `is_disabled` (`bool`)
- `url` (`str`)
- `media_size` (`large` or `small`)
- `show_above_text` (`bool`)

## Variable Sources

Custom command text supports runtime formatting with the same user context used
for public responses:

- `id`
- `first_name`
- `last_name`
- `username`
- `full_name`
- `date`

Example:

```yaml
commands:
  profile: |
    ID: {id}
    Name: {full_name}
    Username: {username}
    Date: {date}
```

## Constants

Placeholders from `constants.yml` are resolved during startup (same behavior as
message templates). Use the `constants` namespace, for example
`{constants.emoji.status.successful}`.

For object-style command entries, constants are applied to `text`.

## Reserved Command Names

These commands are handled by the app and cannot be overridden in
`config/commands.yml`:

- `start`
- `ask`
- `goto`
- `state`
- `settings`
- `error`

## Validation and Errors

On startup, command config validation checks:

- reserved command name usage
- invalid placeholder references
- invalid `link_preview` shape/type
- invalid command object shape

If validation fails, the bot will fail fast with a configuration error.

## Best Practices

- Keep command names short and explicit (for example `help`, `contacts`).
- Keep placeholders unchanged unless you are sure the variable is provided.
- When switching parse mode, recheck HTML/Markdown syntax in every command
  template.
