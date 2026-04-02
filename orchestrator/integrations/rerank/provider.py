from orchestrator.core.config import config
from orchestrator.core.requests import (
    RerankCandidate,
    RerankRequestTemplate,
    request_templates,
)
from orchestrator.integrations.rerank.http_client import rerank_http_client
from shared.http.client import InternalApiClient


class RerankProvider:
    def __init__(
        self,
        client: InternalApiClient,
        template: RerankRequestTemplate,
    ) -> None:
        self.template = template
        self.client = client

    async def rerank(self, query: str, candidates: list[RerankCandidate]) -> list[int]:
        body = self.template.build(query, candidates)
        response_data = await self._send_request(body)
        reranking = self.template.extract(response_data)
        return reranking

    async def _send_request(self, body: dict) -> dict | list:
        return await self.client.request(
            self.template.method,
            self.template.url,
            headers=self.template.headers,
            json_data=body,
        )


if config.suggestion.rerank:
    template = request_templates.rerank
    client = rerank_http_client
    assert (
        template is not None
    ), "rerank template must be set when SUGGESTION_RERANK=true"
    assert client is not None, "rerank client must be set when SUGGESTION_RERANK=true"
    rerank_provider: RerankProvider | None = RerankProvider(client, template)
else:
    rerank_provider = None
