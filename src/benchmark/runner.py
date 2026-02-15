"""Benchmark runner — orchestrates all frameworks, collects metrics."""

import logging
import time
from importlib import import_module
from pathlib import Path

import pandas as pd

from shared.config import BenchmarkSettings
from eval_core.judge import LLMJudge
from eval_core.schemas import EvalResult
from eval_core.reporter import results_to_csv_rows, results_to_markdown_table
from benchmark.metrics import calculate_cost

logger = logging.getLogger(__name__)

FRAMEWORK_MODULES: dict[str, str] = {
    "crewai": "crewai_impl.crew",
    "langgraph": "langgraph_impl.graph",
    "autogen": "autogen_impl.workflow",
    "msagent": "msagent_impl.workflow",
    "agents_sdk": "agents_sdk_impl.pipeline",
}


def _create_judge_provider(settings: BenchmarkSettings):
    """Create an LLM provider for the judge based on settings.

    Args:
        settings: Benchmark configuration.

    Returns:
        A BaseLLMProvider instance for the judge.
    """
    if settings.judge_provider == "ollama":
        from llm_core.providers.ollama import OllamaProvider

        return OllamaProvider(
            model=settings.judge_model,
            host=settings.ollama_host,
        )
    elif settings.judge_provider == "openai":
        from benchmark.providers import OpenAIProvider

        return OpenAIProvider(
            api_key=settings.openai_api_key,
            model=settings.judge_model,
        )
    elif settings.judge_provider == "anthropic":
        from llm_core.providers.anthropic import AnthropicProvider

        return AnthropicProvider(
            api_key=settings.anthropic_api_key,
            model=settings.judge_model,
        )
    else:
        msg = f"Unsupported judge provider: {settings.judge_provider}"
        raise ValueError(msg)


def run_benchmark(settings: BenchmarkSettings | None = None) -> list[EvalResult]:
    """Execute full benchmark: all frameworks x all companies x N iterations.

    Args:
        settings: Benchmark configuration. Uses defaults if None.

    Returns:
        List of EvalResult for all benchmark runs.
    """
    if settings is None:
        settings = BenchmarkSettings()

    results: list[EvalResult] = []
    judge = LLMJudge(provider=_create_judge_provider(settings))

    total_runs = len(settings.frameworks) * len(settings.companies) * settings.iterations
    run_count = 0

    for framework_name in settings.frameworks:
        module_path = FRAMEWORK_MODULES.get(framework_name)
        if module_path is None:
            logger.warning("Unknown framework: %s, skipping", framework_name)
            continue

        try:
            module = import_module(module_path)
        except ImportError as exc:
            logger.error("Failed to import %s: %s", module_path, exc)
            continue

        for company in settings.companies:
            for i in range(settings.iterations):
                run_count += 1
                logger.info(
                    "[%d/%d] Running %s for %s (iteration %d)",
                    run_count,
                    total_runs,
                    framework_name,
                    company,
                    i + 1,
                )

                try:
                    start = time.perf_counter()
                    report_text, token_usage = module.run(company, settings)
                    latency = time.perf_counter() - start
                except Exception as exc:
                    logger.error(
                        "Failed: %s / %s / iteration %d: %s",
                        framework_name,
                        company,
                        i + 1,
                        exc,
                    )
                    continue

                # Determine model name for cost calculation
                if settings.llm_provider == "openai":
                    model = settings.openai_model
                elif settings.llm_provider == "anthropic":
                    model = settings.anthropic_model
                else:
                    model = settings.llm_model

                # Evaluate quality
                try:
                    quality = judge.evaluate(
                        report_text,
                        f"Research report about {company}",
                    )
                except Exception as exc:
                    logger.error("Judge evaluation failed: %s", exc)
                    continue

                prompt_tokens = token_usage.get("prompt", 0)
                completion_tokens = token_usage.get("completion", 0)

                result = EvalResult(
                    framework=framework_name,
                    company=company,
                    iteration=i + 1,
                    quality=quality,
                    latency_seconds=round(latency, 2),
                    input_tokens=prompt_tokens,
                    output_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens,
                    estimated_cost=calculate_cost(
                        token_usage, model, settings.llm_provider
                    ),
                    report_text=report_text,
                )
                results.append(result)
                logger.info(
                    "  -> Quality: %.1f | Latency: %.1fs | Tokens: %d",
                    quality.overall,
                    latency,
                    prompt_tokens + completion_tokens,
                )

    return results


def save_results(results: list[EvalResult], settings: BenchmarkSettings) -> Path:
    """Save benchmark results to CSV.

    Args:
        results: List of evaluation results.
        settings: Benchmark configuration.

    Returns:
        Path to the saved CSV file.
    """
    results_dir = Path(settings.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    csv_path = results_dir / "benchmark_results.csv"
    rows = results_to_csv_rows(results)
    new_df = pd.DataFrame(rows)

    if csv_path.exists():
        existing_df = pd.read_csv(csv_path)
        # Drop rows that match new results (framework+company+iteration)
        key_cols = ["framework", "company", "iteration"]
        merge_keys = new_df[key_cols].drop_duplicates()
        mask = existing_df.merge(merge_keys, on=key_cols, how="left", indicator=True)
        existing_df = existing_df[mask["_merge"] == "left_only"]
        df = pd.concat([existing_df, new_df], ignore_index=True)
        logger.info("Appended %d new rows to existing %s", len(new_df), csv_path)
    else:
        df = new_df

    df.to_csv(csv_path, index=False)
    logger.info("Results saved to %s (%d total rows)", csv_path, len(df))

    return csv_path


def main() -> None:
    """CLI entry point for running the benchmark."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    settings = BenchmarkSettings()
    logger.info("Starting benchmark with settings:")
    logger.info("  Provider: %s", settings.llm_provider)
    logger.info("  Model: %s", settings.llm_model)
    logger.info("  Frameworks: %s", settings.frameworks)
    logger.info("  Companies: %s", settings.companies)
    logger.info("  Iterations: %d", settings.iterations)

    results = run_benchmark(settings)

    if results:
        csv_path = save_results(results, settings)
        print(f"\nResults saved to: {csv_path}")
        print("\n" + results_to_markdown_table(results))
    else:
        print("No results collected. Check logs for errors.")


if __name__ == "__main__":
    main()
