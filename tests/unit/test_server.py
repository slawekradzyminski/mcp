"""Tests for server.py module."""

import importlib.util
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import click.testing
import pytest

# Load server.py directly to avoid confusion with server/ package
spec = importlib.util.spec_from_file_location(
    "server_module", "mcp_simple_tool/server.py"
)
server_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server_module)


@pytest.mark.asyncio
async def test_fetch_website():
    """Test the fetch_website function."""
    # given
    mock_response = MagicMock()
    mock_response.text = "Website content"
    mock_response.raise_for_status = AsyncMock()

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.get.return_value = mock_response

    # Need to patch at the module level where it's actually used
    with patch.object(
        server_module, "create_mcp_http_client", return_value=mock_client
    ):
        # when
        result = await server_module.fetch_website("https://example.com")

        # Verify that the mock was awaited
        mock_response.raise_for_status.assert_awaited_once()

        # then
        assert len(result) == 1
        assert result[0].type == "text"
        assert result[0].text == "Website content"
        mock_client.get.assert_called_once_with("https://example.com")


def test_main_cli():
    """Test the main CLI function."""
    # given
    runner = click.testing.CliRunner()

    # when/then
    with patch("uvicorn.run") as mock_run:
        # Create mock for FastMCP
        mock_mcp = MagicMock()
        mock_mcp.sse_app.return_value = MagicMock()

        # Patch FastMCP directly in the server_module
        with patch.object(
            server_module, "FastMCP", return_value=mock_mcp
        ) as mock_fastmcp:
            # Run the CLI
            result = runner.invoke(server_module.main, ["--port", "8000"])

            # Verify results
            assert result.exit_code == 0
            assert "Starting MCP website fetcher server on port 8000" in result.output

            # Use ANY to match the ASGI app
            mock_run.assert_called_once_with(ANY, host="0.0.0.0", port=8000)

            # Verify FastMCP was used correctly
            mock_fastmcp.assert_called_once_with("mcp-website-fetcher-sse")
            mock_mcp.tool.assert_called()
            mock_mcp.sse_app.assert_called_once()


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
