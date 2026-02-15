"""AutoGen workflow execution for the company research pipeline."""

import asyncio

from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat

from shared.config import BenchmarkSettings
from shared.tools import gather_all_search_results
from autogen_impl.agents import create_agents


async def run_async(company: str, settings: BenchmarkSettings) -> tuple[str, dict]:
    """Run AutoGen implementation (async).

    Args:
        company: Company name to research.
        settings: Benchmark configuration.

    Returns:
        Tuple of (report_text, token_usage_dict).
    """
    researcher, analyst, writer, model_client = create_agents(company, settings)

    search_results = gather_all_search_results(company)

    # MaxMessageTermination(4) = 1 user message + 3 agent responses (one round).
    # This matches the sequential pipeline: researcher -> analyst -> writer.
    # We avoid TextMentionTermination because the trigger word in any message
    # (including the initial task) causes immediate termination.
    termination = MaxMessageTermination(4)
    team = RoundRobinGroupChat(
        [researcher, analyst, writer],
        termination_condition=termination,
    )

    task = (
        f"Research and write a comprehensive report about {company}. "
        f"Here is the available research data:\n\n{search_results}\n\n"
        f"The researcher should organize the facts, the analyst should identify "
        f"key insights, and the writer should produce the final 500-800 word report."
    )

    result = await team.run(task=task)

    # Collect token usage from messages
    total_tokens = {"prompt": 0, "completion": 0}
    for msg in result.messages:
        if hasattr(msg, "models_usage") and msg.models_usage:
            total_tokens["prompt"] += msg.models_usage.prompt_tokens or 0
            total_tokens["completion"] += msg.models_usage.completion_tokens or 0

    # Close the model client
    if hasattr(model_client, "close"):
        await model_client.close()

    # Extract the last substantive message as the report.
    # Strip thinking tags that Qwen3 and similar models may include.
    report_text = ""
    for msg in reversed(result.messages):
        content = msg.content if hasattr(msg, "content") else str(msg)
        if content and len(content) > 100:
            report_text = content.replace("TERMINATE", "").strip()
            # Strip model thinking artifacts (e.g. <think>...</think>)
            if "</think>" in report_text:
                report_text = report_text.split("</think>", 1)[-1].strip()
            break

    return report_text, total_tokens


def run(company: str, settings: BenchmarkSettings) -> tuple[str, dict]:
    """Sync wrapper for AutoGen async implementation.

    Args:
        company: Company name to research.
        settings: Benchmark configuration.

    Returns:
        Tuple of (report_text, token_usage_dict).
    """
    return asyncio.run(run_async(company, settings))
