"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class LLMResponse:
    """Response from an LLM provider."""

    text: str
    model: str
    input_tokens: int
    output_tokens: int


class BaseLLMProvider(ABC):
    """Abstract interface for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, *, system: str = "") -> LLMResponse:
        """Generate a response from the LLM.

        Args:
            prompt: The user prompt.
            system: Optional system prompt.

        Returns:
            LLMResponse with the generated text and metadata.
        """
        ...
