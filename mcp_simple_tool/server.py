import click
import mcp.types as types
import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp.shared._httpx_utils import create_mcp_http_client


async def fetch_website(
    url: str,
) -> list[types.TextContent]:
    headers = {
        "User-Agent": "MCP Test Server (github.com/modelcontextprotocol/python-sdk)"
    }
    async with create_mcp_http_client(headers=headers) as client:
        response = await client.get(url)
        await response.raise_for_status()
        return [types.TextContent(type="text", text=response.text)]


@click.command()
@click.option("--port", default=7000, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="sse",
    help="Transport type (only SSE is supported)",
)
def main(port: int, transport: str) -> int:
    mcp = FastMCP("mcp-website-fetcher-sse")

    @mcp.tool()
    async def fetch(url: str) -> list[types.TextContent]:
        """Fetches a website and returns its content"""
        return await fetch_website(url)

    if transport != "sse":
        print("Warning: Only SSE transport is supported. Using SSE transport.")

    print(f"Starting MCP website fetcher server on port {port}")
    print(f"Server URL: http://localhost:{port}/sse")

    starlette_app = mcp.sse_app()
    uvicorn.run(starlette_app, host="0.0.0.0", port=port)

    return 0
