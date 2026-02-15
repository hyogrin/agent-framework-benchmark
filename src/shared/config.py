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
