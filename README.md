# Agent Framework Benchmark

An objective, data-driven comparison of **5 multi-agent frameworks** using the same "Company Research Agent" workflow, with automated benchmarking and LLM-as-judge evaluation.

**Local-first** — runs on local models via Ollama by default, with cloud providers (OpenAI, Anthropic) as configurable alternatives.

## Frameworks Compared

| # | Framework | Version | Architecture | Status |
|---|-----------|---------|--------------|--------|
| 1 | **CrewAI** | 1.9.x | Task-based sequential | Active development |
| 2 | **LangGraph** | 1.0.x | Graph-based state machine | Production/Stable (1.0 GA) |
| 3 | **AutoGen** | 0.7.x | Async group chat | Maintenance mode |
| 4 | **MS Agent Framework** | 1.0.0b | Sequential orchestration | Beta (GA ~March 2026) |
| 5 | **OpenAI Agents SDK** | latest | Runner-based pipeline | Active |

## Key Results

> **Full analysis:** [Article Series](#) | [Interactive Notebook](notebooks/analysis.ipynb)

| Framework | Quality (1-10) | Latency | Tokens | Consistency (Std) |
|-----------|---------------|---------|--------|-------------------|
| **MS Agent Framework** | **9.87** | **93s** | **7,006** | **0.10** |
| CrewAI | 9.66 | 246s | 27,684 | 0.30 |
| AutoGen | 9.63 | 572s | 10,793 | 0.45 |
| LangGraph | 9.42 | 506s | 8,823 | 0.32 |
| OpenAI Agents SDK | 9.31 | 448s | 8,676 | 0.36 |

**Key finding:** All frameworks produce excellent output (9.0+). The real differentiators are **speed** (6x gap), **token efficiency** (4x gap), and **consistency**.

![Quality vs Latency](results/figures/07_quality_vs_latency.png)

## Architecture

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

Each framework implementation follows the same 3-agent pipeline:

1. **Researcher** — gathers company information from mock search data
2. **Analyst** — identifies key insights, strengths, and risks
3. **Writer** — produces a structured 500-800 word report

### Fair Comparison Rules

All 5 implementations use:
- Identical system prompts (from `shared/prompts.py`)
- Identical mock tools (from `shared/tools.py`)
- Same LLM model (configured via `BenchmarkSettings`)
- Same temperature (`0` for deterministic comparison)
- No framework-specific optimizations

### Module Dependencies

```
llm_core         <── eval_core (judge uses BaseLLMProvider)

shared/          <── crewai_impl/
                 <── langgraph_impl/
                 <── autogen_impl/
                 <── msagent_impl/
                 <── agents_sdk_impl/
                 <── benchmark/

eval_core        <── benchmark/ (runner uses judge for evaluation)

No framework implementation imports from another.
```

## Project Structure

```
agent-framework-benchmark/
├── src/
│   ├── shared/              # Shared config, prompts, schemas, mock tools
│   ├── crewai_impl/         # CrewAI implementation (agents, tasks, crew)
│   ├── langgraph_impl/      # LangGraph implementation (state, nodes, graph)
│   ├── autogen_impl/        # AutoGen implementation (agents, workflow)
│   ├── msagent_impl/        # MS Agent Framework (agents, workflow)
│   ├── agents_sdk_impl/     # OpenAI Agents SDK (agents, pipeline)
│   ├── benchmark/           # Runner, metrics collection, reporting
│   ├── eval_core/           # Reusable LLM-as-judge evaluation block
│   └── llm_core/            # Vendored LLM abstraction (from rag-cli-tool)
├── notebooks/
│   └── analysis.ipynb       # Results analysis with Plotly charts
├── tests/                   # pytest test suite
├── results/                 # Benchmark output (CSV + JSON)
├── pyproject.toml
├── .env.example
└── CLAUDE.md
```

## Setup

### Prerequisites

- **Python 3.12+**
- **uv** ([install guide](https://docs.astral.sh/uv/getting-started/installation/))
- **Ollama** (for local-first mode) with a model pulled:
  ```bash
  ollama pull qwen3:14b
  ```

### Install

```bash
git clone https://github.com/LukaszGrochal/agent-framework-benchmark.git
cd agent-framework-benchmark

# Install core dependencies + dev tools
uv sync --extra dev
```

### Install Framework Dependencies

Frameworks have **incompatible version constraints** (e.g., CrewAI pins `openai<1.84` while MS Agent Framework requires `openai>=1.99`). Install them as separate dependency groups:

```bash
# Install one framework at a time
uv sync --group crewai
uv sync --group langgraph
uv sync --group autogen
uv sync --group msagent
uv sync --group agents-sdk

# Or install compatible sets together
uv sync --group langgraph --group autogen --group agents-sdk
```

> **Note:** `crewai` and `msagent`/`agents-sdk` cannot coexist in the same environment due to conflicting `openai` SDK versions. Run them in separate `uv sync` commands.

### Configure

Copy `.env.example` to `.env` and adjust as needed:

```bash
cp .env.example .env
```

Default configuration (local Ollama):
```
BENCH_LLM_PROVIDER=ollama
BENCH_LLM_MODEL=qwen3:14b
BENCH_OLLAMA_HOST=http://localhost:11434
BENCH_JUDGE_PROVIDER=ollama
BENCH_JUDGE_MODEL=qwen3:14b
BENCH_ITERATIONS=3
```

For cloud providers:
```
BENCH_LLM_PROVIDER=openai
BENCH_LLM_MODEL=gpt-4o
OPENAI_API_KEY=sk-...
```

## Usage

### Run Tests

```bash
uv run pytest
```

### Run the Benchmark

```bash
# Run full benchmark (45 runs: 3 companies x 5 frameworks x 3 iterations)
uv run python -m benchmark.runner

# Results saved to results/benchmark_results.csv
```

### Analyze Results

```bash
uv run jupyter notebook notebooks/analysis.ipynb
```

The notebook generates:
- Grouped bar chart: quality scores per framework
- Bar chart: average latency per framework
- Stacked bar chart: token usage per framework
- Cost comparison table
- Box plots: score distribution per framework (showing variance)

## Metrics Collected

| Metric | Method |
|--------|--------|
| **Output Quality** | LLM-as-judge scoring (1-10) on: completeness, accuracy, structure, insight, readability |
| **Latency** | `time.perf_counter()` end-to-end per run |
| **Token Usage** | Framework-native tracking (prompt + completion tokens) |
| **Cost** | Calculated from token counts + model pricing table |
| **Lines of Code** | Per implementation directory (excluding shared/) |

## LLM-as-Judge Evaluation

Reports are scored by an LLM judge (configurable separately from the benchmark model) on 5 criteria:

| Criterion | What It Measures |
|-----------|-----------------|
| **Completeness** | Coverage of leadership, products, market position, news, metrics |
| **Accuracy** | Factual correctness, absence of fabrications |
| **Structure** | Organization, clear sections, adherence to format |
| **Insight** | Analysis depth beyond surface-level facts |
| **Readability** | Professional writing quality and clarity |

The judge uses `temperature=0` and retries on JSON parse failures for reliable scoring.

## Test Companies

| Company | Why |
|---------|-----|
| **Anthropic** | AI company, lots of public info |
| **Stripe** | Fintech, well-documented |
| **Datadog** | Observability, relevant to portfolio |

Mock search data is pre-built for all 3 companies, ensuring deterministic and reproducible benchmarks without requiring real API calls.

## When to Use Which Framework

Based on framework characteristics (benchmark results will refine these recommendations):

| Use Case | Recommended Framework | Why |
|----------|----------------------|-----|
| **Quick prototype** | CrewAI | Simplest API, task-based, minimal boilerplate |
| **Production pipeline** | LangGraph | 1.0 GA stability, graph-based control flow, strongest guarantees |
| **Async-first workflows** | AutoGen | Native async, group chat patterns |
| **Microsoft ecosystem** | MS Agent Framework | Azure integration, successor to AutoGen + Semantic Kernel |
| **OpenAI-native apps** | OpenAI Agents SDK | Tightest OpenAI integration, built-in tracing |

## Reusable Blocks

### `llm_core` (vendored from rag-cli-tool)

Vendored LLM abstraction providing:
- `BaseLLMProvider` ABC with `generate(prompt, system) -> LLMResponse`
- `AnthropicProvider`, `OllamaProvider` — concrete implementations
- `@with_retry` decorator — exponential backoff with tenacity
- `LLMSettings` — Pydantic Settings with env var support

### `eval_core` (new — reusable)

LLM-as-judge evaluation block, designed for reuse in future projects:
- `LLMJudge` — scores reports using any `BaseLLMProvider`
- `QualityScores` / `EvalResult` — frozen dataclasses for results
- `BaseMetric` ABC — extensible metric framework
- `QualityMetric` — wraps LLMJudge for the BaseMetric interface

## Tech Stack

| Component | Choice |
|-----------|--------|
| Language | Python 3.12+ |
| Package Manager | uv |
| Build System | Hatchling |
| Default LLM | Qwen 3 14B via Ollama |
| Evaluation | LLM-as-judge (eval_core) |
| Visualization | Plotly |
| Data Analysis | Pandas |
| Testing | pytest + pytest-asyncio |
| Linting | ruff |
| Type Checking | mypy |

## License

MIT
