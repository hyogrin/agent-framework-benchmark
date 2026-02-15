# How I Built a Fair AI Agent Benchmark (Architecture & Methodology)

Comparing frameworks is easy. Comparing them *fairly* is the hard part.

---

In [Part 1 of this series](./01-benchmark-results.md), I published the results of benchmarking five AI agent frameworks head-to-head. MS Agent Framework won on speed and consistency. Quality scores were nearly identical across the board. The results surprised me.

But results without methodology are just opinions with charts. This article is about the engineering behind the benchmark: how I designed the system to isolate framework behavior from everything else, the architectural decisions that made fair comparison possible, and the mistakes I'd fix if I ran it again.

If you've ever tried to compare two libraries by building a quick prototype in each, you know the problem. The first one you build teaches you the task. The second one benefits from everything you learned. Your "comparison" is really measuring your own learning curve. I wanted to eliminate that entirely.

## The Fairness Problem

Most framework comparisons I've seen online have the same fundamental flaw: they're benchmarking prompt quality, not framework quality.

Think about what typically happens. Someone builds a project in LangGraph, writes carefully tuned prompts, gets great results. Then they try CrewAI, use slightly different wording, maybe a different model temperature, and get different results. They write a blog post declaring one framework superior. But what actually differed? The prompts. The configuration. The author's familiarity with each API. The framework was maybe 10% of the equation.

There are several ways naive comparisons fail:

- **Different prompts** — Each implementation uses hand-written instructions. Prompt phrasing changes output quality dramatically.
- **Different tools** — One version calls a real API, another uses a mock. Network latency and API variability dominate the measurement.
- **Temperature randomness** — Running at temperature 0.7 means every run produces different output. You're measuring random variance, not framework capability.
- **Framework-specific optimizations** — Tuning one framework's settings while leaving another at defaults isn't a framework comparison; it's a configuration comparison.

I wanted to control for all of this. Every variable that isn't "which framework is orchestrating the agents" had to be identical.

## The Task: Company Research Agent

The benchmark task is a 3-agent pipeline:

1. **Researcher** — Gathers raw information about a target company
2. **Analyst** — Synthesizes research findings into structured business insights
3. **Writer** — Produces a polished 500-800 word research report

I chose this task because it hits a sweet spot. It's complex enough to exercise real multi-agent orchestration — three agents with data dependencies, where each agent's output feeds the next. But it's simple enough that the output (a structured report) can be evaluated objectively on dimensions like completeness, accuracy, and readability.

Each framework researches three companies (Anthropic, Stripe, Datadog), three iterations each, for 9 runs per framework and 45 runs total. Three companies gives us variety in available information. Three iterations gives us enough repetition to measure consistency.

## Architecture Overview

The benchmark isn't a loose collection of scripts. It's a modular system with strict dependency boundaries:

```
                   ┌──────────────┐
                   │  Benchmark   │
                   │   Runner     │
                   └──────┬───────┘
                          │
            ┌─────────────┼─────────────┐
            │             │             │
      ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
      │ Framework │ │ Framework │ │ Framework │  x5 frameworks
      │   Impl    │ │   Impl    │ │   Impl    │  x3 companies
      └─────┬─────┘ └─────┬─────┘ └─────┬─────┘  x3 iterations
            │             │             │        = 45 runs
            ▼             ▼             ▼
      ┌─────────────────────────────────────────┐
      │              shared/                    │
      │  prompts.py │ tools.py │ schemas.py     │
      │  config.py (BenchmarkSettings)          │
      └─────────────────────────────────────────┘
                           │
                    ┌──────▼───────┐
                    │  eval_core   │──▶ LLM-as-Judge
                    │  (LLMJudge)  │    Quality Scores
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │ vendor/      │
                    │ llm_core     │──▶ Provider Abstraction
                    └──────────────┘
```

