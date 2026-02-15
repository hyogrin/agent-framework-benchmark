"""Tests for eval_core.metrics module."""

import json

from llm_core.providers.base import BaseLLMProvider, LLMResponse
from eval_core.metrics.quality import QualityMetric


VALID_JUDGE_RESPONSE = json.dumps({
    "completeness": 8,
    "accuracy": 7,
    "structure": 9,
    "insight": 6,
    "readability": 8,
    "overall": 7.6,
    "reasoning": "Solid report with good coverage.",
})


class MockLLMProvider(BaseLLMProvider):
    """Mock LLM provider for testing."""

    def generate(self, prompt: str, *, system: str = "") -> LLMResponse:
        return LLMResponse(
            text=VALID_JUDGE_RESPONSE,
            model="mock-model",
            input_tokens=100,
            output_tokens=50,
        )


class TestQualityMetric:
    """Tests for QualityMetric class."""

    def test_compute_returns_dict_with_all_fields(self):
        provider = MockLLMProvider()
        metric = QualityMetric(provider)
        result = metric.compute(
            report="Sample research report about Stripe.",
            task_description="Research report about Stripe",
        )
        assert isinstance(result, dict)
        assert "completeness" in result
        assert "accuracy" in result
        assert "structure" in result
        assert "insight" in result
        assert "readability" in result
        assert "overall" in result
        assert "reasoning" in result

    def test_compute_scores_in_range(self):
        provider = MockLLMProvider()
        metric = QualityMetric(provider)
        result = metric.compute("test report", "test task")
        for key in ("completeness", "accuracy", "structure", "insight", "readability"):
            assert 1 <= result[key] <= 10, f"{key} score out of range"
        assert 1 <= result["overall"] <= 10
