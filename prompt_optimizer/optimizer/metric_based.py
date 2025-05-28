"""Metric-based prompt optimizer."""

from __future__ import annotations

import logging
from typing import Final

import dspy

from .base import PromptOptimizer

logger: Final[logging.Logger] = logging.getLogger(__name__)


class MetricBasedOptimizer(PromptOptimizer):
    """Optimizer that uses metrics to improve prompts."""

    def _evaluate_prompt(
        self, evaluator: dspy.ChainOfThought, prompt: str
    ) -> dspy.DSPyResult:
        """Return the evaluator payload for ``prompt``."""

        return evaluator(prompt=prompt)

    def _generate_prompt(self, generator: dspy.Predict, prompt: str) -> str:
        """Return a new prompt generated from ``prompt``."""

        result = generator(original_prompt=prompt)
        return result.improved_prompt

    def optimize(self, prompt_text: str) -> str:
        """
        Optimize the prompt using metric-based optimization.

        Args:
            prompt_text: The prompt text to optimize

        Returns:
            The optimized prompt text
        """
        if self.verbose:
            logger.info(
                f"Using metric-based optimization with {self.max_iterations} max iterations"
            )

        # Define a signature for prompt generation
        class PromptGenerator(dspy.Signature):
            """Generate an improved prompt based on specific metrics."""

            original_prompt = dspy.InputField(desc="The original prompt to improve")
            improved_prompt = dspy.OutputField(desc="An improved version of the prompt")

        # Define a signature for evaluating prompts
        class PromptEvaluator(dspy.Signature):
            """Evaluate a prompt based on clarity, specificity, and actionability."""

            prompt = dspy.InputField(desc="The prompt to evaluate")
            clarity_score = dspy.OutputField(desc="Score for clarity (1-10)")
            specificity_score = dspy.OutputField(desc="Score for specificity (1-10)")
            actionability_score = dspy.OutputField(
                desc="Score for actionability (1-10)"
            )
            total_score = dspy.OutputField(desc="Sum of all scores (3-30)")
            feedback = dspy.OutputField(desc="Feedback on how to improve the prompt")

        # Create modules
        generator: dspy.Predict = dspy.Predict(PromptGenerator)
        evaluator: dspy.ChainOfThought = dspy.ChainOfThought(PromptEvaluator)

        # Evaluate the original prompt
        best_prompt: str = prompt_text
        evaluation = self._evaluate_prompt(evaluator, best_prompt)
        best_score: int = int(evaluation.total_score)

        if self.verbose:
            logger.info(f"Original prompt score: {best_score}")
            logger.info(f"Feedback: {evaluation.feedback}")

        # Define the optimization loop
        for i in range(self.max_iterations):
            candidate_prompt: str = self._generate_prompt(generator, best_prompt)
            candidate_evaluation = self._evaluate_prompt(evaluator, candidate_prompt)
            candidate_score: int = int(candidate_evaluation.total_score)

            if self.verbose:
                logger.info(f"Iteration {i + 1} score: {candidate_score}")
                logger.info(f"Feedback: {candidate_evaluation.feedback}")

            if candidate_score > best_score:
                best_prompt = candidate_prompt
                best_score = candidate_score

                if self.verbose:
                    logger.info(f"Found better prompt with score: {best_score}")

        return best_prompt
