"""
Example-based prompt optimizer.
"""

import logging
from typing import Final

import dspy

from .base import PromptOptimizer

logger: Final[logging.Logger] = logging.getLogger(__name__)


DEFAULT_EXAMPLES: Final[list[dspy.Example]] = [
    dspy.Example(
        prompt="Tell me about climate change",
        analysis=(
            "This prompt is too vague and doesn't specify what aspects of "
            "climate change to focus on or what depth of information is needed."
        ),
        improved_prompt=(
            "Provide a comprehensive explanation of the primary causes of "
            "climate change, focusing on both natural and anthropogenic factors. "
            "Include recent scientific consensus on the rate of global warming "
            "and its projected impacts on ecosystems over the next 50 years."
        ),
    ),
    dspy.Example(
        prompt="How do I make a website?",
        analysis=(
            "This prompt lacks specificity about the type of website, the user's "
            "skill level, or what technologies they're interested in using."
        ),
        improved_prompt=(
            "I'm a beginner with basic HTML/CSS knowledge looking to create a "
            "personal portfolio website. Please provide a step-by-step guide on "
            "how to build a responsive portfolio site, including recommended "
            "frameworks, hosting options, and essential features for showcasing "
            "my work effectively."
        ),
    ),
]


def _format_examples(examples: list[dspy.Example]) -> str:
    """Return a formatted string representing prompt transformation examples."""

    return "\n\n".join(
        [
            f"Original: {ex.prompt}\n"
            + f"Analysis: {ex.analysis}\n"
            + f"Improved: {ex.improved_prompt}"
            for ex in examples
        ]
    )


class ExampleBasedOptimizer(PromptOptimizer):
    """Optimizer that uses examples to improve prompts."""

    def optimize(self, prompt_text: str) -> str:
        """
        Optimize the prompt using example-based optimization.

        Args:
            prompt_text: The prompt text to optimize

        Returns:
            The optimized prompt text
        """
        if self.verbose:
            logger.info("Using example-based optimization approach")

        # Define a signature for prompt refinement with examples
        class ExamplePromptRefiner(dspy.Signature):
            """Refine a prompt based on examples of good prompts."""

            prompt = dspy.InputField(desc="The original prompt that needs refinement")
            examples = dspy.InputField(
                desc="Examples of good prompt transformations to learn from"
            )
            analysis = dspy.OutputField(
                desc="Analysis of the prompt's strengths and weaknesses"
            )
            improved_prompt = dspy.OutputField(
                desc="A refined version of the prompt that addresses the weaknesses"
            )

        # Format examples as context text
        examples_text = _format_examples(DEFAULT_EXAMPLES)
        # Create a module that uses the signature with examples
        refiner: dspy.ChainOfThought = dspy.ChainOfThought(ExamplePromptRefiner)

        # Apply the module with examples as context to refine the prompt
        refinement_payload = refiner(prompt=prompt_text, examples=examples_text)

        if self.verbose:
            logger.info(f"Analysis: {refinement_payload.analysis}")

        return refinement_payload.improved_prompt
