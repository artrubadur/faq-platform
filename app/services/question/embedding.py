from app.core.exceptions import YandexAPIError

from .sdk_instance import sdk


class EmbeddingService:
    def __init__(self, new_sdk=None) -> None:
        self.sdk = new_sdk or sdk
        self.model = self.sdk.models.text_embeddings("query")

    async def compute(self, text: str) -> tuple[float, ...]:
        try:
            response = await self.model.run(text)
            return response.embedding
        except Exception:
            raise YandexAPIError(
                "Failed to compute vector representation of question",
            )


embedding_service = EmbeddingService()
