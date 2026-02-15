"""Tests for shared.tools module."""

from shared.tools import gather_all_search_results, search_company


class TestSearchCompany:
    """Tests for the mock search_company tool."""

    def test_known_company_returns_data(self):
        result = search_company("Anthropic", "company overview")
        assert "Anthropic" in result
        assert "AI safety" in result or "Dario Amodei" in result

    def test_known_company_case_insensitive(self):
        result = search_company("STRIPE", "products and services")
        assert "Stripe" in result or "payment" in result.lower()

    def test_unknown_company_returns_generic(self):
        result = search_company("UnknownCorp", "overview")
        assert "UnknownCorp" in result
        assert "mock search tool" in result.lower()

    def test_different_aspects_return_different_data(self):
        overview = search_company("Datadog", "company overview")
        financials = search_company("Datadog", "financial metrics and revenue")
        assert overview != financials

    def test_all_benchmark_companies_have_data(self):
        for company in ["Anthropic", "Stripe", "Datadog"]:
            result = search_company(company, "overview")
            assert len(result) > 50, f"Insufficient data for {company}"


class TestGatherAllSearchResults:
    """Tests for gather_all_search_results helper."""

    def test_returns_combined_results_for_known_company(self):
        result = gather_all_search_results("Anthropic")
        # Should include data from all 6 aspects
        assert "AI safety" in result or "Dario Amodei" in result  # overview/leadership
        assert "Claude" in result  # products
        assert "billion" in result.lower()  # financials

    def test_covers_all_six_aspects(self):
        result = gather_all_search_results("Stripe")
        # Each aspect query should produce a "Search results for" header
        assert result.count("Search results for") == 6

    def test_returns_generic_for_unknown_company(self):
        result = gather_all_search_results("UnknownCorp")
        assert "mock search tool" in result.lower()
