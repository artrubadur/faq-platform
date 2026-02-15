from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)
from pydantic_settings_yaml import YamlBaseSettings

CONFIG_DIR = Path.cwd() / "config" / "responses.yml"


class SearchExceptions(BaseModel):
    empty_result: str = "It seems that we failed to understand the question"


class Exceptions(BaseModel):
    search: SearchExceptions = SearchExceptions()


class Responses(YamlBaseSettings):
    commands: dict[str, str] = {}
    exceptions: Exceptions = Exceptions()

    start_template: str = (
        "Hello, {username}! I will help you find the answer — just send a question"
        "or choose one of the most popular ones below!"
    )
    failed_template: str = "{exception}. Try to reformulate it and ask again"

    model_config = SettingsConfigDict(yaml_file=CONFIG_DIR, secrets_dir=None)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (init_settings, env_settings, YamlConfigSettingsSource(settings_cls))


responses: Responses = Responses()
