# Article Series Design: Agent Framework Benchmark

**Date:** 2026-02-15
**Status:** Approved
**Platforms:** dev.to, Medium (articles), LinkedIn (posts)

## Overview

Turn benchmark data (45 runs, 5 frameworks, 3 companies, 3 iterations) into a 3-article series + 4 LinkedIn posts. Tone: pragmatic engineer + curious builder ("I was curious about X, ran the numbers, here's what surprised me").

## Target Audiences

- Engineering managers choosing frameworks
- ML/AI engineers building with agent frameworks
- Broad tech audience (developers, tech leads)
- Portfolio showcase (demonstrating analytical/engineering skills)

## Content Inventory

### Data Available

- 45 benchmark runs across 5 frameworks (LangGraph, CrewAI, AutoGen, MS Agent Framework, OpenAI Agents SDK)
- 3 test companies (Anthropic, Stripe, Datadog)
- Quality metrics: completeness, accuracy, structure, insight, readability, overall (all 9.0+)
- Performance metrics: latency (93s-572s), tokens (0-28K), cost ($0 local)
- Statistical testing: Kruskal-Wallis, Mann-Whitney U with Bonferroni correction
- Consistency analysis: std dev, min/max ranges
- 13 generated Plotly charts

### Key Storylines

1. All frameworks score 9+ quality — quality is NOT the differentiator
2. Latency varies 6x (statistically significant, p=0.000001)
3. Token usage varies 3x — cost implications at scale
4. Consistency varies dramatically (msagent std=0.10 vs autogen std=0.45)
5. Beta frameworks outperform stable ones — speed vs stability tradeoff

---

## Article 1: "I Benchmarked 5 AI Agent Frameworks — Here's What Actually Matters"

**Purpose:** Hook piece. Drive traffic. Establish the benchmark's credibility.
**Length:** ~1,800 words
**LinkedIn post:** Key chart + "quality isn't the differentiator" hook

### Structure

1. **Hook** — "I ran 45 benchmarks expecting a clear winner. The answer wasn't what I expected."
2. **The Setup** — 5 frameworks, the Company Research Agent task, why this matters in 2026
3. **Quality Results** — Radar chart (fig 08). All score 9.0+. Small differences.
4. **What Actually Differentiates** — Latency (6x gap), tokens (3x gap), consistency. Scatter plot (fig 07), latency bar (fig 02).
5. **Statistical Reality Check** — Quality differences = noise. Speed differences = real. p-values in plain English.
6. **Summary Table** — Rankings with quality, latency, tokens, consistency
7. **Series Teaser** — Links to Part 2 (methodology) and Part 3 (decision guide)

### Charts

- Radar quality profiles (fig 08)
- Quality vs latency scatter (fig 07)
- Latency bar chart (fig 02)
- Summary table from notebook

---

## Article 2: "How I Built a Fair AI Agent Benchmark (Architecture & Methodology)"

**Purpose:** Portfolio showcase. Demonstrate engineering depth and systematic thinking.
**Length:** ~2,000 words
**LinkedIn post:** Architecture diagram + "Building a benchmark is harder than running one"

### Structure

1. **Hook** — "Comparing frameworks is easy. Comparing them fairly is the hard part."
2. **The Fairness Problem** — Why naive comparisons fail (different prompts, tools, temperature)
3. **Architecture** — 3-agent pipeline (Researcher -> Analyst -> Writer). ASCII diagram.
4. **Fair Comparison Rules** — Identical prompts, tools, model (Qwen 3 14B), temperature=0, no optimizations
5. **Module Dependency Fence** — eval_core isolation, no cross-framework imports, vendored llm_core
6. **LLM-as-Judge** — 5 criteria, why LLM eval, reliability measures
7. **Local-First Design** — Ollama, $0 cost, reproducibility, no API dependency
8. **Dependency Hell** — CrewAI pins openai<1.84, MS Agent needs >=1.99. Solution: uv groups.
9. **Retrospective** — What I'd do differently (honest reflection)

### Visuals

- Architecture diagram (from README)
- Module dependency diagram
- Code snippets from shared config

---

## Article 3: "Choosing an Agent Framework in 2026: A Data-Driven Decision Guide"

**Purpose:** Actionable takeaways. The piece people bookmark and share.
**Length:** ~1,500 words
**LinkedIn post:** Decision matrix + "Which framework should you pick?"

### Structure

1. **Hook** — "You've seen the benchmarks. Which one should YOU use?"
2. **Decision Matrix** — Use case -> framework mapping with data backing
3. **Consistency Factor** — Why variance > mean in production. Range comparisons.
4. **Token Cost Story** — 27K vs 8.7K tokens. At-scale cost projections.
5. **Production Readiness Tiers** — T1: LangGraph (GA), T2: CrewAI+SDK (stable), T3: AutoGen (maintenance), T4: msagent (beta)
6. **My Recommendation** — Opinionated, data-backed, situation-dependent
7. **Full Data** — Link to GitHub repo, notebook, raw CSV

### Charts

- Token efficiency (fig 11)
- Score distribution box plots (fig 04)
- Quality heatmap (fig 13)

---

## Standalone LinkedIn Post: "All 5 AI Agent Frameworks Scored 9+ Out of 10"

**Purpose:** Contrarian hook. Generate discussion. No external link required.
**Length:** ~200 words (LinkedIn native)

### Draft

```
I benchmarked 5 AI agent frameworks. All of them scored 9+ out of 10.

Quality isn't the differentiator anymore.

Here's what actually separates them:

Speed: 93 seconds vs 572 seconds (6x gap)
Token cost: 8K vs 28K tokens (3x gap)
Consistency: 0.2 vs 1.4 score range

The frameworks: LangGraph, CrewAI, AutoGen, MS Agent Framework, OpenAI Agents SDK

The task: 45 automated research reports with LLM-as-judge scoring

My takeaway: In 2026, picking an agent framework is less about
"which one is smartest" and more about "which one fits your constraints."

[Series link in comments]
```

---

## Publishing Schedule

| Day | Platform | Content |
|-----|----------|---------|
| Day 1 | dev.to + Medium | Article 1 (benchmark results) |
| Day 1 | LinkedIn | Post 1 (key chart + hook for Article 1) |
| Day 4 | LinkedIn | Standalone post (contrarian "9+ quality" insight) |
| Day 7 | dev.to + Medium | Article 2 (methodology) |
| Day 7 | LinkedIn | Post 2 (architecture diagram + hook for Article 2) |
| Day 11 | dev.to + Medium | Article 3 (decision guide) |
| Day 11 | LinkedIn | Post 3 (decision matrix + hook for Article 3) |

## GitHub Preparation

Before publishing:
- Clean up repo (ensure README is polished, results committed)
- Add LICENSE if missing
- Ensure notebooks run cleanly
- Add link to article series in README
