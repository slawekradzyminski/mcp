"""Tests for MCP tool handlers."""

import httpx
import mcp.types as types
import pytest
import respx

from mcp_simple_tool.server.handlers import fetch_tool, list_tools


@pytest.mark.asyncio
async def test_list_tools():
    """Test tool listing functionality."""
    # when
    tools = await list_tools()

    # then
    assert len(tools) == 1
    assert tools[0].name == "fetch"
    assert tools[0].description == "Fetches a website and returns its content"
    assert "url" in tools[0].inputSchema["properties"]


@pytest.mark.asyncio
async def test_fetch_tool_invalid_name():
    """Test error handling for invalid tool names."""
    # when/then
    with pytest.raises(ValueError, match="Unknown tool"):
        await fetch_tool("unknown", {"url": "http://example.com"})


@pytest.mark.asyncio
async def test_fetch_tool_missing_url():
    """Test error handling for missing URL parameter."""
    # when/then
    with pytest.raises(ValueError, match="Missing required argument 'url'"):
        await fetch_tool("fetch", {})


@respx.mock
@pytest.mark.asyncio
async def test_fetch_tool_success():
    """Test successful fetch tool execution."""
    # given
    respx.get("http://example.com").mock(
        return_value=httpx.Response(200, text="Example content")
    )

    # when
    result = await fetch_tool("fetch", {"url": "http://example.com"})

    # then
    assert len(result) == 1
    assert isinstance(result[0], types.TextContent)
    assert result[0].text == "Example content"
