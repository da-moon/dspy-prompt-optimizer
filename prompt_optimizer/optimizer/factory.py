"""
Factory function for creating and using prompt optimizers.
"""

from .base import PromptOptimizer
from .self_refinement import SelfRefinementOptimizer
from .example_based import ExampleBasedOptimizer
from .metric_based import MetricBasedOptimizer


def optimize_prompt(
    prompt_text: str,
    *,
    model: str,
    api_key: str,
    optimization_type: str = "self",
    max_iterations: int = 3,
    max_tokens: int = 64000,
    verbose: bool = False,
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

    Returns:
        The optimized prompt text
    """
    optimizer: PromptOptimizer
    # Select the appropriate optimizer based on the optimization type
    if optimization_type == "example":
        optimizer = ExampleBasedOptimizer(
            model=model, api_key=api_key, max_tokens=max_tokens, verbose=verbose
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
