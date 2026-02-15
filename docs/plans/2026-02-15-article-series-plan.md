# Article Series Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Produce 3 publishable articles (dev.to/Medium) + 4 LinkedIn posts from the benchmark data, and prepare the GitHub repo as a portfolio piece.

**Architecture:** Articles live in `articles/` as Markdown with embedded image references to `results/figures/`. LinkedIn posts live in `articles/linkedin/`. Repo gets cleaned up and pushed as public portfolio project.

**Tech Stack:** Markdown (articles), PNG charts (from Plotly notebook), Git

---

## Task 1: Commit Current Work & Create Articles Structure

**Files:**
- Stage: `notebooks/analysis.ipynb`, `results/benchmark_results.csv`, `src/msagent_impl/workflow.py`, `results/figures/`, `scripts/`, `docs/`
- Create: `articles/` directory
- Create: `articles/linkedin/` directory

**Step 1: Commit all pending benchmark work**

```bash
git add notebooks/analysis.ipynb results/benchmark_results.csv src/msagent_impl/workflow.py results/figures/ results/.gitkeep scripts/ docs/
git commit -m "Add benchmark results, analysis figures, and article series design"
```

**Step 2: Create article directories**

```bash
mkdir -p articles/linkedin
```

**Step 3: Commit structure**

```bash
git add articles/
git commit -m "Add articles directory structure"
```

---

## Task 2: Write Article 1 — "I Benchmarked 5 AI Agent Frameworks"

**Files:**
- Create: `articles/01-benchmark-results.md`

**Context needed:**
- Summary table from notebook cell 14 (framework rankings)
- Key stats: quality range 9.31-9.87, latency range 93s-572s, token range 0-28K
- Statistical significance: Kruskal-Wallis p=0.0052 (quality), p=0.000001 (latency)
- Charts: `results/figures/08_radar_quality_profiles.png`, `07_quality_vs_latency.png`, `02_latency.png`

**Step 1: Write the article**

Create `articles/01-benchmark-results.md` with this structure:

```markdown
# I Benchmarked 5 AI Agent Frameworks — Here's What Actually Matters

*45 runs. 5 frameworks. 3 companies. The results surprised me.*

## Why I Built This

[2-3 paragraphs: Agent frameworks are proliferating in 2026. Teams are choosing between LangGraph, CrewAI, AutoGen, MS Agent Framework, and OpenAI Agents SDK with little objective data. I built a controlled benchmark to find out which one actually performs best.]

## The Experiment

[Setup paragraph: Same 3-agent pipeline (Researcher → Analyst → Writer), same prompts, same tools, same LLM (Qwen 3 14B via Ollama), temperature=0. Each framework researched 3 companies × 3 iterations = 9 runs per framework, 45 total. Output scored by LLM-as-judge on 5 criteria.]

**Frameworks tested:**

| Framework | Version | Architecture |
|-----------|---------|-------------|
| LangGraph | 1.0.x | Graph-based state machine |
| CrewAI | 1.9.x | Task-based sequential |
| AutoGen | 0.7.x | Async group chat |
| MS Agent Framework | 1.0.0b | Sequential orchestration |
| OpenAI Agents SDK | latest | Runner-based pipeline |

## The Results Everyone Expects: Quality Scores

[Paragraph: reveal all frameworks score 9.0+ out of 10. Show radar chart.]

![Quality Dimension Profiles](../results/figures/08_radar_quality_profiles.png)

**Summary table:**

| Framework | Quality | Completeness | Accuracy | Structure | Insight | Readability |
|-----------|---------|-------------|----------|-----------|---------|-------------|
| MS Agent | 9.87 | 10.00 | 10.00 | 10.00 | 9.33 | 10.00 |
| CrewAI | 9.66 | 9.44 | 9.44 | 9.89 | 9.56 | 10.00 |
| AutoGen | 9.63 | 9.44 | 9.67 | 9.89 | 9.33 | 9.89 |
| LangGraph | 9.42 | 9.11 | 9.44 | 9.89 | 9.22 | 9.78 |
| Agents SDK | 9.31 | 9.00 | 9.11 | 9.89 | 9.00 | 9.78 |

[Paragraph: The spread is just 0.56 points. On a 10-point scale, that's noise. All frameworks produce excellent output for this task.]

## What Actually Differentiates Them

[Paragraph: If quality is a wash, what IS different? Three things: speed, token cost, and consistency.]

### Speed: A 6x Gap

![Latency by Framework](../results/figures/02_latency.png)

[Paragraph: MS Agent Framework completes in 93 seconds. AutoGen takes 572 seconds. That's not a subtle difference — it's 6x. CrewAI lands at 246s, LangGraph at 506s, Agents SDK at 448s.]

### Token Cost: 3x Difference

[Paragraph: CrewAI consumed 27,684 tokens per run — 3x more than LangGraph (8,823) or Agents SDK (8,676). Same quality output, triple the token bill. At GPT-4o pricing ($5/1M input, $15/1M output), that adds up fast at scale.]

### Consistency: Who Do You Trust in Production?

[Paragraph: MS Agent Framework had a standard deviation of just 0.10 on quality scores (range: 9.8-10.0). AutoGen swung from 8.6 to 10.0 (std=0.45). In production, predictability matters as much as peak performance.]

## Are These Differences Real? A Statistical Check

![Quality vs Latency](../results/figures/07_quality_vs_latency.png)

[Paragraph: Kruskal-Wallis H-test on quality: p=0.005 — differences exist. But after Bonferroni correction on pairwise tests, only one pair (Agents SDK vs MS Agent, p=0.0003) is statistically significant. Most quality differences are noise.]

[Paragraph: Latency tells a different story. Kruskal-Wallis p=0.000001. The speed differences are very real.]

[Paragraph: Translation: Don't pick a framework for quality — they're all good. Pick for speed, cost, and consistency.]

## The Ranking

| Framework | Quality | Latency | Tokens | Consistency (Std) |
|-----------|---------|---------|--------|-------------------|
| MS Agent | 9.87 | 93s | N/A* | 0.10 |
| CrewAI | 9.66 | 246s | 27,684 | 0.30 |
| AutoGen | 9.63 | 572s | 10,793 | 0.45 |
| LangGraph | 9.42 | 506s | 8,823 | 0.32 |
| Agents SDK | 9.31 | 448s | 8,676 | 0.36 |

*MS Agent Framework beta didn't expose token tracking at time of benchmark.

## What's Next

In **Part 2**, I'll show how I built this benchmark to be actually fair — the architecture decisions, dependency hell, and why "just run them all" doesn't work.

In **Part 3**, a practical decision guide: which framework for which situation, backed by this data.

**Full data and code:** [GitHub repo link]

---

*Built with Python 3.12, uv, Ollama (Qwen 3 14B), and too many hours debugging dependency conflicts.*
```

**Step 2: Review and refine prose**

Read through the article. Ensure:
- Hook is compelling (first 2 sentences)
- Data points are accurate (cross-check with CSV)
- Charts are referenced correctly
- Tone is "pragmatic engineer + curious builder"
- Length is ~1,800 words

**Step 3: Commit**

```bash
git add articles/01-benchmark-results.md
git commit -m "Add Article 1: benchmark results comparison"
```

---

## Task 3: Write Article 2 — "How I Built a Fair AI Agent Benchmark"

**Files:**
- Create: `articles/02-benchmark-methodology.md`

**Context needed:**
- Architecture diagram from README.md (lines 19-48)
- Module dependency rules from CLAUDE.md
- Fair comparison rules from README.md (lines 56-63)
- Dependency conflict details from README.md (lines 126-142)
- Code from `src/shared/config.py`, `src/shared/prompts.py`, `src/eval_core/`

**Step 1: Write the article**

Create `articles/02-benchmark-methodology.md` with this structure:

```markdown
# How I Built a Fair AI Agent Benchmark (Architecture & Methodology)

*Comparing agent frameworks is easy. Comparing them fairly is the hard part.*

## The Problem with Framework Comparisons

[2-3 paragraphs: Most "comparisons" use different prompts, different tools, different temperatures. Framework X gets a carefully tuned prompt while Framework Y gets a generic one. The results tell you about prompt engineering skill, not framework quality. I wanted a comparison where the ONLY variable was the framework itself.]

## The Task: Company Research Agent

[Paragraph: describe the 3-agent pipeline]

1. **Researcher** — gathers company information from mock search data
2. **Analyst** — identifies key insights, strengths, and risks
3. **Writer** — produces a structured 500-800 word research report

[Paragraph: Why this task? It tests real agent capabilities: tool use, multi-step reasoning, synthesis, and structured output. Simple enough to implement in all frameworks, complex enough to reveal differences.]

## Architecture

```
[Include ASCII architecture diagram from README]
```

[Paragraph explaining: benchmark runner orchestrates 45 runs, each framework uses shared infrastructure, eval_core scores outputs independently.]

## The 5 Rules of Fair Comparison

[Section with 5 numbered rules, each with explanation:]

1. **Identical prompts** — All frameworks use the same system prompts from `shared/prompts.py`
2. **Identical tools** — Same mock search tools from `shared/tools.py` (deterministic, no real API calls)
3. **Same model** — Qwen 3 14B via Ollama for all frameworks
4. **Temperature = 0** — Eliminate randomness from the model itself
5. **No framework-specific optimizations** — No tuning, no custom chains, no tricks

[Code snippet showing shared config]

## The Dependency Fence

[Diagram of module dependencies]

[Paragraph: eval_core CANNOT import from shared/ or any framework. Frameworks CANNOT import from each other. llm_core is vendored and unmodified. This prevents accidental coupling and ensures the judge is truly independent.]

## LLM-as-Judge: Automated Quality Scoring

[Paragraph: Each report scored on 5 criteria (completeness, accuracy, structure, insight, readability) by a separate LLM judge call.]

[Table of criteria and what each measures — from README lines 214-220]

[Paragraph: Why LLM-as-judge instead of human evaluation? Scale (45 reports), consistency (no evaluator fatigue), and reproducibility. The judge uses temperature=0 and retries on JSON parse failures.]

[Paragraph: Limitation — LLM judges have known biases (verbosity preference, position bias). For a framework comparison where all outputs are structurally similar, these biases affect all frameworks equally, so relative rankings remain valid.]

## Local-First: Why Ollama Instead of GPT-4

[Paragraph: Running 45 benchmark iterations through GPT-4 would cost hundreds of dollars. With Ollama + Qwen 3 14B, the cost is $0. More importantly: no API rate limits, no network variability in latency measurements, complete reproducibility.]

[Paragraph: Trade-off — local models are smaller and less capable than frontier models. But since we're measuring relative framework performance (not absolute model capability), this is fine. A local model reveals framework overhead more clearly because there's no network latency masking it.]

## Surviving Dependency Hell

[Paragraph: The hardest part wasn't the code — it was getting 5 frameworks to coexist. CrewAI pins `openai<1.84`. MS Agent Framework requires `openai>=1.99`. They literally cannot be installed together.]

[Paragraph: Solution — uv dependency groups. Each framework is its own install group. The benchmark runner installs one group at a time, runs that framework's tests, then swaps.]

```bash
uv sync --group crewai      # Install CrewAI (pins openai<1.84)
uv sync --group msagent     # Install MS Agent (needs openai>=1.99)
```

[Paragraph: This is a real-world concern for teams evaluating frameworks. Your existing dependency tree might rule out certain choices before you even write a line of code.]

## What I'd Do Differently

[Honest retrospective, 3-4 bullet points:]
- More test companies (3 is small — 5-7 would give better statistical power)
- Multiple task types (research is one workflow; add coding, data analysis, customer support)
- Human eval baseline (validate that LLM judge rankings match human intuition)
- Test with cloud models too (GPT-4o, Claude) to see if framework rankings change with model capability

## The Full Stack

| Component | Choice | Why |
|-----------|--------|-----|
| Language | Python 3.12+ | Type hints, async/await, framework support |
| Package Manager | uv | Fast, dependency groups for conflicts |
| LLM | Qwen 3 14B (Ollama) | Free, local, reproducible |
| Evaluation | LLM-as-judge (eval_core) | Scalable, consistent |
| Visualization | Plotly | Interactive charts, publication quality |
| Testing | pytest | Standard, async support |

**Full code:** [GitHub repo link]

---

*Part 1 covered the results. Part 3 will be a practical guide for choosing your framework.*
```

**Step 2: Review and refine**

- Verify architecture diagram matches actual README
- Check that code snippets are accurate
- Ensure dependency version numbers match pyproject.toml
- Tone: educational, showing thought process
- Length: ~2,000 words

**Step 3: Commit**

```bash
git add articles/02-benchmark-methodology.md
git commit -m "Add Article 2: benchmark methodology deep dive"
```

---

## Task 4: Write Article 3 — "Choosing an Agent Framework in 2026"

**Files:**
- Create: `articles/03-decision-guide.md`

