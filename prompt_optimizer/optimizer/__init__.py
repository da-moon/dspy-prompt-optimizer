"""
DSPy-based prompt optimization module.
"""

from typing import Final

from .base import PromptOptimizer
from .example_based import ExampleBasedOptimizer
from .factory import optimize_prompt
from .metric_based import MetricBasedOptimizer
from .self_refinement import SelfRefinementOptimizer
from .strategies import (
    ExampleBasedConfig,
    MetricBasedConfig,
    OptimizationStrategy,
    SelfRefinementConfig,
)

__all__: Final[list[str]] = [
    "PromptOptimizer",
    "SelfRefinementOptimizer",
    "ExampleBasedOptimizer",
    "MetricBasedOptimizer",
    "SelfRefinementConfig",
    "ExampleBasedConfig",
    "MetricBasedConfig",
    "OptimizationStrategy",
    "optimize_prompt",
]
