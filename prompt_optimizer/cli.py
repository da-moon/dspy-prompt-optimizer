"""
Command-line interface for DSPy Prompt Optimizer.
"""

import json
import sys
from pathlib import Path
from typing import Optional, TextIO

import click

from .history import HISTORY_PATH, load_history
from .optimizer import optimize_prompt


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx: click.Context) -> None:
    """DSPy Prompt Optimizer command line interface."""
    if ctx.invoked_subcommand is None:
        ctx.forward(optimize)


@main.command(name="optimize")
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
    default="claude-3-7-sonnet-latest",
    help="Model to use for optimization. Defaults to claude-3-7-sonnet-latest.",
)
@click.option(
    "--api-key",
    "-k",
    envvar="ANTHROPIC_API_KEY",
    help="Anthropic API key. Can also be set via ANTHROPIC_API_KEY environment variable.",
)
@click.option(
    "--optimization-type",
    "-t",
    type=click.Choice(["self", "example", "metric"]),
    default="self",
    help="Type of optimization to perform: self-refinement, example-based, or metric-based.",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output.")
def optimize(
    input_prompt: TextIO,
    output: TextIO,
    model: str,
    api_key: Optional[str],
    optimization_type: str,
    verbose: bool,
) -> None:
    """
    Optimize a prompt using DSPy framework.

    INPUT_PROMPT: File containing the prompt to optimize, or stdin if not specified.
    """
    if not api_key:
        click.echo(
            "Error: Anthropic API key is required. Provide it with --api-key or set ANTHROPIC_API_KEY environment variable.",
            err=True,
        )
        sys.exit(1)

    prompt_text = input_prompt.read().strip()

    if verbose:
        click.echo(
            f"Optimizing prompt using {optimization_type} approach with model {model}...",
            err=True,
        )

    try:
        optimized_prompt = optimize_prompt(
            prompt_text=prompt_text,
            model=model,
            api_key=api_key,
            optimization_type=optimization_type,
            verbose=verbose,
        )

        output.write(optimized_prompt)

        if verbose:
            click.echo("Prompt optimization complete!", err=True)

    except Exception as e:
        click.echo(f"Error during prompt optimization: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.option("--limit", "-n", type=int, default=None, help="Number of entries to show")
@click.option("--clear", is_flag=True, help="Clear the history log")
def history(limit: int | None, clear: bool) -> None:
    """Show or clear optimization history."""
    log_file = HISTORY_PATH

    if clear:
        if log_file.exists():
            log_file.unlink()
        click.echo("History log cleared.")
        return

    entries = load_history(limit)
    if not entries:
        click.echo("No history found.")
        return

    for entry in entries:
        click.echo(json.dumps(entry, indent=2))


if __name__ == "__main__":
    main()


@click.command()
@click.option("--limit", "-n", type=int, default=None, help="Number of entries to show")
@click.option("--clear", is_flag=True, help="Clear the history log")
def history_command(limit: int | None, clear: bool) -> None:
    """Entry point for history script."""
    log_file = HISTORY_PATH

    if clear:
        if log_file.exists():
            log_file.unlink()
        click.echo("History log cleared.")
        return

    entries = load_history(limit)
    if not entries:
        click.echo("No history found.")
        return

    for entry in entries:
        click.echo(json.dumps(entry, indent=2))
