"""OpenAI Agents SDK agent definitions for the company research pipeline."""

from agents import Agent, ModelSettings

from shared.prompts import ANALYST_SYSTEM, RESEARCHER_SYSTEM, WRITER_SYSTEM
from shared.config import BenchmarkSettings


def create_agents(
    company: str, settings: BenchmarkSettings
) -> tuple[Agent, Agent, Agent, str]:
    """Create the researcher, analyst, and writer agents.

    Args:
        company: Company name for research context.
        settings: Benchmark configuration.

    Returns:
        Tuple of (researcher, analyst, writer, model_name).
    """
    if settings.llm_provider == "openai":
        model = settings.openai_model
    elif settings.llm_provider == "anthropic":
        model = settings.anthropic_model
    else:
        model = settings.llm_model

    researcher = Agent(
        name="Researcher",
        model=model,
        instructions=RESEARCHER_SYSTEM.format(company=company),
        model_settings=ModelSettings(temperature=0),
    )

    analyst = Agent(
        name="Analyst",
        model=model,
        instructions=ANALYST_SYSTEM.format(company=company),
        model_settings=ModelSettings(temperature=0),
    )

    writer = Agent(
        name="Writer",
        model=model,
        instructions=WRITER_SYSTEM.format(company=company),
        model_settings=ModelSettings(temperature=0),
    )

    return researcher, analyst, writer, model
