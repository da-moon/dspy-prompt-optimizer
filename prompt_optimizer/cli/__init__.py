from __future__ import annotations

import click

from .example_cmd import example_command
from .generate_examples_cmd import generate_examples_command
from .metric_cmd import metric_command
from .self_cmd import self_command


@click.group()
def main() -> None:
    """DSPy Prompt Optimizer - Optimize prompts using different strategies."""


main.add_command(self_command)
main.add_command(example_command)
main.add_command(metric_command)
main.add_command(generate_examples_command)
