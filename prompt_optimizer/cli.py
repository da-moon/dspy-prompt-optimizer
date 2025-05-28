"""
Command-line interface for DSPy Prompt Optimizer.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Final, Optional, TextIO

import click

from .example_generator import ExampleGenerator
from .optimizer import optimize_prompt

DEFAULT_MODEL: Final[str] = "claude-sonnet-4-20250514"
DEFAULT_OPTIMIZATION_TYPE: Final[str] = "self"
DEFAULT_MAX_ITERATIONS: Final[int] = 3
DEFAULT_MAX_TOKENS: Final[int] = 64000
DEFAULT_NUM_EXAMPLES: Final[int] = 5


from typing import Any, Callable, TypeVar

CommandFunc = TypeVar("CommandFunc", bound=Callable[..., Any])


def common_options(command: CommandFunc) -> CommandFunc:
    """Decorator to apply common optimization options."""

    command = click.argument("input_prompt", type=click.File("r"), default=sys.stdin)(
        command
    )
    command = click.option(
        "--output",
        "-o",
        type=click.File("w"),
        default=sys.stdout,
        help="Output file for the optimized prompt. Defaults to stdout.",
    )(command)
    command = click.option(
        "--model",
        "-m",
        default=DEFAULT_MODEL,
        show_default=True,
        help="Model to use for optimization.",
    )(command)
    command = click.option(
        "--api-key",
        "-k",
        envvar="ANTHROPIC_API_KEY",
        help="Anthropic API key. Can also be set via ANTHROPIC_API_KEY env variable.",
    )(command)
    command = click.option(
        "--optimization-type",
        "-t",
        type=click.Choice(["self", "example", "metric"]),
        default=DEFAULT_OPTIMIZATION_TYPE,
        show_default=True,
        help="Type of optimization: self-refinement, example-based, or metric-based.",
    )(command)
    command = click.option(
        "--max-iterations",
        "-i",
        type=int,
        default=DEFAULT_MAX_ITERATIONS,
        show_default=True,
        help="Maximum number of iterations for metric-based optimization.",
    )(command)
    command = click.option(
        "--max-tokens",
        type=int,
        default=DEFAULT_MAX_TOKENS,
        show_default=True,
        help="Maximum number of tokens for LM generation.",
    )(command)
    command = click.option(
        "--examples-file",
        type=click.Path(path_type=Path),
        help="JSON file containing optimization examples.",
    )(command)
    command = click.option(
        "--num-examples",
        type=int,
        default=DEFAULT_NUM_EXAMPLES,
        show_default=True,
        help="Number of examples to generate if no file is provided.",
    )(command)
    command = click.option(
        "--example-generator-model",
        type=str,
        default=DEFAULT_MODEL,
        show_default=True,
        help="Model for example generation.",
    )(command)
    command = click.option(
        "--example-generator-api-key",
        envvar="ANTHROPIC_API_KEY",
        help="API key for example generation. Overrides ANTHROPIC_API_KEY if set.",
    )(command)
    command = click.option(
        "--verbose", "-v", is_flag=True, help="Enable verbose output."
    )(command)
    return command


@click.group(invoke_without_command=True)
@common_options
@click.pass_context
def main(
    ctx: click.Context,
    input_prompt: TextIO,
    output: TextIO,
    *,
    model: str,
    api_key: Optional[str],
    optimization_type: str,
    max_iterations: int,
    max_tokens: int,
    examples_file: Optional[Path],
    num_examples: int,
    example_generator_model: str,
    example_generator_api_key: Optional[str],
    verbose: bool,
) -> None:
    """DSPy Prompt Optimizer command group."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(
            optimize,
            input_prompt=input_prompt,
            output=output,
            model=model,
            api_key=api_key,
            optimization_type=optimization_type,
            max_iterations=max_iterations,
            max_tokens=max_tokens,
            examples_file=examples_file,
            num_examples=num_examples,
            example_generator_model=example_generator_model,
            example_generator_api_key=example_generator_api_key,
            verbose=verbose,
        )


def _validate_parameters(
    api_key: Optional[str], max_iterations: int, max_tokens: int, model: str
) -> None:
    """Validate CLI parameters."""
    if not api_key:
        raise ValueError(
            "Anthropic API key is required. Provide it with --api-key or set ANTHROPIC_API_KEY."
        )
    if max_iterations <= 0:
        raise ValueError("max_iterations must be positive")
    if max_tokens <= 0:
        raise ValueError("max_tokens must be positive")
    if not model:
        raise ValueError("model cannot be empty")


