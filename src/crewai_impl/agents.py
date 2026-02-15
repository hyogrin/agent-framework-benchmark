"""CrewAI agent definitions for the company research pipeline."""

from crewai import Agent, LLM

from shared.prompts import ANALYST_SYSTEM, RESEARCHER_SYSTEM, WRITER_SYSTEM
from shared.config import BenchmarkSettings


def _create_llm(settings: BenchmarkSettings) -> LLM:
    """Create a CrewAI LLM instance from benchmark settings.

    Args:
        settings: Benchmark configuration.

    Returns:
        Configured CrewAI LLM.
    """
    if settings.llm_provider == "ollama":
        # Use CrewAI's native OpenAI provider with Ollama's compatible API
        # to avoid requiring litellm as a dependency.
        return LLM(
            model=settings.llm_model,
            provider="openai",
            base_url=f"{settings.ollama_host}/v1",
            api_key="ollama",
            temperature=0,
        )
    elif settings.llm_provider == "lmstudio":
        return LLM(
            model=settings.llm_model,
            provider="openai",
            base_url=f"{settings.lmstudio_host}/v1",
            api_key="lm-studio",
            temperature=0,
        )
    elif settings.llm_provider == "openai":
        return LLM(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0,
        )
    elif settings.llm_provider == "anthropic":
        return LLM(
            model=settings.anthropic_model,
            api_key=settings.anthropic_api_key,
            temperature=0,
        )
    else:
        msg = f"Unsupported LLM provider: {settings.llm_provider}"
        raise ValueError(msg)


def create_agents(company: str, settings: BenchmarkSettings) -> tuple[Agent, Agent, Agent]:
    """Create the researcher, analyst, and writer agents.

    Args:
        company: Company name for research context.
        settings: Benchmark configuration.

    Returns:
        Tuple of (researcher, analyst, writer) agents.
    """
    llm = _create_llm(settings)

    researcher = Agent(
        role="Senior Company Researcher",
        goal=f"Gather comprehensive information about {company}",
        backstory=RESEARCHER_SYSTEM.format(company=company),
        llm=llm,
        verbose=False,
        allow_delegation=False,
        memory=False,
    )

    analyst = Agent(
        role="Senior Business Analyst",
        goal=f"Analyze research data about {company} and identify key insights",
        backstory=ANALYST_SYSTEM.format(company=company),
        llm=llm,
        verbose=False,
        allow_delegation=False,
        memory=False,
    )

    writer = Agent(
        role="Professional Report Writer",
        goal=f"Create a structured research report about {company}",
        backstory=WRITER_SYSTEM.format(company=company),
        llm=llm,
        verbose=False,
        allow_delegation=False,
        memory=False,
    )

    return researcher, analyst, writer
