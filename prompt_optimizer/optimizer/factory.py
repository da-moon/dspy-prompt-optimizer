"""Convenience helpers for prompt optimization."""

from __future__ import annotations

from .strategies import OptimizationStrategy


def optimize_prompt(prompt_text: str, strategy: OptimizationStrategy) -> str:
    """Optimize ``prompt_text`` using ``strategy``."""
    return strategy.optimize(prompt_text)
