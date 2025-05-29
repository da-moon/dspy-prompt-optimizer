"""Interfaces and configuration models for optimizers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

import dspy


class OptimizationStrategy(ABC):
    """Abstract interface for prompt optimization strategies."""

    @abstractmethod
    def optimize(self, prompt_text: str) -> str:
        """Return an optimized version of ``prompt_text``."""
        raise NotImplementedError


@dataclass
class SelfRefinementConfig:
    """Configuration for :class:`SelfRefinementOptimizer`."""

    model: str
    api_key: str
    max_tokens: int = 64000
    verbose: bool = False


@dataclass
class ExampleBasedConfig:
    """Configuration for :class:`ExampleBasedOptimizer`."""

    model: str
    api_key: str
    max_tokens: int
    verbose: bool = False
    num_examples: int = 3
    examples: list[dspy.Example] | None = None
    examples_file: Path | None = None
    example_generator_model: str | None = None
    example_generator_api_key: str | None = None
    example_generator_max_tokens: int | None = None


@dataclass
class MetricBasedConfig:
    """Configuration for :class:`MetricBasedOptimizer`."""

    model: str
    api_key: str
    max_iterations: int = 3
    max_tokens: int = 64000
    verbose: bool = False