def _read_prompt(input_prompt: TextIO) -> str:
    """Read and validate the input prompt."""
    try:
        text = input_prompt.read()
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Unexpected error reading input prompt: {exc}") from exc
    text = text.strip()
    if not text:
        raise ValueError("Input prompt cannot be empty")
    return text


def _write_output(output: TextIO, prompt: str) -> None:
    """Write the optimized prompt to the output file."""
    try:
        _ = output.write(prompt)
    except PermissionError as exc:
        raise PermissionError(f"Cannot write to output: {exc}") from exc
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Unexpected error writing output: {exc}") from exc


def _run_optimizer(
    prompt_text: str,
    model: str,
    api_key: str,
    optimization_type: str,
    max_iterations: int,
    max_tokens: int,
    verbose: bool,
) -> str:
    """Wrapper to keep the main function concise."""
    return optimize_prompt(
        prompt_text=prompt_text,
        model=model,
        api_key=api_key,
        optimization_type=optimization_type,
        max_iterations=max_iterations,
        max_tokens=max_tokens,
        verbose=verbose,
    )


@main.command(name="optimize")
@common_options
def optimize(
    input_prompt: TextIO,
    output: TextIO,
    *,
    model: str,
    api_key: Optional[str],
    optimization_type: str,
    max_iterations: int,
    max_tokens: int,
    examples_file: Optional[Path],
    num_examples: int,
    example_generator_model: str,
    example_generator_api_key: Optional[str],
    verbose: bool,
) -> None:
    """Optimize a prompt using DSPy.

    Args:
        input_prompt: File containing the prompt to optimize. Defaults to
            ``stdin``.
        output: File to write the optimized prompt. Defaults to ``stdout``.
        model: Model used for optimization.
        api_key: Anthropic API key.
        optimization_type: Type of optimization to perform (``self``,
            ``example``, or ``metric``).
        max_iterations: Maximum number of iterations for metric-based
            optimization.
        max_tokens: Maximum token limit for LM generation.
        examples_file: Path to a JSON file containing examples for optimization.
        num_examples: Number of examples to generate when ``examples_file`` is
            not provided.
        example_generator_model: Model used for generating examples.
        example_generator_api_key: API key for generating examples.
        verbose: Whether to print progress messages.

    Returns:
        None

    Raises:
        SystemExit: If the API key is missing or prompt optimization fails.
        ValueError: If ``optimization_type`` is invalid.
    """
    try:
        _validate_parameters(api_key, max_iterations, max_tokens, model)
        prompt_text = _read_prompt(input_prompt)
        if verbose:
            click.echo(
                f"Optimizing prompt using {optimization_type} approach with model {model} (max_tokens={max_tokens})...",
                err=True,
            )
        optimized_prompt = _run_optimizer(
            prompt_text,
            model,
            api_key or "",
            optimization_type,
            max_iterations,
            max_tokens,
            verbose,
        )
        _write_output(output, optimized_prompt)
        if verbose:
            click.echo("Prompt optimization complete!", err=True)
    except (ValueError, PermissionError, RuntimeError, KeyError) as exc:
        click.echo(f"Error during prompt optimization: {exc}", err=True)
        sys.exit(1)


@main.command(name="generate-examples")
@click.option(
    "--output-file",
    "-o",
    type=click.Path(path_type=Path),
    required=True,
    help="File path to write generated examples as JSON.",
)
@click.option(
    "--num-examples",
    type=int,
    default=DEFAULT_NUM_EXAMPLES,
    show_default=True,
    help="Number of examples to generate.",
)
@click.option(
    "--model",
    "-m",
    default=DEFAULT_MODEL,
    show_default=True,
    help="Model to use for example generation.",
)
@click.option(
    "--api-key",
    "-k",
    envvar="ANTHROPIC_API_KEY",
    help="Anthropic API key for example generation.",
)
def generate_examples(
    *, output_file: Path, num_examples: int, model: str, api_key: Optional[str]
) -> None:
    """Generate optimization examples using :class:`ExampleGenerator`."""
    try:
        generator = ExampleGenerator(model=model, api_key=api_key or "")
        generator.write_examples(num_examples, output_file)
    except (ValueError, PermissionError, RuntimeError) as exc:
        click.echo(f"Error generating examples: {exc}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
