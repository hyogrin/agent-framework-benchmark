"""Abstract base class for evaluation metrics."""

from abc import ABC, abstractmethod


class BaseMetric(ABC):
    """Abstract base for evaluation metrics.

    Subclasses implement specific scoring logic (e.g., quality assessment,
    factual accuracy) that can be computed over generated reports.
    """

    @abstractmethod
    def compute(self, report: str, task_description: str) -> dict:
        """Compute metric scores for a generated report.

        Args:
            report: The generated report text to evaluate.
            task_description: Description of what was asked.

        Returns:
            Dictionary with metric scores.
        """
        ...