The runner dynamically imports each framework module, passes it a company name and settings, and collects the report text plus token usage. It then sends each report through the LLM judge for quality scoring. Everything feeds into a CSV of results for analysis.

## The 5 Rules of Fair Comparison

### Rule 1: Identical Prompts

Every framework implementation imports its prompts from the same `shared/prompts.py` file. No framework gets custom instructions. Here are the actual prompt strings:

```python
RESEARCHER_SYSTEM = (
    "You are a company research specialist. Your task is to gather comprehensive "
    "information about {company}. Focus on: company overview, key leadership, "
    "products/services, recent news and developments, market position, and key "
    "financial or operational metrics. Be thorough and factual. Present your "
    "findings as a structured list of facts with categories."
)

ANALYST_SYSTEM = (
    "You are a business analyst specializing in {company}. Review the research data "
    "provided and identify: key strengths, potential risks and challenges, market "
    "trends affecting {company}, competitive advantages, and notable strategic "
    "insights. Provide data-driven analysis with clear reasoning."
)

WRITER_SYSTEM = (
    "You are a professional report writer covering {company}. Create a structured "
    "research report with these sections: Executive Summary, Company Overview, "
    "Products & Services, Market Position, Key Insights, and Conclusion. Write "
    "clearly and professionally. The report should be 500-800 words."
)
```

If CrewAI got "Be incredibly detailed and thorough" while LangGraph got "Be concise," we'd be testing prompt engineering, not frameworks. Sharing a single source file eliminates that variable entirely.

### Rule 2: Identical Tools

The agents use a mock search tool from `shared/tools.py` with pre-built data for each benchmark company. This is critical for two reasons.

First, determinism. Real API calls return different results at different times. A company's stock price changes, news articles rotate, search rankings shift. Mock data guarantees every framework gets the exact same input information on every run.

Second, isolation. If one framework happens to make API calls faster due to connection pooling, or runs into rate limiting, that shows up as a latency difference that has nothing to do with the framework's orchestration quality. Mock tools remove network variability from the equation.

The `gather_all_search_results()` function runs the same six standard queries for every company, ensuring all implementations receive identical raw data regardless of how they choose to call the search tool.

### Rule 3: Same Model

All five frameworks run against Qwen 3 14B via Ollama, configured through `BenchmarkSettings`:

```python
class BenchmarkSettings(BaseSettings):
    llm_provider: str = "ollama"
    llm_model: str = "qwen3:14b"
    ollama_host: str = "http://localhost:11434"
```

One model, one machine, one inference server. No framework gets a smarter model or a faster endpoint.

### Rule 4: temperature=0 Everywhere