**Context needed:**
- Summary table from notebook cell 14
- Consistency data from notebook cell 18
- Token efficiency from notebook cell 28
- Production readiness from README lines 233-243
- Score distribution: `results/figures/04_score_distribution.png`
- Token efficiency: `results/figures/11_token_efficiency.png`
- Quality heatmap: `results/figures/13_quality_heatmap.png`

**Step 1: Write the article**

Create `articles/03-decision-guide.md` with this structure:

```markdown
# Choosing an Agent Framework in 2026: A Data-Driven Decision Guide

*You've seen the benchmarks. Now the question that matters: which one should YOU use?*

## The Short Answer

There is no "best" framework. There's the best framework **for your situation**. Here's how to figure out which one that is.

## The Decision Matrix

| Your Priority | Best Choice | Why (Data) |
|--------------|-------------|------------|
| **Fastest prototype** | CrewAI | Simplest API, 246s latency, 9.66 quality |
| **Production stability** | LangGraph | 1.0 GA, graph-based control, 9.42 quality |
| **Raw speed** | MS Agent Framework | 93s latency (6x faster), 9.87 quality |
| **Microsoft/Azure** | MS Agent Framework | Ecosystem integration, successor to AutoGen + Semantic Kernel |
| **OpenAI-native** | Agents SDK | Tightest OpenAI integration, built-in tracing |
| **Lowest token cost** | Agents SDK | 8,676 tokens/run (vs CrewAI's 27,684) |
| **Most consistent** | MS Agent Framework | Std=0.10, range=0.2 (narrowest) |

## Factor 1: Consistency Matters More Than Average

[Paragraph: In production, you care less about "what's the best case?" and more about "what's the worst case?" A framework that averages 9.5 but occasionally drops to 8.6 is harder to deploy than one that consistently hits 9.8-10.0.]

![Score Distribution](../results/figures/04_score_distribution.png)

| Framework | Mean | Std Dev | Min | Max | Range |
|-----------|------|---------|-----|-----|-------|
| MS Agent | 9.87 | 0.10 | 9.8 | 10.0 | 0.2 |
| CrewAI | 9.66 | 0.30 | 9.2 | 10.0 | 0.8 |
| LangGraph | 9.42 | 0.32 | 9.0 | 10.0 | 1.0 |
| Agents SDK | 9.31 | 0.36 | 8.6 | 9.6 | 1.0 |
| AutoGen | 9.63 | 0.45 | 8.6 | 10.0 | 1.4 |

[Paragraph: MS Agent Framework is remarkable — tightest range in both quality AND latency. The catch: it's still in beta (GA expected ~March 2026).]

## Factor 2: Token Cost at Scale

[Paragraph: At $0 with local Ollama, tokens don't matter. But if you're deploying with GPT-4o or Claude, they matter a lot.]

![Token Efficiency](../results/figures/11_token_efficiency.png)

[Quick cost projection table:]

| Framework | Tokens/Run | Cost at GPT-4o rates* | 1,000 runs/month |
|-----------|-----------|----------------------|-------------------|
| Agents SDK | 8,676 | ~$0.09 | ~$90 |
| LangGraph | 8,823 | ~$0.09 | ~$90 |
| AutoGen | 10,793 | ~$0.11 | ~$110 |
| CrewAI | 27,684 | ~$0.28 | ~$280 |

*Estimated using GPT-4o pricing ($5/1M input, $15/1M output), rough split.

[Paragraph: CrewAI's 3x token overhead matters. For the same quality, you'd pay 3x more at scale. Understand WHY before choosing — CrewAI's task decomposition generates more intermediate LLM calls.]

## Factor 3: Production Readiness

[Tiered assessment:]

**Tier 1 — Production Ready**
- **LangGraph 1.0** — GA release, graph-based architecture gives explicit control over agent flow, largest community, best debugging tools

**Tier 2 — Stable, Active Development**
- **CrewAI 1.9** — Rapidly evolving, large community, good docs, some API churn between versions
- **OpenAI Agents SDK** — Backed by OpenAI, stable API, but tightly coupled to OpenAI ecosystem

**Tier 3 — Use with Caution**
- **AutoGen 0.7** — In maintenance mode. Microsoft is putting energy into MS Agent Framework instead. Still works but unlikely to get major improvements.

**Tier 4 — High Potential, Not Yet GA**
- **MS Agent Framework 1.0.0b** — Topped every metric in our benchmark. Beta with GA ~March 2026. If timeline allows, worth waiting for.

## Factor 4: Architecture Style

[Brief paragraph per framework's architectural approach and when it fits:]

- **Graph-based (LangGraph):** Best when you need explicit control over agent flow. You define nodes and edges. Great for complex, branching workflows.
- **Task-based (CrewAI):** Best for quick prototypes. Define tasks and agents, framework handles orchestration. Lowest boilerplate.
- **Group chat (AutoGen):** Best for collaborative multi-agent scenarios. Agents discuss in a shared context. Novel but harder to debug.
- **Sequential (MS Agent Framework):** Clean pipeline. Each agent processes and passes forward. Simple mental model.
- **Runner-based (Agents SDK):** Pipeline with handoffs. Good integration with OpenAI tools and tracing.

## My Recommendation

[Opinionated, honest take:]

**If I were starting a production project today:** LangGraph. It's the only 1.0 GA framework, the graph model gives you explicit control, and the quality/latency tradeoff is acceptable.

**If I were prototyping:** CrewAI. Fastest to get running, good quality, accept the token overhead for speed of development.

**If I could wait 2 months:** MS Agent Framework. The benchmark numbers are remarkable, and Microsoft's backing means strong enterprise support post-GA.

**If I were already in the OpenAI ecosystem:** Agents SDK. Don't fight your stack.

## Get the Data

Everything is open source:
- **GitHub:** [repo link] — Full benchmark code, all 5 implementations, analysis notebook
- **Raw data:** 45 runs with quality scores, latency, tokens, and full report text
- **Notebook:** Interactive Plotly charts you can explore yourself

---

*This is Part 3 of a 3-part series. [Part 1: The benchmark results](link) | [Part 2: The methodology](link)*
```

