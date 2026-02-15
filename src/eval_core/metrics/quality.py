"""Quality metric using LLM-as-judge evaluation."""

from llm_core.providers.base import BaseLLMProvider

from eval_core.metrics.base import BaseMetric
from eval_core.judge import LLMJudge
from eval_core.schemas import QualityScores


class QualityMetric(BaseMetric):
    """Evaluate report quality using an LLM as judge.

    Wraps LLMJudge to conform to the BaseMetric interface, allowing
    quality evaluation to be used alongside other metric types.
    """

    def __init__(self, provider: BaseLLMProvider) -> None:
        self._judge = LLMJudge(provider)

    def compute(self, report: str, task_description: str) -> dict:
        """Compute quality scores for a generated report.

        Args:
            report: The generated report text to evaluate.
            task_description: Description of what was asked.

        Returns:
            Dictionary with quality scores matching QualityScores fields.
        """
        scores: QualityScores = self._judge.evaluate(report, task_description)
        return {
            "completeness": scores.completeness,
            "accuracy": scores.accuracy,
            "structure": scores.structure,
            "insight": scores.insight,
            "readability": scores.readability,
            "overall": scores.overall,
            "reasoning": scores.reasoning,
        }
