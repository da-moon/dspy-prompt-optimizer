"""
Metric-based prompt optimizer.
"""

import dspy
import logging
from .base import PromptOptimizer

logger = logging.getLogger(__name__)


class MetricBasedOptimizer(PromptOptimizer):
    """Optimizer that uses metrics to improve prompts."""

    def optimize(self, prompt_text: str) -> str:
        """
        Optimize the prompt using metric-based optimization.

        Args:
            prompt_text: The prompt text to optimize

        Returns:
            The optimized prompt text
        """
        if self.verbose:
            logger.info(f"Using metric-based optimization approach with {self.max_iterations} max iterations")

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
            actionability_score = dspy.OutputField(desc="Score for actionability (1-10)")
            total_score = dspy.OutputField(desc="Sum of all scores (3-30)")
            feedback = dspy.OutputField(desc="Feedback on how to improve the prompt")

        # Create modules
        generator: dspy.Predict = dspy.Predict(PromptGenerator)
        evaluator: dspy.ChainOfThought = dspy.ChainOfThought(PromptEvaluator)

        # Define the optimization loop
        best_prompt: str = prompt_text
        best_score: int = 0

        for i in range(self.max_iterations):
            if i == 0:
                # Evaluate the original prompt
                evaluation: dspy.DSPyResult = evaluator(prompt=best_prompt)
                best_score = int(evaluation.total_score)

                if self.verbose:
                    logger.info(f"Original prompt score: {best_score}")
                    logger.info(f"Feedback: {evaluation.feedback}")

            # Generate an improved prompt
            result: dspy.DSPyResult = generator(original_prompt=best_prompt)
            candidate_prompt: str = result.improved_prompt

            # Evaluate the candidate prompt
            candidate_evaluation: dspy.DSPyResult = evaluator(prompt=candidate_prompt)
            candidate_score: int = int(candidate_evaluation.total_score)

            if self.verbose:
                logger.info(f"Iteration {i+1} score: {candidate_score}")
                logger.info(f"Feedback: {candidate_evaluation.feedback}")

            # Keep the better prompt
            if candidate_score > best_score:
                best_prompt = candidate_prompt
                best_score = candidate_score

                if self.verbose:
                    logger.info(f"Found better prompt with score: {best_score}")

        return best_prompt
