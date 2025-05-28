"""
Command-line interface for DSPy Prompt Optimizer.
"""

import sys
from typing import Optional, TextIO

import click

from .optimizer import optimize_prompt


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


@click.command()
@click.argument("input_prompt", type=click.File("r"), default=sys.stdin)
@click.option(
    "--output",
    "-o",
    type=click.File("w"),
    default=sys.stdout,
    help="Output file for the optimized prompt. Defaults to stdout.",
)
@click.option(
    "--model",
    "-m",
    default="claude-sonnet-4-20250514",
    help="Model to use for optimization. Defaults to claude-sonnet-4-20250514.",
)
@click.option(
    "--api-key",
    "-k",
    envvar="ANTHROPIC_API_KEY",
    help="Anthropic API key. Can also be set via ANTHROPIC_API_KEY env variable.",
)
@click.option(
    "--optimization-type",
    "-t",
    type=click.Choice(["self", "example", "metric"]),
    default="self",
    help="Type of optimization: self-refinement, example-based, or metric-based.",
)
@click.option(
    "--max-iterations",
    "-i",
    type=int,
    default=3,
    help="Maximum number of iterations for metric-based optimization. Defaults to 3.",
)
@click.option(
    "--max-tokens",
    type=int,
    default=64000,
    help="Maximum number of tokens for LM generation. Defaults to 64000.",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output.")
def main(
    input_prompt: TextIO,
    output: TextIO,
    *,
    model: str,
    api_key: Optional[str],
    optimization_type: str,
    max_iterations: int,
    max_tokens: int,
    verbose: bool,
) -> None:
    """Entry point for the command-line interface.

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


if __name__ == "__main__":
    main()  # pylint: disable=missing-kwoa,no-value-for-parameter
