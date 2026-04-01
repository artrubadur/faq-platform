from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class PathsConfig(BaseModel):
    requests: str = "config/orchestrator/requests.yandex.yml"


class RequestsConfig(BaseModel):
    model_config = ConfigDict(extra="allow")


class DBConfig(BaseModel):
    name: str
    user: str
    password: str
    host: str


class DBSchemaConfig(BaseModel):
    max_question_text_len: int = Field(
        default=384,
        ge=1,
        validation_alias=AliasChoices("max_question_text_len", "question_text_max_len"),
    )
    max_answer_text_len: int = Field(
        default=384,
        ge=1,
        validation_alias=AliasChoices(
            "max_answer_text_len",
            "maxanswer_text_len",
            "answer_text_max_len",
        ),
    )
    embedding_dim: int = Field(
        default=256,
        ge=1,
        validation_alias=AliasChoices("embedding_dim", "question_embedding_dim"),
    )
    admins: list[int] = Field(default_factory=list)

    @field_validator("admins", mode="before")
    @classmethod
    def normalize_admins(cls, value):
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

        raise ValueError("admins must be int, list[int], or comma-separated string")


class QuestionsConfig(BaseModel):
    similarest_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    similar_threshold: float = Field(default=0.4, ge=0.0, le=1.0)


class OrchestratorConfig(BaseModel):
    base_url: str
    timeout: float = Field(default=5.0, gt=0)
    retries: int = Field(default=2, ge=0)
    retry_delay: float = Field(default=0.5, ge=0)


class ApiConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1, le=65535)
    title: str = "FAQ Bot Orchestrator"
    version: str = "1.0.0"
    docs_url: str | None = "/docs"
    redoc_url: str | None = "/redoc"
    openapi_url: str | None = "/openapi.json"


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="orchestrator.env",
        env_file_encoding="utf-8",
        frozen=True,
        env_nested_delimiter="__",
        extra="ignore",
    )

    paths: PathsConfig = Field(default_factory=PathsConfig)
    requests: RequestsConfig = Field(default_factory=RequestsConfig)
    db: DBConfig
    db_schema: DBSchemaConfig
    questions: QuestionsConfig = Field(default_factory=QuestionsConfig)
    orchestrator: OrchestratorConfig
    api: ApiConfig = Field(default_factory=ApiConfig)


config = Config()  # pyright: ignore[reportCallIssue]
