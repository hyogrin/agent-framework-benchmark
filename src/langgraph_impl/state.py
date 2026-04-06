"""LangGraph state schema for the company research pipeline."""

import operator
from typing import Annotated, TypedDict


class PipelineState(TypedDict):
    """State that flows through the LangGraph pipeline.

    Each node reads from and writes to this shared state dictionary.
    Previous agent outputs are accumulated in `history` as AIMessages,
    while each node still receives its own dedicated instructions.
    """

    company: str
    task: str
    history: Annotated[list, operator.add]
    report: str
