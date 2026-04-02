from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr
from pydantic_settings import SettingsConfigDict

from orchestrator.core.config import config
from shared.utils.config import YamlSettings

REQUESTS_PATH = Path("config/requests.yml")


class RequestTemplate(BaseModel):
    model_config = ConfigDict(frozen=True)

    method: str = "POST"
    url: str
    headers: dict = Field(default_factory=dict)
    body: dict = Field(default_factory=dict)

    def _format_template_value(
        self,
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

    def model_post_init(self, __context) -> None:
        request_vars = config.requests.model_dump()

        headers = {}
        for key, value in self.headers.items():
            if isinstance(value, str):
                headers[key] = self._format_template_value(
                    value, request_vars, "headers", key
                )
            else:
                headers[key] = value

        body = {}
        for key, value in self.body.items():
            if isinstance(value, str):
                body[key] = self._format_template_value(
                    value, request_vars, "body", key
                )
            else:
                body[key] = value

        object.__setattr__(self, "headers", headers)
        object.__setattr__(self, "body", body)


class EmbeddingRequestPaths(BaseModel):
    embedding: list[str | int]
    text: list[str | int]

class EmbeddingRequestTemplate(RequestTemplate):
    path: EmbeddingRequestPaths

    def build(self, text: str) -> dict:
        body = dict(self.body)
        tokens = self.path.text

        current = body
        for token in tokens[:-1]:
            current = current.setdefault(token, {})
        current[tokens[-1]] = text

        return body

    def extract(self, data) -> Any:
        current = data
        for token in self.path.embedding:
            try:
                current = current[token]
            except (KeyError, IndexError, TypeError) as exc:
                raise ValueError(
                    f"Failed to extract embedding by '{self.path.embedding}' at token '{token}'"
                ) from exc
        return current


class RequestTemplates(YamlSettings):
    embedding: EmbeddingRequestTemplate

    model_config = SettingsConfigDict(yaml_file=REQUESTS_PATH, frozen=True)


request_templates = RequestTemplates()  # pyright: ignore[reportCallIssue]

status = "Failed to check the status of requests"
if not REQUESTS_PATH.exists() or not REQUESTS_PATH.is_file():
    status = f"No requests loaded: File {str(REQUESTS_PATH)} does not exist. Attempts to access the external api will result in errors."
elif len(request_templates.model_fields_set) == 0:
    status = f"No requests loaded: File {str(REQUESTS_PATH)} is empty. Attempts to access the external api will result in errors."
else:
    status = f"Requests has been loaded from {str(REQUESTS_PATH)}"
