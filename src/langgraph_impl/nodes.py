"""LangGraph node functions for the company research pipeline."""

from langchain_core.messages import HumanMessage, SystemMessage

from shared.prompts import ANALYST_SYSTEM, RESEARCHER_SYSTEM, WRITER_SYSTEM
from shared.tools import gather_all_search_results
from langgraph_impl.state import PipelineState


def researcher(state: PipelineState, llm) -> dict:
    """Research node: gathers company information.

    Args:
        state: Current pipeline state.
        llm: LangChain chat model.

    Returns:
        Dict with 'research' key containing gathered information.
    """
    company = state["company"]

    search_results = gather_all_search_results(company)

    messages = [
        SystemMessage(content=RESEARCHER_SYSTEM.format(company=company)),
        HumanMessage(
            content=(
                f"Research {company} using the following information and compile "
                f"a structured list of facts:\n\n{search_results}"
            )
        ),
    ]
    response = llm.invoke(messages)
    return {"research": response.content}


def analyst(state: PipelineState, llm) -> dict:
    """Analyst node: analyzes research data.

    Args:
        state: Current pipeline state with research data.
        llm: LangChain chat model.

    Returns:
        Dict with 'analysis' key containing analytical insights.
    """
    company = state["company"]
    messages = [
        SystemMessage(content=ANALYST_SYSTEM.format(company=company)),
        HumanMessage(
            content=(
                f"Analyze the following research data about {company} and provide "
                f"key insights:\n\n{state['research']}"
            )
        ),
    ]
    response = llm.invoke(messages)
    return {"analysis": response.content}


def writer(state: PipelineState, llm) -> dict:
    """Writer node: creates the final report.

    Args:
        state: Current pipeline state with research and analysis.
        llm: LangChain chat model.

    Returns:
        Dict with 'report' key containing the final report text.
    """
    company = state["company"]
    messages = [
        SystemMessage(content=WRITER_SYSTEM.format(company=company)),
        HumanMessage(
            content=(
                f"Write a research report about {company} using the following "
                f"research and analysis:\n\n"
                f"## Research\n{state['research']}\n\n"
                f"## Analysis\n{state['analysis']}"
            )
        ),
    ]
    response = llm.invoke(messages)
    return {"report": response.content}
