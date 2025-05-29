from __future__ import annotations

from typing import Optional, TextIO

import click

from ..optimizer.metric_based import MetricBasedOptimizer
from ..optimizer.strategies import MetricBasedConfig
from .common import (
    common_options,
    echo_start,
    read_input_prompt,
    validate_api_key,
    write_output_with_logging,
)


@click.command(name="metric")
@common_options
@click.option(
    "--max-iterations",
    "-i",
    type=int,
    default=3,
    help="Maximum number of iterations for metric-based optimization. Defaults to 3.",
)
def metric_command(
    input_prompt: TextIO,
    output: TextIO,
    model: str,
    api_key: Optional[str],
    max_iterations: int,
    max_tokens: int,
    verbose: bool,
) -> None:
    """Optimize a prompt using metric-based approach."""
    _run_metric_optimization(
        input_prompt, output, model, api_key, max_iterations, max_tokens, verbose
    )


def _run_metric_optimization(
    input_prompt: TextIO,
    output: TextIO,
    model: str,
    api_key: Optional[str],
    max_iterations: int,
    max_tokens: int,
    verbose: bool,
) -> None:
    """Execute metric-based optimization workflow."""
    validated_api_key = validate_api_key(api_key)
    prompt_text = read_input_prompt(input_prompt)
    echo_start("metric-based", model, max_tokens, verbose)
    config = _create_metric_config(
        model, validated_api_key, max_iterations, max_tokens, verbose
    )
    optimized_prompt = _execute_metric_optimization(config, prompt_text)
    write_output_with_logging(output, optimized_prompt, verbose)


def _create_metric_config(
    model: str,
    api_key: str,
    max_iterations: int,
    max_tokens: int,
    verbose: bool,
) -> MetricBasedConfig:
    """Create configuration for metric-based optimization."""
    return MetricBasedConfig(
        model=model,
        api_key=api_key,
        max_iterations=max_iterations,
        max_tokens=max_tokens,
        verbose=verbose,
    )


def _execute_metric_optimization(
    config: MetricBasedConfig, prompt_text: str
) -> str:
    """Execute the optimization using the provided configuration."""
    optimizer = MetricBasedOptimizer(config)
    return optimizer.optimize(prompt_text)
