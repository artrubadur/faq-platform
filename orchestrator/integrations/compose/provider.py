from orchestrator.core.config import config
from orchestrator.core.requests import (
    ComposeCandidate,
    ComposeRequestTemplate,
    request_templates,
)
from orchestrator.integrations.compose.http_client import compose_http_client
from shared.api.client import ApiClient


class ComposeProvider:
    def __init__(
        self,
        client: ApiClient,
        template: ComposeRequestTemplate,
    ) -> None:
        self.template = template
        self.client = client

    async def compose(
        self,
        query: str,
        best_candidate: ComposeCandidate,
        supporting_candidates: list[ComposeCandidate],
    ) -> str:
        body = self.template.build(query, best_candidate, supporting_candidates)
        response_data = await self._send_request(body)
        composition = self.template.extract(response_data)
        return composition

    async def _send_request(self, body: dict) -> dict | list:
        return await self.client.request(
            self.template.method,
            self.template.url,
            headers=self.template.headers,
            json_data=body,
        )


if config.suggestion.compose.enabled:
    template = request_templates.compose
    client = compose_http_client
    assert (
        template is not None
    ), "compose template must be set when SUGGESTION__COMPOSE__ENABLED=true"
    assert (
        client is not None
    ), "compose client must be set when SUGGESTION__COMPOSE__ENABLED=true"
    compose_provider: ComposeProvider | None = ComposeProvider(client, template)
else:
    compose_provider = None
