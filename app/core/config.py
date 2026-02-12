from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    env: str

    tg_bot_token: str

    db_name: str
    db_user: str
    db_pass: str
    db_host: str

    yc_folder_id: str
    yc_api_key: str

    qn_sim_threshold: float


config = Config()  # pyright: ignore[reportCallIssue]
