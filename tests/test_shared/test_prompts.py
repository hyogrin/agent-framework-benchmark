"""Tests for shared.prompts module."""

from shared.prompts import ANALYST_SYSTEM, RESEARCHER_SYSTEM, WRITER_SYSTEM


class TestPrompts:
    """Tests for shared prompt templates."""

    def test_all_prompts_accept_company_placeholder(self):
        """Every prompt must contain {company} and format without error."""
        for name, prompt in [
            ("RESEARCHER_SYSTEM", RESEARCHER_SYSTEM),
            ("ANALYST_SYSTEM", ANALYST_SYSTEM),
            ("WRITER_SYSTEM", WRITER_SYSTEM),
        ]:
            assert "{company}" in prompt, f"{name} is missing {{company}} placeholder"
            formatted = prompt.format(company="TestCorp")
            assert "TestCorp" in formatted, f"{name} did not interpolate company"

    def test_researcher_mentions_key_tasks(self):
        prompt = RESEARCHER_SYSTEM.format(company="Acme")
        assert "Acme" in prompt
        assert "research" in prompt.lower() or "gather" in prompt.lower()

    def test_writer_mentions_report_structure(self):
        prompt = WRITER_SYSTEM.format(company="Acme")
        assert "Executive Summary" in prompt
        assert "500-800 words" in prompt
