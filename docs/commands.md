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

commands:
  help: "Contact support at https://example.com"
  about: |
    Project: FAQ Bot
    Version: 1
```

- Key = command name (without `/`).
- Value = response template.

## Parse Mode

Top-level `parse_mode` is configured in `commands.yml` (`html`, `markdown`,
`markdownv2`, or `null`) and applies only to dynamic custom commands.

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

If validation fails, the bot will fail fast with a configuration error.

## Best Practices

- Keep command names short and explicit (for example `help`, `contacts`).
- Keep placeholders unchanged unless you are sure the variable is provided.
- When switching parse mode, recheck HTML/Markdown syntax in every command
  template.
