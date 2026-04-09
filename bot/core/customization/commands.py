from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import SettingsConfigDict

from bot.core.customization.constants import constants
from bot.core.customization.formatter import SafeFormatter
from bot.core.customization.messages import _MESSAGES_PATH
from shared.utils.config import YamlSettings

_SYSTEM_COMMANDS = {"start", "ask", "goto", "state", "settings", "error"}
_COMMANDS_PATH = Path("config/commands.yml")


class Commands(YamlSettings):
    model_config = SettingsConfigDict(yaml_file=_COMMANDS_PATH, frozen=True)

    parse_mode: Literal["html", "markdown", "markdownv2", None] = "html"

    @field_validator("parse_mode", mode="before")
    def validate_parse_mode(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v

    commands: dict[str, str] = Field(default_factory=dict)

    @field_validator("commands", mode="before")
    def apply_constants(cls, commands: dict[str, str]) -> dict[str, str]:
        formatter = SafeFormatter()

        for command, value in commands.items():
            try:
                commands[command] = formatter.format(
                    value,
                    constants=constants.constants,
                )  # pyright: ignore[reportCallIssue]
            except AttributeError as exc:
                raise ValueError(
                    f"Attempt to access a non-existent constant: {value}"
                ) from exc

        return commands

    @field_validator("commands", mode="before")
    def validate_commands(cls, commands: dict[str, str]) -> dict[str, str]:
        inter = _SYSTEM_COMMANDS & set(commands.keys())
        if "start" in inter:
            raise ValueError(
                f"The start command must be specified in the '{str(_MESSAGES_PATH)}' file"
            )
        if len(inter) > 0:
            commands_str = ", ".join([f"'{command}'" for command in commands])
            raise ValueError(f"{commands_str} cannot be changed")

        return commands


commands: Commands = Commands()


status = "Failed to check the status of commands"
if not _COMMANDS_PATH.exists() or not _COMMANDS_PATH.is_file():
    status = f"No commands loaded: File {str(_COMMANDS_PATH)} does not exist."
elif len(commands.model_fields_set) == 0:
    status = f"No commands loaded: File {str(_COMMANDS_PATH)} is empty."
else:
    status = f"Commands have been loaded from {str(_COMMANDS_PATH)}"
