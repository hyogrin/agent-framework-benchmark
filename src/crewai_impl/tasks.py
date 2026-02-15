"""CrewAI task definitions for the company research pipeline."""

from crewai import Agent, Task

from shared.tools import gather_all_search_results


def create_tasks(
    company: str,
    researcher: Agent,
    analyst: Agent,
    writer: Agent,
) -> tuple[Task, Task, Task]:
    """Create the research, analysis, and writing tasks.

    Args:
        company: Company name for research context.
        researcher: The researcher agent.
        analyst: The analyst agent.
        writer: The writer agent.

    Returns:
        Tuple of (research_task, analysis_task, writing_task).
    """
    search_results = gather_all_search_results(company)

    research_task = Task(
        description=(
            f"Research {company} thoroughly using the provided information. "
            f"Compile a comprehensive list of facts organized by category.\n\n"
            f"Available information:\n{search_results}"
        ),
        expected_output=(
            "A structured list of facts about the company organized into categories: "
            "Overview, Leadership, Products & Services, Recent News, Market Position, "
            "and Financial Metrics."
        ),
        agent=researcher,
    )

    analysis_task = Task(
        description=(
            f"Analyze the research data about {company}. Identify key strengths, "
            "risks, market trends, competitive advantages, and strategic insights. "
            "Provide data-driven analysis with clear reasoning."
        ),
        expected_output=(
            "A detailed analysis covering: key strengths, potential risks, "
            "market trends, competitive advantages, and strategic insights."
        ),
        agent=analyst,
    )

    writing_task = Task(
        description=(
            f"Write a professional research report about {company} with these sections: "
            "Executive Summary, Company Overview, Products & Services, Market Position, "
            "Key Insights, and Conclusion. The report should be 500-800 words."
        ),
        expected_output=(
            "A well-structured research report of 500-800 words with clear sections: "
            "Executive Summary, Company Overview, Products & Services, Market Position, "
            "Key Insights, and Conclusion."
        ),
        agent=writer,
    )

    return research_task, analysis_task, writing_task
