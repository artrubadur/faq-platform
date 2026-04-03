from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from shared.api.client import ApiClientConfig


class RequestsConfig(BaseModel):
    model_config = ConfigDict(extra="allow")


class DBConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    user: str
    password: str
    host: str


class DBSchemaConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_text_max_len: int = Field(
        default=384,
        ge=1,
    )
    answer_text_max_len: int = Field(
        default=384,
        ge=1,
    )
    question_embedding_dim: int = Field(
        default=256,
        ge=1,
    )


class SearchConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    best_match_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
    )
    best_match_margin: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
    )
    related_threshold: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
    )
    obvious_margin: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
    )


class SuggestionConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rerank: bool = True
    composition: bool = True


class ApiConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1, le=65535)


class AdminConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ids: list[int] = Field(
        default_factory=list,
    )

    @field_validator("ids", mode="before")
    @classmethod
    def normalize_ids(cls, value):
        if value is None:
            return []

        if isinstance(value, int):
            return [value]

        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return []
            if stripped.startswith("[") and stripped.endswith("]"):
                stripped = stripped[1:-1]
            return [int(item.strip()) for item in stripped.split(",") if item.strip()]

        if isinstance(value, (list, tuple, set)):
            return [int(item) for item in value]

        raise ValueError("ids must be int, list[int], or comma-separated string")


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="env/orchestrator.env",
        env_file_encoding="utf-8",
        frozen=True,
        env_nested_delimiter="__",
        extra="forbid",
    )

    requests: RequestsConfig = Field(default_factory=RequestsConfig)
    db: DBConfig
    db_schema: DBSchemaConfig = Field(default_factory=DBSchemaConfig)
    search: SearchConfig = Field(
        default_factory=SearchConfig,
    )
    suggestion: SuggestionConfig = Field(default_factory=SuggestionConfig)
    embedding_client: ApiClientConfig = Field(default_factory=ApiClientConfig)
    rerank_client: ApiClientConfig = Field(default_factory=ApiClientConfig)
    admin: AdminConfig = Field(
        default_factory=AdminConfig,
    )
    api: ApiConfig = Field(default_factory=ApiConfig)


config = Config()  # pyright: ignore[reportCallIssue]
