"""Configuration for LLM and RAG settings via environment variables."""

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_model_string(model_string: str) -> tuple[str, str]:
    """Parse a provider:model string into (provider, model) tuple.

    Examples:
        'ollama:llama3.2'        -> ('ollama', 'llama3.2')
        'ollama:nomic-embed-text' -> ('ollama', 'nomic-embed-text')
        'claude-3-5-sonnet-latest' -> ('', 'claude-3-5-sonnet-latest')
    """
    if ":" in model_string:
        provider, _, model = model_string.partition(":")
        return (provider.lower(), model)
    return ("", model_string)


class LLMSettings(BaseSettings):
    """Settings loaded from environment variables.

    RAG-specific settings use RAG_CLI_ prefix. API keys use standard names.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="RAG_CLI_",
        extra="ignore",
    )

    # API keys — no prefix, standard env var names
    # Defaults to "" so settings load without keys (validated at usage time)
    anthropic_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("ANTHROPIC_API_KEY", "RAG_CLI_ANTHROPIC_API_KEY"),
    )
    openai_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("OPENAI_API_KEY", "RAG_CLI_OPENAI_API_KEY"),
    )

    # Ollama settings
    ollama_host: str = "http://localhost:11434"

    # Model settings
    model: str = "claude-3-5-sonnet-latest"
    embedding_model: str = "text-embedding-3-small"

    # Chunking settings
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # Retrieval settings
    top_k: int = 3
