from __future__ import annotations

from pathlib import Path
from typing import Optional, TextIO

import click

from .common import (
    common_options,
    create_example_optimizer,
    echo_start,
    example_options,
    read_input_prompt,
    validate_api_key,
    write_output_with_logging,
)


@click.command(name="example")
@common_options
@example_options
def example_command(
    input_prompt: TextIO,
    output: TextIO,
    model: str,
    api_key: Optional[str],
    max_tokens: int,
    verbose: bool,
    num_examples: int,
    example_generator_model: Optional[str],
    example_generator_api_key: Optional[str],
    example_generator_max_tokens: Optional[int],
    examples_file: Optional[Path],
) -> None:
    """Optimize a prompt using example-based approach."""
    api = validate_api_key(api_key)
    prompt = read_input_prompt(input_prompt)
    echo_start("example-based", model, max_tokens, verbose)
    optimizer = create_example_optimizer(
        model,
        api,
        max_tokens,
        verbose,
        num_examples,
        examples_file,
        example_generator_model,
        example_generator_api_key,
        example_generator_max_tokens,
    )
    write_output_with_logging(output, optimizer.optimize(prompt), verbose)
