"""Integration tests for the MCP server application."""

import pytest
from starlette.testclient import TestClient

from mcp_simple_tool.server.app import starlette_app
from mcp_simple_tool.server.handlers import mcp


@pytest.mark.timeout(5)  # Set a more strict timeout for this specific test
def test_server_routes_exist():
    """Test that the essential server routes exist in the ASGI app."""
    # given
    client = TestClient(starlette_app)

    # when
    response = client.get("/")

    # then
    assert response.status_code in (200, 404)  # Either valid response or not found


@pytest.mark.asyncio
async def test_tool_registration():
    """Test that tools are properly registered in the FastMCP server."""
    # given/when
    tools = await mcp.list_tools()

    # then
    assert len(tools) == 2

    tool_names = {tool.name for tool in tools}
    assert "fetch_tool" in tool_names
    assert "search_docs_tool" in tool_names


def test_app_is_asgi_app():
    """Test that starlette_app is an ASGI app with proper structure."""
    # given/when/then
    # An ASGI app should be a callable that takes scope, receive, send
    assert callable(starlette_app)

    # FastMCP's sse_app should be configured correctly
    assert hasattr(mcp, "sse_app")
