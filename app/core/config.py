from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RequestsConfig(BaseModel):
    model_config = ConfigDict(extra="allow")


class PathConfig(BaseModel):
    logging: Path = Path("./config/logging.yml")
    constants: Path = Path("./config/bot/constants.yml")
    messages: Path = Path("./config/bot/messages.yml")
    commands: Path = Path("./config/bot/commands.yml")
    requests: Path = Path("./config/api/requests.yml")


class BotConfig(BaseModel):
    token: str
    admins: list = Field(default_factory=list)


class DBConfig(BaseModel):
    name: str
    user: str
    password: str
    host: str


class RedisConfig(BaseModel):
    host: str
    password: str
    long_ttl: int = 86400
    short_ttl: int = 300


class DBSchemaConfig(BaseModel):
    question_text_max_len: int = Field(default=384, ge=1)
    answer_text_max_len: int = Field(default=384, ge=1)
    question_embedding_dim: int = Field(ge=1)


class QuestionsConfig(BaseModel):
    similarest_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    similar_threshold: float = Field(default=0.4, ge=0.0, le=1.0)
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


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        frozen=True,
        env_nested_delimiter="__",
    )

    paths: PathConfig = PathConfig()
    requests: RequestsConfig
    bot: BotConfig
    db: DBConfig
    redis: RedisConfig
    questions: QuestionsConfig = Field(default_factory=QuestionsConfig)
    db_schema: DBSchemaConfig
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)


config = Config()  # pyright: ignore[reportCallIssue]
