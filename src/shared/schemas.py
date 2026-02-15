"""Common output schemas shared across all framework implementations."""

from pydantic import BaseModel


class ResearchReport(BaseModel):
    """Structured output schema for the final research report."""

    executive_summary: str
    company_overview: str
    products_and_services: str
    market_position: str
    key_insights: str
    conclusion: str
    word_count: int
