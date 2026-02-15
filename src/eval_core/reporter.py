"""Generate evaluation reports from benchmark results."""

from eval_core.schemas import EvalResult

__all__ = [
    "results_to_csv_rows",
    "results_to_markdown_table",
]


def results_to_markdown_table(results: list[EvalResult]) -> str:
    """Generate a markdown comparison table from evaluation results.

    Groups results by framework, computing averages across companies and iterations.

    Args:
        results: List of EvalResult from benchmark runs.

    Returns:
        Markdown-formatted comparison table as a string.
    """
    if not results:
        return "No results to report."

    # Group by framework and compute averages
    framework_stats: dict[str, dict[str, list[float]]] = {}
    for r in results:
        if r.framework not in framework_stats:
            framework_stats[r.framework] = {
                "completeness": [],
                "accuracy": [],
                "structure": [],
                "insight": [],
                "readability": [],
                "overall": [],
                "latency": [],
                "tokens": [],
                "cost": [],
            }
        stats = framework_stats[r.framework]
        stats["completeness"].append(r.quality.completeness)
        stats["accuracy"].append(r.quality.accuracy)
        stats["structure"].append(r.quality.structure)
        stats["insight"].append(r.quality.insight)
        stats["readability"].append(r.quality.readability)
        stats["overall"].append(r.quality.overall)
        stats["latency"].append(r.latency_seconds)
        stats["tokens"].append(float(r.total_tokens))
        stats["cost"].append(r.estimated_cost)

    def _avg(values: list[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    # Build table
    header = (
        "| Framework | Quality | Complete | Accurate | Structure | Insight "
        "| Readable | Latency (s) | Tokens | Cost ($) |"
    )
    separator = (
        "|-----------|---------|----------|----------|-----------|---------|"
        "----------|-------------|--------|----------|"
    )

    rows = []
    for fw, stats in sorted(framework_stats.items()):
        row = (
            f"| {fw} "
            f"| {_avg(stats['overall']):.1f} "
            f"| {_avg(stats['completeness']):.1f} "
            f"| {_avg(stats['accuracy']):.1f} "
            f"| {_avg(stats['structure']):.1f} "
            f"| {_avg(stats['insight']):.1f} "
            f"| {_avg(stats['readability']):.1f} "
            f"| {_avg(stats['latency']):.1f} "
            f"| {_avg(stats['tokens']):.0f} "
            f"| {_avg(stats['cost']):.4f} |"
        )
        rows.append(row)

    return "\n".join([header, separator, *rows])


def results_to_csv_rows(results: list[EvalResult]) -> list[dict]:
    """Convert evaluation results to flat dictionaries for CSV export.

    Args:
        results: List of EvalResult from benchmark runs.

    Returns:
        List of flat dictionaries suitable for pandas DataFrame / CSV.
    """
    rows = []
    for r in results:
        rows.append({
            "framework": r.framework,
            "company": r.company,
            "iteration": r.iteration,
            "completeness": r.quality.completeness,
            "accuracy": r.quality.accuracy,
            "structure": r.quality.structure,
            "insight": r.quality.insight,
            "readability": r.quality.readability,
            "overall": r.quality.overall,
            "reasoning": r.quality.reasoning,
            "latency_seconds": r.latency_seconds,
            "input_tokens": r.input_tokens,
            "output_tokens": r.output_tokens,
            "total_tokens": r.total_tokens,
            "estimated_cost": r.estimated_cost,
            "report_text": r.report_text,
        })
    return rows
