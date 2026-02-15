"""Tests for shared.config module."""

from shared.config import BenchmarkSettings


class TestBenchmarkSettings:
    """Tests for BenchmarkSettings."""

    def test_default_values(self, monkeypatch):
        # Prevent .env from overriding code defaults.
        monkeypatch.delenv("BENCH_LLM_MODEL", raising=False)
        monkeypatch.setattr(BenchmarkSettings, "model_config", {})
        settings = BenchmarkSettings()
        assert settings.llm_provider == "ollama"
        assert settings.llm_model == "qwen3:14b"
        assert settings.iterations == 3
        assert len(settings.companies) == 3
        assert len(settings.frameworks) == 5

    def test_default_companies(self):
        settings = BenchmarkSettings()
        assert "Anthropic" in settings.companies
        assert "Stripe" in settings.companies
        assert "Datadog" in settings.companies

    def test_default_frameworks(self):
        settings = BenchmarkSettings()
        expected = ["crewai", "langgraph", "autogen", "msagent", "agents_sdk"]
        assert settings.frameworks == expected
