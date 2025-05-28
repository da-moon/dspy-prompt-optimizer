# DSPy Prompt Optimizer

A Python CLI tool that uses the DSPy framework to optimize prompts for large
language models, with a focus on improving prompts for thinking models like
Claude Sonnet 3.7.

## Table of Contents

- [Introduction to DSPy](#introduction-to-dspy)
- [Installation](#installation)
- [Usage](#usage)
- [Using Poetry Commands](#using-poetry-commands)
- [Understanding DSPy Concepts](#understanding-dspy-concepts)
- [Optimization Approaches](#optimization-approaches)
- [Example Workflow](#example-workflow)
- [Build and Packaging](#build-and-packaging)
- [Development Setup](#development-setup)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)

## Introduction to DSPy

DSPy (Declarative Self-improving Prompting) is a framework for programming with
foundation models. Unlike traditional prompt engineering, DSPy allows you to:

1. **Declare what you want** rather than how to get it
2. **Optimize prompts automatically** based on examples or metrics
3. **Compose complex pipelines** of language model calls
4. **Improve performance systematically** through teleprompters and optimizers

DSPy was developed by researchers at Stanford, and it represents a significant
advancement in how we interact with and optimize language models.

## Installation

### Prerequisites

- Python 3.10 or higher (but less than 3.13 due to dependency constraints)
- Poetry (dependency management tool)

### Installing Poetry

If you don't have Poetry installed, you can install it following the
[official instructions](https://python-poetry.org/docs/#installation):

**On Linux, macOS, Windows (WSL):**

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**On Windows (PowerShell):**

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

Verify the installation:

```bash
poetry --version
```

### Setup

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/dspy-prompt-optimizer.git
   cd dspy-prompt-optimizer
   ```

2. Install dependencies using Poetry:

   ```bash
   poetry install
   ```

This will:

- Create a virtual environment for the project
- Install all required dependencies
- Install development dependencies if you add the `--with dev` flag

### Dependency Notes

DSPy has complex dependency requirements which are handled automatically by
Poetry. The project's `pyproject.toml` file specifies the exact version
constraints needed for compatibility.

### Using pyenv

Since this project requires Python >=3.10,<3.13, you may need to use pyenv to
manage Python versions if your system Python is incompatible (e.g., Python
3.13+).

1. Install pyenv if not already installed:

   ```bash
   # On Linux/macOS
   curl https://pyenv.run | bash

   # Add to your shell configuration (.bashrc, .zshrc, etc.)
   echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
   echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
   echo 'eval "$(pyenv init -)"' >> ~/.bashrc
   ```

2. Install a compatible Python version:

   ```bash
   # List available Python versions
   pyenv install --list | grep " 3.1[0-2]"

   # Install a specific version (e.g., Python 3.12.7)
   pyenv install 3.12.7
   ```

3. Configure Poetry to use the installed Python version:

   ```bash
   # Verify available Python versions
   pyenv versions

   # Configure Poetry to use a specific Python version
   poetry env use 3.12.7

   # Verify Poetry environment configuration
   poetry env info
   ```

This ensures that Poetry creates a virtual environment with a Python version
compatible with the project requirements.

## Usage

The DSPy Prompt Optimizer uses a command-line interface with subcommands for different optimization strategies:

### Basic Usage Patterns

```bash
# Self-refinement optimization (simplest approach)
cat your_prompt.txt | poetry run dspy-prompt-optimizer -- self

# Example-based optimization
poetry run dspy-prompt-optimizer -- example your_prompt.txt -o optimized_prompt.txt

# Metric-based optimization with custom iterations
poetry run dspy-prompt-optimizer -- metric your_prompt.txt -i 5 -o optimized_prompt.txt

# Generate examples for two-phase approach
poetry run dspy-prompt-optimizer -- generate-examples examples.json

# Use pre-generated examples
poetry run dspy-prompt-optimizer -- example your_prompt.txt --examples-file examples.json
```

### Advanced Configuration

```bash
# Configure maximum tokens for longer responses
poetry run dspy-prompt-optimizer -- self your_prompt.txt --max-tokens 128000

# Use different models for optimization and example generation
poetry run dspy-prompt-optimizer -- example your_prompt.txt \
  --model claude-sonnet-4-20250514 \
  --example-generator-model claude-3-5-haiku-latest \
  --example-generator-max-tokens 4000

# Enable verbose output for all operations
poetry run dspy-prompt-optimizer -- metric your_prompt.txt -v -i 3
```

### Available Commands

The tool provides four main commands:

#### `self` - Self-Refinement Optimization
Optimizes prompts using self-analysis and improvement.

```bash
poetry run dspy-prompt-optimizer -- self [OPTIONS] [INPUT_PROMPT]
```

#### `example` - Example-Based Optimization
Uses examples to guide prompt optimization.

```bash
poetry run dspy-prompt-optimizer -- example [OPTIONS] [INPUT_PROMPT]
```

#### `metric` - Metric-Based Optimization
Iteratively optimizes based on quantifiable metrics.

```bash
poetry run dspy-prompt-optimizer -- metric [OPTIONS] [INPUT_PROMPT]
```

#### `generate-examples` - Example Generation
Generates examples for later use in example-based optimization.

```bash
poetry run dspy-prompt-optimizer -- generate-examples [OPTIONS] OUTPUT_FILE
```

### Common Options (Available for All Commands)

- `INPUT_PROMPT`: File containing the prompt to optimize (defaults to stdin)
- `--output, -o`: Output file for the optimized prompt (defaults to stdout)
- `--model, -m`: Model to use for optimization (defaults to claude-sonnet-4-20250514)
- `--api-key, -k`: Anthropic API key (can also be set via `ANTHROPIC_API_KEY` environment variable)
- `--max-tokens`: Maximum number of tokens for LM generation (defaults to 8000)
- `--verbose, -v`: Enable verbose output

### Example-Specific Options

- `--num-examples, -n`: Number of examples to generate or use (defaults to 3)
- `--example-generator-model, --eg-model`: Model for example generation (defaults to claude-3-5-haiku-latest)
- `--example-generator-api-key, --eg-api-key`: Separate API key for example generation
- `--example-generator-max-tokens, --eg-max-tokens`: Maximum tokens for example generator (defaults to same as optimizer)
- `--examples-file, -f`: JSON file containing pre-generated examples

### Metric-Specific Options

- `--max-iterations, -i`: Maximum number of iterations for optimization (defaults to 3)

## Using Poetry Commands

Poetry provides a streamlined way to work with Python packages and
dependencies. Here's how to use Poetry with DSPy Prompt Optimizer:

### Running Commands

Poetry automatically manages the virtual environment for you. To run the tool,
use:

```bash
# Run the tool using Poetry
poetry run dspy-prompt-optimizer [arguments]
```

### Activating the Virtual Environment

If you prefer to activate the virtual environment and then run commands
directly:

```bash
# Activate the Poetry virtual environment
poetry shell

# Now you can run the tool directly
dspy-prompt-optimizer [arguments]

# When finished, exit the Poetry shell
exit
```

### Managing Dependencies

Poetry automatically handles all dependencies based on the `pyproject.toml`
file:

```bash
# Add a new dependency
poetry add package-name

# Add a development dependency
poetry add --group dev package-name

# Update dependencies
poetry update
```

### Available Scripts

The following scripts are available through Poetry:

```bash
# Run the main prompt optimizer
poetry run dspy-prompt-optimizer
```

## Understanding DSPy Concepts

DSPy introduces several key concepts that make it powerful for prompt
optimization:

### 1. Signatures

Signatures in DSPy define the inputs and outputs of language model operations.
They're like function signatures but for LM interactions:

```python
class PromptRefiner(dspy.Signature):
    """Refine a prompt to make it more effective."""

    prompt = dspy.InputField(desc="The original prompt that needs refinement")
    analysis = dspy.OutputField(desc="Analysis of the prompt's strengths and weaknesses")
    improved_prompt = dspy.OutputField(desc="A refined version of the prompt")
```

This declarative approach allows DSPy to understand what you want from the
model.

### 2. Modules

DSPy modules are the building blocks that use signatures to perform specific
tasks:

- **Predict**: Simple prediction based on a signature
- **ChainOfThought**: Adds reasoning steps before producing outputs
- **MultiChainOfThought**: Generates multiple reasoning paths and selects the
  best one

Example:

```python
refiner = dspy.Predict(PromptRefiner)  # Simple prediction
refiner = dspy.ChainOfThought(PromptRefiner)  # With reasoning steps
```

### 3. Optimizers

Optimizers (formerly called Teleprompters) are DSPy's optimization engines.
They take examples and metrics to improve module performance:

```python
# Example of using a DSPy optimizer
from dspy.teleprompt import BootstrapFewShot
optimizer = BootstrapFewShot(max_bootstrapped_demos=3)
compiled_module = optimizer.compile(module=refiner, trainset=examples, metric=my_metric)
```

This process automatically generates better prompts based on the examples and
metrics provided.

### 4. LM Configuration

DSPy abstracts away the specifics of different LM providers, making it easy to
switch between them:

```python
lm = dspy.LM('anthropic/claude-sonnet-4-20250514', api_key="your-api-key")
dspy.configure(lm=lm)
```

## Optimization Approaches

This tool implements three different approaches to prompt optimization:

### 1. Self-Refinement

The self-refinement approach uses the language model to analyze and improve its
own prompts. It:

- Analyzes the strengths and weaknesses of the original prompt
- Generates an improved version addressing the identified issues
- Does not require examples or metrics

This is the simplest approach and works well for many use cases.

### 2. Example-Based Optimization

Example-based optimization uses examples of good prompts to guide the
improvement process:

- Learns patterns from examples of original prompts and their improved versions
- Applies these patterns to new prompts
- Requires curated examples of good prompt transformations

This approach is more powerful when you have specific examples of the kinds of
improvements you want.

### 3. Metric-Based Optimization

Metric-based optimization iteratively improves prompts based on quantifiable
metrics:

- Defines metrics like clarity, specificity, and actionability
- Generates candidate improvements and evaluates them
- Keeps the best-performing version
- Can run for multiple iterations to progressively improve
- The number of iterations can be configured using the `--max-iterations` flag

This approach is the most sophisticated and can achieve the best results with
sufficient iterations. You can control the optimization intensity by adjusting
the maximum number of iterations (default is 3).

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
   poetry run dspy-prompt-optimizer -- metric original_prompt.txt -o optimized_prompt.txt -v
   ```

   Or with custom iterations for more intensive optimization:

   ```bash
   poetry run dspy-prompt-optimizer -- metric original_prompt.txt -o optimized_prompt.txt -i 5 -v
   ```

4. Review the optimized prompt in `optimized_prompt.txt`

5. Try different optimization approaches to compare results:
   ```bash
   poetry run dspy-prompt-optimizer -- self original_prompt.txt -o optimized_self.txt -v
   poetry run dspy-prompt-optimizer -- example original_prompt.txt -o optimized_example.txt -v
   poetry run dspy-prompt-optimizer -- metric original_prompt.txt -o optimized_metric.txt -v
   ```

6. For advanced example-based optimization, use the two-phase approach:
   ```bash
   # Phase 1: Generate examples
   poetry run dspy-prompt-optimizer -- generate-examples examples.json -n 5 -v
   
   # Phase 2: Use examples for optimization
   poetry run dspy-prompt-optimizer -- example original_prompt.txt -f examples.json -o optimized_prompt.txt -v
   ```

## Build and Packaging

This project uses Poetry for managing dependencies, building, and packaging.

### Building the Project

Poetry simplifies the build process. To build the source and wheel distributions, run the following command in the project's root directory:

```bash
poetry build
```

This command performs several steps:
1.  It resolves the project dependencies.
2.  It creates a source distribution (sdist) in `.tar.gz` format.
3.  It creates a wheel distribution (a built package) in `.whl` format.

Both build artifacts will be placed in the `dist/` directory within your project. For example:
```
dist/
├── dspy_prompt_optimizer-0.1.0-py3-none-any.whl
└── dspy-prompt-optimizer-0.1.0.tar.gz
```
(The version number `0.1.0` will correspond to the version specified in your `pyproject.toml` file.)

These files can then be used for distribution or installation using pip:
```bash
pip install dist/dspy_prompt_optimizer-0.1.0-py3-none-any.whl
```

### Publishing (Optional)

If you intend to publish the package to the Python Package Index (PyPI) or a private repository, Poetry provides the `publish` command:

```bash
poetry publish --build
```
The `--build` option tells Poetry to build the package (if not already built) before publishing.

Before publishing, you will need to configure Poetry with your repository credentials. For PyPI, this usually involves setting up an API token. Refer to the [official Poetry documentation on publishing](https://python-poetry.org/docs/publishing/) for detailed instructions.

### Cleaning Build Artifacts

Poetry does not have a dedicated `clean` command like `make clean`. To remove build artifacts, you can manually delete the `dist/` directory:

```bash
rm -rf dist/
```
If you also want to remove any build-specific caches or compiled Python files, you might also consider removing `*.pyc` files and `__pycache__` directories, though these are generally managed by Python itself.
```

</edits>

## Troubleshooting

### API Key Issues

If you encounter errors related to the API key:

- Ensure you've set the `ANTHROPIC_API_KEY` environment variable or passed it
  with `-k`
- Verify the API key is valid and has not expired
- Check for any whitespace or special characters that might have been copied
  with the key

### Poetry Issues

If you encounter issues with Poetry:

- **Poetry installation fails**: Refer to the
  [official installation documentation](https://python-poetry.org/docs/#installation)
- **Dependency resolution takes too long**: Try
  `poetry add packagename --no-update` and then run `poetry update` separately
- **Virtual environment not activating**: Use `poetry env info` to debug
  environment issues
- **Unknown command errors**: Ensure you're running Poetry commands from the
  project root directory
- **Version conflicts**: Check your `pyproject.toml` file for dependency
  version constraints

### Token Limit Issues

If you encounter errors related to token limits:

- **Error message**: "LM response was truncated due to exceeding max_tokens=8000"

- **Solution**: Use the `--max-tokens` flag to increase the token limit:
  ```bash
  poetry run dspy-prompt-optimizer -- self your_prompt.txt --max-tokens 128000
  ```

- **Default value**: The default is 8000 tokens, which should handle most use cases
- **Considerations**: Higher token limits may increase response time and API costs
- **For complex prompts**: Use higher values like 128000 or 256000 tokens
- **For example generation**: Use separate token limits with `--example-generator-max-tokens`:
  ```bash
  poetry run dspy-prompt-optimizer -- example your_prompt.txt \
    --max-tokens 128000 \
    --example-generator-max-tokens 4000
  ```

### Dependency Issues

### Python Version Compatibility

If you encounter Python version compatibility issues:

- **Error message**: "The currently activated Python version X is not supported
  by the project (>=3.10,<3.13)"

- **Solution**:

  1. Install a compatible Python version using pyenv:
     ```bash
     pyenv install 3.12.7  # or any version between 3.10 and 3.12
     ```
  2. Configure Poetry to use this version:
     ```bash
     poetry env use 3.12.7
     ```
  3. Check your Poetry environment configuration:
     ```bash
     poetry env info
     ```
  4. List all Poetry environments:
     ```bash
     poetry env list
     ```

- **Prevention**: Always check the Python version requirements in
  `pyproject.toml` before setting up the project. This project requires
  Python >=3.10,<3.13.

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

This project was created to demonstrate DSPy's capabilities for prompt
optimization. For more information about DSPy, visit the
[official DSPy documentation](https://dspy-docs.vercel.app/).
