"""
Self-refinement based prompt optimizer.
"""

import logging
from typing import Final

import dspy

from .base import PromptOptimizer
from .strategies import OptimizationStrategy, SelfRefinementConfig

LOGGER: Final[logging.Logger] = logging.getLogger(__name__)


class SelfRefinementOptimizer(PromptOptimizer, OptimizationStrategy):
    """Optimizer that uses self-refinement to improve prompts."""

    def __init__(self, config: SelfRefinementConfig) -> None:
        """Initialize the optimizer with ``config``."""
        super().__init__(
            model=config.model,
            api_key=config.api_key,
            max_tokens=config.max_tokens,
            verbose=config.verbose,
        )

    def optimize(self, prompt_text: str) -> str:
        """
        Optimize the prompt using self-refinement.

        Args:
            prompt_text: The prompt text to optimize

        Returns:
            The optimized prompt text
        """
        if self.verbose:
            LOGGER.info("Using self-refinement optimization approach")

        # Define a signature for prompt refinement
        class PromptRefiner(dspy.Signature):
            """Refine a prompt to make it more effective."""

            prompt = dspy.InputField(desc="The original prompt that needs refinement")
            analysis = dspy.OutputField(
                desc="Analysis of the prompt's strengths and weaknesses"
            )
            improved_prompt = dspy.OutputField(
                desc="A refined version of the prompt that addresses the weaknesses"
            )

        # Create a module that uses the signature
        refiner: dspy.Predict = dspy.Predict(PromptRefiner)

        # Apply the module to refine the prompt
        result = refiner(prompt=prompt_text)

        if self.verbose:
            LOGGER.info("Analysis: %s", result.analysis)

        return result.improved_prompt
