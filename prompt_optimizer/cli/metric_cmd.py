from __future__ import annotations

from typing import Optional, TextIO

import click

from ..optimizer.metric_based import MetricBasedOptimizer
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
    api = validate_api_key(api_key)
    prompt = read_input_prompt(input_prompt)
    echo_start("metric-based", model, max_tokens, verbose)
    optimizer = MetricBasedOptimizer(
        model=model,
        api_key=api,
        max_iterations=max_iterations,
        max_tokens=max_tokens,
        verbose=verbose,
    )
    write_output_with_logging(output, optimizer.optimize(prompt), verbose)
