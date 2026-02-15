# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**agent-framework-benchmark** is a benchmarking framework that implements the same "Company Research Agent" workflow across **5 different agent frameworks**, with automated benchmarking and LLM-as-judge evaluation.

**Key design principle:** Local-first — runs on local models via Ollama by default, with cloud providers (OpenAI, Anthropic) as configurable alternatives.

## Project Status

Scaffolding is complete. All modules, tests, and documentation are in place. Ready for framework-level integration testing against a running Ollama instance.

## Language & Tooling

- **Language:** Python 3.12+
- **Package Manager:** uv
- **Build System:** Hatchling
- **Linter/Formatter:** ruff (`.ruff_cache/` in gitignore)
- **Type Checker:** mypy (`.mypy_cache/` in gitignore)
- **Test Framework:** pytest (`.pytest_cache/` in gitignore)
- **Environment:** Uses `.env` for configuration (in gitignore — never commit secrets)

## Common Commands

```bash
uv sync --extra dev                 # Install core + dev dependencies
uv sync --group langgraph           # Install a framework group
uv run pytest                       # Run tests (30 tests)
uv run python -m benchmark.runner   # Run the benchmark
uv run jupyter notebook             # Open analysis notebook
```

## Dependency Groups

Frameworks have incompatible version constraints and are installed as separate dependency groups:

- `crewai` — conflicts with `msagent` and `agents-sdk` (openai version pin)
- `langgraph`, `autogen`, `agents-sdk` — can be installed together
- `msagent` — beta, requires prerelease

## Architecture Rules

- `eval_core` must NOT import from `shared/` or any framework implementation
- `eval_core` may import from `llm_core` (for the judge)
- Framework implementations import from `shared/` but NOT from each other
- Vendored `llm_core` (at `src/llm_core/`) must remain UNMODIFIED from rag-cli-tool
- All imports use `from llm_core.*` (the package lives directly under `src/`)

## Code Quality Requirements

- Type hints on all functions (Python 3.12+ syntax: `list[str]` not `List[str]`)
- Google-style docstrings on all public functions
- No bare `except:` clauses
- Use `pathlib.Path` instead of string paths
- Module-level `__all__` exports
- All frameworks must use temperature=0 for fair comparison
