"""CrewAI crew assembly and execution."""

from crewai import Crew, Process

from shared.config import BenchmarkSettings
from crewai_impl.agents import create_agents
from crewai_impl.tasks import create_tasks


def create_crew(company: str, settings: BenchmarkSettings) -> Crew:
    """Create and return a CrewAI crew for company research.

    Args:
        company: Company name to research.
        settings: Benchmark configuration.

    Returns:
        Configured Crew ready to execute.
    """
    researcher, analyst, writer = create_agents(company, settings)
    research_task, analysis_task, writing_task = create_tasks(
        company, researcher, analyst, writer
    )

    return Crew(
        agents=[researcher, analyst, writer],
        tasks=[research_task, analysis_task, writing_task],
        process=Process.sequential,
        verbose=False,
    )


def run(company: str, settings: BenchmarkSettings) -> tuple[str, dict]:
    """Run CrewAI implementation.

    Args:
        company: Company name to research.
        settings: Benchmark configuration.

    Returns:
        Tuple of (report_text, token_usage_dict).
    """
    crew = create_crew(company, settings)
    result = crew.kickoff()

    # Extract token usage from CrewAI's built-in tracking
    token_usage = {
        "prompt": 0,
        "completion": 0,
    }
    if hasattr(result, "token_usage") and result.token_usage:
        usage = result.token_usage
        # CrewAI returns token_usage as a dict, not an object
        if isinstance(usage, dict):
            token_usage["prompt"] = usage.get("prompt_tokens", 0) or 0
            token_usage["completion"] = usage.get("completion_tokens", 0) or 0
        else:
            token_usage["prompt"] = getattr(usage, "prompt_tokens", 0) or 0
            token_usage["completion"] = getattr(usage, "completion_tokens", 0) or 0

    return result.raw, token_usage
