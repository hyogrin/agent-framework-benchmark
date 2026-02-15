"""MS Agent Framework workflow execution for the company research pipeline."""

import asyncio

from agent_framework import add_usage_details
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

    # Extract token usage from workflow events.
    # AgentExecutor emits executor_invoked events carrying AgentExecutorResponse
    # whose agent_response.usage_details holds the Ollama token counts
    # (prompt_eval_count → input_token_count, eval_count → output_token_count).
    combined_usage = None
    for event in result:
        data = event.data
        if data is not None and hasattr(data, "agent_response"):
            usage = getattr(data.agent_response, "usage_details", None)
            if usage:
                combined_usage = add_usage_details(combined_usage, usage)

    token_usage = {
        "prompt": (combined_usage or {}).get("input_token_count", 0) or 0,
        "completion": (combined_usage or {}).get("output_token_count", 0) or 0,
    }

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
