"""MCP tool handlers."""

from typing import List

import mcp.types as types
from mcp.server.fastmcp import FastMCP

from mcp_simple_tool.semantic_search.search import semantic_search

from .config import Settings
from .http import fetch

settings = Settings()
mcp = FastMCP("mcp-website-fetcher-sse")


@mcp.tool()
async def fetch_tool(url: str) -> List[types.TextContent]:
    """
    Handler for the fetch tool.

    Args:
        url: The URL of the website to fetch

    Returns:
        A list of content items
    """
    text = await fetch(url, headers={"User-Agent": settings.user_agent})
    return [types.TextContent(type="text", text=text)]


@mcp.tool()
async def search_docs_tool(query: str, k: int = 3) -> List[types.TextContent]:
    """
    Handler for the search_docs tool.

    Args:
        query: The search query
        k: Number of results to return

    Returns:
        A list of TextContent items with search results
    """
    results = semantic_search(query, k)

    contents: List[types.TextContent] = []
    for r in results:
        pretty = (
            f"**{r['file']}**  (score {r['score']:.3f})\n\n"
            f"{r['excerpt'].strip()}\n\n---\n"
        )
        contents.append(types.TextContent(type="text", text=pretty))
    return contents
