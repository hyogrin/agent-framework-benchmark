"""Tests for eval_core.judge module."""

import json

import pytest

from llm_core.providers.base import BaseLLMProvider, LLMResponse
from eval_core.judge import LLMJudge, _parse_scores
from eval_core.schemas import QualityScores


class MockLLMProvider(BaseLLMProvider):
    """Mock LLM provider that returns pre-defined responses."""

    def __init__(self, response_text: str) -> None:
        self._response_text = response_text

    def generate(self, prompt: str, *, system: str = "") -> LLMResponse:
        return LLMResponse(
            text=self._response_text,
            model="mock-model",
            input_tokens=100,
            output_tokens=50,
        )


VALID_JUDGE_RESPONSE = json.dumps({
    "completeness": 8,
    "accuracy": 7,
    "structure": 9,
    "insight": 6,
    "readability": 8,
    "overall": 7.6,
    "reasoning": "The report covers key areas well with good structure.",
})


class TestParseScores:
    """Tests for _parse_scores helper."""

    def test_parse_valid_json(self):
        scores = _parse_scores(VALID_JUDGE_RESPONSE)
        assert isinstance(scores, QualityScores)
        assert scores.completeness == 8.0
        assert scores.accuracy == 7.0
        assert scores.structure == 9.0
        assert scores.insight == 6.0
        assert scores.readability == 8.0
        assert scores.overall == 7.6
        assert "structure" in scores.reasoning.lower() or len(scores.reasoning) > 0

    def test_parse_json_with_code_block(self):
        wrapped = f"```json\n{VALID_JUDGE_RESPONSE}\n```"
        scores = _parse_scores(wrapped)
        assert scores.completeness == 8.0

    def test_parse_invalid_json_raises(self):
        with pytest.raises((json.JSONDecodeError, KeyError, ValueError)):
            _parse_scores("not valid json")

    def test_parse_missing_field_raises(self):
        incomplete = json.dumps({"completeness": 5})
        with pytest.raises(KeyError):
            _parse_scores(incomplete)

    def test_parse_clamps_out_of_range_scores(self):
        """Scores outside 1-10 should be clamped to the valid range."""
        out_of_range = json.dumps({
            "completeness": 15,
            "accuracy": 0,
            "structure": -1,
            "insight": 11,
            "readability": 10,
            "overall": 0.5,
            "reasoning": "Out of range test",
        })
        scores = _parse_scores(out_of_range)
        assert scores.completeness == 10.0
        assert scores.accuracy == 1.0
        assert scores.structure == 1.0
        assert scores.insight == 10.0
        assert scores.readability == 10.0
        assert scores.overall == 1.0


class TestLLMJudge:
    """Tests for LLMJudge class."""

    def test_evaluate_returns_quality_scores(self):
        provider = MockLLMProvider(VALID_JUDGE_RESPONSE)
        judge = LLMJudge(provider)
        scores = judge.evaluate(
            report="This is a sample research report about Anthropic.",
            task_description="Research report about Anthropic",
        )
        assert isinstance(scores, QualityScores)
        assert 1 <= scores.completeness <= 10
        assert 1 <= scores.overall <= 10

    def test_evaluate_retries_on_parse_failure(self):
        """Judge should retry on parse failure and eventually succeed."""
        call_count = 0

        class FailThenSucceedProvider(BaseLLMProvider):
            def generate(self, prompt: str, *, system: str = "") -> LLMResponse:
                nonlocal call_count
                call_count += 1
                if call_count < 3:
                    return LLMResponse(
                        text="invalid json",
                        model="mock",
                        input_tokens=10,
                        output_tokens=10,
                    )
                return LLMResponse(
                    text=VALID_JUDGE_RESPONSE,
                    model="mock",
                    input_tokens=100,
                    output_tokens=50,
                )

        judge = LLMJudge(FailThenSucceedProvider())
        scores = judge.evaluate("test report", "test task")
        assert isinstance(scores, QualityScores)
        assert call_count == 3

    def test_evaluate_raises_after_all_retries_fail(self):
        provider = MockLLMProvider("always invalid")
        judge = LLMJudge(provider)
        with pytest.raises(ValueError, match="Failed to parse"):
            judge.evaluate("test report", "test task")
