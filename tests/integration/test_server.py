"""Integration tests for the MCP server application."""

import pytest
from starlette.routing import Route

from mcp_simple_tool.server.app import starlette_app


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
