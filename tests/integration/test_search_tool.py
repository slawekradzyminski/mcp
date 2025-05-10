"""Integration tests for the search_docs MCP tool."""

import pytest
from unittest.mock import patch, MagicMock

import mcp.types as types
from mcp_simple_tool.server.handlers import search_docs_tool


@pytest.mark.timeout(30)  # Allow more time for model loading
@patch("mcp_simple_tool.server.handlers.semantic_search", autospec=True)
async def test_search_docs_tool_response_format(mock_semantic_search) -> None:
    """Test that the search_docs tool returns properly formatted results."""
    # given
    mock_semantic_search.return_value = [
        {"file": "test.md", "score": 0.95, "excerpt": "This is a test document"},
        {"file": "other.md", "score": 0.8, "excerpt": "This is another test"},
    ]

    # when
    results = await search_docs_tool("search_docs", {"query": "test"})

    # then
    assert isinstance(results, list)
    assert len(results) == 2
    assert all(isinstance(item, types.TextContent) for item in results)
    assert "**test.md**" in results[0].text
    assert "(score 0.950)" in results[0].text
    assert "This is a test document" in results[0].text


async def test_search_docs_tool_validation() -> None:
    """Test that the search_docs tool validates its input."""
    # given
    invalid_tool_name = "invalid_tool"
    missing_query = {}

    # when/then
    with pytest.raises(ValueError, match="Unknown tool"):
        await search_docs_tool(invalid_tool_name, {"query": "test"})

    with pytest.raises(ValueError, match="Missing required argument"):
        await search_docs_tool("search_docs", missing_query)


@pytest.mark.timeout(30)  # Allow more time for model loading
@patch("mcp_simple_tool.server.handlers.semantic_search", autospec=True)
async def test_search_docs_tool_k_parameter(mock_search) -> None:
    """Test that the search_docs tool respects the k parameter."""
    # given
    # Create args with explicit k
    args_with_k = {"query": "test", "k": 5}
    mock_search.return_value = [
        {"file": f"doc{i}.md", "score": 1.0 - (i * 0.1), "excerpt": f"Content {i}"}
        for i in range(5)
    ]

    # when
    await search_docs_tool("search_docs", args_with_k)

    # then
    mock_search.assert_called_once_with("test", 5)
