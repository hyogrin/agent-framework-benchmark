"""Tests for shared.schemas module."""

from shared.schemas import ResearchReport


class TestResearchReport:
    """Tests for ResearchReport schema."""

    def test_valid_report(self):
        report = ResearchReport(
            executive_summary="Test summary",
            company_overview="Test overview",
            products_and_services="Test products",
            market_position="Test position",
            key_insights="Test insights",
            conclusion="Test conclusion",
            word_count=100,
        )
        assert report.executive_summary == "Test summary"
        assert report.word_count == 100

    def test_report_serialization(self):
        report = ResearchReport(
            executive_summary="Summary",
            company_overview="Overview",
            products_and_services="Products",
            market_position="Position",
            key_insights="Insights",
            conclusion="Conclusion",
            word_count=50,
        )
        data = report.model_dump()
        assert isinstance(data, dict)
        assert data["word_count"] == 50
        assert len(data) == 7
