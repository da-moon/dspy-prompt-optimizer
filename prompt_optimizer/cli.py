"""
Command-line interface for DSPy Prompt Optimizer.
"""

import sys
from pathlib import Path
from typing import Callable, Optional, TextIO, TypeVar, ParamSpec

import click

from .optimizer.example_based import ExampleBasedOptimizer, ExampleGenerator
from .optimizer.metric_based import MetricBasedOptimizer
from .optimizer.self_refinement import SelfRefinementOptimizer


# Common options for all subcommands
P = ParamSpec('P')
R = TypeVar('R')


def common_options(func: Callable[P, R]) -> Callable[P, R]:
    """Decorator to add common options to all subcommands."""
    func = click.option("--verbose", "-v", is_flag=True, help="Enable verbose output.")(func)
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


# Common options for example-based operations
def example_options(func: Callable[P, R]) -> Callable[P, R]:
    """Decorator to add example-specific options."""
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


def _validate_api_key(api_key: Optional[str]) -> str:
    """Validate and return API key or exit with error."""
    if not api_key:
        click.echo(
            "Error: Anthropic API key is required. Provide it with --api-key or set ANTHROPIC_API_KEY environment variable.",
            err=True,
        )
        sys.exit(1)
    return api_key


def _read_input_prompt(input_prompt: TextIO) -> str:
    """Read and return prompt text from input."""
    return input_prompt.read().strip()


def _write_output_with_logging(output: TextIO, result: str, verbose: bool) -> None:
    """Write result to output with optional logging."""
    _ = output.write(result)
    if verbose:
        click.echo("Prompt optimization complete!", err=True)


@click.group()
def main() -> None:
    """DSPy Prompt Optimizer - Optimize prompts using different strategies."""


@main.command()
@common_options
def self(
    input_prompt: TextIO,
    output: TextIO,
    model: str,
    api_key: Optional[str],
    max_tokens: int,
    verbose: bool,
) -> None:
    """
    Optimize a prompt using self-refinement approach.

    INPUT_PROMPT: File containing the prompt to optimize, or stdin if not specified.
    """
    api_key = _validate_api_key(api_key)
    prompt_text = _read_input_prompt(input_prompt)

    if verbose:
        click.echo(
            f"Optimizing prompt using self-refinement approach with model {model} (max_tokens={max_tokens})...",
            err=True,
        )

    try:
        # Direct instantiation - proper OOP
        optimizer = SelfRefinementOptimizer(
            model=model,
            api_key=api_key,
            max_tokens=max_tokens,
            verbose=verbose,
        )
        optimized_prompt = optimizer.optimize(prompt_text)
        _write_output_with_logging(output, optimized_prompt, verbose)

    except (ValueError, RuntimeError, KeyError) as e:
        click.echo(f"Error during prompt optimization: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@common_options
@example_options
def example(
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
    """
    Optimize a prompt using example-based approach.

    Supports both one-phase (generate examples + optimize) and two-phase
    (use pre-generated examples) approaches.

    INPUT_PROMPT: File containing the prompt to optimize, or stdin if not specified.
    """
    api_key = _validate_api_key(api_key)
    prompt_text = _read_input_prompt(input_prompt)

    if verbose:
        click.echo(
            f"Optimizing prompt using example-based approach with model {model} (max_tokens={max_tokens})...",
            err=True,
        )
        if example_generator_max_tokens and example_generator_max_tokens != max_tokens:
            click.echo(
                f"Using separate max tokens for example generator: example_generator_max_tokens={example_generator_max_tokens}",
                err=True,
            )

    try:
        # Direct instantiation - proper OOP
        optimizer = ExampleBasedOptimizer(
            model=model,
            api_key=api_key,
            max_tokens=max_tokens,
            verbose=verbose,
            examples_file=examples_file,
            example_generator_model=example_generator_model,
            example_generator_api_key=example_generator_api_key,
            example_generator_max_tokens=example_generator_max_tokens or max_tokens,
            num_examples=num_examples,
        )
        optimized_prompt = optimizer.optimize(prompt_text)
        _write_output_with_logging(output, optimized_prompt, verbose)

    except (ValueError, RuntimeError, KeyError) as e:
        click.echo(f"Error during prompt optimization: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@common_options
@click.option(
    "--max-iterations",
    "-i",
    type=int,
    default=3,
    help="Maximum number of iterations for metric-based optimization. Defaults to 3.",
)
def metric(
    input_prompt: TextIO,
    output: TextIO,
    model: str,
    api_key: Optional[str],
    max_iterations: int,
    max_tokens: int,
    verbose: bool,
) -> None:
    """
    Optimize a prompt using metric-based approach.

    INPUT_PROMPT: File containing the prompt to optimize, or stdin if not specified.
    """
    api_key = _validate_api_key(api_key)
    prompt_text = _read_input_prompt(input_prompt)

    if verbose:
        click.echo(
            f"Optimizing prompt using metric-based approach with model {model} (max_tokens={max_tokens})...",
            err=True,
        )

    try:
        # Direct instantiation - proper OOP
        optimizer = MetricBasedOptimizer(
            model=model,
            api_key=api_key,
            max_iterations=max_iterations,
            max_tokens=max_tokens,
            verbose=verbose,
        )
        optimized_prompt = optimizer.optimize(prompt_text)
        _write_output_with_logging(output, optimized_prompt, verbose)

    except (ValueError, RuntimeError, KeyError) as e:
        click.echo(f"Error during prompt optimization: {str(e)}", err=True)
        sys.exit(1)


@main.command("generate-examples")
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
def generate_examples(
    api_key: Optional[str],
    model: str,
    num_examples: int,
    max_tokens: int,
    verbose: bool,
    output_file: Path,
) -> None:
    """
    Generate examples for prompt optimization and save to JSON file.

    This is the first phase of the two-phase approach. Generate examples,
    review them manually, then use them with the 'example' command.

    OUTPUT_FILE: Path where to save the generated examples as JSON.
    """
    if not api_key:
        click.echo(
            "Error: Anthropic API key is required. Provide it with --api-key or set ANTHROPIC_API_KEY environment variable.",
            err=True,
        )
        sys.exit(1)

    if verbose:
        click.echo(
            f"Generating {num_examples} examples using model {model} (max_tokens={max_tokens})...",
            err=True,
        )

    try:
        generator = ExampleGenerator(
            model=model,
            api_key=api_key,
            num_examples=num_examples,
            max_tokens=max_tokens,
            verbose=verbose,
        )

        # Generate examples and save them
        generator.write_examples(output_file)

        if verbose:
            click.echo(f"Examples saved to {output_file}", err=True)
            click.echo("Review and edit the examples, then use them with: dspy-prompt-optimizer example --examples-file", err=True)
        else:
            click.echo(str(output_file))

    except (ValueError, RuntimeError, KeyError) as e:
        click.echo(f"Error during example generation: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
