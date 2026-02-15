"""MS Agent Framework agent definitions for the company research pipeline."""

from agent_framework import Agent, ChatOptions

from shared.prompts import ANALYST_SYSTEM, RESEARCHER_SYSTEM, WRITER_SYSTEM
from shared.config import BenchmarkSettings


def _create_chat_client(settings: BenchmarkSettings):
    """Create an MS Agent Framework chat client from benchmark settings.

    Args:
        settings: Benchmark configuration.

    Returns:
        Configured chat client.
    """
    if settings.llm_provider == "ollama":
        from agent_framework.ollama import OllamaChatClient

        return OllamaChatClient(
            model_id=settings.llm_model,
            host=settings.ollama_host,
        )
    elif settings.llm_provider in ("lmstudio", "llamacpp"):
        from agent_framework.openai import OpenAIChatClient

        host = (
            settings.lmstudio_host
            if settings.llm_provider == "lmstudio"
            else settings.llamacpp_host
        )
        return OpenAIChatClient(
            model_id=settings.llm_model,
            api_key="local",
            endpoint=f"{host}/v1",
        )
    elif settings.llm_provider == "openai":
        from agent_framework.openai import OpenAIChatClient

        return OpenAIChatClient(
            model_id=settings.openai_model,
            api_key=settings.openai_api_key,
        )
    elif settings.llm_provider == "anthropic":
        # MS Agent Framework beta does not have a native Anthropic client.
        # The Anthropic API is NOT OpenAI-compatible, so we cannot
        # use OpenAIChatClient with the Anthropic endpoint.
        msg = (
            "MS Agent Framework does not natively support Anthropic. "
            "Use 'ollama' or 'openai' provider instead."
        )
        raise ValueError(msg)
    else:
        msg = f"Unsupported LLM provider: {settings.llm_provider}"
        raise ValueError(msg)


def create_agents(
    company: str, settings: BenchmarkSettings
) -> tuple[Agent, Agent, Agent]:
    """Create the researcher, analyst, and writer agents.

    Args:
        company: Company name for research context.
        settings: Benchmark configuration.

    Returns:
        Tuple of (researcher, analyst, writer) agents.
    """
    client = _create_chat_client(settings)
    opts: ChatOptions = {"temperature": 0}

    researcher = Agent(
        client=client,
        instructions=RESEARCHER_SYSTEM.format(company=company),
        name="researcher",
        default_options=opts,
    )

    analyst = Agent(
        client=client,
        instructions=ANALYST_SYSTEM.format(company=company),
        name="analyst",
        default_options=opts,
    )

    writer = Agent(
        client=client,
        instructions=WRITER_SYSTEM.format(company=company),
        name="writer",
        default_options=opts,
    )

    return researcher, analyst, writer
