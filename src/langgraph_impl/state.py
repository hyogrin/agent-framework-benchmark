"""LangGraph state schema for the company research pipeline."""

from typing import TypedDict


class PipelineState(TypedDict):
    """State that flows through the LangGraph pipeline.

    Each node reads from and writes to this shared state dictionary.
    """

    company: str
    research: str
    analysis: str
    report: str
