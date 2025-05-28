"""
Command-line interface for DSPy Prompt Optimizer.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable, Final, Optional, TextIO, TypeVar

import click

from .example_generator import ExampleGenerator
from .optimizer import optimize_prompt

DEFAULT_MODEL: Final[str] = "claude-sonnet-4-20250514"
DEFAULT_OPTIMIZATION_TYPE: Final[str] = "self"
DEFAULT_MAX_ITERATIONS: Final[int] = 3
DEFAULT_MAX_TOKENS: Final[int] = 64000
DEFAULT_NUM_EXAMPLES: Final[int] = 5

CommandFunc = TypeVar("CommandFunc", bound=Callable[..., Any])


def _add_io_options(command: CommandFunc) -> CommandFunc:
    """Add input/output related options."""
    command = click.option(
        "--output",
        "-o",
        type=click.File("w"),
        default=sys.stdout,
        help="Output file for the optimized prompt. Defaults to stdout.",
    )(command)
    command = click.option(
        "--verbose", "-v", is_flag=True, help="Enable verbose output."
    )(command)
    return command


def _add_model_options(command: CommandFunc) -> CommandFunc:
    """Add model and API key related options."""
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
    return command


def _add_optimization_options(command: CommandFunc) -> CommandFunc:
    """Add optimization behavior related options."""
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
    return command


def _add_example_options(command: CommandFunc) -> CommandFunc:
    """Add example generation related options."""
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
    return command


def common_options(command: CommandFunc) -> CommandFunc:
    """Decorator to apply common optimization options."""
    command = _add_io_options(command)
    command = _add_model_options(command)
    command = _add_optimization_options(command)
    command = _add_example_options(command)
    command = click.argument("input_prompt", type=click.File("r"), default=sys.stdin)(
        command
    )
    return command


def _invoke_default_optimize_command(
    ctx: click.Context,
    input_prompt: TextIO,
    output: TextIO,
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
    """Invoke the optimize command with all parameters."""
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
        _invoke_default_optimize_command(
            ctx,
            input_prompt,
            output,
            model,
            api_key,
            optimization_type,
            max_iterations,
            max_tokens,
            examples_file,
            num_examples,
            example_generator_model,
            example_generator_api_key,
            verbose,
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
    if text := text.strip():
        return text
    else:
        raise ValueError("Input prompt cannot be empty")


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


def _log_optimization_start(
    optimization_type: str, model: str, max_tokens: int, verbose: bool
) -> None:
    """Log optimization start message if verbose."""
    if verbose:
        message = (
            f"Optimizing prompt using {optimization_type} approach "
            f"with model {model} (max_tokens={max_tokens})..."
        )
        click.echo(message, err=True)


def _log_optimization_complete(verbose: bool) -> None:
    """Log optimization completion message if verbose."""
    if verbose:
        click.echo("Prompt optimization complete!", err=True)


def _handle_optimization_error(exc: Exception) -> None:
    """Handle optimization errors and exit."""
    click.echo(f"Error during prompt optimization: {exc}", err=True)
    sys.exit(1)


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
    examples_file: Optional[Path],  # pylint: disable=unused-argument
    num_examples: int,  # pylint: disable=unused-argument
    example_generator_model: str,  # pylint: disable=unused-argument
    example_generator_api_key: Optional[str],  # pylint: disable=unused-argument
    verbose: bool,
) -> None:
    """Optimize a prompt using DSPy."""
    try:
        _validate_parameters(api_key, max_iterations, max_tokens, model)
        prompt_text = _read_prompt(input_prompt)
        _log_optimization_start(optimization_type, model, max_tokens, verbose)

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
        _log_optimization_complete(verbose)
    except (ValueError, PermissionError, RuntimeError, KeyError) as exc:
        _handle_optimization_error(exc)


def _create_example_generator(model: str, api_key: Optional[str]) -> ExampleGenerator:
    """Create and return an ExampleGenerator instance."""
    return ExampleGenerator(model=model, api_key=api_key or "")


def _handle_example_generation_error(exc: Exception) -> None:
    """Handle example generation errors and exit."""
    click.echo(f"Error generating examples: {exc}", err=True)
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
    """Generate optimization examples using ExampleGenerator."""
    try:
        generator = _create_example_generator(model, api_key)
        generator.write_examples(num_examples, output_file)
    except (ValueError, PermissionError, RuntimeError) as exc:
        _handle_example_generation_error(exc)


if __name__ == "__main__":
    main(prog_name="prompt-optimizer")
