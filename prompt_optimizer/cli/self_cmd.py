from __future__ import annotations

from typing import Optional, TextIO

import click

from ..optimizer.self_refinement import SelfRefinementOptimizer
from .common import (
    common_options,
    echo_start,
    read_input_prompt,
    validate_api_key,
    write_output_with_logging,
)


@click.command(name="self")
@common_options
def self_command(
    input_prompt: TextIO,
    output: TextIO,
    model: str,
    api_key: Optional[str],
    max_tokens: int,
    verbose: bool,
) -> None:
    """Optimize a prompt using self-refinement approach."""
    api = validate_api_key(api_key)
    prompt = read_input_prompt(input_prompt)
    echo_start("self-refinement", model, max_tokens, verbose)
    optimizer = SelfRefinementOptimizer(
        model=model, api_key=api, max_tokens=max_tokens, verbose=verbose
    )
    write_output_with_logging(output, optimizer.optimize(prompt), verbose)
