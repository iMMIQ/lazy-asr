"""Tests for CLI commands"""

import pytest
from typer.testing import CliRunner


def test_cli_help(runner: CliRunner):
    """Test CLI help command"""
    from app.cli.main import app
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "lazy-asr" in result.stdout
    assert "transcribe" in result.stdout
    assert "scan" in result.stdout


def test_transcribe_help(runner: CliRunner):
    """Test transcribe command help"""
    from app.cli.main import app
    result = runner.invoke(app, ["transcribe", "--help"])
    assert result.exit_code == 0
    assert "file" in result.stdout
    assert "--method" in result.stdout


def test_scan_help(runner: CliRunner):
    """Test scan command help"""
    from app.cli.main import app
    result = runner.invoke(app, ["scan", "--help"])
    assert result.exit_code == 0
    assert "path" in result.stdout
    assert "--recursive" in result.stdout


def test_plugins_command(runner: CliRunner):
    """Test plugins list command"""
    from app.cli.main import app
    result = runner.invoke(app, ["plugins"])
    assert result.exit_code == 0
    assert "ASR" in result.stdout or "Plugins" in result.stdout


def test_version_command(runner: CliRunner):
    """Test version command"""
    from app.cli.main import app
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "lazy-asr" in result.stdout


def test_transcribe_missing_file(runner: CliRunner):
    """Test transcribe with missing file"""
    from app.cli.main import app
    result = runner.invoke(app, ["transcribe", "/nonexistent/file.wav"])
    assert result.exit_code == 1
    assert "not found" in result.stdout.lower()


@pytest.mark.asyncio
async def test_progress_reporter():
    """Test ConsoleProgressReporter"""
    from app.cli.progress import ConsoleProgressReporter
    from rich.console import Console

    console = Console()
    reporter = ConsoleProgressReporter(console)

    # Test info message
    reporter.print_info("Test info message")

    # Test success message
    reporter.print_success("Test success message")

    # Test error message
    reporter.print_error("Test error message")

    # Test warning message
    reporter.print_warning("Test warning message")

    # Test stats display
    reporter.print_stats({"total": 10, "processed": 8, "failed": 2})
