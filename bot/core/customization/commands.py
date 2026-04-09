from pathlib import Path
from typing import Any, Literal

from aiogram.types import LinkPreviewOptions
from pydantic import Field, field_validator, model_validator
from pydantic_settings import SettingsConfigDict

from bot.core.customization.constants import constants
from bot.core.customization.messages import _MESSAGES_PATH
from bot.utils.config.formatter import SafeFormatter
from bot.utils.config.send_text import SendText, parse_link_preview
from shared.utils.config import YamlSettings

_SYSTEM_COMMANDS = {"start", "ask", "goto", "state", "settings", "error"}
_COMMANDS_PATH = Path("config/commands.yml")


class Commands(YamlSettings):
    model_config = SettingsConfigDict(yaml_file=_COMMANDS_PATH, frozen=True)

    parse_mode: Literal["html", "markdown", "markdownv2", None] = "html"
    link_preview: LinkPreviewOptions | None = None

    @field_validator("parse_mode", mode="before")
    def validate_parse_mode(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v

    @field_validator("link_preview", mode="before")
    def validate_link_preview(cls, v):
        return parse_link_preview(v)

    commands: dict[str, SendText] = Field(default_factory=dict)

    @field_validator("commands", mode="before")
    def apply_constants_and_link_preview(
        cls, commands: dict[str, Any]
    ) -> dict[str, SendText]:
        if not isinstance(commands, dict):
            raise ValueError("commands must be a dict")

        formatter = SafeFormatter()

        def _format(text: str) -> str:
            try:
                return formatter.format(text, constants=constants.constants)
            except (AttributeError, ValueError) as exc:
                raise ValueError(
                    "Attempt to access a non-existent constant in commands config"
                ) from exc

        for command, value in commands.items():
            if isinstance(value, str):
                commands[command] = _format(value)
                continue

            if isinstance(value, dict):
                text = value.get("text")
                if isinstance(text, str):
                    commands[command]["text"] = _format(text)

                continue

        inter = _SYSTEM_COMMANDS & set(commands.keys())
        if "start" in inter:
            raise ValueError(
                f"The start command must be specified in the '{str(_MESSAGES_PATH)}' file"
            )
        if len(inter) > 0:
            commands_str = ", ".join([f"'{command}'" for command in commands])
            raise ValueError(f"{commands_str} cannot be changed")

        return {
            command: SendText.from_config(value) for command, value in commands.items()
        }

    @model_validator(mode="after")
    def apply_default_link_preview(self) -> "Commands":
        for command in self.commands.values():
            command.apply_global_link_preview(self.link_preview)

        return self


commands: Commands = Commands()


status = "Failed to check the status of commands"
if not _COMMANDS_PATH.exists() or not _COMMANDS_PATH.is_file():
    status = f"No commands loaded: File {str(_COMMANDS_PATH)} does not exist."
elif len(commands.model_fields_set) == 0:
    status = f"No commands loaded: File {str(_COMMANDS_PATH)} is empty."
else:
    status = f"Commands have been loaded from {str(_COMMANDS_PATH)}"
