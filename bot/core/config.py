from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from shared.api.client import ApiClientConfig


class BotConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str


class RedisConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    host: str
    password: str
    long_ttl: int = 86400
    short_ttl: int = 300


class QuestionLimitsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    max_question_text_len: int = Field(default=384, ge=1)
    max_answer_text_len: int = Field(
        default=384,
        ge=1,
    )
    max_similar_amount: int = Field(default=7, ge=0)
    max_popular_amount: int = Field(default=7, ge=0)
    max_amount: int = Field(default=7, ge=1)

    @model_validator(mode="after")
    def validate_amount_limits(self) -> "QuestionLimitsConfig":
        if self.max_similar_amount > self.max_amount:
            raise ValueError("'max_similar_amount' cannot be greater than 'max_amount'")
        if self.max_popular_amount > self.max_amount:
            raise ValueError("'max_popular_amount' cannot be greater than 'max_amount'")
        return self


class RateLimitConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    max_requests: int = Field(default=5, ge=1)
    window: int = Field(default=10, ge=1)
    skip_admin: bool = True


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="env/bot.env",
        env_file_encoding="utf-8",
        frozen=True,
        env_nested_delimiter="__",
        extra="forbid",
    )

    bot: BotConfig
    redis: RedisConfig
    question_limits: QuestionLimitsConfig = Field(
        default_factory=QuestionLimitsConfig,
    )
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    orchestrator_client: ApiClientConfig


config = Config()  # pyright: ignore[reportCallIssue]
