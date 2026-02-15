"""OpenAI provider for embeddings."""

from openai import OpenAI

from llm_core.retry import with_retry


class OpenAIEmbeddingProvider:
    """Embedding provider using the OpenAI API."""

    def __init__(self, api_key: str, model: str = "text-embedding-3-small") -> None:
        self._client = OpenAI(api_key=api_key)
        self._model = model

    @with_retry(max_attempts=3)
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        if not texts:
            return []
        response = self._client.embeddings.create(
            model=self._model,
            input=texts,
        )
        return [item.embedding for item in response.data]