**Step 2: Review and refine**

- Verify all numbers match the CSV data
- Ensure cost projections are reasonable (sanity check GPT-4o pricing)
- Check production readiness claims against actual framework versions
- Tone: opinionated but backed by data
- Length: ~1,500 words

**Step 3: Commit**

```bash
git add articles/03-decision-guide.md
git commit -m "Add Article 3: framework decision guide"
```

---

## Task 5: Write LinkedIn Posts

**Files:**
- Create: `articles/linkedin/post-1-results-hook.md`
- Create: `articles/linkedin/post-2-contrarian-standalone.md`
- Create: `articles/linkedin/post-3-methodology.md`
- Create: `articles/linkedin/post-4-decision-guide.md`

**Step 1: Write all 4 LinkedIn posts**

**Post 1** (`post-1-results-hook.md`) — Accompanies Article 1:
```markdown
I spent weeks benchmarking 5 AI agent frameworks.

45 runs. Same task. Same model. Same prompts. Zero shortcuts.

The frameworks: LangGraph, CrewAI, AutoGen, MS Agent Framework, OpenAI Agents SDK.

Here's what I expected: a clear quality winner.
Here's what I found: they ALL scored 9+ out of 10.

The real differences? Not quality.

- Speed: 93s vs 572s (a 6x gap)
- Tokens: 8K vs 28K (a 3x cost difference)
- Consistency: some frameworks swing wildly between runs

Quality is table stakes. The framework you pick should depend on what you're optimizing for.

Full breakdown with data and charts:
[Article 1 link]

#AI #AgentFrameworks #LLM #Benchmark #Python
```

**Post 2** (`post-2-contrarian-standalone.md`) — Standalone, no article:
```markdown
I benchmarked 5 AI agent frameworks.

All of them scored 9+ out of 10 on quality.

Quality isn't the differentiator anymore.

Here's what actually separates them:

Speed: 93 seconds vs 572 seconds (6x gap)
Token cost: 8K vs 28K tokens per run (3x gap)
Consistency: 0.2 vs 1.4 point score range

The frameworks: LangGraph, CrewAI, AutoGen, MS Agent Framework, OpenAI Agents SDK

The task: 45 automated company research reports scored by LLM-as-judge

My takeaway after running the numbers:

In 2026, picking an agent framework is less about "which one is smartest" and more about "which one fits your constraints."

Speed-constrained? Different answer.
Cost-constrained? Different answer.
Need predictability? Different answer.

The data is open source if you want to check my work: [repo link]

#AI #AgentFrameworks #DataDriven #Python #MachineLearning
```

