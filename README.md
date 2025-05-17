# DSPy Prompt Optimizer

A Python CLI tool that uses the DSPy framework to optimize prompts for large language models, with a focus on improving prompts for thinking models like Claude Sonnet 3.7.

## Table of Contents

- [Introduction to DSPy](#introduction-to-dspy)
- [Installation](#installation)
- [Usage](#usage)
- [Understanding DSPy Concepts](#understanding-dspy-concepts)
- [Optimization Approaches](#optimization-approaches)
- [Example Workflow](#example-workflow)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)

## Introduction to DSPy

DSPy (Declarative Self-improving Prompting) is a framework for programming with foundation models. Unlike traditional prompt engineering, DSPy allows you to:

1. **Declare what you want** rather than how to get it
2. **Optimize prompts automatically** based on examples or metrics
3. **Compose complex pipelines** of language model calls
4. **Improve performance systematically** through teleprompters and optimizers

DSPy was developed by researchers at Stanford, and it represents a significant advancement in how we interact with and optimize language models.

## Installation

### Prerequisites

- Python 3.10 or higher (but less than 3.13 due to dependency constraints)
- Virtual environment (recommended)

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/dspy-prompt-optimizer.git
   cd dspy-prompt-optimizer
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package:
   ```bash
   pip install -e .
   ```

### Dependency Notes

DSPy has complex dependency requirements. If you encounter issues with Poetry installation, the recommended approach is to use pip with a virtual environment as shown above.

## Usage

The DSPy Prompt Optimizer can be used as a command-line tool:

```bash
# Basic usage (reads from stdin, outputs to stdout)
cat your_prompt.txt | dspy-prompt-optimizer

# Specify input and output files
dspy-prompt-optimizer your_prompt.txt -o optimized_prompt.txt

# Choose optimization approach
dspy-prompt-optimizer your_prompt.txt -t example

# Enable verbose output
dspy-prompt-optimizer your_prompt.txt -v
```

### Command-line Options

- `INPUT_PROMPT`: File containing the prompt to optimize (defaults to stdin)
- `--output, -o`: Output file for the optimized prompt (defaults to stdout)
- `--model, -m`: Model to use for optimization (defaults to claude-3-sonnet-20240229)
- `--api-key, -k`: Anthropic API key (can also be set via ANTHROPIC_API_KEY environment variable)
- `--optimization-type, -t`: Type of optimization to perform: self, example, or metric (defaults to self)
- `--verbose, -v`: Enable verbose output

## Understanding DSPy Concepts

DSPy introduces several key concepts that make it powerful for prompt optimization:

### 1. Signatures

Signatures in DSPy define the inputs and outputs of language model operations. They're like function signatures but for LM interactions:

```python
class PromptRefiner(dspy.Signature):
    """Refine a prompt to make it more effective."""
    
    prompt = dspy.InputField(desc="The original prompt that needs refinement")
    analysis = dspy.OutputField(desc="Analysis of the prompt's strengths and weaknesses")
    improved_prompt = dspy.OutputField(desc="A refined version of the prompt")
```

This declarative approach allows DSPy to understand what you want from the model.

### 2. Modules

DSPy modules are the building blocks that use signatures to perform specific tasks:

- **Predict**: Simple prediction based on a signature
- **ChainOfThought**: Adds reasoning steps before producing outputs
- **MultiChainOfThought**: Generates multiple reasoning paths and selects the best one

Example:
```python
refiner = dspy.Predict(PromptRefiner)  # Simple prediction
refiner = dspy.ChainOfThought(PromptRefiner)  # With reasoning steps
```

### 3. Optimizers

Optimizers (formerly called Teleprompters) are DSPy's optimization engines. They take examples and metrics to improve module performance:

```python
# Example of using a DSPy optimizer
from dspy.teleprompt import BootstrapFewShot
optimizer = BootstrapFewShot(max_bootstrapped_demos=3)
compiled_module = optimizer.compile(module=refiner, trainset=examples, metric=my_metric)
```

This process automatically generates better prompts based on the examples and metrics provided.

### 4. LM Configuration

DSPy abstracts away the specifics of different LM providers, making it easy to switch between them:

```python
lm = dspy.LM('anthropic/claude-3-sonnet-20240229', api_key="your-api-key")
dspy.configure(lm=lm)
```

## Optimization Approaches

This tool implements three different approaches to prompt optimization:

### 1. Self-Refinement

The self-refinement approach uses the language model to analyze and improve its own prompts. It:
- Analyzes the strengths and weaknesses of the original prompt
- Generates an improved version addressing the identified issues
- Does not require examples or metrics

This is the simplest approach and works well for many use cases.

### 2. Example-Based Optimization

Example-based optimization uses examples of good prompts to guide the improvement process:
- Learns patterns from examples of original prompts and their improved versions
- Applies these patterns to new prompts
- Requires curated examples of good prompt transformations

This approach is more powerful when you have specific examples of the kinds of improvements you want.

**Note:** In the current implementation with DSPy 2.6.23, the example-based optimization approach has compatibility issues due to API changes in DSPy. This is documented as a known limitation and may require updates as DSPy evolves.

### 3. Metric-Based Optimization

Metric-based optimization iteratively improves prompts based on quantifiable metrics:
- Defines metrics like clarity, specificity, and actionability
- Generates candidate improvements and evaluates them
- Keeps the best-performing version
- Can run for multiple iterations to progressively improve

This approach is the most sophisticated and can achieve the best results with sufficient iterations.

## Example Workflow

Here's a typical workflow for optimizing a prompt for Claude Sonnet 3.7:

1. Start with a basic prompt idea:
   ```
   I have noticed thinking LLMs such as Claude Sonnet 3.7 tend to have tendencies to go down rabbit holes, go on sidequests and loose the original mission statement; they often blow out the scope of the request and make things a lot more complicated; It's like they have ADHD and OCD at the same time;

   Are there any research, academic or enthusiast based on this? have researchers or the community been able to come up with battle-tested prompts (user or system prompt) to deal with this behaviour and get the LLMs that have built-in chain of thought to focus? based on recent advancements in prompt engineering and other comminuty and researcher work, present me a "Rule" (prompt) for this matter
   ```

2. Save this to a file:
   ```bash
   echo "Your prompt text..." > original_prompt.txt
   ```

3. Run the optimizer:
   ```bash
   export ANTHROPIC_API_KEY="your-api-key"
   dspy-prompt-optimizer original_prompt.txt -o optimized_prompt.txt -t metric -v
   ```

4. Review the optimized prompt in `optimized_prompt.txt`

5. Try different optimization approaches to compare results:
   ```bash
   dspy-prompt-optimizer original_prompt.txt -o optimized_self.txt -t self -v
   dspy-prompt-optimizer original_prompt.txt -o optimized_example.txt -t example -v
   dspy-prompt-optimizer original_prompt.txt -o optimized_metric.txt -t metric -v
   ```

## Troubleshooting

### API Key Issues

If you encounter errors related to the API key:
- Ensure you've set the `ANTHROPIC_API_KEY` environment variable or passed it with `-k`
- Verify the API key is valid and has not expired
- Check for any whitespace or special characters that might have been copied with the key

### Dependency Issues

DSPy has complex dependencies that can sometimes conflict:
- Use a fresh virtual environment to avoid conflicts with existing packages
- If using Poetry fails, try direct pip installation in a virtual environment
- Ensure you're using Python 3.10-3.12 as some dependencies have specific version requirements

### Optimization Quality

If the optimized prompts aren't improving as expected:
- Try a different optimization approach (`-t` option)
- Enable verbose mode (`-v`) to see the analysis and reasoning
- Consider providing better examples if using example-based optimization
- Increase iterations for metric-based optimization (requires code modification)

## Future Enhancements

Potential improvements for future versions:

- Support for more LLM providers beyond Anthropic
- Custom optimization metrics definition
- User interface for interactive prompt optimization
- Integration with prompt management systems
- Batch processing of multiple prompts
- Fine-tuning optimization parameters
- Additional optimization approaches
- Persistent storage of optimization history

---

This project was created to demonstrate DSPy's capabilities for prompt optimization. For more information about DSPy, visit the [official DSPy documentation](https://dspy-docs.vercel.app/).
