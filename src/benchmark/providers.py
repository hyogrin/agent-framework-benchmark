"""LLM providers for benchmark judge evaluation."""

from openai import AzureOpenAI, OpenAI

from llm_core.providers.base import BaseLLMProvider, LLMResponse
from llm_core.retry import with_retry


def _get_azure_token_provider():
    """Create an Azure AD token provider using DefaultAzureCredential."""
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider

    return get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )


class OpenAIProvider(BaseLLMProvider):
    """OpenAI chat provider implementing BaseLLMProvider.

    Used by the benchmark judge for evaluation when the judge provider
    is set to 'openai'. The vendored llm_core only ships an embedding
    provider for OpenAI, so this fills the chat completion gap.

    Args:
        api_key: OpenAI API key.
        model: Model identifier (e.g. 'gpt-4o').
    """

    def __init__(self, api_key: str, model: str) -> None:
        self._client = OpenAI(api_key=api_key)
        self._model = model

    @with_retry(max_attempts=3)
    def generate(self, prompt: str, *, system: str = "") -> LLMResponse:
        """Generate a chat completion response.

        Args:
            prompt: The user prompt.
            system: Optional system prompt.

        Returns:
            LLMResponse with the generated text and token metadata.
        """
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0,
        )
        choice = response.choices[0]
        usage = response.usage
        return LLMResponse(
            text=choice.message.content or "",
            model=self._model,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
        )


class AzureOpenAIProvider(BaseLLMProvider):
    """Azure OpenAI chat provider implementing BaseLLMProvider.

    Args:
        api_key: Azure OpenAI API key.
        endpoint: Azure OpenAI endpoint URL.
        deployment: Model deployment name.
        api_version: API version string.
    """

    def __init__(
        self, api_key: str, endpoint: str, deployment: str, api_version: str
    ) -> None:
        self._client = AzureOpenAI(
            azure_ad_token_provider=_get_azure_token_provider(),
            azure_endpoint=endpoint,
            api_version=api_version,
        )
        self._deployment = deployment

    @with_retry(max_attempts=3)
    def generate(self, prompt: str, *, system: str = "") -> LLMResponse:
        """Generate a chat completion response.

        Args:
            prompt: The user prompt.
            system: Optional system prompt.

        Returns:
            LLMResponse with the generated text and token metadata.
        """
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = self._client.chat.completions.create(
            model=self._deployment,
            messages=messages,
            temperature=0,
        )
        choice = response.choices[0]
        usage = response.usage
        return LLMResponse(
            text=choice.message.content or "",
            model=self._deployment,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
        )
