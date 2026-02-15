"""Data schemas for LLM-as-judge evaluation results."""

from dataclasses import dataclass


@dataclass(frozen=True)
class QualityScores:
    """Individual quality scores from LLM-as-judge evaluation.

    All scores are on a 1-10 scale. Higher is better.
    """

    completeness: float
    accuracy: float
    structure: float
    insight: float
    readability: float
    overall: float
    reasoning: str


@dataclass(frozen=True)
class EvalResult:
    """Complete evaluation result for a single benchmark run.

    Combines quality scores from the LLM judge with runtime metrics
    (latency, tokens, cost) from the framework execution.
    """

    framework: str
    company: str
    iteration: int
    quality: QualityScores
    latency_seconds: float
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: float
    report_text: str
