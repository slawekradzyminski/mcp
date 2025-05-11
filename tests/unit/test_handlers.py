"""Tests for MCP tool handlers."""

import httpx
import mcp.types as types
import pytest
from unittest.mock import AsyncMock, MagicMock

from mcp_simple_tool.server.handlers import (
    http_fetch_tool,
    mcp,
    search_docs_tool,
    settings,
)


@pytest.mark.asyncio
async def test_tools_registration():
    """Test that tools are properly registered with FastMCP."""
    # when
    tools = await mcp.list_tools()

    # then
    assert len(tools) == 3

    # Find the fetch tool
    fetch_tool_def = next((t for t in tools if t.name == "http_fetch_tool"), None)
    assert fetch_tool_def is not None
    assert fetch_tool_def.inputSchema is not None
    assert "url" in fetch_tool_def.inputSchema["properties"]

    # Find the search_docs tool
    search_tool_def = next((t for t in tools if t.name == "search_docs_tool"), None)
    assert search_tool_def is not None
    assert search_tool_def.inputSchema is not None
    assert "query" in search_tool_def.inputSchema["properties"]
    assert "k" in search_tool_def.inputSchema["properties"]

    # Find the get_content tool
    get_local_content_tool_def = next(
        (t for t in tools if t.name == "get_local_content_tool"), None
    )
    assert get_local_content_tool_def is not None
    assert get_local_content_tool_def.inputSchema is not None
    assert "file" in get_local_content_tool_def.inputSchema["properties"]


@pytest.mark.asyncio
async def test_fetch_tool_success():
    """Test successful fetch tool execution."""
    # given - mock the fetch function
    mock_fetch = AsyncMock(return_value="Example content")

    # patch the http.fetch function
    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("mcp_simple_tool.server.handlers.fetch", mock_fetch)

        # when
        result = await http_fetch_tool("http://example.com")

        # then
        mock_fetch.assert_called_once_with(
            "http://example.com", headers={"User-Agent": settings.user_agent}
        )
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert result[0].text == "Example content"


@pytest.mark.asyncio
async def test_search_docs_tool():
    """Test the search_docs_tool with mocked semantic search."""
    # given
    # Patch the semantic_search function to return a known result
    with pytest.MonkeyPatch().context() as mp:
        mp.setattr(
            "mcp_simple_tool.server.handlers.semantic_search",
            lambda query, k: [
                {
                    "file": "test.md",
                    "score": 0.95,
                    "excerpt": "Test excerpt",
                }
            ],
        )

        # when
        result = await search_docs_tool("test query")

        # then
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "test.md" in result[0].text
        assert "0.950" in result[0].text
        assert "Test excerpt" in result[0].text
