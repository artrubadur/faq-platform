from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", frozen=True
    )

    env: Literal["dev", "prod"]

    assets: str | None = None
    constants: str | None = None
    messages: str | None = None
    commands: str | None = None

    @model_validator(mode="before")
    def set_defaults(cls, data):
        assets = data.get("assets")
        if assets:
            for field in ["constants", "messages", "commands"]:
                value = data.get(field)
                if value is None:
                    data[field] = assets
                if value == "":
                    data[field] = None

        return data

    tg_bot_token: str

    db_name: str
    db_user: str
    db_pass: str
    db_host: str

    redis_host: str
    redis_pass: str
    redis_ttl: int

    yc_folder_id: str
    yc_api_key: str

    qn_sim_threshold: float


config = Config()  # pyright: ignore[reportCallIssue]
