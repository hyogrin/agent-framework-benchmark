"""Anthropic LLM provider adapter."""

from anthropic import Anthropic

from llm_core.providers.base import BaseLLMProvider, LLMResponse
from llm_core.retry import with_retry


class AnthropicProvider(BaseLLMProvider):
    """LLM provider using the Anthropic API (Claude models)."""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-latest", max_tokens: int = 4096) -> None:
        self._client = Anthropic(api_key=api_key)
        self._model = model
        self._max_tokens = max_tokens

    @with_retry(max_attempts=3)
    def generate(self, prompt: str, *, system: str = "") -> LLMResponse:
        """Generate a response using the Anthropic API."""
        message = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return LLMResponse(
            text=message.content[0].text,
            model=message.model,
            input_tokens=message.usage.input_tokens,
            output_tokens=message.usage.output_tokens,
        )
