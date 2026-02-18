from pathlib import Path

from pydantic import field_validator
from pydantic_settings import SettingsConfigDict

from app.core.config import config
from app.core.exceptions import ConfigError
from app.utils.config import YamlSettings

COMMANDS_PATH = (
    Path.cwd()
    / "config"
    / (f"commands.{config.commands}.yml" if config.commands else "commands.yml")
)

SYSTEM_COMMANDS = {"start", "ask", "goto", "state", "settings", "error"}


class Commands(YamlSettings):
    commands: dict[str, str] = {}

    @field_validator("commands", mode="before")
    def validate_commands(cls, commands):
        inter = SYSTEM_COMMANDS & set(commands.keys())
        if "start" in inter:
            raise ConfigError(
                "The start command must be specified in the 'messages.*.yml' file"
            )
        if len(inter) > 0:
            commands_str = ", ".join([f"'{command}'" for command in commands])
            raise ConfigError(f"{commands_str} cannot be changed")

        return commands

    model_config = SettingsConfigDict(yaml_file=COMMANDS_PATH, frozen=True)


commands: Commands = Commands()


status = "Failed to check the status of commands"
if not COMMANDS_PATH.exists():
    status = f"No commands loaded: File {str(COMMANDS_PATH)} does not exists."
elif len(commands.model_fields_set) == 0:
    status = f"No commands loaded: File {str(COMMANDS_PATH)} is empty."
else:
    status = f"Commands has been loaded from {str(COMMANDS_PATH)}"
