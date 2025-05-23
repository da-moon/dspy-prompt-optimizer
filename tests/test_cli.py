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
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    # Check that max-iterations flag is in the help output
    assert "--max-iterations" in result.output
    assert "Maximum number of iterations" in result.output


def test_cli_max_tokens_flag() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    # Check that max-tokens flag is in the help output
    assert "--max-tokens" in result.output
    assert "Maximum number of tokens" in result.output
    # Check that the default value is shown
    assert "64000" in result.output
