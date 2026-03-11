from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr
from pydantic_settings import SettingsConfigDict

from app.core.config import config
from app.core.exceptions import ConfigError
from app.utils.config import YamlSettings


class RequestTemplate(BaseModel):
    model_config = ConfigDict(frozen=True)

    url: str
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"] = "POST"
    headers: dict[str, str] = Field(default_factory=dict)
    body: dict[str, Any] = Field(default_factory=dict)

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
            raise ConfigError(
                f"Unknown request variable '{missing}' in '{section}.{key}'"
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


class EmbeddingRequestTemplate(RequestTemplate):
    embedding_path: str
    text_path: str
    _embedding_path_tokens: tuple[str, ...] = PrivateAttr(default=())
    _text_path_tokens: tuple[str, ...] = PrivateAttr(default=())

    def model_post_init(self, __context) -> None:
        super().model_post_init(__context)
        object.__setattr__(
            self, "_embedding_path_tokens", self._compile_path(self.embedding_path)
        )
        object.__setattr__(
            self, "_text_path_tokens", self._compile_path(self.text_path)
        )

    def _compile_path(self, path: str) -> tuple[str, ...]:
        tokens = []
        for part in path.split("."):
            part = part.strip()
            if not part:
                raise ConfigError("Request response_path contains an empty part")
            tokens.append(part)

        if tokens and tokens[0] == "body":
            tokens = tokens[1:]

        if len(tokens) == 0:
            raise ConfigError("Request text_path contains an empty part")

        return tuple(tokens)

    def build(self, text: str) -> dict[str, Any]:
        body = dict(self.body)
        tokens = self._text_path_tokens

        current = body
        for token in tokens[:-1]:
            current = current.setdefault(token, {})
        current[tokens[-1]] = text

        return {
            "url": self.url,
            "method": self.method,
            "headers": dict(self.headers),
            "body": body,
        }

    def extract(self, data) -> Any:
        current = data
        for token in self._embedding_path_tokens:
            try:
                current = current[token]
            except (KeyError, IndexError, TypeError) as exc:
                raise ConfigError(
                    f"Failed to extract embedding_path '{self.embedding_path}' at token '{token}'"
                ) from exc
        return current


class RequestTemplates(YamlSettings):
    embedding: EmbeddingRequestTemplate

    model_config = SettingsConfigDict(yaml_file=config.paths.requests, frozen=True)


request_templates: RequestTemplates = (
    RequestTemplates()
)  # pyright: ignore[reportCallIssue]


status = "Failed to check the status of requests"
if not config.paths.requests.exists():
    status = f"No requests loaded: File {str(config.paths.requests)} does not exist."
elif len(request_templates.model_fields_set) == 0:
    status = f"No requests loaded: File {str(config.paths.requests)} is empty."
else:
    status = f"Requests has been loaded from {str(config.paths.requests)}"
