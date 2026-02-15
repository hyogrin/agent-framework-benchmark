"""Ollama provider for local LLM generation and embeddings."""

import ollama as _ollama_lib

from llm_core.providers.base import BaseLLMProvider, LLMResponse
from llm_core.retry import with_retry


class OllamaProvider(BaseLLMProvider):
    """LLM provider using a local Ollama server."""

    def __init__(self, model: str, host: str = "http://localhost:11434") -> None:
        self._client = _ollama_lib.Client(host=host)
        self._model = model

    @with_retry(max_attempts=3)
    def generate(self, prompt: str, *, system: str = "") -> LLMResponse:
        """Generate a response using the local Ollama server."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self._client.chat(model=self._model, messages=messages)

        return LLMResponse(
            text=response.message.content,
            model=response.model,
            input_tokens=getattr(response, "prompt_eval_count", 0) or 0,
            output_tokens=getattr(response, "eval_count", 0) or 0,
        )


class OllamaEmbeddingProvider:
    """Embedding provider using a local Ollama server."""

    def __init__(self, model: str, host: str = "http://localhost:11434") -> None:
        self._client = _ollama_lib.Client(host=host)
        self._model = model

    @with_retry(max_attempts=3)
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        if not texts:
            return []
        response = self._client.embed(model=self._model, input=texts)
        return response.embeddings
