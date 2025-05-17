from click.testing import CliRunner
from prompt_optimizer.cli import main


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    # Help message should contain usage information
    assert "Usage" in result.output or "Show this message" in result.output
