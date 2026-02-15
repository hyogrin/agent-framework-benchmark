"""OpenAI Agents SDK pipeline execution for the company research pipeline."""

import asyncio

from openai import AsyncOpenAI
from agents import Runner, set_default_openai_client

from shared.config import BenchmarkSettings
from shared.tools import gather_all_search_results
from agents_sdk_impl.agents import create_agents


def _configure_client(settings: BenchmarkSettings) -> None:
    """Configure the default OpenAI client based on benchmark settings.

    For local providers (Ollama, LM Studio, llama.cpp), this points the
    OpenAI client at the local server's OpenAI-compatible API endpoint.

    Args:
        settings: Benchmark configuration.
    """
    if settings.llm_provider == "ollama":
        client = AsyncOpenAI(
            base_url=f"{settings.ollama_host}/v1",
            api_key="ollama",
        )
        set_default_openai_client(client)
    elif settings.llm_provider == "lmstudio":
        client = AsyncOpenAI(
            base_url=f"{settings.lmstudio_host}/v1",
            api_key="lm-studio",
        )
        set_default_openai_client(client)
    elif settings.llm_provider == "llamacpp":
        client = AsyncOpenAI(
            base_url=f"{settings.llamacpp_host}/v1",
            api_key="local",
        )
        set_default_openai_client(client)
    elif settings.llm_provider == "openai":
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        set_default_openai_client(client)
    elif settings.llm_provider == "anthropic":
        # OpenAI Agents SDK doesn't natively support Anthropic;
        # use litellm prefix if available or raise error
        msg = (
            "OpenAI Agents SDK does not natively support Anthropic. "
            "Use 'ollama' or 'openai' provider instead."
        )
        raise ValueError(msg)


async def run_async(company: str, settings: BenchmarkSettings) -> tuple[str, dict]:
    """Run OpenAI Agents SDK implementation (async).

    Args:
        company: Company name to research.
        settings: Benchmark configuration.

    Returns:
        Tuple of (report_text, token_usage_dict).
    """
    _configure_client(settings)
    researcher, analyst, writer, _model = create_agents(company, settings)

    search_results = gather_all_search_results(company)

    # Sequential: researcher -> analyst -> writer
    research_input = (
        f"Research {company} using the following information and compile "
        f"a structured list of facts:\n\n{search_results}"
    )
    research_result = await Runner.run(researcher, research_input)

    analysis_input = (
        f"Analyze the following research data about {company} and provide "
        f"key insights:\n\n{research_result.final_output}"
    )
    analysis_result = await Runner.run(analyst, analysis_input)

    writing_input = (
        f"Write a professional research report about {company} (500-800 words) "
        f"based on the following research and analysis:\n\n"
        f"## Research\n{research_result.final_output}\n\n"
        f"## Analysis\n{analysis_result.final_output}"
    )
    report_result = await Runner.run(writer, writing_input)

    # Extract token usage from RunResult.raw_responses.
    # The Agents SDK wraps responses in ModelResponse objects whose usage
    # fields are named input_tokens/output_tokens (not prompt_tokens/completion_tokens).
    token_usage = {"prompt": 0, "completion": 0}
    for result in (research_result, analysis_result, report_result):
        if hasattr(result, "raw_responses"):
            for response in result.raw_responses:
                usage = getattr(response, "usage", None)
                if usage:
                    token_usage["prompt"] += getattr(usage, "input_tokens", 0) or 0
                    token_usage["completion"] += getattr(usage, "output_tokens", 0) or 0

    return report_result.final_output, token_usage


def run(company: str, settings: BenchmarkSettings) -> tuple[str, dict]:
    """Sync wrapper for OpenAI Agents SDK async implementation.

    Args:
        company: Company name to research.
        settings: Benchmark configuration.

    Returns:
        Tuple of (report_text, token_usage_dict).
    """
    return asyncio.run(run_async(company, settings))
