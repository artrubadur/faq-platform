from orchestrator.core.config import config
from orchestrator.core.requests import GenerationRequestTemplate, request_templates
from orchestrator.integrations.generation.http_client import generation_http_client
from shared.api.client import ApiClient


class GenerationProvider:
    def __init__(
        self,
        client: ApiClient,
        template: GenerationRequestTemplate,
    ) -> None:
        self.template = template
        self.client = client

    async def generate(
        self,
        question_text: str,
        amount: int,
    ) -> list[str]:
        body = self.template.build(question_text, amount)
        response_data = await self._send_request(body)
        formulations = self.template.extract(response_data)
        return formulations

    async def _send_request(self, body: dict) -> dict | list:
        return await self.client.request(
            self.template.method,
            self.template.url,
            headers=self.template.headers,
            json_data=body,
        )


if config.suggestion.generation.enabled:
    template = request_templates.generation
    client = generation_http_client
    assert (
        template is not None
    ), "generation template must be set when SUGGESTION__GENERATION__ENABLED=true"
    assert (
        client is not None
    ), "generation client must be set when SUGGESTION__GENERATION__ENABLED=true"
    generation_provider: GenerationProvider | None = GenerationProvider(
        client, template
    )
else:
    generation_provider = None
