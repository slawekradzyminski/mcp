"""HTTP utilities for the MCP server."""

from typing import Dict

from mcp.shared._httpx_utils import create_mcp_http_client


async def fetch(url: str, headers: Dict[str, str]) -> str:
    """
    Fetch a website and return its content as text.

    Args:
        url: The URL to fetch
        headers: HTTP headers to include in the request

    Returns:
        The text content of the response
    """
    async with create_mcp_http_client(headers=headers) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text
