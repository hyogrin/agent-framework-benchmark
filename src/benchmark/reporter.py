"""Generate benchmark comparison reports for console and file output."""

from pathlib import Path

import pandas as pd

from eval_core.schemas import EvalResult
from eval_core.reporter import results_to_csv_rows, results_to_markdown_table


def generate_console_report(results: list[EvalResult]) -> str:
    """Generate a human-readable console report.

    Args:
        results: List of evaluation results.

    Returns:
        Formatted report string for console output.
    """
    if not results:
        return "No benchmark results available."

    lines = [
        "=" * 80,
        "AGENT FRAMEWORK BENCHMARK RESULTS",
        "=" * 80,
        "",
        results_to_markdown_table(results),
        "",
        "-" * 80,
        f"Total runs: {len(results)}",
    ]

    # Summary statistics
    frameworks = sorted(set(r.framework for r in results))
    for fw in frameworks:
        fw_results = [r for r in results if r.framework == fw]
        avg_quality = sum(r.quality.overall for r in fw_results) / len(fw_results)
        avg_latency = sum(r.latency_seconds for r in fw_results) / len(fw_results)
        total_cost = sum(r.estimated_cost for r in fw_results)
        lines.append(
            f"  {fw}: avg quality={avg_quality:.1f}, "
            f"avg latency={avg_latency:.1f}s, total cost=${total_cost:.4f}"
        )

    lines.append("=" * 80)
    return "\n".join(lines)


def save_detailed_csv(results: list[EvalResult], output_dir: str = "results") -> Path:
    """Save detailed results to CSV with all metrics.

    Args:
        results: List of evaluation results.
        output_dir: Directory to save the CSV file.

    Returns:
        Path to the saved CSV file.
    """
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)

    csv_path = path / "benchmark_results.csv"
    rows = results_to_csv_rows(results)
    df = pd.DataFrame(rows)
    df.to_csv(csv_path, index=False)

    return csv_path


def save_summary_csv(results: list[EvalResult], output_dir: str = "results") -> Path:
    """Save aggregated summary to CSV (one row per framework).

    Args:
        results: List of evaluation results.
        output_dir: Directory to save the CSV file.

    Returns:
        Path to the saved CSV file.
    """
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)

    rows = results_to_csv_rows(results)
    df = pd.DataFrame(rows)

    # Aggregate by framework
    numeric_cols = [
        "completeness", "accuracy", "structure", "insight",
        "readability", "overall", "latency_seconds",
        "input_tokens", "output_tokens", "total_tokens", "estimated_cost",
    ]
    summary = df.groupby("framework")[numeric_cols].mean().round(2)
    summary["run_count"] = df.groupby("framework").size()

    csv_path = path / "benchmark_summary.csv"
    summary.to_csv(csv_path)

    return csv_path
