import json
from copy import deepcopy
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic_settings import SettingsConfigDict

from orchestrator.core.config import config
from shared.utils.config import YamlSettings

REQUESTS_PATH = Path("config/requests.yml")


class RequestPath(BaseModel):
    target: list[str | int]
    source: list[str | int]


class RequestTemplate(BaseModel):
    model_config = ConfigDict(frozen=True)

    method: str = "POST"
    url: str
    headers: dict = Field(default_factory=dict)
    body: dict = Field(default_factory=dict)
    path: RequestPath

    @staticmethod
    def _format_template_value(
        value: str,
        request_vars: dict[str, Any],
        section: str,
        key: str,
    ) -> str:
        try:
            return value.format(**request_vars)
        except KeyError as exc:
            missing = str(exc.args[0])
            raise ValueError(
                f"Unknown request variable '{missing}' in '{section}.{key}'. You have to specify this in the REQUESTS__{missing} enviroment variable."
            )

    @model_validator(mode="before")
    @classmethod
    def interpolate_template_variables(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        request_vars = config.requests.model_dump()

        for section in ("headers", "body"):
            values = data.get(section)
            if not isinstance(values, dict):
                continue

            rendered: dict = {}
            for key, value in values.items():
                if isinstance(value, str):
                    rendered[key] = cls._format_template_value(
                        value, request_vars, section, str(key)
                    )
                else:
                    rendered[key] = value
            data[section] = rendered

        return data


class EmbeddingRequestTemplate(RequestTemplate):
    def build(self, query: str) -> dict:
        body = deepcopy(self.body)
        tokens = self.path.target

        current = body
        for token in tokens[:-1]:
            current = current[token]
        current[tokens[-1]] = query

        return body

    def extract(self, data) -> list[float]:
        current = data
        for token in self.path.source:
            try:
                current = current[token]
            except (KeyError, IndexError, TypeError) as exc:
                raise ValueError(
                    f"Failed to extract embedding from '{self.path.source}' at token '{token}'"
                ) from exc
        return current


@dataclass
class RerankCandidate:
    id: int
    text: str
    score: float


class RerankRequestTemplate(RequestTemplate):
    def build(self, query: str, candidates: list[RerankCandidate]) -> dict:
        body = deepcopy(self.body)
        tokens = self.path.target
        candidates_str = json.dumps([asdict(candidate) for candidate in candidates])

        current = body
        for token in tokens[:-1]:
            current = current[token]
        current[tokens[-1]] = current[tokens[-1]].format(
            query=query, candidates=candidates_str
        )

        return body

    def extract(self, data) -> list[int]:
        current = data
        for token in self.path.source:
            try:
                current = current[token]
            except (KeyError, IndexError, TypeError) as exc:
                raise ValueError(
                    f"Failed to extract ranking from '{self.path.source}' at token '{token}'"
                ) from exc
        return json.loads(current)


class RequestTemplates(YamlSettings):
    model_config = SettingsConfigDict(yaml_file=REQUESTS_PATH, frozen=True)

    embedding: EmbeddingRequestTemplate
    rerank: RerankRequestTemplate | None = None

    @model_validator(mode="after")
    def validate_steps(self):
        if config.suggestion.rerank and self.rerank is None:
            raise ValueError(
                "`rerank` template is required when SUGGESTION_RERANK=true"
            )
        return self


request_templates = RequestTemplates()  # pyright: ignore[reportCallIssue]

status = "Failed to check the status of requests"
if not REQUESTS_PATH.exists() or not REQUESTS_PATH.is_file():
    status = f"No requests loaded: File {str(REQUESTS_PATH)} does not exist. Attempts to access the external api will result in errors."
elif len(request_templates.model_fields_set) == 0:
    status = f"No requests loaded: File {str(REQUESTS_PATH)} is empty. Attempts to access the external api will result in errors."
else:
    status = f"Requests has been loaded from {str(REQUESTS_PATH)}"
