from orchestrator.core.requests import EmbeddingRequestTemplate, request_templates
from orchestrator.integrations.embedding.http_client import embedding_http_client
from shared.http.client import InternalApiClient


class EmbeddingProvider:
    def __init__(
        self,
        client: InternalApiClient,
        template: EmbeddingRequestTemplate,
    ) -> None:
        self.template = template
        self.client = client

    async def compute_embedding(self, text: str) -> list[float]:
        body = self.template.build(text)
        response_data = await self._send_request(body)
        embedding = self.template.extract(response_data)
        return [float(value) for value in embedding]

    async def _send_request(self, body: dict) -> dict | list:
        return await self.client.request(
            self.template.method,
            self.template.url,
            headers=self.template.headers,
            json_data=body,
        )


embedding_provider = EmbeddingProvider(
    embedding_http_client, request_templates.embedding
)
