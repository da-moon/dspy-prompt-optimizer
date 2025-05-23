"""
DSPy-based prompt optimization module.
"""

from .base import PromptOptimizer
from .example_based import ExampleBasedOptimizer
from .factory import optimize_prompt
from .metric_based import MetricBasedOptimizer
from .self_refinement import SelfRefinementOptimizer

__all__ = [
    "PromptOptimizer",
    "SelfRefinementOptimizer",
    "ExampleBasedOptimizer",
    "MetricBasedOptimizer",
    "optimize_prompt",
]
