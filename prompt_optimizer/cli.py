"""
Command-line interface for DSPy Prompt Optimizer.
"""

import sys
from pathlib import Path
from typing import Optional, TextIO

import click

from .optimizer import optimize_prompt


def optimize_text(
    prompt_text: str,
    model: str,
    api_key: str,
    optimization_type: str,
    verbose: bool,
) -> str:
    """Optimize a piece of prompt text."""
    if verbose:
        click.echo(
            f"Optimizing prompt using {optimization_type} approach with model {model}...",
            err=True,
        )

    return optimize_prompt(
        prompt_text=prompt_text,
        model=model,
        api_key=api_key,
        optimization_type=optimization_type,
        verbose=verbose,
    )


def optimize_stream(
    input_stream: TextIO,
    output_stream: TextIO,
    model: str,
    api_key: str,
    optimization_type: str,
    verbose: bool,
) -> None:
    """Optimize a prompt read from ``input_stream`` and write to ``output_stream``."""
    prompt_text = input_stream.read().strip()
    optimized = optimize_text(prompt_text, model, api_key, optimization_type, verbose)
    output_stream.write(optimized)


def optimize_file(
    input_path: Path,
    output_path: Path,
    model: str,
    api_key: str,
    optimization_type: str,
    verbose: bool,
) -> None:
    """Optimize the contents of ``input_path`` and write to ``output_path``."""
    with input_path.open("r") as inp, output_path.open("w") as out:
        optimize_stream(inp, out, model, api_key, optimization_type, verbose)


@click.group()
def main() -> None:
    """DSPy Prompt Optimizer CLI."""
    pass


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
def optimize_command(
    input_prompt: TextIO,
    output: TextIO,
    model: str,
    api_key: Optional[str],
    optimization_type: str,
    verbose: bool,
) -> None:
    """Optimize a single prompt."""
    if not api_key:
        click.echo(
            "Error: Anthropic API key is required. Provide it with --api-key or set ANTHROPIC_API_KEY environment variable.",
            err=True,
        )
        sys.exit(1)

    optimize_stream(input_prompt, output, model, api_key, optimization_type, verbose)


@main.command()
@click.argument("source", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(file_okay=False, path_type=Path),
    required=True,
    help="Directory to write optimized prompts.",
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
def batch(
    source: Path,
    output_dir: Path,
    model: str,
    api_key: Optional[str],
    optimization_type: str,
    verbose: bool,
) -> None:
    """Optimize multiple prompts from ``SOURCE``."""
    if not api_key:
        click.echo(
            "Error: Anthropic API key is required. Provide it with --api-key or set ANTHROPIC_API_KEY environment variable.",
            err=True,
        )
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    if source.is_dir():
        for file in source.iterdir():
            if file.is_file():
                out_file = output_dir / file.name
                optimize_file(file, out_file, model, api_key, optimization_type, verbose)
    else:
        prompts = [line.strip() for line in source.read_text().splitlines() if line.strip()]
        for idx, prompt in enumerate(prompts, start=1):
            out_file = output_dir / f"{source.stem}_{idx}{source.suffix}"
            out_file.write_text(
                optimize_text(prompt, model, api_key, optimization_type, verbose)
            )


if __name__ == '__main__':
    main()
