"""Tests for server.py module."""

import importlib.util
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import click.testing

# Load server.py directly to avoid confusion with server/ package
spec = importlib.util.spec_from_file_location(
    "server_module", "mcp_simple_tool/server.py"
)
server_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server_module)


def test_main_cli_help():
    """Test the main CLI help command."""
    # given
    runner = click.testing.CliRunner()

    # when
    result = runner.invoke(server_module.main, ["--help"])

    # then
    assert result.exit_code == 0
    assert "--port" in result.output
    assert "--transport" in result.output
