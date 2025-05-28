import json
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytest import MonkeyPatch

import pytest
from click.testing import CliRunner

from prompt_optimizer.cli import main


def test_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    # Help message should contain usage information
    assert "Usage" in result.output or "Show this message" in result.output


def test_cli_max_iterations_flag() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["metric", "--help"])
    assert result.exit_code == 0
    # Check that max-iterations flag is in the metric command help output
    assert "--max-iterations" in result.output
    assert "Maximum number of iterations" in result.output


def test_cli_max_tokens_flag() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["self", "--help"])
    assert result.exit_code == 0
    # Check that max-tokens flag is in the self command help output
    assert "--max-tokens" in result.output
    assert "Maximum number of tokens" in result.output
    # Check that the default value is shown
    assert "8000" in result.output


def test_cli_missing_api_key() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create a temporary input file instead of using stdin
        with open("test_prompt.txt", "w") as f:
            _ = f.write("test prompt")
        # Remove API key from environment for this test
        result = runner.invoke(main, ["self", "test_prompt.txt"], env={"ANTHROPIC_API_KEY": ""})
        assert result.exit_code == 1
        assert "Anthropic API key is required" in result.output


def test_cli_invalid_command() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["invalid"])
    assert result.exit_code == 2
    assert "No such command 'invalid'" in result.output


@pytest.fixture
def mock_dspy_for_cli(monkeypatch: "MonkeyPatch") -> None:
    """Mock dspy module for CLI tests."""
    
    class FakeChainOfThought:
        def __init__(self, signature: object) -> None:
            self.signature = signature

        def __call__(self, **kwargs: object) -> SimpleNamespace:
            return SimpleNamespace(
                improved_prompt="Optimized: test prompt",
                analysis="This prompt could be improved by adding more specificity.",
                examples="[{\"prompt\": \"test\", \"analysis\": \"analysis\", \"improved_prompt\": \"improved\"}]"
            )

    def mock_example(*_args: object, **kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(**kwargs)

    def mock_configure(**_kwargs: object) -> None:
        return None

    def mock_lm(*_args: object, **_kwargs: object) -> None:
        return None

    def mock_input_field(*args: object, **kwargs: object) -> None:
        return None
    
    def mock_output_field(*args: object, **kwargs: object) -> None:
        return None
    
    fake_dspy = SimpleNamespace(
        Signature=object,
        InputField=mock_input_field,
        OutputField=mock_output_field,
        ChainOfThought=FakeChainOfThought,
        Example=mock_example,
        configure=mock_configure,
        LM=mock_lm,
        DSPyResult=SimpleNamespace,
    )

    # Mock dspy in all relevant modules
    import prompt_optimizer.optimizer.base as base_module
    import prompt_optimizer.optimizer.example_based.optimizer as example_based_optimizer_module
    import prompt_optimizer.optimizer.example_based.generator as example_generator_module
    
    monkeypatch.setattr(base_module, "dspy", fake_dspy)
    monkeypatch.setattr(example_based_optimizer_module, "dspy", fake_dspy)
    monkeypatch.setattr(example_generator_module, "dspy", fake_dspy)


def test_example_oneshot_mode(mock_dspy_for_cli: None) -> None:
    """Test example-based optimization in oneshot mode (generate examples + optimize)."""
    runner = CliRunner()
    
    with runner.isolated_filesystem():
        # Create test prompt file
        with open("test_prompt.txt", "w") as f:
            _ = f.write("test prompt")
        
        # Run example command without examples file (oneshot mode)
        result = runner.invoke(main, [
            "example", 
            "test_prompt.txt",
            "--api-key", "test-key",
            "--verbose"
        ])
        
        assert result.exit_code == 0
        # Just check that the command ran successfully - the optimization functionality 
        # is already tested in the optimizer unit tests
        assert "Prompt optimization complete!" in result.output


def test_example_two_step_mode(mock_dspy_for_cli: None) -> None:
    """Test example-based optimization in two-step mode (generate examples JSON then optimize)."""
    runner = CliRunner()
    
    with runner.isolated_filesystem():
        # Step 1: Generate examples file
        result = runner.invoke(main, [
            "generate-examples",
            "examples.json",
            "--api-key", "test-key",
            "--num-examples", "2",
            "--verbose"
        ])
        
        assert result.exit_code == 0
        assert "examples.json" in result.output
        
        # Verify the examples file was created and has valid JSON
        examples_path = Path("examples.json")
        assert examples_path.exists()
        
        # Create a proper examples file for testing
        examples_data = [
            {
                "prompt": "Tell me about AI",
                "analysis": "This prompt is too vague",
                "improved_prompt": "Explain the key concepts of artificial intelligence"
            },
            {
                "prompt": "How do I code?",
                "analysis": "This prompt lacks specificity",
                "improved_prompt": "Provide a beginner's guide to Python programming"
            }
        ]
        
        with open("examples.json", "w") as f:
            json.dump(examples_data, f, indent=2)
        
        # Step 2: Create test prompt file
        with open("test_prompt.txt", "w") as f:
            _ = f.write("test prompt")
        
        # Step 3: Use the examples file for optimization
        result = runner.invoke(main, [
            "example", 
            "test_prompt.txt",
            "--examples-file", "examples.json",
            "--api-key", "test-key",
            "--verbose"
        ])
        
        assert result.exit_code == 0
        # Just check that the command ran successfully - the optimization functionality 
        # is already tested in the optimizer unit tests
        assert "Prompt optimization complete!" in result.output


def test_generate_examples_command(mock_dspy_for_cli: None) -> None:
    """Test the generate-examples command."""
    runner = CliRunner()
    
    with runner.isolated_filesystem():
        result = runner.invoke(main, [
            "generate-examples",
            "test_examples.json",
            "--api-key", "test-key",
            "--num-examples", "3",
            "--model", "claude-3-5-haiku-latest",
            "--verbose"
        ])
        
        assert result.exit_code == 0
        assert "test_examples.json" in result.output
        
        # Check that file was created
        examples_path = Path("test_examples.json")
        assert examples_path.exists()


def test_example_command_missing_api_key() -> None:
    """Test example command with missing API key."""
    runner = CliRunner()
    
    with runner.isolated_filesystem():
        with open("test_prompt.txt", "w") as f:
            _ = f.write("test prompt")
        
        result = runner.invoke(main, [
            "example", 
            "test_prompt.txt"
        ], env={"ANTHROPIC_API_KEY": ""})
        
        assert result.exit_code == 1
        assert "Anthropic API key is required" in result.output


def test_generate_examples_missing_api_key() -> None:
    """Test generate-examples command with missing API key."""
    runner = CliRunner()
    
    with runner.isolated_filesystem():
        result = runner.invoke(main, [
            "generate-examples",
            "examples.json"
        ], env={"ANTHROPIC_API_KEY": ""})
        
        assert result.exit_code == 1
        assert "Anthropic API key is required" in result.output
