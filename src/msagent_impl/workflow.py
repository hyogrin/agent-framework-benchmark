"""MS Agent Framework workflow execution for the company research pipeline."""

import asyncio

from agent_framework.orchestrations import SequentialBuilder

from shared.config import BenchmarkSettings
from shared.tools import gather_all_search_results
from msagent_impl.agents import create_agents


async def run_async(company: str, settings: BenchmarkSettings) -> tuple[str, dict]:
    """Run MS Agent Framework implementation (async).

    Args:
        company: Company name to research.
        settings: Benchmark configuration.

    Returns:
        Tuple of (report_text, token_usage_dict).
    """
    researcher, analyst, writer = create_agents(company, settings)

    workflow = SequentialBuilder(participants=[researcher, analyst, writer]).build()

    search_results = gather_all_search_results(company)

    task = (
        f"Research and write a comprehensive report about {company}. "
        f"Here is the available research data:\n\n{search_results}\n\n"
        f"The researcher should organize the facts, the analyst should identify "
        f"key insights, and the writer should produce the final 500-800 word report."
    )

    result = await workflow.run(task)

    # Extract the final report — pick the longest assistant message,
    # as the framework may split responses across multiple messages.
    report_text = ""
    outputs = result.get_outputs()
    if outputs:
        last_messages = outputs[-1]
        for msg in last_messages:
            if msg.role == "assistant" and msg.text and len(msg.text) > len(report_text):
                report_text = msg.text

    # Token tracking is limited in the beta Ollama backend
    token_usage = {"prompt": 0, "completion": 0}

    return report_text, token_usage


def run(company: str, settings: BenchmarkSettings) -> tuple[str, dict]:
    """Sync wrapper for MS Agent Framework async implementation.

    Args:
        company: Company name to research.
        settings: Benchmark configuration.

    Returns:
        Tuple of (report_text, token_usage_dict).
    """
    return asyncio.run(run_async(company, settings))
