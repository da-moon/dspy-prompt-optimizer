"""
DSPy Prompt Optimizer - A tool to optimize prompts using DSPy framework.
"""

from typing import Final

from .optimizer import optimize_prompt
__version__: Final[str] = "0.1.0"
__all__: Final[list[str]] = ["optimize_prompt"]
