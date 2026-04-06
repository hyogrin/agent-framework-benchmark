"""Benchmark configuration with local-first defaults."""

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BenchmarkSettings(BaseSettings):
    """Benchmark configuration with local-first defaults.

    All settings can be overridden via environment variables with the BENCH_ prefix,
    or via a .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="BENCH_",
        extra="ignore",
    )

    # LLM Serving
    llm_provider: str = "ollama"
    llm_model: str = "qwen3:14b"
    ollama_host: str = "http://localhost:11434"
    lmstudio_host: str = "http://localhost:1234"
    llamacpp_host: str = "http://localhost:8000"

    # Cloud API keys (optional — only needed if llm_provider is openai/anthropic)
    openai_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("OPENAI_API_KEY", "BENCH_OPENAI_API_KEY"),
    )
    anthropic_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("ANTHROPIC_API_KEY", "BENCH_ANTHROPIC_API_KEY"),
    )
    openai_model: str = "gpt-4o"
    anthropic_model: str = "claude-sonnet-4-5-20250929"

    # Azure OpenAI (optional)
    azure_openai_endpoint: str = Field(
        default="",
        validation_alias=AliasChoices("AZURE_OPENAI_ENDPOINT", "BENCH_AZURE_OPENAI_ENDPOINT"),
    )
    azure_openai_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("AZURE_OPENAI_API_KEY", "BENCH_AZURE_OPENAI_API_KEY"),
    )
    azure_openai_api_version: str = Field(
        default="2025-03-01-preview",
        validation_alias=AliasChoices("AZURE_OPENAI_API_VERSION", "BENCH_AZURE_OPENAI_API_VERSION"),
    )
    azure_openai_deployment: str = Field(
        default="",
        validation_alias=AliasChoices(
            "AZURE_AI_MODEL_DEPLOYMENT_NAME",
            "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME",
            "BENCH_AZURE_OPENAI_DEPLOYMENT",
        ),
    )

    # Judge configuration (which LLM evaluates the reports)
    judge_provider: str = "ollama"
    judge_model: str = "qwen3:14b"

    # Benchmark parameters
    companies: list[str] = ["Anthropic", "Stripe", "Datadog"]
    iterations: int = 3
    frameworks: list[str] = [
        "crewai",
        "langgraph",
        "autogen",
        "msagent",
        "agents_sdk",
    ]

    # Output
    results_dir: str = "results"
