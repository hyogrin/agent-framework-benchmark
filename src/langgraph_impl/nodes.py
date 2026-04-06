"""LangGraph node functions for the company research pipeline."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from shared.prompts import ANALYST_SYSTEM, RESEARCHER_SYSTEM, WRITER_SYSTEM
from shared.tools import gather_all_search_results
from langgraph_impl.state import PipelineState


def _build_task(company: str) -> str:
    """Build the shared team task message, identical to MS Agent's task."""
    search_results = gather_all_search_results(company)
    return (
        f"Research and write a comprehensive report about {company}. "
        f"Here is the available research data:\n\n{search_results}\n\n"
        f"The researcher should organize the facts, the analyst should identify "
        f"key insights, and the writer should produce the final 500-800 word report."
    )


def researcher(state: PipelineState, llm) -> dict:
    """Research node: gathers company information.

    Args:
        state: Current pipeline state.
        llm: LangChain chat model.

    Returns:
        Dict with 'task' and 'history' keys.
    """
    company = state["company"]
    task = _build_task(company)

    messages = [
        SystemMessage(content=RESEARCHER_SYSTEM.format(company=company)),
        HumanMessage(content=task),
    ]
    response = llm.invoke(messages)
    return {"task": task, "history": [AIMessage(content=response.content)]}


def analyst(state: PipelineState, llm) -> dict:
    """Analyst node: analyzes research data.

    Receives the same team task as user message plus previous agent
    outputs as assistant messages — identical to MS Agent's pattern.

    Args:
        state: Current pipeline state with conversation history.
        llm: LangChain chat model.

    Returns:
        Dict with 'history' key appending the analyst's response.
    """
    company = state["company"]
    messages = [
        SystemMessage(content=ANALYST_SYSTEM.format(company=company)),
        HumanMessage(content=state["task"]),
        *state["history"],
    ]
    response = llm.invoke(messages)
    return {"history": [AIMessage(content=response.content)]}


def writer(state: PipelineState, llm) -> dict:
    """Writer node: creates the final report.

    Receives the same team task as user message plus full conversation
    history — identical to MS Agent's pattern.

    Args:
        state: Current pipeline state with full conversation history.
        llm: LangChain chat model.

    Returns:
        Dict with 'report' key containing the final report text.
    """
    company = state["company"]
    messages = [
        SystemMessage(content=WRITER_SYSTEM.format(company=company)),
        HumanMessage(content=state["task"]),
        *state["history"],
    ]
    response = llm.invoke(messages)
    return {"report": response.content}
