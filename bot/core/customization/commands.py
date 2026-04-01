from pydantic import Field, field_validator
from pydantic_settings import SettingsConfigDict

from bot.core.config import config
from bot.core.customization.constants import BOT_SYSTEM_KEYS, constants
from bot.core.customization.formatter import SafeFormatter
from bot.utils.config import YamlSettings

SYSTEM_COMMANDS = {"start", "ask", "goto", "state", "settings", "error"}


class Commands(YamlSettings):
    commands: dict[str, str] = Field(default_factory=dict)

    @field_validator("commands", mode="before")
    def apply_constants(cls, commands: dict[str, str]) -> dict[str, str]:
        formatter = SafeFormatter(BOT_SYSTEM_KEYS)

        for command, value in commands.items():
            try:
                commands[command] = formatter.format(
                    value, **constants.model_extra
                )  # pyright: ignore[reportCallIssue]
            except AttributeError as exc:
                raise ValueError(
                    f"Attempt to access a non-existent constant: {value}"
                ) from exc

        return commands

    @field_validator("commands", mode="before")
    def validate_commands(cls, commands: dict[str, str]) -> dict[str, str]:
        inter = SYSTEM_COMMANDS & set(commands.keys())
        if "start" in inter:
            raise ValueError(
                "The start command must be specified in the 'PATH__COMMANDS' file"
            )
        if len(inter) > 0:
            commands_str = ", ".join([f"'{command}'" for command in commands])
            raise ValueError(f"{commands_str} cannot be changed")

        return commands

    model_config = SettingsConfigDict(yaml_file=config.paths.commands, frozen=True)


commands: Commands = Commands()


status = "Failed to check the status of commands"
if not config.paths.commands.exists():
    status = f"No commands loaded: File {str(config.paths.commands)} does not exists."
elif len(commands.model_fields_set) == 0:
    status = f"No commands loaded: File {str(config.paths.commands)} is empty."
else:
    status = f"Commands has been loaded from {str(config.paths.commands)}"
