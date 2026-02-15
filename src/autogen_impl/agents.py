"""AutoGen agent definitions for the company research pipeline."""

from autogen_agentchat.agents import AssistantAgent

from shared.prompts import ANALYST_SYSTEM, RESEARCHER_SYSTEM, WRITER_SYSTEM
from shared.config import BenchmarkSettings


def _create_model_client(settings: BenchmarkSettings):
    """Create an AutoGen model client from benchmark settings.

    Args:
        settings: Benchmark configuration.

    Returns:
        Configured AutoGen model client.
    """
    if settings.llm_provider == "ollama":
        from autogen_ext.models.ollama import OllamaChatCompletionClient

        return OllamaChatCompletionClient(
            model=settings.llm_model,
            host=settings.ollama_host,
            temperature=0,
        )
    elif settings.llm_provider in ("lmstudio", "llamacpp"):
        from autogen_ext.models.openai import OpenAIChatCompletionClient

        host = (
            settings.lmstudio_host
            if settings.llm_provider == "lmstudio"
            else settings.llamacpp_host
        )
        return OpenAIChatCompletionClient(
            model=settings.llm_model,
            base_url=f"{host}/v1",
            api_key="local",
            temperature=0,
        )
    elif settings.llm_provider == "openai":
        from autogen_ext.models.openai import OpenAIChatCompletionClient

        return OpenAIChatCompletionClient(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0,
        )
    elif settings.llm_provider == "anthropic":
        # AutoGen 0.7 does not have a native Anthropic client.
        # The Anthropic API is NOT OpenAI-compatible, so we cannot
        # use OpenAIChatCompletionClient with the Anthropic endpoint.
        msg = (
            "AutoGen does not natively support Anthropic. "
            "Use 'ollama' or 'openai' provider instead."
        )
        raise ValueError(msg)
    else:
        msg = f"Unsupported LLM provider: {settings.llm_provider}"
        raise ValueError(msg)


def create_agents(
    company: str, settings: BenchmarkSettings
) -> tuple[AssistantAgent, AssistantAgent, AssistantAgent, object]:
    """Create the researcher, analyst, and writer agents.

    Args:
        company: Company name for research context.
        settings: Benchmark configuration.

    Returns:
        Tuple of (researcher, analyst, writer, model_client).
    """
    model_client = _create_model_client(settings)

    researcher = AssistantAgent(
        name="researcher",
        model_client=model_client,
        system_message=RESEARCHER_SYSTEM.format(company=company),
    )

    analyst = AssistantAgent(
        name="analyst",
        model_client=model_client,
        system_message=ANALYST_SYSTEM.format(company=company),
    )

    writer = AssistantAgent(
        name="writer",
        model_client=model_client,
        system_message=WRITER_SYSTEM.format(company=company),
    )

    return researcher, analyst, writer, model_client
