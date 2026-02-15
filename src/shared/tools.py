"""Common tools shared across all framework implementations.

Provides a mock web search tool with pre-built data for benchmark companies,
ensuring deterministic and reproducible benchmark results without API keys.
"""

# Pre-built company data for deterministic benchmarks.
# Each company has multiple search aspects with realistic information.
_COMPANY_DATA: dict[str, dict[str, str]] = {
    "anthropic": {
        "overview": (
            "Anthropic is an AI safety company founded in 2021 by Dario Amodei (CEO) and "
            "Daniela Amodei (President), along with several former OpenAI researchers. "
            "Headquartered in San Francisco, California. The company focuses on developing "
            "safe, beneficial AI systems. Anthropic has raised over $7 billion in funding "
            "from investors including Google, Spark Capital, and Salesforce Ventures."
        ),
        "leadership": (
            "Key leadership at Anthropic: Dario Amodei (CEO) — former VP of Research at "
            "OpenAI, PhD in computational neuroscience from Princeton. Daniela Amodei "
            "(President) — former VP of Operations at OpenAI. Tom Brown — co-lead of GPT-3 "
            "at OpenAI. Chris Olah — renowned ML interpretability researcher. Jared Kaplan "
            "— co-author of neural scaling laws research."
        ),
        "products": (
            "Anthropic's main product is Claude, a family of large language models. "
            "Claude 3.5 Sonnet is positioned as a balanced model for most tasks. "
            "Claude 3 Opus is the most capable model. Claude 3 Haiku is optimized for "
            "speed and cost. The Claude API provides developer access. Anthropic also "
            "offers Claude for Enterprise with enhanced security and admin features. "
            "Claude.ai is the consumer-facing chat interface."
        ),
        "news": (
            "Recent developments: Anthropic launched Claude 3.5 Sonnet with improved "
            "coding and reasoning. The company reached a $18 billion valuation. Amazon "
            "invested up to $4 billion in Anthropic. Google invested $2 billion. "
            "Anthropic published research on Constitutional AI and RLHF alignment. "
            "The company expanded its enterprise offerings and achieved SOC 2 compliance."
        ),
        "market": (
            "Anthropic competes in the foundation model market against OpenAI, Google "
            "DeepMind, Meta AI, and Mistral. The company differentiates through its focus "
            "on AI safety and Constitutional AI training methodology. Claude is used by "
            "major enterprises including Notion, DuckDuckGo, Quora, and many Fortune 500 "
            "companies. Market position: top 3 in commercial LLM providers."
        ),
        "financials": (
            "Anthropic's financial metrics: Total funding raised exceeds $7 billion. "
            "Annualized revenue reportedly exceeds $800 million as of 2024. "
            "Company valuation estimated at $18 billion. Employee count approximately "
            "800-1000. Key revenue drivers: API access, enterprise contracts, and Claude "
            "Pro subscriptions at $20/month."
        ),
    },
    "stripe": {
        "overview": (
            "Stripe is a financial technology company founded in 2010 by Irish brothers "
            "Patrick Collison (CEO) and John Collison (President). Headquartered in San "
            "Francisco and Dublin. Stripe provides payment processing software and APIs "
            "for internet businesses. The company processes hundreds of billions of dollars "
            "annually and is valued at approximately $65 billion."
        ),
        "leadership": (
            "Key leadership at Stripe: Patrick Collison (CEO) — co-founded Stripe at age 22, "
            "previously sold Auctomatic to Live Current Media. John Collison (President) — "
            "youngest self-made billionaire at time of appointment. David Singleton (CTO). "
            "Dhivya Suryadevara (CFO) — former CFO of General Motors. Will Gaybrick "
            "(Chief Product Officer)."
        ),
        "products": (
            "Stripe's product suite includes: Stripe Payments — core payment processing "
            "accepting 135+ currencies. Stripe Connect — marketplace payments platform. "
            "Stripe Billing — subscription and invoicing management. Stripe Atlas — "
            "company incorporation service. Stripe Radar — ML-powered fraud detection. "
            "Stripe Treasury — banking-as-a-service. Stripe Climate — carbon removal "
            "commitments. Stripe Identity — identity verification."
        ),
        "news": (
            "Recent developments: Stripe completed a $6.5 billion Series I funding round. "
            "Launched Stripe Tax for automated tax compliance. Expanded into crypto payments "
            "with USDC support. Launched Stripe Financial Connections. Acquired Paystack "
            "to expand into Africa. Processing volume exceeded $800 billion annually. "
            "Stripe achieved profitability in 2024."
        ),
        "market": (
            "Stripe competes with PayPal/Braintree, Adyen, Square (Block), and Worldpay. "
            "Stripe holds an estimated 20% share of online payment processing in the US. "
            "Key competitive advantages: developer-first API design, extensive documentation, "
            "broad currency and payment method support. Used by Amazon, Google, Shopify, "
            "and millions of businesses worldwide from startups to Fortune 500."
        ),
        "financials": (
            "Stripe's financial metrics: Valued at approximately $65 billion (2024). "
            "Annual processing volume exceeds $800 billion. Revenue estimated at $14+ "
            "billion annually. Total funding raised: approximately $8.7 billion. "
            "Employee count: approximately 8,000. The company achieved GAAP profitability "
            "in 2024 after years of rapid growth investment."
        ),
    },
    "datadog": {
        "overview": (
            "Datadog is a cloud monitoring and analytics platform founded in 2010 by "
            "Olivier Pomel (CEO) and Alexis Le-Quoc (CTO). Headquartered in New York City. "
            "The company went public on NASDAQ (DDOG) in September 2019. Datadog provides "
            "a unified platform for infrastructure monitoring, application performance "
            "monitoring (APM), log management, and security."
        ),
        "leadership": (
            "Key leadership at Datadog: Olivier Pomel (CEO and co-founder) — previously at "
            "Wireless Generation. Alexis Le-Quoc (CTO and co-founder) — infrastructure "
            "engineering background. David Obstler (CFO) — former CFO at Cowen Group. "
            "Amit Agarwal (Chief Product Officer). Yanbing Li (Chief Strategy Officer) — "
            "former VP at Google Cloud."
        ),
        "products": (
            "Datadog's product platform includes: Infrastructure Monitoring — servers, "
            "containers, cloud services. APM (Application Performance Monitoring) — "
            "distributed tracing and profiling. Log Management — centralized logging with "
            "analytics. Synthetics — proactive API and browser testing. RUM (Real User "
            "Monitoring) — frontend performance tracking. Security Monitoring — SIEM "
            "and threat detection. CI Visibility — pipeline monitoring."
        ),
        "news": (
            "Recent developments: Datadog launched Bits AI, an AI assistant for operations. "
            "Expanded LLM observability features for monitoring AI applications. Revenue "
            "grew 26% year-over-year. Launched Cloud Security Management. Achieved "
            "FedRAMP authorization for government customers. Expanded to 26,800+ customers. "
            "Introduced Workflow Automation for incident response."
        ),
        "market": (
            "Datadog competes with Splunk (Cisco), New Relic, Dynatrace, Elastic, and "
            "Grafana Labs. The company is a leader in Gartner's Magic Quadrant for APM "
            "and observability. Key competitive advantage: unified platform approach vs. "
            "point solutions. 26,800+ customers including Samsung, Peloton, Whole Foods, "
            "and many cloud-native companies. Market cap approximately $40 billion."
        ),
        "financials": (
            "Datadog's financial metrics (DDOG on NASDAQ): FY2023 revenue approximately "
            "$2.1 billion, up 26% YoY. Gross margin approximately 80%. Operating margin "
            "improving toward profitability. Market cap approximately $40 billion. "
            "Customer count: 26,800+. Customers with ARR > $100K: 3,190+. Dollar-based "
            "net retention rate exceeds 120%. Employee count approximately 5,200."
        ),
    },
}

