"""LLM-as-judge evaluation for report quality scoring."""

import json
import logging

from llm_core.providers.base import BaseLLMProvider

from eval_core.schemas import QualityScores

logger = logging.getLogger(__name__)

_JUDGE_PROMPT = """\
You are an expert evaluator of research reports. Score the following report on a \
scale of 1-10 for each criterion. Be rigorous and fair.

## Criteria

1. **Completeness** (1-10): Does the report cover key aspects of the company? \
(leadership, products, market position, recent developments, metrics)
2. **Accuracy** (1-10): Are the stated facts verifiable and reasonable? \
Are there any obvious fabrications?
3. **Structure** (1-10): Is the report well-organized with clear sections? \
Does it follow the requested format?
4. **Insight** (1-10): Does the report provide analysis beyond surface-level facts? \
Are there meaningful observations?
5. **Readability** (1-10): Is it well-written, professional, and clear?

## Task Description
The agent was asked to: {task_description}

## Report to Evaluate
{report}

Respond with ONLY valid JSON (no markdown, no code blocks):
{{"completeness": <int 1-10>, "accuracy": <int 1-10>, "structure": <int 1-10>, \
"insight": <int 1-10>, "readability": <int 1-10>, "overall": <float 1-10>, \
"reasoning": "<brief 2-3 sentence explanation>"}}"""

_JUDGE_SYSTEM = (
    "You are a strict, fair evaluator of research reports. "
    "Always respond with valid JSON only. No markdown, no code blocks."
)

_MAX_RETRIES = 3


def _parse_scores(text: str) -> QualityScores:
    """Parse LLM judge response into QualityScores.

    Args:
        text: Raw text response from the LLM judge.

    Returns:
        Parsed QualityScores.

    Raises:
        ValueError: If the response cannot be parsed as valid scores.
    """
    # Strip common formatting artifacts
    cleaned = text.strip()
    if cleaned.startswith("```"):
        # Remove code block markers
        lines = cleaned.split("\n")
        lines = [line for line in lines if not line.strip().startswith("```")]
        cleaned = "\n".join(lines).strip()

    data = json.loads(cleaned)

    def _clamp(value: float, lo: float = 1.0, hi: float = 10.0) -> float:
        return max(lo, min(hi, value))

    return QualityScores(
        completeness=_clamp(float(data["completeness"])),
        accuracy=_clamp(float(data["accuracy"])),
        structure=_clamp(float(data["structure"])),
        insight=_clamp(float(data["insight"])),
        readability=_clamp(float(data["readability"])),
        overall=_clamp(float(data["overall"])),
        reasoning=str(data["reasoning"]),
    )


class LLMJudge:
    """Evaluate report quality using an LLM as judge.

    Uses a BaseLLMProvider to score reports on multiple quality criteria.
    The judge prompt asks for structured JSON output with scores 1-10.

    Args:
        provider: LLM provider to use for evaluation.
    """

    def __init__(self, provider: BaseLLMProvider) -> None:
        self._provider = provider

    def evaluate(self, report: str, task_description: str) -> QualityScores:
        """Score a report using LLM-as-judge.

        Sends the report to the LLM with a structured evaluation prompt and
        parses the JSON response into QualityScores. Retries on parse failure.

        Args:
            report: The generated report text to evaluate.
            task_description: Description of the original task.

        Returns:
            QualityScores with scores on each criterion.

        Raises:
            ValueError: If parsing fails after all retries.
        """
        prompt = _JUDGE_PROMPT.format(
            task_description=task_description,
            report=report,
        )

        last_error: Exception | None = None
        for attempt in range(1, _MAX_RETRIES + 1):
            response = self._provider.generate(prompt, system=_JUDGE_SYSTEM)
            try:
                return _parse_scores(response.text)
            except (json.JSONDecodeError, KeyError, TypeError) as exc:
                last_error = exc
                logger.warning(
                    "Judge parse attempt %d/%d failed: %s",
                    attempt,
                    _MAX_RETRIES,
                    exc,
                )

        msg = f"Failed to parse judge response after {_MAX_RETRIES} attempts: {last_error}"
        raise ValueError(msg)
