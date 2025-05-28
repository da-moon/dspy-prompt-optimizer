from __future__ import annotations

from pathlib import Path
from typing import Optional

import click

from ..optimizer.example_based import ExampleGenerator
from .common import (
    echo_generation_start,
    notify_examples_path,
    validate_api_key,
)


@click.command(name="generate-examples")
@click.option(
    "--api-key",
    "-k",
    envvar="ANTHROPIC_API_KEY",
    help="Anthropic API key. Can also be set via ANTHROPIC_API_KEY env variable.",
)
@click.option(
    "--model",
    "-m",
    default="claude-3-5-haiku-latest",
    help="Model to use for example generation. Defaults to claude-3-5-haiku-latest.",
)
@click.option(
    "--num-examples",
    "-n",
    type=int,
    default=3,
    help="Number of examples to generate. Defaults to 3.",
)
@click.option(
    "--max-tokens",
    type=int,
    default=8000,
    help="Maximum number of tokens for LM generation. Defaults to 8000.",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output.")
@click.argument("output_file", type=click.Path(path_type=Path))
def generate_examples_command(
    api_key: Optional[str],
    model: str,
    num_examples: int,
    max_tokens: int,
    verbose: bool,
    output_file: Path,
) -> None:
    """Generate optimization examples and save them to a file."""
    api = validate_api_key(api_key)
    echo_generation_start(num_examples, model, max_tokens, verbose)
    ExampleGenerator(
        model=model,
        api_key=api,
        num_examples=num_examples,
        max_tokens=max_tokens,
        verbose=verbose,
    ).write_examples(output_file)
    notify_examples_path(output_file, verbose)