**Post 3** (`post-3-methodology.md`) — Accompanies Article 2:
```markdown
Building a fair AI benchmark is harder than building the agents.

When I set out to compare 5 agent frameworks, I realized most existing comparisons have a fatal flaw: they don't control for variables.

Different prompts. Different tools. Different temperatures. You end up measuring prompt engineering skill, not framework quality.

So I built a controlled experiment:

- Same 3-agent pipeline across all 5 frameworks
- Identical system prompts (shared module)
- Identical mock tools (no real API variance)
- Same LLM (Qwen 3 14B via Ollama)
- Temperature = 0 everywhere
- Automated LLM-as-judge scoring

The hardest part? Dependency management.

CrewAI requires openai<1.84.
MS Agent Framework requires openai>=1.99.

They literally cannot coexist in the same Python environment.

Solution: uv dependency groups. Each framework gets its own install profile.

If you're evaluating agent frameworks for your team, methodology matters as much as results.

Full architecture breakdown: [Article 2 link]

#Python #AI #SoftwareEngineering #Benchmarking #AgentFrameworks
```

**Post 4** (`post-4-decision-guide.md`) — Accompanies Article 3:
```markdown
"Which AI agent framework should I use?"

After benchmarking 5 of them with 45 controlled runs, here's my honest answer:

It depends on exactly 4 factors:

1. SPEED — MS Agent Framework finishes in 93s. AutoGen takes 572s. If latency matters, this alone narrows your choice.

2. COST — CrewAI uses 3x more tokens than Agents SDK for the same quality output. At GPT-4o prices, that's ~$280/month vs ~$90/month for 1,000 runs.

3. CONSISTENCY — MS Agent Framework varies by 0.2 points. AutoGen by 1.4. In production, predictable beats brilliant.

4. PRODUCTION READINESS — Only LangGraph is at 1.0 GA. MS Agent Framework is beta (GA ~March 2026). AutoGen is in maintenance mode.

My recommendations:

Starting production today? LangGraph.
Prototyping fast? CrewAI.
Can wait 2 months? MS Agent Framework.
Already on OpenAI? Agents SDK.

Full decision guide with data: [Article 3 link]

#AI #AgentFrameworks #Engineering #TechLeadership #Python
```

**Step 2: Commit**

```bash
git add articles/linkedin/
git commit -m "Add 4 LinkedIn posts for article series"
```

---

## Task 6: Polish README for Portfolio

**Files:**
- Modify: `README.md` (add Results section, article links placeholder)

**Step 1: Add a Results Summary section to README**

After the "Frameworks Compared" table, add:

```markdown
## Key Results

> Full analysis: [Article Series] | [Interactive Notebook](notebooks/analysis.ipynb)

| Framework | Quality (1-10) | Latency | Tokens | Consistency |
|-----------|---------------|---------|--------|-------------|
| MS Agent Framework | **9.87** | **93s** | N/A* | **0.10** |
| CrewAI | 9.66 | 246s | 27,684 | 0.30 |
| AutoGen | 9.63 | 572s | 10,793 | 0.45 |
| LangGraph | 9.42 | 506s | 8,823 | 0.32 |
| OpenAI Agents SDK | 9.31 | 448s | 8,676 | 0.36 |

**Key finding:** All frameworks produce excellent output (9.0+). The real differentiators are speed (6x gap), token efficiency (3x gap), and consistency.

![Quality vs Latency](results/figures/07_quality_vs_latency.png)
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "Add benchmark results summary to README"
```

---

## Task 7: Final Review & Push

**Step 1: Review all articles for consistency**

Cross-check:
- All data points match between articles (same numbers everywhere)
- Chart references are correct file paths
- Series cross-links are consistent
- Tone is consistent across all pieces

**Step 2: Push to GitHub**

```bash
git push origin main
```

**Step 3: Note placeholder links**

After publishing each article on dev.to/Medium, come back and:
- Update article cross-links with real URLs
- Update README with article links
- Update LinkedIn posts with article URLs

---

## Publishing Checklist

After all content is written and pushed:

- [ ] Publish Article 1 on dev.to
- [ ] Cross-post Article 1 on Medium
- [ ] Post LinkedIn Post 1 (Day 1)
- [ ] Post LinkedIn Post 2 — standalone (Day 4)
- [ ] Publish Article 2 on dev.to + Medium (Day 7)
- [ ] Post LinkedIn Post 3 (Day 7)
- [ ] Publish Article 3 on dev.to + Medium (Day 11)
- [ ] Post LinkedIn Post 4 (Day 11)
- [ ] Update all cross-links with real URLs
- [ ] Update README with article links
