from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Optional, ParamSpec, TextIO, TypeVar

import click

if TYPE_CHECKING:
    from ..optimizer.example_based import ExampleBasedOptimizer

P = ParamSpec("P")
R = TypeVar("R")


@dataclass
class ExampleOptimizerConfig:
    """Configuration for creating an ExampleBasedOptimizer."""
    model: str
    api_key: str
    max_tokens: int
    verbose: bool
    num_examples: int
    examples_file: Path | None = None
    example_generator_model: str | None = None
    example_generator_api_key: str | None = None
    example_generator_max_tokens: int | None = None


def common_options(func: Callable[P, R]) -> Callable[P, R]:
    """Add options shared by all commands."""
    func = click.option("--verbose", "-v", is_flag=True, help="Enable verbose output.")(
        func
    )
    func = click.option(
        "--max-tokens",
        type=int,
        default=8000,
        help="Maximum number of tokens for LM generation. Defaults to 8000.",
    )(func)
    func = click.option(
        "--api-key",
        "-k",
        envvar="ANTHROPIC_API_KEY",
        help="Anthropic API key. Can also be set via ANTHROPIC_API_KEY env variable.",
    )(func)
    func = click.option(
        "--model",
        "-m",
        default="claude-sonnet-4-20250514",
        help="Model to use for optimization. Defaults to claude-sonnet-4-20250514.",
    )(func)
    func = click.option(
        "--output",
        "-o",
        type=click.File("w"),
        default=sys.stdout,
        help="Output file for the optimized prompt. Defaults to stdout.",
    )(func)
    func = click.argument("input_prompt", type=click.File("r"), default=sys.stdin)(func)
    return func


def example_options(func: Callable[P, R]) -> Callable[P, R]:
    """Add options specific to example-based commands."""
    func = click.option(
        "--num-examples",
        "-n",
        type=int,
        default=3,
        help="Number of examples to generate or use. Defaults to 3.",
    )(func)
    func = click.option(
        "--example-generator-model",
        "--eg-model",
        help="Model to use for example generation. Defaults to claude-3-5-haiku-latest.",
    )(func)
    func = click.option(
        "--example-generator-api-key",
        "--eg-api-key",
        envvar="ANTHROPIC_EXAMPLE_API_KEY",
        help="API key for example generation. Defaults to same as optimization API key.",
    )(func)
    func = click.option(
        "--example-generator-max-tokens",
        "--eg-max-tokens",
        type=int,
        help="Maximum tokens for example generator. Defaults to same as optimizer max-tokens.",
    )(func)
    func = click.option(
        "--examples-file",
        "-f",
        type=click.Path(exists=True, path_type=Path),
        help="JSON file containing pre-generated examples for two-phase approach.",
    )(func)
    return func


def validate_api_key(api_key: Optional[str]) -> str:
    """Return API key or exit with a clear error."""
    if not api_key:
        click.echo(
            "Error: Anthropic API key is required. Provide it with --api-key or set ANTHROPIC_API_KEY environment variable.",
            err=True,
        )
        sys.exit(1)
    return api_key


def read_input_prompt(input_prompt: TextIO) -> str:
    """Read prompt text from input."""
    return input_prompt.read().strip()


def write_output_with_logging(output: TextIO, result: str, verbose: bool) -> None:
    """Write result to output with optional status message."""
    _ = output.write(result)
    if verbose:
        click.echo("Prompt optimization complete!", err=True)


def echo_start(kind: str, model: str, max_tokens: int, verbose: bool) -> None:
    """Emit a verbose start message."""
    if verbose:
        click.echo(
            f"Optimizing prompt using {kind} approach with model {model} (max_tokens={max_tokens})...",
            err=True,
        )


def echo_generation_start(
    num_examples: int, model: str, max_tokens: int, verbose: bool
) -> None:
    """Emit a verbose generation message."""
    if verbose:
        click.echo(
            f"Generating {num_examples} examples using model {model} (max_tokens={max_tokens})...",
            err=True,
        )


def notify_examples_path(output_file: Path, verbose: bool) -> None:
    """Display path to examples file."""
    if verbose:
        click.echo(f"Examples saved to {output_file}", err=True)
        click.echo(
            "Review and edit the examples, then use them with: dspy-prompt-optimizer example --examples-file",
            err=True,
        )
    else:
        click.echo(str(output_file))


def create_example_optimizer(config: ExampleOptimizerConfig) -> ExampleBasedOptimizer:
    """Return a configured :class:`ExampleBasedOptimizer`."""
    from ..optimizer.example_based import ExampleBasedOptimizer

    return ExampleBasedOptimizer(
        model=config.model,
        api_key=config.api_key,
        max_tokens=config.max_tokens,
        verbose=config.verbose,
        num_examples=config.num_examples,
        examples_file=config.examples_file,
        example_generator_model=config.example_generator_model,
        example_generator_api_key=config.example_generator_api_key,
        example_generator_max_tokens=config.example_generator_max_tokens or config.max_tokens,
    )
