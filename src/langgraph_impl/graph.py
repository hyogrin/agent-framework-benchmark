"""LangGraph graph definition and execution."""

from functools import partial

from langchain_core.callbacks import UsageMetadataCallbackHandler
from langgraph.graph import END, START, StateGraph

from shared.config import BenchmarkSettings
from langgraph_impl.nodes import analyst, researcher, writer
from langgraph_impl.state import PipelineState


def _create_llm(settings: BenchmarkSettings):
    """Create a LangChain chat model from benchmark settings.

    Args:
        settings: Benchmark configuration.

    Returns:
        Configured LangChain chat model.
    """
    if settings.llm_provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=settings.llm_model,
            base_url=settings.ollama_host,
            temperature=0,
        )
    elif settings.llm_provider == "lmstudio":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.llm_model,
            base_url=f"{settings.lmstudio_host}/v1",
            api_key="lm-studio",
            temperature=0,
        )
    elif settings.llm_provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0,
        )
    elif settings.llm_provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=settings.anthropic_model,
            api_key=settings.anthropic_api_key,
            temperature=0,
        )
    else:
        msg = f"Unsupported LLM provider: {settings.llm_provider}"
        raise ValueError(msg)


def build_graph(settings: BenchmarkSettings) -> StateGraph:
    """Build and compile the LangGraph workflow.

    Args:
        settings: Benchmark configuration.

    Returns:
        Compiled LangGraph workflow.
    """
    llm = _create_llm(settings)

    workflow = StateGraph(PipelineState)
    workflow.add_node("researcher", partial(researcher, llm=llm))
    workflow.add_node("analyst", partial(analyst, llm=llm))
    workflow.add_node("writer", partial(writer, llm=llm))
    workflow.add_edge(START, "researcher")
    workflow.add_edge("researcher", "analyst")
    workflow.add_edge("analyst", "writer")
    workflow.add_edge("writer", END)
    return workflow.compile()


def run(company: str, settings: BenchmarkSettings) -> tuple[str, dict]:
    """Run LangGraph implementation.

    Args:
        company: Company name to research.
        settings: Benchmark configuration.

    Returns:
        Tuple of (report_text, token_usage_dict).
    """
    callback = UsageMetadataCallbackHandler()
    graph = build_graph(settings)
    result = graph.invoke(
        {"company": company, "research": "", "analysis": "", "report": ""},
        config={"callbacks": [callback]},
    )

    # Extract token usage from callback.
    # usage_metadata is a dict keyed by model name, e.g.:
    # {"gpt-4o": {"input_tokens": 100, "output_tokens": 50, "total_tokens": 150}}
    token_usage = {"prompt": 0, "completion": 0}
    if hasattr(callback, "usage_metadata") and callback.usage_metadata:
        for model_usage in callback.usage_metadata.values():
            token_usage["prompt"] += model_usage.get("input_tokens", 0) or 0
            token_usage["completion"] += model_usage.get("output_tokens", 0) or 0

    return result["report"], token_usage
