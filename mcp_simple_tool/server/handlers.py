"""MCP tool handlers."""

import mcp.types as types
from mcp.server.lowlevel import Server

from .config import Settings
from .http import fetch

settings = Settings()
server = Server("mcp-website-fetcher-sse")


@server.call_tool()
async def fetch_tool(
    name: str, arguments: dict
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
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


@server.list_tools()
async def list_tools() -> list[types.Tool]:
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
        )
    ]
