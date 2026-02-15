"""Token counting, cost calculation, and latency utilities."""

# Pricing per 1M tokens (input/output) for common models.
# Local models (Ollama, LM Studio, llama.cpp) are effectively free.
_PRICING: dict[str, tuple[float, float]] = {
    # (input_cost_per_1M, output_cost_per_1M)
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4-turbo": (10.00, 30.00),
    "claude-sonnet-4-5-20250929": (3.00, 15.00),
    "claude-3-5-sonnet-latest": (3.00, 15.00),
    "claude-3-opus-latest": (15.00, 75.00),
    "claude-3-haiku-20240307": (0.25, 1.25),
}


def calculate_cost(
    token_usage: dict,
    model: str,
    provider: str = "ollama",
) -> float:
    """Calculate estimated cost based on token usage and model pricing.

    Local providers (ollama, lmstudio, llamacpp) return 0.0 since they're free.
    Cloud providers look up pricing from the pricing table.

    Args:
        token_usage: Dict with 'prompt' and 'completion' token counts.
        model: Model name for pricing lookup.
        provider: LLM provider name.

    Returns:
        Estimated cost in USD.
    """
    # Local providers are free
    if provider in ("ollama", "lmstudio", "llamacpp"):
        return 0.0

    prompt_tokens = token_usage.get("prompt", 0)
    completion_tokens = token_usage.get("completion", 0)

    if model in _PRICING:
        input_rate, output_rate = _PRICING[model]
    else:
        # Default to gpt-4o pricing as a reasonable estimate
        input_rate, output_rate = _PRICING["gpt-4o"]

    cost = (prompt_tokens * input_rate + completion_tokens * output_rate) / 1_000_000
    return round(cost, 6)


def count_lines_of_code(directory: str) -> int:
    """Count lines of Python code in a directory (excluding empty lines and comments).

    Args:
        directory: Path to the directory to count.

    Returns:
        Total lines of Python code.
    """
    from pathlib import Path

    total = 0
    path = Path(directory)
    if not path.exists():
        return 0

    for py_file in path.rglob("*.py"):
        for line in py_file.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                total += 1

    return total
