"""MCP tool handlers."""

from typing import Any, Dict, List, Union

import mcp.types as types
from mcp.server.lowlevel import Server

from mcp_simple_tool.semantic_search.search import semantic_search

from .config import Settings
from .http import fetch

settings = Settings()
server: Server = Server("mcp-website-fetcher-sse")  # type: ignore


@server.call_tool()  # type: ignore
async def fetch_tool(
    name: str, arguments: Dict[str, Any]
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """
    Handler for the fetch tool.

    Args:
        name: The name of the tool being called
        arguments: The arguments provided to the tool

    Returns:
        A list of content items

    Raises:
        ValueError: If the tool name is unknown or required arguments are missing
    """
    if name != "fetch":
        raise ValueError(f"Unknown tool: {name}")

    if "url" not in arguments:
        raise ValueError("Missing required argument 'url'")

    url: str = arguments["url"]
    text = await fetch(url, headers={"User-Agent": settings.user_agent})
    return [types.TextContent(type="text", text=text)]

@server.call_tool()  # type: ignore
async def search_docs_tool(
    name: str, arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """
    Handler for the search_docs tool.

    Args:
        name: The name of the tool being called
        arguments: The arguments provided to the tool

    Returns:
        A list of TextContent items with search results

    Raises:
        ValueError: If the tool name is unknown or required arguments are missing
    """
    if name != "search_docs":
        raise ValueError(f"Search docs tool: Unknown tool: {name}")

    query: str | None = arguments.get("query")
    if not query:
        raise ValueError("Missing required argument 'query'")

    k = int(arguments.get("k", 3))
    results = semantic_search(query, k)

    contents: List[types.TextContent] = []
    for r in results:
        pretty = (
            f"**{r['file']}**  (score {r['score']:.3f})\n\n"
            f"{r['excerpt'].strip()}\n\n---\n"
        )
        contents.append(types.TextContent(type="text", text=pretty))
    return contents


@server.list_tools()  # type: ignore
async def list_tools() -> List[types.Tool]:
    """
    List the available tools.

    Returns:
        A list of available tools
    """

    return [
        types.Tool(
            name="fetch",
            description="Fetches a website and returns its content",
            inputSchema={
                "type": "object",
                "required": ["url"],
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to fetch",
                    }
                },
            },
        ),
        types.Tool(
            name="search_docs",
            description="Semantic search across SDK docs (.md, .txt, .yml).",
            inputSchema={
                "type": "object",
                "required": ["query"],
                "properties": {
                    "query": {"type": "string", "description": "Search phrase"},
                    "k": {
                        "type": "integer",
                        "description": "Number of matches to return (default 3)",
                    },
                },
            },
        ),
    ]
