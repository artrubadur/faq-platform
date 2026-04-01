# Custom Command System

Custom commands let you add public Telegram commands without changing Python
code. They are loaded from `config/commands.yml`.

## File Format

```yaml
commands:
  help: "Contact support at https://example.com"
  about: |
    Project: FAQ Bot
    Version: 1
```

- Key = command name (without `/`).
- Value = response template.

Reference example: [config/bot/commands.example.yml](../config/bot/commands.example.yml)

## Reserved Command Names

These commands are handled by the app and cannot be overridden in
`config/commands.yml`:

- `start`
- `ask`
- `goto`
- `state`
- `settings`
- `error`

## Variables and Formatting

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

Top-level `parse_mode` comes from `messages.yml` (`html`, `markdown`, or
`null`).

## Constants Support

Placeholders from `constants.yml` are resolved during startup (same behavior as
message templates). This is useful for static labels and symbols.

## Multiline Tips

Use YAML block operators:

```yaml
commands:
  literal_lines: |
    Line 1
    Line 2

  folded_lines: >
    Line 1
    Line 2
```

- `|` keeps line breaks.
- `>` folds lines into a single paragraph.

## Validation and Errors

On startup, command config validation checks:

- reserved command name usage
- invalid placeholder references

If validation fails, the bot will fail fast with a configuration error.
