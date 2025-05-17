"""
Command-line interface for DSPy Prompt Optimizer.
"""

import sys
import click
from typing import Optional, TextIO

from .optimizer import optimize_prompt


@click.command()
@click.argument('input_prompt', type=click.File('r'), default=sys.stdin)
@click.option('--output', '-o', type=click.File('w'), default=sys.stdout,
              help='Output file for the optimized prompt. Defaults to stdout.')
@click.option('--model', '-m', default='claude-3-7-sonnet-latest',
              help='Model to use for optimization. Defaults to claude-3-7-sonnet-latest.')
@click.option('--api-key', '-k', envvar='ANTHROPIC_API_KEY',
              help='Anthropic API key. Can also be set via ANTHROPIC_API_KEY environment variable.')
@click.option('--optimization-type', '-t', type=click.Choice(['self', 'example', 'metric']), default='self',
              help='Type of optimization to perform: self-refinement, example-based, or metric-based.')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output.')
def main(input_prompt: TextIO, output: TextIO, model: str, api_key: Optional[str], 
         optimization_type: str, verbose: bool) -> None:
    """
    Optimize a prompt using DSPy framework.
    
    INPUT_PROMPT: File containing the prompt to optimize, or stdin if not specified.
    """
    if not api_key:
        click.echo("Error: Anthropic API key is required. Provide it with --api-key or set ANTHROPIC_API_KEY environment variable.", err=True)
        sys.exit(1)
    
    # Read the input prompt
    prompt_text = input_prompt.read().strip()
    
    if verbose:
        click.echo(f"Optimizing prompt using {optimization_type} approach with model {model}...", err=True)
    
    # Optimize the prompt using DSPy
    try:
        optimized_prompt = optimize_prompt(
            prompt_text=prompt_text,
            model=model,
            api_key=api_key,
            optimization_type=optimization_type,
            verbose=verbose
        )
        
        # Write the optimized prompt to the output
        _ = output.write(optimized_prompt)
        
        if verbose:
            click.echo("Prompt optimization complete!", err=True)
            
    except Exception as e:
        click.echo(f"Error during prompt optimization: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