# Mapping from query keywords to data keys for flexible matching
_QUERY_KEYWORDS: dict[str, list[str]] = {
    "overview": ["overview", "about", "general", "company", "background", "history", "founded"],
    "leadership": ["leadership", "ceo", "cto", "founder", "team", "management", "executive"],
    "products": ["products", "services", "offering", "platform", "features", "api", "tools"],
    "news": ["news", "recent", "developments", "updates", "latest", "announced", "launched"],
    "market": ["market", "competition", "competitors", "position", "share", "advantage"],
    "financials": ["financials", "revenue", "funding", "valuation", "metrics", "growth", "profit"],
}


def _match_query_to_aspect(query: str) -> str:
    """Match a search query to the most relevant data aspect.

    Args:
        query: The search query to match.

    Returns:
        The best-matching aspect key, or 'overview' as default.
    """
    query_lower = query.lower()
    best_match = "overview"
    best_score = 0

    for aspect, keywords in _QUERY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in query_lower)
        if score > best_score:
            best_score = score
            best_match = aspect

    return best_match


def search_company(company: str, query: str) -> str:
    """Mock web search tool for company research.

    Returns pre-built information for benchmark companies (Anthropic, Stripe, Datadog).
    For unknown companies, returns a generic response.

    Args:
        company: Company name to research.
        query: Specific aspect to search for.

    Returns:
        Search results as a formatted string.
    """
    company_key = company.lower().strip()
    data = _COMPANY_DATA.get(company_key)

    if data is None:
        return (
            f"Search results for '{company}' — '{query}': "
            f"{company} is a technology company. Limited public information is available "
            f"for this benchmark query. Please note this is a mock search tool."
        )

    aspect = _match_query_to_aspect(query)
    result = data.get(aspect, data["overview"])
    return f"Search results for '{company}' — '{query}':\n{result}"


# Standard search queries used by all framework implementations.
_STANDARD_QUERIES = [
    "company overview and background",
    "leadership and management team",
    "products and services",
    "recent news and developments",
    "market position and competition",
    "financial metrics and revenue",
]


def gather_all_search_results(company: str) -> str:
    """Run all standard search queries for a company and combine results.

    This ensures all 5 framework implementations use the exact same
    search inputs, preventing drift if queries are modified.

    Args:
        company: Company name to research.

    Returns:
        Combined search results separated by double newlines.
    """
    return "\n\n".join(
        search_company(company, query) for query in _STANDARD_QUERIES
    )
