"""
Factory function for creating and using prompt optimizers.
"""

from pathlib import Path

import dspy

from .base import PromptOptimizer
from .example_based import ExampleBasedOptimizer
from .metric_based import MetricBasedOptimizer
from .self_refinement import SelfRefinementOptimizer


def optimize_prompt(
    prompt_text: str,
    *,
    model: str,
    api_key: str,
    optimization_type: str = "self",
    max_iterations: int = 3,
    max_tokens: int = 64000,
    verbose: bool = False,
    examples: list[dspy.Example] | None = None,
    examples_file: Path | None = None,
    example_generator_model: str | None = None,
    example_generator_api_key: str | None = None,
    num_examples: int = 3,
) -> str:
    """
    Optimize a prompt using the specified optimization approach.

    Args:
        prompt_text: The prompt text to optimize
        model: The model to use for optimization
        api_key: Anthropic API key
        optimization_type: Type of optimization ('self', 'example', or 'metric')
        max_iterations: Maximum number of iterations for metric-based optimization
        max_tokens: Maximum number of tokens for LM generation
        verbose: Whether to enable verbose output
        examples: Examples to use for optimization
        examples_file: Path to a JSON file with examples
        example_generator_model: Model to use for generating examples
        example_generator_api_key: API key for the example generator model
        num_examples: Number of examples to generate if needed

    Returns:
        The optimized prompt text
    """
    optimizer: PromptOptimizer
    # Select the appropriate optimizer based on the optimization type
    if optimization_type == "example":
        optimizer = ExampleBasedOptimizer(
            model=model,
            api_key=api_key,
            max_tokens=max_tokens,
            verbose=verbose,
            examples=examples,
            examples_file=examples_file,
            example_generator_model=example_generator_model,
            example_generator_api_key=example_generator_api_key,
            num_examples=num_examples,
        )
    elif optimization_type == "metric":
        optimizer = MetricBasedOptimizer(
            model=model,
            api_key=api_key,
            max_iterations=max_iterations,
            max_tokens=max_tokens,
            verbose=verbose,
        )
    elif optimization_type == "self":
        optimizer = SelfRefinementOptimizer(
            model=model, api_key=api_key, max_tokens=max_tokens, verbose=verbose
        )
    else:
        raise ValueError(f"Unknown optimization type: {optimization_type}")

    # Optimize the prompt
    return optimizer.optimize(prompt_text)
