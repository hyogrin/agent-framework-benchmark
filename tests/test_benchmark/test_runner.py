"""Tests for benchmark.runner module."""

from benchmark.metrics import calculate_cost, count_lines_of_code


class TestCalculateCost:
    """Tests for cost calculation."""

    def test_local_provider_is_free(self):
        for provider in ("ollama", "lmstudio", "llamacpp"):
            cost = calculate_cost(
                {"prompt": 10000, "completion": 5000},
                model="qwen3:14b",
                provider=provider,
            )
            assert cost == 0.0

    def test_openai_cost_calculation(self):
        cost = calculate_cost(
            {"prompt": 1_000_000, "completion": 1_000_000},
            model="gpt-4o",
            provider="openai",
        )
        # gpt-4o: $2.50 input + $10.00 output per 1M
        assert cost == 12.5

    def test_zero_tokens(self):
        cost = calculate_cost(
            {"prompt": 0, "completion": 0},
            model="gpt-4o",
            provider="openai",
        )
        assert cost == 0.0

    def test_unknown_model_uses_default(self):
        cost = calculate_cost(
            {"prompt": 1_000_000, "completion": 0},
            model="unknown-model",
            provider="openai",
        )
        # Should use gpt-4o input rate: $2.50/1M
        assert cost == 2.5


class TestCountLinesOfCode:
    """Tests for lines of code counting."""

    def test_nonexistent_directory(self):
        assert count_lines_of_code("/nonexistent/path") == 0