Every framework implementation sets `temperature=0` for all LLM calls. This eliminates random sampling from the generation process. With temperature 0, the model always picks the highest-probability next token, making outputs as deterministic as the framework allows. (Some variation still occurs due to floating-point nondeterminism in GPU computation, but it's minimal.)

### Rule 5: No Framework-Specific Optimizations

No custom retry logic, no framework-specific prompt tweaking, no tuning of agent count or conversation structure beyond what the pipeline requires. Every implementation gets the most straightforward translation of the three-agent pipeline into that framework's idiom. If a framework makes certain patterns easier or harder, that's a legitimate difference worth measuring.

## The Module Dependency Fence

Beyond shared inputs, architectural boundaries prevent accidental coupling between components:

```
llm_core         <── eval_core (judge uses BaseLLMProvider)
shared/          <── all framework implementations
eval_core        <── benchmark/ (runner uses judge)
No framework implementation imports from another.
```

Three rules make this work:

1. **eval_core CANNOT import shared/.** The judge evaluates reports as plain text. It doesn't know what prompts were used, what tools were available, or how agents were structured. This prevents the evaluation from being biased toward the specific task design.

2. **Framework implementations CANNOT import each other.** If the LangGraph implementation imported a utility from the CrewAI implementation, we'd have hidden coupling. Each implementation is self-contained within its own package.

3. **llm_core is vendored and unmodified.** The LLM provider abstraction layer (`BaseLLMProvider`, `OllamaProvider`, etc.) is vendored from another project and treated as a frozen dependency. No benchmark-specific modifications.

This might seem overly strict for a benchmark project. But without these boundaries, it's easy for shared state or implicit dependencies to contaminate the comparison. I've seen benchmark repos where "shared utilities" slowly accumulate framework-specific logic. Explicit import rules prevent that drift.

## LLM-as-Judge Evaluation

Each of the 45 reports is scored by an LLM judge on five criteria, each rated 1-10:

1. **Completeness** — Does the report cover key aspects? (leadership, products, market position, developments, metrics)
2. **Accuracy** — Are stated facts verifiable and reasonable? Any fabrications?
3. **Structure** — Well-organized with clear sections? Follows the requested format?
4. **Insight** — Analysis beyond surface-level facts? Meaningful observations?
5. **Readability** — Well-written, professional, clear?

The judge receives the report as plain text along with a task description, and returns a structured JSON response:

```python
_JUDGE_PROMPT = """\
You are an expert evaluator of research reports. Score the following report on a \
scale of 1-10 for each criterion. Be rigorous and fair.

## Criteria
1. **Completeness** (1-10): Does the report cover key aspects of the company?
2. **Accuracy** (1-10): Are the stated facts verifiable and reasonable?
3. **Structure** (1-10): Is the report well-organized with clear sections?
4. **Insight** (1-10): Does the report provide analysis beyond surface-level facts?
5. **Readability** (1-10): Is it well-written, professional, and clear?

## Report to Evaluate
{report}

Respond with ONLY valid JSON (no markdown, no code blocks):
{"completeness": <int>, "accuracy": <int>, "structure": <int>,
 "insight": <int>, "readability": <int>, "overall": <float>,
 "reasoning": "<brief explanation>"}"""
```

Why an LLM judge instead of human evaluation? Three reasons: **scale** (45 reports is a lot to evaluate manually), **consistency** (human evaluators drift over time — the 40th report gets different attention than the 5th), and **reproducibility** (anyone can re-run the judge and get the same scores).

The limitations are real. LLM judges have known biases — they tend to prefer verbose, well-formatted output over concise but equally correct output. But since all five frameworks produce structurally similar reports (they're all following the same writer prompt with the same section headings), this bias affects all frameworks roughly equally. It's a systematic offset, not a confound.

The judge uses `temperature=0` for consistency and retries up to 3 times on JSON parse failures. Failed parses get logged and the response is re-requested. This handles the occasional case where the model wraps its JSON in markdown code blocks despite being told not to.

## Local-First: Why Ollama Instead of Cloud APIs

The entire benchmark runs locally using Ollama. No cloud API keys required. This was a deliberate choice with several advantages:

- **$0 cost.** Forty-five benchmark runs plus 45 judge evaluations. At cloud pricing, that's potentially hundreds of dollars. Locally, it's electricity.
- **No rate limits.** Cloud APIs throttle concurrent requests. Running 45 sequential calls against GPT-4o means dealing with rate limiting, retry backoff, and variable response times that have nothing to do with framework quality.
- **No network variability.** When measuring latency differences between frameworks, the last thing you want is network jitter adding 50-500ms of noise per request.
- **Complete reproducibility.** Anyone with an Ollama installation and the Qwen 3 14B model can reproduce these results exactly. No API key, no billing account, no waiting list.

The trade-off is obvious: Qwen 3 14B isn't GPT-4o. The absolute quality of outputs is lower than what you'd get from a frontier model. But this benchmark measures *relative* framework performance — how much overhead each framework adds, how consistently each one produces results, how efficiently each one uses tokens. Those relative measurements hold regardless of the underlying model's capability.

The configuration supports cloud providers too (`openai`, `anthropic` are valid `llm_provider` values), so you can re-run with GPT-4o or Claude if you want to validate that framework rankings hold at higher model capability levels.

## Surviving Dependency Hell

Here's a problem I didn't anticipate: the five frameworks literally cannot all be installed in the same Python environment.

CrewAI pins `openai<1.84`. MS Agent Framework requires `openai>=1.99`. These are hard version constraints in their respective `pyproject.toml` files. pip will just fail. Even if you could force-install both, one of them would break at runtime.

The solution: uv's dependency groups (PEP 735). Each framework gets its own resolution context:

```bash
uv sync --group crewai      # Installs CrewAI (pins openai<1.84)
uv sync --group msagent     # Installs MS Agent Framework (needs openai>=1.99)
```

Groups that are compatible can be installed together:

```bash
uv sync --group langgraph --group autogen --group agents-sdk
```

I also declared explicit conflicts in `pyproject.toml` so that uv resolves these groups independently rather than trying to find a single unified solution:

```toml
[tool.uv]
conflicts = [
    [{ group = "crewai" }, { group = "msagent" }],
    [{ group = "crewai" }, { group = "agents-sdk" }],
]
```

This is a real-world takeaway that goes beyond benchmarking: **your existing dependency tree might rule out certain frameworks before you write a line of code.** If your project already depends on `openai>=1.90`, CrewAI is off the table until they update their pin. If you're on an older `openai` version and can't upgrade, the newer frameworks won't work. Check compatibility before you invest a week building a proof of concept.

## What I'd Do Differently

No benchmark is perfect, and this one has gaps I'd address in a v2:

**More test companies.** Three companies gives us variety, but 5-7 would provide better statistical power. With only 9 runs per framework, the confidence intervals on quality scores are wide enough that most pairwise differences aren't statistically significant (as the Mann-Whitney U tests in Part 1 confirmed).

**Multiple task types.** Company research is one workflow pattern. A more comprehensive benchmark would include a coding task (generate and debug code), a data analysis task (interpret a dataset), and a customer support task (handle multi-turn conversations). Different frameworks might excel at different patterns.

**Human eval baseline.** I'd recruit 3-5 evaluators to score a subset of reports independently and compare their rankings to the LLM judge's rankings. This would validate whether the judge's quality scores match human intuition or if systematic biases are distorting results.

**Test with cloud models.** Running the same benchmark with GPT-4o and Claude Sonnet would answer an important question: do framework rankings change with model capability? It's possible that a framework that adds overhead with a strong model actually helps compensate for a weaker model's limitations, or vice versa.

**Standardized token tracking.** Token tracking varies across frameworks — some report tokens natively, others require instrumentation hooks. A complete benchmark needs a framework-agnostic way to capture token usage at the provider level, rather than relying on each framework's own reporting.

## Tech Stack

| Component | Tool |
|-----------|------|
| Language | Python 3.12 |
| Package Manager | uv |
| Build System | Hatchling |
| LLM Serving | Ollama (Qwen 3 14B) |
| Linter/Formatter | ruff |
| Type Checker | mypy |
| Testing | pytest |
| Analysis | pandas + Plotly |
| Notebooks | Jupyter |

All code, data, and analysis notebooks are open source: [agent-framework-benchmark](https://github.com/LukaszGrochal/agent-framework-benchmark)

## Series Navigation

- **Part 1: [I Benchmarked 5 AI Agent Frameworks — Here's What Actually Matters](./01-benchmark-results.md)** — The results: quality scores, latency, token efficiency, and consistency across all 45 runs.
- **Part 2: How I Built a Fair Benchmark** — You are here. Architecture, methodology, and the engineering behind controlled comparisons.
- **Part 3: A Practical Decision Guide** — Flowchart for picking the right framework based on your actual constraints.

---

*Built with Python 3.12, uv, Ollama, and a determination to answer "which framework is best?" with data instead of opinions.*
