from pathlib import Path

from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class PathConfig(BaseModel):
    logging: Path = Path("./config/logging.yml")
    constants: Path = Path("./config/bot/constants.yml")
    messages: Path = Path("./config/bot/messages.yml")
    commands: Path = Path("./config/bot/commands.yml")


class BotConfig(BaseModel):
    token: str


class RedisConfig(BaseModel):
    host: str
    password: str
    long_ttl: int = 86400
    short_ttl: int = 300


class QuestionsConfig(BaseModel):
    max_question_text_len: int = Field(default=384, ge=1)
    max_answer_text_len: int = Field(default=384, ge=1)
    max_similar_amount: int = Field(default=7, ge=0)
    max_popular_amount: int = Field(default=7, ge=0)
    max_amount: int = Field(default=7, ge=1)

    @model_validator(mode="after")
    def validate_amount_limits(self) -> "QuestionsConfig":
        if self.max_similar_amount > self.max_amount:
            raise ValueError("'max_similar_amount' cannot be greater than 'max_amount'")
        if self.max_popular_amount > self.max_amount:
            raise ValueError("'max_popular_amount' cannot be greater than 'max_amount'")
        return self


class RateLimitConfig(BaseModel):
    enabled: bool = True
    max_requests: int = Field(default=5, ge=1)
    window: int = Field(default=10, ge=1)
    skip_admin: bool = True


class OrchestratorConfig(BaseModel):
    base_url: str
    timeout: float = Field(default=5.0, gt=0)
    retries: int = Field(default=2, ge=0)
    retry_delay: float = Field(default=0.5, ge=0)


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="bot.env",
        env_file_encoding="utf-8",
        frozen=True,
        env_nested_delimiter="__",
    )

    paths: PathConfig = Field(default_factory=PathConfig)
    bot: BotConfig
    redis: RedisConfig
    questions: QuestionsConfig = Field(default_factory=QuestionsConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    orchestrator: OrchestratorConfig


config = Config()  # pyright: ignore[reportCallIssue]
