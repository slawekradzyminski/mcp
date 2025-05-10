"""Integration tests for the MCP server application."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_simple_tool.server.app import handle_sse, starlette_app


@pytest.mark.timeout(5)  # Set a more strict timeout for this specific test
def test_server_routes_exist():
    """Test that the essential server routes exist."""
    # given/when
    routes = [route.path for route in starlette_app.routes]

    # then
    assert "/sse" in routes
    assert any(path.startswith("/messages") for path in routes)


def test_sse_head():
    """Test HEAD request to the SSE endpoint."""
    # given/when
    sse_route = next(
        (route for route in starlette_app.routes if route.path == "/sse"), None
    )

    # then
    assert sse_route is not None
    assert "GET" in sse_route.methods


@pytest.mark.asyncio
async def test_handle_sse():
    """Test the handle_sse function handles SSE connections properly."""
    # given
    mock_request = MagicMock()
    mock_request.scope = {"path": "/sse"}
    mock_request.receive = AsyncMock()
    mock_request._send = AsyncMock()

    # Create mock for SSE context manager
    mock_streams = (AsyncMock(), AsyncMock())
    mock_connect_sse = AsyncMock()
    mock_connect_sse.__aenter__.return_value = mock_streams
    mock_connect_sse.__aexit__.return_value = None

    with (
        patch(
            "mcp_simple_tool.server.app.sse.connect_sse", return_value=mock_connect_sse
        ),
        patch("mcp_simple_tool.server.app.server.run", AsyncMock()) as mock_run,
        patch(
            "mcp_simple_tool.server.app.server.create_initialization_options",
            return_value={"foo": "bar"},
        ),
    ):

        # when
        response = await handle_sse(mock_request)

        # then
        assert response.status_code == 200
        mock_run.assert_awaited_once_with(
            mock_streams[0], mock_streams[1], {"foo": "bar"}
        )
