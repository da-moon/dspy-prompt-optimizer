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

    def _create_prompt_generator_signature(self) -> type[dspy.Signature]:
        """Create and return the PromptGenerator signature class."""
        class PromptGenerator(dspy.Signature):
            """Generate an improved prompt based on specific metrics."""

            original_prompt = dspy.InputField(desc="The original prompt to improve")
            improved_prompt = dspy.OutputField(desc="An improved version of the prompt")

        return PromptGenerator

    def _create_prompt_evaluator_signature(self) -> type[dspy.Signature]:
        """Create and return the PromptEvaluator signature class."""
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

        return PromptEvaluator

    def _setup_modules(self) -> tuple[dspy.Predict, dspy.ChainOfThought]:
        """Set up and return the generator and evaluator modules."""
        generator_signature = self._create_prompt_generator_signature()
        evaluator_signature = self._create_prompt_evaluator_signature()
        
        generator: dspy.Predict = dspy.Predict(generator_signature)
        evaluator: dspy.ChainOfThought = dspy.ChainOfThought(evaluator_signature)
        
        return generator, evaluator

    def _log_initial_state(self) -> None:
        """Log initial optimization parameters."""
        if self.verbose:
            logger.info(
                f"Using metric-based optimization with {self.max_iterations} max iterations"
            )

    def _evaluate_and_log_prompt(self, evaluator: dspy.ChainOfThought, prompt: str, label: str) -> tuple[int, str]:
        """Evaluate a prompt and log the results if verbose mode is enabled."""
        evaluation = self._evaluate_prompt(evaluator, prompt)
        score: int = int(evaluation.total_score)
        
        if self.verbose:
            logger.info(f"{label} score: {score}")
            logger.info(f"Feedback: {evaluation.feedback}")
            
        return score, evaluation.feedback

    def _update_best_if_improved(self, candidate_prompt: str, candidate_score: int,
                                best_prompt: str, best_score: int) -> tuple[str, int]:
        """Update best prompt and score if candidate is better."""
        if candidate_score > best_score:
            if self.verbose:
                logger.info(f"Found better prompt with score: {candidate_score}")
            return candidate_prompt, candidate_score
        return best_prompt, best_score

    def _process_optimization_iteration(self, generator: dspy.Predict, evaluator: dspy.ChainOfThought,
                                       best_prompt: str, best_score: int, iteration: int) -> tuple[str, int]:
        """Process a single optimization iteration and return updated best prompt and score."""
        candidate_prompt: str = self._generate_prompt(generator, best_prompt)
        candidate_score, _ = self._evaluate_and_log_prompt(
            evaluator, candidate_prompt, f"Iteration {iteration + 1}"
        )

        return self._update_best_if_improved(candidate_prompt, candidate_score, best_prompt, best_score)

    def _run_optimization_loop(self, generator: dspy.Predict, evaluator: dspy.ChainOfThought, 
                              initial_prompt: str, initial_score: int) -> str:
        """Run the optimization loop and return the best prompt found."""
        best_prompt: str = initial_prompt
        best_score: int = initial_score

        for i in range(self.max_iterations):
            best_prompt, best_score = self._process_optimization_iteration(
                generator, evaluator, best_prompt, best_score, i
            )

        return best_prompt

    def optimize(self, prompt_text: str) -> str:
        """
        Optimize the prompt using metric-based optimization.

        Args:
            prompt_text: The prompt text to optimize

        Returns:
            The optimized prompt text
        """
        self._log_initial_state()
        generator, evaluator = self._setup_modules()
        
        initial_score, _ = self._evaluate_and_log_prompt(
            evaluator, prompt_text, "Original prompt"
        )
        
        return self._run_optimization_loop(generator, evaluator, prompt_text, initial_score)
